import secrets
import string
import time
from datetime import datetime
import sys
from pathlib import Path
import os

BACKEND = Path(__file__).resolve().parents[1] / 'backend'
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))

import httpx

from app import main as _model_registry
from app.database import SessionLocal
from app.models.operator import Operator
from app.repositories.project_repository import ProjectRepository
from app.services.audit_service import append_event, verify_chain
from app.services.password_service import hash_password

BASE = 'http://127.0.0.1:8000'
suffix = secrets.token_hex(4)


def password():
  return 'Z!' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(18)) + '7a'


credentials = {}
with SessionLocal() as db:
  for role in ('TESTER', 'APPROVER', 'ADMIN'):
    username = f'accept-{role.lower()}-{suffix}'
    secret = password()
    item = Operator(username=username, display_name=f'Acceptance {role}', password_hash=hash_password(secret), role=role, is_active=True)
    db.add(item); db.flush(); append_event(db, 'OPERATOR_CREATED', actor_type='SYSTEM', resource_type='OPERATOR', resource_id=str(item.id), metadata={'username': username, 'role': role, 'acceptance': True})
    credentials[role] = (item.id, username, secret)
  project_id = next(project.id for project in ProjectRepository(db).list_active() if project.product_code == 'AUTOQA')
  db.commit()


def login(role):
  client = httpx.Client(base_url=BASE)
  _, username, secret = credentials[role]
  response = client.post('/api/auth/login', json={'username': username, 'password': secret}); response.raise_for_status()
  return client, response.json()['csrf_token']


tester, tester_csrf = login('TESTER')
for endpoint in ('/api/auth/me', '/api/projects', '/api/test-runs', '/api/dashboard/summary'):
  response = tester.get(endpoint); response.raise_for_status()
created = tester.post('/api/test-runs', headers={'X-CSRF-Token': tester_csrf}, json={'project_id': project_id, 'suite_name': 'dashboard-smoke', 'browser': 'chromium', 'environment': 'local'}); created.raise_for_status()
run = created.json()
denied = tester.post(f"/api/test-runs/{run['id']}/approve", headers={'X-CSRF-Token': tester_csrf}, json={'confirmation': 'APPROVE LOCAL TEST EXECUTION'})
assert denied.status_code == 403
tester.close()

approver, approver_csrf = login('APPROVER')
approved = approver.post(f"/api/test-runs/{run['id']}/approve", headers={'X-CSRF-Token': approver_csrf}, json={'confirmation': 'APPROVE LOCAL TEST EXECUTION'}); approved.raise_for_status()
started = approver.post(f"/api/test-runs/{run['id']}/execute", headers={'X-CSRF-Token': approver_csrf}, json={'confirm_local_execution': True}); started.raise_for_status()
for _ in range(90):
  detail = approver.get(f"/api/test-runs/{run['id']}"); detail.raise_for_status(); result = detail.json()
  if result['status'] in ('PASSED', 'FAILED', 'CANCELLED'): break
  time.sleep(1)
else: raise RuntimeError('Acceptance run did not reach a terminal state.')
assert result['status'] == 'PASSED'
assert result['created_by_operator_id'] == credentials['TESTER'][0]
assert result['approved_by_operator_id'] == credentials['APPROVER'][0]
assert result['executed_by_operator_id'] == credentials['APPROVER'][0]
approver.close()

admin, _ = login('ADMIN')
verification = admin.get('/api/audit/verify'); verification.raise_for_status(); assert verification.json()['valid'] is True
events = admin.get(f"/api/audit/events?resource_type=TEST_RUN&resource_id={run['id']}&limit=50"); events.raise_for_status(); assert len(events.json()) >= 3
admin.close()

with SessionLocal() as db:
  for role, (operator_id, _, _) in credentials.items():
    item = db.get(Operator, operator_id); item.is_active = False
    append_event(db, 'OPERATOR_DEACTIVATED', actor_type='SYSTEM', resource_type='OPERATOR', resource_id=str(operator_id), metadata={'acceptance_cleanup': True, 'role': role})
  db.commit(); valid, total, invalid = verify_chain(db); assert valid and invalid is None

print(f"acceptance_run_id={run['id']} status={result['status']} total={result['total_tests']} passed={result['passed_tests']} audit_valid=true audit_events={total} accounts_deactivated=true")
