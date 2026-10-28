"""
Company Task → AutoQA Orchestration Bridge.

This service is the "missing link" that connects:
  CompanyTask (URL + expected_flow + acceptance_criteria)
    → Playwright step generation (deterministic arrow-flow parser)
    → automated_execution.create_run()
    → execute_next_job() in background thread
    → auto-update task status on completion (PASSED / FAILED / BACK_TO_DEVELOPER)

Flow parsing strategy: DETERMINISTIC (Option A)
  Parses "Home → Products → iFive IoT → Page Opens" arrow notation
  Maps each token to the safest Playwright action type.
  No external AI required — works offline.

Execution mode: BACKGROUND THREAD (Option B)
  Non-blocking. Tester gets immediate 202 response.
  Frontend polls GET /api/company-tasks/{id}/run-status for progress.
"""
from __future__ import annotations

import json
import logging
import re
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.automated_execution import AutomatedRun, ExecutionArtifact, ExecutionJob
from app.models.company_task import CompanyTask
from app.models.connection_target import ConnectionTarget
from app.services import automated_execution
from app.services.audit_service import append_event

logger = logging.getLogger('autoqa.company_task_autoqa')

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# These path prefixes are safe to navigate — allow any relative path from URL
# (the engine validates the host is pinned; paths are checked against allowed list)
_SAFE_PATH_PATTERN = re.compile(r'^/[a-zA-Z0-9/_\-\.]*$')

# Keywords that map to CLICK actions in the flow
_CLICK_KEYWORDS = {
  'click', 'press', 'tap', 'select', 'choose', 'open', 'expand',
  'navigate', '→', '->', 'go to', 'visit',
}

# Keywords that suggest a page assertion (not navigation)
_ASSERT_KEYWORDS = {
  'page opens', 'page loads', 'visible', 'should see', 'verify', 'check',
  'confirm', 'loaded', 'appears', 'displayed', 'shown',
}

# Maximum generated steps (safety cap)
MAX_GENERATED_STEPS = 30


# ---------------------------------------------------------------------------
# URL → Connection Target
# ---------------------------------------------------------------------------

def _parse_url(target_url: str) -> tuple[str, str, int, str, bool]:
  """
  Parse target_url → (scheme, host, port, origin, tls_required).
  Raises HTTPException if URL is invalid or production.
  """
  try:
    parsed = urlparse(target_url.strip())
  except Exception:
    raise HTTPException(status_code=422, detail='Invalid target URL in task.')

  scheme = parsed.scheme.lower()
  if scheme not in ('http', 'https'):
    raise HTTPException(status_code=422, detail='Task target URL must use http or https.')

  host = parsed.hostname or ''
  if not host:
    raise HTTPException(status_code=422, detail='Task target URL has no host.')

  # Block production domains
  if any(prod in host.lower() for prod in ('prod.', 'production.', 'live.')):
    raise HTTPException(status_code=403, detail='Production targets are blocked for AutoQA.')

  default_port = 443 if scheme == 'https' else 80
  port = parsed.port or default_port
  origin = f'{scheme}://{host}' + (f':{port}' if port not in (80, 443) else '')
  tls = scheme == 'https'
  return scheme, host, port, origin, tls


def ensure_task_connection_target(db: Session, task: CompanyTask, operator_id: int) -> ConnectionTarget:
  """
  Find or create a ConnectionTarget for the given CompanyTask's target_url.
  Reuses an existing target if host+port matches.
  """
  if not task.target_url:
    raise HTTPException(status_code=400, detail='Task has no target URL.')

  scheme, host, port, origin, tls = _parse_url(task.target_url)

  # Find existing approved target for this host:port
  existing = db.scalar(
    select(ConnectionTarget).where(
      ConnectionTarget.normalized_host == host,
      ConnectionTarget.normalized_port == port,
      ConnectionTarget.project_id == (task.project_id or _fallback_project_id(db)),
      ConnectionTarget.lifecycle_state == 'APPROVED',
      ConnectionTarget.execution_enabled.is_(True),
    )
  )
  if existing:
    # Update allowed paths to include current URL path
    _extend_allowed_paths(existing, task.target_url)
    db.flush()
    return existing

  # Parse URL path to derive initial allowed paths
  parsed = urlparse(task.target_url)
  initial_path = parsed.path or '/'
  allowed_paths = _derive_allowed_paths(task.expected_flow, initial_path)

  target = ConnectionTarget(
    project_id=task.project_id or _fallback_project_id(db),
    target_key=f'TASK-TARGET-{task.id}-{host.replace(".", "-")}',
    name=f'AutoQA Target — {host}',
    description=f'Auto-created for Company Task #{task.id}: {task.title[:80]}',
    environment_type='LOCAL' if 'localhost' in host or '127.0.0.1' in host else 'DEVELOPMENT',
    base_url=origin,
    normalized_scheme=scheme,
    normalized_host=host,
    normalized_port=port,
    normalized_origin=origin,
    allowed_probe_paths_json=json.dumps(allowed_paths),
    tls_required=tls,
    tls_verify=True,
    connection_timeout_seconds=15,
    lifecycle_state='APPROVED',
    enabled=True,
    execution_enabled=True,
    execution_approved_by=operator_id,
    created_by=operator_id,
  )
  db.add(target)
  db.flush()
  return target


def _fallback_project_id(db: Session) -> int:
  """Return first project id as fallback when task has no project_id."""
  from app.models.project import Project
  row = db.scalar(select(Project.id).limit(1))
  return row or 1


def _extend_allowed_paths(target: ConnectionTarget, url: str) -> None:
  """Add the URL's path to the target's allowed_probe_paths list."""
  parsed = urlparse(url)
  path = parsed.path or '/'
  existing: list[str] = json.loads(target.allowed_probe_paths_json or '[]')
  if path not in existing:
    existing.append(path)
    target.allowed_probe_paths_json = json.dumps(existing)


def _derive_allowed_paths(expected_flow: str | None, initial_path: str) -> list[str]:
  """
  Derive a list of allowed paths from the expected_flow text + initial URL path.
  Scans for path-like tokens (/something/path) in the flow description.
  Always includes '/' and common web application paths.
  """
  paths = {'/', '/login', '/dashboard', '/products', '/cart', '/tasks', '/projects', '/settings', '/api/auth/login', '/api/health'}
  if initial_path and initial_path.startswith('/'):
    paths.add(initial_path)
    # Add parent paths
    parts = initial_path.strip('/').split('/')
    cumulative = ''
    for part in parts:
      cumulative += '/' + part
      paths.add(cumulative)

  if expected_flow:
    # Extract any explicit path tokens like /products/iot
    for match in re.finditer(r'/[a-zA-Z0-9/_\-]+', expected_flow):
      candidate = match.group()
      if _SAFE_PATH_PATTERN.match(candidate):
        paths.add(candidate)

  return sorted(paths)


# ---------------------------------------------------------------------------
# Flow → Playwright Steps (Deterministic Parser)
# ---------------------------------------------------------------------------

from app.services.website_discovery import NavigationMap

def _clean_diagram_flow(raw_flow: str) -> str:
  """Clean up ASCII tree diagrams (lines with │, ▼, ├──, etc.) into clean arrow notation."""
  if not raw_flow:
    return ""
  # Strip ASCII box-drawing characters and diagram arrows
  cleaned = re.sub(r'[\u2500-\u257F\u25B2\u25BC\u25C0\u25B6\u25C4\u25BA▼▲◄►│├└─│┌┐└┘├┤┬┴┼\|\+]+', ' ', raw_flow)
  lines = [l.strip() for l in cleaned.splitlines() if l.strip()]

  filtered = []
  for line in lines:
    if line.lower() in ('user', 'end', 'start', 'v', 'arrow', 'next', 'flow', 'login page'):
      continue
    filtered.append(line)

  merged = []
  i = 0
  while i < len(filtered):
    curr = filtered[i]
    curr_lower = curr.lower()
    if i + 1 < len(filtered):
      nxt = filtered[i + 1]
      if 'username' in curr_lower and 'fill' not in curr_lower:
        merged.append(f'fill username with {nxt}')
        i += 2
        continue
      elif 'password' in curr_lower and 'fill' not in curr_lower:
        merged.append(f'fill password with {nxt}')
        i += 2
        continue
      elif 'company' in curr_lower and 'select' not in curr_lower:
        merged.append(f'select {nxt} in Company')
        i += 2
        continue
    merged.append(curr)
    i += 1

  return ' → '.join(merged)


def parse_expected_flow_to_steps(task: CompanyTask, nav_map: NavigationMap | None = None) -> list[dict]:
  parsed = urlparse(task.target_url or '/')
  base_path = parsed.path or '/'

  raw_flow = (task.expected_flow or '').strip()
  if not raw_flow:
    return _minimal_steps(base_path)

  # Pre-process flow text to strip diagram box-drawing lines if user pasted an ASCII tree
  if any(ch in raw_flow for ch in ('│', '▼', '├──', '└──', '├', '└', '─')):
    raw_flow = _clean_diagram_flow(raw_flow)

  # Split on arrow & separator notations: →, ->, =>, >, newlines, semicolons, or pipes (preserving paths with /)
  parts = re.split(r'\s*(?:→|->|=>|>|\n|;|\|)\s*', raw_flow)
  parts = [p.strip() for p in parts if p.strip() and p.strip().lower() not in ('user', 'end', 'start', 'v')]

  steps: list[dict] = []
  step_num = 1

  # Step 1: Always navigate to the base URL path
  steps.append({'step_number': step_num, 'action': json.dumps({'action': 'NAVIGATE', 'path': base_path, 'risk_level': 'READ_ONLY'}), 'expected_result': f'Navigate to {base_path}'})
  step_num += 1

  steps.append({'step_number': step_num, 'action': json.dumps({'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'}), 'expected_result': 'Capture initial state'})
  step_num += 1

  for token in parts:
    if step_num > MAX_GENERATED_STEPS:
      break

    token_lower = token.lower()
    generated = _token_to_steps(token, token_lower, base_path, nav_map)

    for step_action in generated:
      if step_num > MAX_GENERATED_STEPS:
        break
      steps.append({'step_number': step_num, 'action': json.dumps(step_action), 'expected_result': f'{step_action["action"]} — {token}'})
      step_num += 1

  # Final screenshot always
  if step_num <= MAX_GENERATED_STEPS:
    steps.append({'step_number': step_num, 'action': json.dumps({'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'}), 'expected_result': 'Capture final state for evidence'})

  # Add acceptance criteria assertion if defined
  if task.acceptance_criteria and step_num <= MAX_GENERATED_STEPS:
    # Try to derive an assertion from the acceptance criteria
    criteria_steps = _criteria_to_assertions(task.acceptance_criteria, step_num)
    steps.extend(criteria_steps)

  return steps


def _field_to_selector(field_name: str, nav_map: NavigationMap | None = None) -> str:
  """Convert a field name (e.g. username, search, password) into Playwright CSS selector candidates."""
  clean = field_name.strip().strip('"\'')
  lower = clean.lower()
  slug = lower.replace(' ', '-').replace('_', '-')
  snake = lower.replace(' ', '_').replace('-', '_')

  if nav_map and nav_map.elements:
    for el in nav_map.elements:
      if lower in (el.text.lower(), (el.testId or '').lower(), (el.name or '').lower()):
        if el.testId:
          return f'[data-testid="{el.testId}"]'
        if el.tag in ('input', 'textarea', 'select') and el.name:
          return f'{el.tag}[name="{el.name}"]'

  if lower in ('username', 'user', 'user name', 'employee_number', 'employee number', 'emp_no'):
    return 'input[name="username"], input[name="user"], input[name="employee_number"], #username, #user, #employee_number, [data-testid="login-username"], [data-testid="username"], input[placeholder*="username" i], input[type="text"]'

  if lower in ('password', 'pass', 'pass word', 'pin'):
    return 'input[type="password"], input[name="password"], #password, [data-testid="login-password"], [data-testid="password"], input[placeholder*="password" i]'

  if lower in ('search', 'search box', 'query', 'find'):
    return 'input[type="search"], input[name="search"], input[name="q"], input[name="query"], #search, [data-testid*="search"], input[placeholder*="search" i]'

  if lower in ('email', 'email address', 'e-mail'):
    return 'input[type="email"], input[name="email"], #email, [data-testid="email"], input[placeholder*="email" i]'

  candidates = [
    f'select[name*="{snake}" i]',
    f'select[name="{snake}_id"]',
    f'select[name="{snake}"]',
    f'select[name="{slug}"]',
    f'select.{snake}_id',
    f'select.{snake}',
    f'input[name="{snake}"]',
    f'input[name="{slug}"]',
    f'input[name="{lower}"]',
    f'input[id="{snake}"]',
    f'input[id="{slug}"]',
    f'[data-testid="{slug}"]',
    f'[data-testid*="{slug}"]',
    f'input[placeholder*="{clean}" i]',
    f'textarea[name="{snake}"]',
    f'textarea[name="{slug}"]',
    f'#{snake}',
    f'#{slug}',
  ]

  unique = list(dict.fromkeys(candidates))
  return ', '.join(unique)


def _parse_fill_token(token: str, nav_map: NavigationMap | None = None) -> list[dict] | None:
  """
  Try to parse token as a FILL, TYPE, INPUT, SET, SELECT, or SEARCH action.
  Returns list of step dicts if matched, or None if not a fill token.
  """
  clean_token = token.strip()
  token_lower = clean_token.lower()

  # Pattern 1: Fill/Input <field> with/as/= <value>
  m = re.match(r'^(?:fill|input)\s+["\']?([^"\'=]+?)["\']?\s+(?:with|as|=)\s+["\']?([^"\']+)["\']?$', clean_token, re.IGNORECASE)
  if m:
    field_name, value = m.group(1).strip(), m.group(2).strip()
    selector = _field_to_selector(field_name, nav_map)
    return [
      {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
      {'action': 'FILL', 'selector': selector, 'value': value, 'risk_level': 'SAFE_INTERACTION'},
    ]

  # Pattern 2: Type/Enter/Input <value> in/into/for/to <field>
  m = re.match(r'^(?:type|enter|input)\s+["\']?(.+?)["\']?\s+(?:in|into|for|to)\s+["\']?(.+?)["\']?$', clean_token, re.IGNORECASE)
  if m:
    value, field_name = m.group(1).strip(), m.group(2).strip()
    field_clean = re.sub(r'\s+(field|box|input|textbox|area)$', '', field_name, flags=re.IGNORECASE).strip()
    selector = _field_to_selector(field_clean, nav_map)
    return [
      {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
      {'action': 'FILL', 'selector': selector, 'value': value, 'risk_level': 'SAFE_INTERACTION'},
    ]

  # Pattern 3: Set <field> to/= <value>
  m = re.match(r'^set\s+["\']?([^"\'=]+?)["\']?\s+(?:to|=)\s+["\']?([^"\']+)["\']?$', clean_token, re.IGNORECASE)
  if m:
    field_name, value = m.group(1).strip(), m.group(2).strip()
    selector = _field_to_selector(field_name, nav_map)
    return [
      {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
      {'action': 'FILL', 'selector': selector, 'value': value, 'risk_level': 'SAFE_INTERACTION'},
    ]

  # Pattern 4: Search for <query> / Search <query>
  m = re.match(r'^search\s+(?:for\s+)?["\']?(.+?)["\']?$', clean_token, re.IGNORECASE)
  if m:
    query = m.group(1).strip()
    search_sel = 'input[type="search"], input[name*="search" i], input[placeholder*="search" i], [data-testid*="search"], #search'
    btn_sel = 'button[type="submit"], button:has-text("Search"), [data-testid*="search-submit"]'
    return [
      {'action': 'ASSERT_VISIBLE', 'selector': search_sel, 'risk_level': 'READ_ONLY'},
      {'action': 'FILL', 'selector': search_sel, 'value': query, 'risk_level': 'SAFE_INTERACTION'},
      {'action': 'CLICK', 'selector': btn_sel, 'risk_level': 'SAFE_INTERACTION'},
    ]

  # Pattern 5: Select <option> from/in <dropdown>
  m = re.match(r'^select\s+["\']?(.+?)["\']?\s+(?:from|in)\s+["\']?(.+?)["\']?$', clean_token, re.IGNORECASE)
  if m:
    value, field_name = m.group(1).strip(), m.group(2).strip()
    field_clean = re.sub(r'\s+(dropdown|select|menu)$', '', field_name, flags=re.IGNORECASE).strip()
    f_lower = field_clean.lower()
    selector = f'select[name*="{f_lower}" i], select[name="{f_lower}_id"], select[name="{f_lower}"], select.{f_lower}_id, select.{f_lower}, select#{f_lower}, [data-testid*="{f_lower}"]'
    return [
      {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
      {'action': 'SELECT', 'selector': selector, 'value': value, 'risk_level': 'SAFE_INTERACTION'},
    ]
    return [
      {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
      {'action': 'SELECT', 'selector': selector, 'value': value, 'risk_level': 'SAFE_INTERACTION'},
    ]

  # Pattern 6: Key-Value pair "<field> : <value>" or "<field> = <value>"
  m = re.match(r'^([a-zA-Z0-9_\-\s]{2,30})\s*[:=]\s*(.+)$', clean_token)
  if m and not token_lower.startswith('http') and not token_lower.startswith('/'):
    field_name, value = m.group(1).strip(), m.group(2).strip()
    if field_name.lower() not in ('http', 'https', 'url', 'path', 'page'):
      selector = _field_to_selector(field_name, nav_map)
      return [
        {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
        {'action': 'FILL', 'selector': selector, 'value': value, 'risk_level': 'SAFE_INTERACTION'},
      ]

  return None


def _token_to_steps(token: str, token_lower: str, base_path: str, nav_map: NavigationMap | None = None) -> list[dict]:
  """Convert a single flow token to one or more Playwright action dicts."""
  # Skip "home" / "homepage" — already navigated
  if token_lower in ('home', 'homepage', 'landing page', 'start'):
    return []

  # Explicit screenshot instruction
  if token_lower in ('screenshot', 'capture screenshot', 'take screenshot', 'screenshot evidence', 'capture final state', 'capture evidence'):
    return [{'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'}]

  # Check if token is a FILL, TYPE, SET, SEARCH, or SELECT instruction
  fill_steps = _parse_fill_token(token, nav_map)
  if fill_steps:
    return fill_steps

  # Navigation verbs: "Navigate to /products", "Go to /login", "Visit /dashboard"
  nav_match = re.match(r'^(?:navigate\s+to|go\s+to|visit|open)\s+(.+)$', token, re.IGNORECASE)
  if nav_match:
    target_path = nav_match.group(1).strip()
    if target_path.startswith('/') and _SAFE_PATH_PATTERN.match(target_path):
      return [
        {'action': 'NAVIGATE', 'path': target_path, 'risk_level': 'READ_ONLY'},
        {'action': 'ASSERT_URL', 'expected': target_path, 'risk_level': 'READ_ONLY'},
        {'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
      ]

  # Verification verbs: "assert visible Logo", "check visible Navbar"
  assert_vis_match = re.match(r'^(?:assert\s+visible|check\s+visible|verify\s+visible|assert)\s+(.+)$', token, re.IGNORECASE)
  if assert_vis_match:
    target_label = assert_vis_match.group(1).strip().strip('"\'')
    selector = _label_to_selector(target_label, nav_map)
    return [
      {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
      {'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
    ]

  # Verification verbs: "assert url /contact"
  assert_url_match = re.match(r'^(?:assert\s+url|check\s+url|verify\s+url)\s+(.+)$', token, re.IGNORECASE)
  if assert_url_match:
    target_path = assert_url_match.group(1).strip().strip('"\'')
    return [
      {'action': 'ASSERT_URL', 'expected': target_path, 'risk_level': 'READ_ONLY'},
      {'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
    ]

  # Verification verbs: "Verify 'Item Added'", "Check Success", "Confirm 'Order Placed'"
  assert_match = re.match(r'^(?:verify|check|confirm|ensure|should\s+see|must\s+see)\s+(.+)$', token, re.IGNORECASE)
  if assert_match:
    expected_text = assert_match.group(1).strip().strip('"\'')
    if expected_text:
      return [
        {'action': 'ASSERT_TEXT', 'selector': 'body', 'expected': expected_text, 'risk_level': 'READ_ONLY'},
        {'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
      ]

  # Explicit URL or path token (e.g. https://ifive.in/ or /products/iot)
  if token.startswith(('http://', 'https://')) or (token.startswith('/') and _SAFE_PATH_PATTERN.match(token)):
    rel_path = '/'
    if token.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        parsed_p = urlparse(token).path
        rel_path = parsed_p if parsed_p else '/'
    else:
        rel_path = token
    return [
      {'action': 'NAVIGATE', 'path': rel_path, 'risk_level': 'READ_ONLY'},
      {'action': 'ASSERT_URL', 'expected': rel_path, 'risk_level': 'READ_ONLY'},
      {'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
    ]

  # "Page Opens" / "Page Loads" → assert URL + screenshot
  if any(kw in token_lower for kw in ('opens', 'loads', 'loaded', 'displayed', 'visible', 'appears')):
    # Try to detect page name for assertion
    page_name = re.sub(r'\s*(opens|loads|loaded|displayed|visible|appears).*$', '', token, flags=re.IGNORECASE).strip()
    if page_name:
      selector = _label_to_selector(page_name)
      return [
        {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
        {'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
      ]
    return [{'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'}]

  # Login page navigation (only if not a click or fill instruction)
  if 'login' in token_lower and not token_lower.startswith(('click', 'press', 'tap')) and not any(kw in token_lower for kw in ('fill', 'type', 'enter', 'input', ':=')):
    return [
      {'action': 'NAVIGATE', 'path': '/login', 'risk_level': 'READ_ONLY'},
      {'action': 'ASSERT_VISIBLE', 'selector': 'input[type="text"], input[name="username"], [data-testid="login-username"]', 'risk_level': 'READ_ONLY'},
      {'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
    ]

  # Dashboard/home navigation
  if 'dashboard' in token_lower and not token_lower.startswith(('click', 'press', 'tap')):
    return [
      {'action': 'ASSERT_URL', 'expected': '/dashboard', 'risk_level': 'READ_ONLY'},
      {'action': 'ASSERT_VISIBLE', 'selector': 'main, [data-testid="dashboard"], .dashboard', 'risk_level': 'READ_ONLY'},
    ]

  # Strip leading action verb like "click", "press", "tap"
  clean_label = re.sub(r'^(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?', '', token, flags=re.IGNORECASE).strip()
  if not clean_label:
    clean_label = token

  # Generic button/link click
  selector = _label_to_selector(clean_label, nav_map)
  return [
    {'action': 'ASSERT_VISIBLE', 'selector': selector, 'risk_level': 'READ_ONLY'},
    {'action': 'CLICK', 'selector': selector, 'risk_level': 'SAFE_INTERACTION'},
  ]


def _label_to_selector(label: str, nav_map: NavigationMap | None = None) -> str:
  """Convert a human-readable label to a Playwright selector. 
  Phase 3.5: Uses nav_map to find the exact existing element."""
  clean = label.strip().strip('"\'')
  if not clean:
    return 'body'
  
  if nav_map and nav_map.elements:
      for el in nav_map.elements:
          if clean.lower() == el.text.lower():
              if el.testId:
                  return f'[data-testid="{el.testId}"]'
              if el.tag == 'a' and el.href:
                  return f'a[href="{el.href}"]'
              return f'{el.tag}:has-text("{clean}")'

  # Clean Playwright selector using valid Playwright locator syntax
  lower = clean.lower()
  testid = lower.replace(' ', '-')

  if lower in ('logo', 'brand', 'company logo', 'site logo'):
    return 'img, svg, .logo, #logo, [data-testid*="logo"], a.navbar-brand, .brand, img[alt*="logo" i]'

  if lower in ('navigation bar', 'navbar', 'navigation', 'topbar', 'menu bar', 'header'):
    return 'nav, header, .navbar, .nav, [role="navigation"], .topbar'

  extra = ""
  if any(kw in lower for kw in ('sign in', 'login', 'log in', 'submit')):
      extra = ', button[type="submit"], button.btn-submit, input[type="submit"]'

  return f'button:has-text("{clean}"), a:has-text("{clean}"){extra}, [data-testid*="{testid}"], text="{clean}"'


def _criteria_to_assertions(criteria: str, start_step: int) -> list[dict]:
  """
  Generate basic ASSERT_VISIBLE steps from acceptance criteria text.
  Looks for quoted strings or "should see X" patterns.
  """
  steps = []
  step_num = start_step

  # Find quoted text → assert it's visible
  quoted = re.findall(r'"([^"]{3,80})"', criteria)
  for q in quoted[:3]:  # max 3 criteria assertions
    if step_num > MAX_GENERATED_STEPS:
      break
    steps.append({
      'step_number': step_num,
      'action': json.dumps({'action': 'ASSERT_TEXT', 'selector': 'body', 'expected': q, 'risk_level': 'READ_ONLY'}),
      'expected_result': f'Acceptance criteria: "{q}" is visible',
    })
    step_num += 1

  return steps


def _minimal_steps(base_path: str) -> list[dict]:
  """Fallback when no expected_flow is defined."""
  return [
    {'step_number': 1, 'action': json.dumps({'action': 'NAVIGATE', 'path': base_path, 'risk_level': 'READ_ONLY'}), 'expected_result': 'Navigate to target'},
    {'step_number': 2, 'action': json.dumps({'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'}), 'expected_result': 'Capture page state'},
    {'step_number': 3, 'action': json.dumps({'action': 'ASSERT_VISIBLE', 'selector': 'body', 'risk_level': 'READ_ONLY'}), 'expected_result': 'Page body visible'},
    {'step_number': 4, 'action': json.dumps({'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'}), 'expected_result': 'Final evidence screenshot'},
  ]


# ---------------------------------------------------------------------------
# Run creation
# ---------------------------------------------------------------------------

def _build_run_snapshot(steps: list[dict]) -> str:
  """Wrap steps into the snapshot format expected by automated_execution."""
  return json.dumps({'steps': steps})


def _sanitize_step_selector(selector_str: str | None) -> str:
  if not selector_str:
    return 'body'
  s = selector_str.strip()
  # Convert invalid pseudo-class :text(...) to valid Playwright locator syntax text=...
  s = re.sub(r':text\((["\'])(.*?)\1\)', r'text=\1\2\1', s)
  # Remove empty quote fragments
  parts = [
    p.strip() for p in s.split(',')
    if p.strip() and not p.strip().endswith(':has-text("")') and not p.strip().endswith(":has-text('')")
    and p.strip() != '[data-testid=""]' and p.strip() != "[data-testid='']" and p.strip() != 'text=""' and p.strip() != "text=''"
  ]
  cleaned = ', '.join(parts)
  return cleaned if cleaned else 'body'


def _create_autoqa_run(db: Session, task: CompanyTask, operator_id: int, custom_steps: list[Any] | None = None) -> AutomatedRun:
  """
  Create the AutomatedRun (in DRAFT state) from CompanyTask data.
  Uses automated_execution internals directly (bypassing the usual
  ConnectionTarget validation flow since we control target creation).
  """
  from app.models.automated_execution import AutomatedRunCase, ExecutionEvent
  from app.services.automated_execution import (
    add_event, next_run_key, validate_snapshot_actions, snapshot_risk_level,
  )

  target = ensure_task_connection_target(db, task, operator_id)

  if custom_steps:
      # Convert custom steps from UI schema to backend Playwright schema
      steps = []
      for cs in custom_steps:
          target_raw = (cs.target or '').strip()
          # Skip diagram noise steps (e.g. target is │, ▼, ├──)
          if target_raw in ('│', '▼', '▲', '├──', '└──', '├', '└', '─', 'User', 'End'):
              continue

          action_dict = {
              'action': cs.action_type,
              'risk_level': getattr(cs, 'risk_level', 'SAFE_INTERACTION')
          }
          if cs.action_type in ('NAVIGATE', 'ASSERT_URL'):
              action_dict['path'] = cs.target or cs.expected_result
          elif cs.action_type == 'SCREENSHOT':
              pass
          else:
              action_dict['selector'] = _sanitize_step_selector(cs.target)

          steps.append({
              'step_number': len(steps) + 1,
              'action': json.dumps(action_dict),
              'expected_result': cs.expected_result
          })
      if not steps:
          steps = parse_expected_flow_to_steps(task)
  else:
      steps = parse_expected_flow_to_steps(task)
      
  snapshot_json = _build_run_snapshot(steps)

  # Validate (safety checks)
  try:
    validated = validate_snapshot_actions(json.loads(snapshot_json))
  except HTTPException as exc:
    raise HTTPException(
      status_code=422,
      detail=f'AutoQA step generation failed safety check: {exc.detail}',
    ) from exc

  if not validated:
    raise HTTPException(status_code=422, detail='No valid AutoQA steps could be generated for this task.')

  risk = snapshot_risk_level(json.loads(snapshot_json))

  run = AutomatedRun(
    project_id=target.project_id,
    run_key=next_run_key(db),
    name=f'AutoQA: {task.title[:120]}',
    description=(
      f'Module: {task.module or "—"} | Feature: {task.feature or "—"}\n'
      f'URL: {task.target_url}\n'
      f'Flow: {(task.expected_flow or "")[:200]}\n'
      f'Criteria: {(task.acceptance_criteria or "")[:200]}'
    ),
    target_id=target.id,
    target_version=target.version,
    target_origin=target.normalized_origin,
    timeout_seconds=120,
    max_retries=0,
    dns_pinning_status='ENFORCED',
    runtime_secret_status='NOT_REQUIRED',
    risk_level=risk,
    created_by=operator_id,
  )
  db.add(run)
  db.flush()

  run.cases.append(AutomatedRunCase(
    project_id=run.project_id,
    case_snapshot_json=snapshot_json,
    sort_order=1,
  ))
  run.total_steps = len(validated)
  add_event(db, run.id, 'autoqa_task_run_created', metadata={
    'task_id': task.id,
    'task_title': task.title[:80],
    'steps': len(validated),
    'risk_level': risk,
  })
  return run


# ---------------------------------------------------------------------------
# Result → Task status update
# ---------------------------------------------------------------------------

def update_task_from_run_result(task_id: int, run: AutomatedRun) -> None:
  """
  Called from the background thread after Playwright completes.
  Opens a fresh DB session (thread-safe) and updates the CompanyTask.
  Auto-creates a Defect on FAILED runs.
  """
  with SessionLocal() as db:
    try:
      task = db.get(CompanyTask, task_id)
      if not task:
        logger.warning('CompanyTask %d not found during result callback.', task_id)
        return

      now = datetime.utcnow()
      run_status = run.status  # PASSED | FAILED | TIMED_OUT | BLOCKED | CANCELLED

      task.autoqa_completed_at = now
      task.autoqa_notes = run.safe_error_message or 'AutoQA execution completed.'

      if run_status == 'PASSED':
        task.status = 'PASSED'
        task.autoqa_result = 'PASS'
        task.autoqa_notes = 'All AutoQA steps completed successfully.'
        logger.info('CompanyTask %d: AutoQA PASSED', task_id)

      elif run_status in ('FAILED', 'TIMED_OUT', 'BLOCKED'):
        task.autoqa_result = 'FAIL'
        task.back_to_developer_at = now
        task.retest_count = (task.retest_count or 0) + 1
        task.autoqa_notes = (run.safe_error_message or 'AutoQA execution failed.') + f' (Retest #{task.retest_count})'
        # Auto-transition to BACK_TO_DEVELOPER
        task.status = 'BACK_TO_DEVELOPER'
        logger.warning('CompanyTask %d: AutoQA FAILED (retest #%d)', task_id, task.retest_count)

      else:
        # CANCELLED or unknown
        task.status = 'TESTING_L2'  # revert to tester queue
        task.autoqa_result = None
        task.autoqa_run_id = None
        task.autoqa_notes = f'AutoQA was cancelled or interrupted (status: {run_status}).'
        logger.warning('CompanyTask %d: AutoQA cancelled/interrupted, reverted to TESTING_L2', task_id)

      append_event(
        db,
        'COMPANY_TASK_AUTOQA_COMPLETED',
        resource_type='COMPANY_TASK',
        resource_id=str(task_id),
        metadata={
          'run_status': run_status,
          'task_status': task.status,
          'retest_count': task.retest_count,
        },
      )
      db.commit()

      # Safely auto-create defect after task status is committed
      if run_status in ('FAILED', 'TIMED_OUT', 'BLOCKED'):
        with SessionLocal() as defect_db:
          t = defect_db.get(CompanyTask, task_id)
          r = defect_db.get(AutomatedRun, run.id)
          if t and r:
            _auto_create_defect(defect_db, t, r)
            defect_db.commit()
    except Exception:
      logger.exception('Error updating CompanyTask %d from AutoQA run result', task_id)
      db.rollback()


def _auto_create_defect(db: Session, task: CompanyTask, run: AutomatedRun) -> None:
  """Create a Defect record linked to the failed AutoQA run."""
  try:
    from app.models.defect import Defect, DefectEvidenceLink
    from app.models.test_management import TestProject
    from sqlalchemy.orm import Session as _Session

    # Find or fallback test project
    test_project = db.scalar(
      select(TestProject).where(TestProject.access_project_id == (task.project_id or 1))
    )
    test_project_id = test_project.id if test_project else (task.project_id or 1)
    creator_id = task.created_by

    defect_key = f'DEF-CT{task.id}-R{task.retest_count}'
    # Ensure unique
    if db.scalar(select(Defect).where(Defect.defect_key == defect_key)):
      defect_key = f'{defect_key}-{run.id}'

    defect = Defect(
      access_project_id=task.project_id or 1,
      defect_key=defect_key,
      title=f'AutoQA Failure: {task.title[:180]}',
      description=(
        f'AutoQA failed on Company Task #{task.id} (Retest #{task.retest_count}).\n\n'
        f'Target URL: {task.target_url}\n'
        f'Expected Flow: {task.expected_flow or "—"}\n\n'
        f'Error: {run.safe_error_message or "Playwright execution failed."}'
      ),
      project_id=test_project_id,
      automated_run_id=run.id,
      severity=task.severity or 'HIGH',
      priority=task.priority or 'HIGH',
      status='NEW',
      reporter_id=creator_id,
      created_by=creator_id,
      environment=task.environment or 'local',
      actual_result=run.safe_error_message or 'AutoQA steps did not complete successfully.',
      expected_result=task.acceptance_criteria or task.expected_result or 'All AutoQA steps complete successfully.',
    )
    db.add(defect)
    db.flush()

    # Link execution artifacts (screenshots) as evidence
    artifacts = list(db.scalars(
      select(ExecutionArtifact).where(ExecutionArtifact.run_id == run.id)
    ))
    for art in artifacts:
      db.add(DefectEvidenceLink(
        project_id=task.project_id or 1,
        defect_id=defect.id,
        execution_artifact_id=art.id,
        link_type='SOURCE',
        created_by=creator_id,
      ))
    db.flush()
    logger.info('Auto-created Defect %s for CompanyTask %d', defect_key, task.id)
  except Exception:
    logger.exception('Failed to auto-create defect for CompanyTask %d', task.id)
    # Don't raise — defect creation failure should not block status update


# ---------------------------------------------------------------------------
# Main trigger entry point
# ---------------------------------------------------------------------------

def trigger_autoqa_for_task(db: Session, task: CompanyTask, operator_id: int, custom_steps: list[Any] | None = None) -> AutomatedRun:
  """
  Main entry point: Tester clicks "Approve & Run AutoQA".

  1. Validates task readiness
  2. Creates ConnectionTarget if needed
  3. Parses flow → Playwright steps
  4. Creates AutomatedRun (DRAFT → QUEUED)
  5. Updates task status → TEST_APPROVED → AUTOQA_RUNNING
  6. Launches background execution thread
  7. Returns the AutomatedRun immediately (non-blocking)
  """
  # ── Validation ────────────────────────────────────────────────────────
  if not task.target_url:
    raise HTTPException(status_code=400, detail='Task has no Target URL. AutoQA cannot run.')
  if not task.expected_flow:
    raise HTTPException(status_code=400, detail='Task has no Expected Flow. AutoQA needs a flow to follow.')
  # ── Auto-advance to TESTING_L2 if needed ────────────────────────────
  if task.status in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'DEVELOPER_COMPLETED', 'BACK_TO_DEVELOPER'):
    now = datetime.utcnow()
    if not task.in_progress_at:
      task.in_progress_at = now
    task.developer_completed_at = now
    task.status = 'TESTING_L2'
    db.commit()

  if task.status not in ('TESTING_L2', 'TEST_APPROVED', 'AUTOQA_RUNNING'):
    raise HTTPException(status_code=409, detail=f'Task status {task.status} cannot run AutoQA.')

  # ── Create AutomatedRun ───────────────────────────────────────────────
  run = _create_autoqa_run(db, task, operator_id, custom_steps)

  # Queue it
  run.status = 'QUEUED'
  db.add(ExecutionJob(project_id=run.project_id, run_id=run.id, status='QUEUED'))

  # ── Update task status ────────────────────────────────────────────────
  now = datetime.utcnow()
  task.status = 'AUTOQA_RUNNING'
  task.test_approved_at = now
  task.autoqa_started_at = now
  task.autoqa_run_id = run.id
  task.approved_by_tester_id = operator_id

  append_event(
    db,
    'COMPANY_TASK_AUTOQA_TRIGGERED',
    operator_id=operator_id,
    resource_type='COMPANY_TASK',
    resource_id=str(task.id),
    metadata={
      'run_key': run.run_key,
      'target_url': task.target_url,
      'steps': run.total_steps,
    },
  )
  db.commit()

  task_id = task.id
  run_id = run.id

  # ── Background execution thread ───────────────────────────────────────
  def _run_in_background() -> None:
    logger.info('AutoQA background thread started for CompanyTask %d (run %d)', task_id, run_id)
    try:
      with SessionLocal() as bg_db:
        completed_run = automated_execution.execute_next_job(
          bg_db,
          worker_key=f'company-task-worker-{task_id}',
          target_run_id=run_id,
        )
        if not completed_run:
          completed_run = bg_db.get(AutomatedRun, run_id)

        if completed_run and completed_run.status in ('PASSED', 'FAILED', 'TIMED_OUT', 'BLOCKED', 'CANCELLED'):
          update_task_from_run_result(task_id, completed_run)
        else:
          logger.warning('execute_next_job returned None or running for CompanyTask %d', task_id)
          # Revert task to TESTING_L2 if worker failed to start
          with SessionLocal() as revert_db:
            t = revert_db.get(CompanyTask, task_id)
            if t and t.status == 'AUTOQA_RUNNING':
              t.status = 'TESTING_L2'
              t.autoqa_run_id = None
              t.autoqa_notes = 'AutoQA worker could not start. Reverted to TESTING_L2.'
              revert_db.commit()
    except Exception:
      logger.exception('AutoQA background thread crashed for CompanyTask %d', task_id)
      # Best-effort status revert
      try:
        with SessionLocal() as fallback_db:
          t = fallback_db.get(CompanyTask, task_id)
          if t and t.status == 'AUTOQA_RUNNING':
            t.status = 'TESTING_L2'
            t.autoqa_notes = 'AutoQA execution error — reverted to TESTING_L2. Check server logs.'
            fallback_db.commit()
      except Exception:
        pass

  thread = threading.Thread(
    target=_run_in_background,
    name=f'autoqa-task-{task_id}',
    daemon=True,
  )
  thread.start()
  logger.info('AutoQA background thread launched for CompanyTask %d', task_id)

  return run
