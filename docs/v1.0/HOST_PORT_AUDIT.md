# HOST_PORT_AUDIT.md — iFive AutoQA X (live 26-router / 19-page product)

## Canonical configuration (correct, centralized)

`backend/app/config.py::Settings` already centralizes the important values via
env vars with safe local-only defaults and validates them (`validate()` rejects
any non-loopback `AUTOQA_FRONTEND_URL`). This is good, existing design — not a
finding, just confirming the pattern that other files below should have followed.

`frontend/vite.config.ts` / `mock-task-portal/frontend/vite.config.ts` /
`demo-product/frontend/vite.config.ts` correctly declare their own ports
(5173 / 5174 / 5175) and proxy targets (8000 / 8001 / 8002) in one place each.

## Real findings: hardcoded literals outside the canonical config

Scanned `backend/app/**/*.py` for `127.0.0.1` / `localhost` outside
`config.py` and `connectors/`. 11 files contain literal host:port strings not
read from `settings`:

| File | Hits | Detail |
| --- | --- | --- |
| `services/task_import_service.py` | 8 | `http://localhost:5175` (demo product default, x3), `http://localhost:8001` (mock task portal error message), `http://localhost:8000` (self-referencing report URLs, x2), plus the `https://ifive.in` / `ifive.in` branch noted below |
| `validation/api_validator.py` | 5 | loopback references in validator logic |
| `ai/local_provider.py` | 1 |  |
| `api/release_governance.py` | 1 | orphaned router (see DEAD_CODE_REPORT.md) |
| `cli/static_server.py` | 1 |  |
| `models/phase13_models.py` | 1 | orphaned feature |
| `services/company_task_autoqa.py` | 1 |  |
| `services/diagnostics.py` | 1 |  |
| `services/playwright_runner.py` | 1 |  |
| `services/release_governance.py` | 1 | orphaned router |
| `services/target_policy.py` | 1 |  |

## Flagged for your review, not modified

`task_import_service.py` lines 88-92, 203, 255 contain an `is_ifive` branch that
resolves to a **real production domain**: `https://ifive.in`. It only activates
if a project's name or URL already contains "ifive" — the current Demo ERP flow
never triggers it. This reads as deliberate design for the PDF's documented
"Controlled pilot sequence" (Section 19: swap the demo URL for an approved
company URL post-approval), not an accident. Per project rule ("do not guess,
search for, or access any real iFive URL") this is outside what I should alter
unilaterally — flagging for your explicit decision rather than touching it.

## Recommended fix (safe, mechanical, not yet applied)

Add two settings to `config.py`:

```python
mock_task_portal_url: str = field(default_factory=lambda: os.getenv('AUTOQA_MOCK_TASK_PORTAL_URL', 'http://127.0.0.1:8001'))
demo_product_url: str = field(default_factory=lambda: os.getenv('AUTOQA_DEMO_PRODUCT_URL', 'http://127.0.0.1:5175'))
```

Then replace the 6 non-`ifive.in` literal occurrences in `task_import_service.py`
(and the single-hit files above where applicable) with `settings.mock_task_portal_url`
/ `settings.demo_product_url`. This is a small, mechanical, low-risk change —
holding off applying it until you confirm, since it touches the exact service
I verified end-to-end this session (real Playwright PASS + real callback) and
I want a full regression run immediately after, not bundled with report-writing.

## Not touched

The `is_ifive` / `ifive.in` branch — explicitly deferred to you, as above.
