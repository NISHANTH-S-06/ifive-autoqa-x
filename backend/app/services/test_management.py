import csv
import hashlib
import json
import re
from io import StringIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.operator import Operator
from app.models.test_management import (
  ManagedTestCase,
  ManagedTestSuite,
  ManualEvidence,
  ManualStepResult,
  ManualTestRun,
  ManualTestRunCase,
  Tag,
  TestCaseStep,
  TestCaseTag,
  TestCaseVersion,
  TestModule,
  TestProject,
)

ACTIVE = 'ACTIVE'
ARCHIVED = 'ARCHIVED'
LIFECYCLE_ACTIVE = {'DRAFT', 'IN_REVIEW', 'APPROVED', 'REJECTED'}
EDITABLE_STATES = {'DRAFT', 'REJECTED'}
RESULT_TERMINAL = {'PASSED', 'FAILED', 'BLOCKED', 'SKIPPED'}
ALLOWED_EVIDENCE = {
  '.png': ('image/png', 'PNG'),
  '.jpg': ('image/jpeg', 'JPG'),
  '.jpeg': ('image/jpeg', 'JPG'),
  '.pdf': ('application/pdf', 'PDF'),
  '.txt': ('text/plain', 'TXT'),
  '.json': ('application/json', 'JSON'),
  '.zip': ('application/zip', 'ZIP'),
}
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024
BACKEND_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = settings.evidence_root
SECRET_PATTERN = re.compile(r'(?i)(bearer\s+[a-z0-9._-]+|password\s*[:=]|token\s*[:=]|csrf|autoqa_session|authorization\s*[:=]|secret\s*[:=])')
CODE_PATTERN = re.compile(r'^[A-Z0-9][A-Z0-9._-]{1,39}$')
TAG_PATTERN = re.compile(r'^[a-z0-9][a-z0-9._-]{0,49}$')
SORT_COLUMNS = {
  'updated_at': ManagedTestCase.updated_at,
  'case_key': ManagedTestCase.case_key,
  'priority': ManagedTestCase.priority,
  'lifecycle_state': ManagedTestCase.lifecycle_state,
}


def normalize_code(value: str) -> str:
  normalized = value.strip().upper()
  if not CODE_PATTERN.fullmatch(normalized):
    raise HTTPException(status_code=422, detail='Code must use letters, numbers, dot, underscore, or hyphen.')
  return normalized


def normalize_tag(value: str) -> tuple[str, str]:
  display = value.strip()
  normalized = display.lower()
  if not TAG_PATTERN.fullmatch(normalized) or SECRET_PATTERN.search(display):
    raise HTTPException(status_code=422, detail='Tag contains unsupported or sensitive content.')
  return display[:50], normalized


def reject_secret_like(value: str | None, field: str) -> None:
  if value and SECRET_PATTERN.search(value):
    raise HTTPException(status_code=422, detail=f'{field} must not contain credential-like content.')


def validate_operator(db: Session, operator_id: int | None) -> Operator | None:
  if operator_id is None:
    return None
  operator = db.get(Operator, operator_id)
  if operator is None or not operator.is_active:
    raise HTTPException(status_code=422, detail='Assigned operator must be active.')
  return operator


def require_project_active(project: TestProject | None) -> TestProject:
  if project is None:
    raise HTTPException(status_code=404, detail='Test project not found.')
  if project.status == ARCHIVED or project.archived_at is not None:
    raise HTTPException(status_code=409, detail='Archived project cannot accept active changes.')
  return project


def require_module_active(module: TestModule | None, project_id: int | None = None) -> TestModule:
  if module is None:
    raise HTTPException(status_code=404, detail='Test module not found.')
  if project_id is not None and module.project_id != project_id:
    raise HTTPException(status_code=422, detail='Module does not belong to the selected project.')
  if module.status == ARCHIVED or module.archived_at is not None:
    raise HTTPException(status_code=409, detail='Archived module cannot accept active changes.')
  return module


def require_suite_active(suite: ManagedTestSuite | None, project_id: int | None = None, module_id: int | None = None) -> ManagedTestSuite:
  if suite is None:
    raise HTTPException(status_code=404, detail='Test suite not found.')
  if project_id is not None and suite.project_id != project_id:
    raise HTTPException(status_code=422, detail='Suite does not belong to the selected project.')
  if module_id is not None and suite.module_id != module_id:
    raise HTTPException(status_code=422, detail='Suite does not belong to the selected module.')
  if suite.status == ARCHIVED or suite.archived_at is not None:
    raise HTTPException(status_code=409, detail='Archived suite cannot accept active changes.')
  return suite


def validate_steps(steps) -> None:
  seen: set[int] = set()
  for step in steps:
    if step.step_number in seen:
      raise HTTPException(status_code=422, detail='Step numbers must be unique.')
    seen.add(step.step_number)
    reject_secret_like(step.test_data, 'Step test data')
  if sorted(seen) != list(range(1, len(seen) + 1)):
    raise HTTPException(status_code=422, detail='Step numbers must be contiguous and ordered from 1.')


def set_case_tags(db: Session, test_case: ManagedTestCase, values: list[str]) -> None:
  normalized = [normalize_tag(value) for value in values]
  if len({item[1] for item in normalized}) != len(normalized):
    raise HTTPException(status_code=422, detail='Duplicate tags are not allowed.')
  test_case.tag_links.clear()
  for display, key in normalized:
    tag = db.scalar(select(Tag).where(Tag.normalized_name == key))
    if tag is None:
      tag = Tag(name=display, normalized_name=key)
      db.add(tag)
      db.flush()
    test_case.tag_links.append(TestCaseTag(access_project_id=test_case.access_project_id, tag=tag))


def case_tags(test_case: ManagedTestCase) -> list[str]:
  return [link.tag.name for link in sorted(test_case.tag_links, key=lambda item: item.tag.normalized_name)]


def snapshot_payload(test_case: ManagedTestCase) -> dict:
  return {
    'id': test_case.id,
    'case_key': test_case.case_key,
    'title': test_case.title,
    'objective': test_case.objective,
    'preconditions': test_case.preconditions,
    'test_type': test_case.test_type,
    'priority': test_case.priority,
    'severity': test_case.severity,
    'status': test_case.status,
    'lifecycle_state': test_case.lifecycle_state,
    'project_id': test_case.project_id,
    'module_id': test_case.module_id,
    'suite_id': test_case.suite_id,
    'owner_operator_id': test_case.owner_operator_id,
    'created_by': test_case.created_by,
    'reviewed_by': test_case.reviewed_by,
    'approved_by': test_case.approved_by,
    'current_version': test_case.current_version,
    'tags': case_tags(test_case),
    'steps': [
      {'step_number': step.step_number, 'action': step.action, 'expected_result': step.expected_result, 'test_data': step.test_data}
      for step in sorted(test_case.steps, key=lambda item: item.step_number)
    ],
  }


def create_version(db: Session, test_case: ManagedTestCase, created_by: int, summary: str, source_state: str | None = None) -> TestCaseVersion:
  next_number = (db.scalar(select(func.max(TestCaseVersion.version_number)).where(TestCaseVersion.test_case_id == test_case.id)) or 0) + 1
  test_case.current_version = next_number
  version = TestCaseVersion(
    access_project_id=test_case.access_project_id,
    test_case_id=test_case.id,
    version_number=next_number,
    snapshot_json=json.dumps(snapshot_payload(test_case), sort_keys=True, separators=(',', ':'), ensure_ascii=True),
    change_summary=summary[:500],
    created_by=created_by,
    source_state=source_state or test_case.lifecycle_state,
  )
  db.add(version)
  db.flush()
  return version


def case_read(test_case: ManagedTestCase) -> dict:
  return {
    'id': test_case.id,
    'project_id': test_case.project_id,
    'module_id': test_case.module_id,
    'suite_id': test_case.suite_id,
    'case_key': test_case.case_key,
    'title': test_case.title,
    'objective': test_case.objective,
    'preconditions': test_case.preconditions,
    'test_type': test_case.test_type,
    'priority': test_case.priority,
    'severity': test_case.severity,
    'status': test_case.status,
    'lifecycle_state': test_case.lifecycle_state,
    'owner_operator_id': test_case.owner_operator_id,
    'created_by': test_case.created_by,
    'reviewed_by': test_case.reviewed_by,
    'approved_by': test_case.approved_by,
    'created_at': test_case.created_at,
    'updated_at': test_case.updated_at,
    'reviewed_at': test_case.reviewed_at,
    'approved_at': test_case.approved_at,
    'archived_at': test_case.archived_at,
    'current_version': test_case.current_version,
    'steps': sorted(test_case.steps, key=lambda item: item.step_number),
    'tags': case_tags(test_case),
  }


def apply_case_steps(test_case: ManagedTestCase, steps) -> None:
  test_case.steps.clear()
  for step in sorted(steps, key=lambda item: item.step_number):
    test_case.steps.append(TestCaseStep(access_project_id=test_case.access_project_id, step_number=step.step_number, action=step.action, expected_result=step.expected_result, test_data=step.test_data))


def next_run_key(db: Session) -> str:
  return f'MRUN-{(db.scalar(select(func.count(ManualTestRun.id))) or 0) + 1:05d}-{uuid4().hex[:6].upper()}'


def ensure_case_approved_for_run(test_case: ManagedTestCase, run: ManualTestRun) -> None:
  if test_case.project_id != run.project_id or test_case.suite_id != run.suite_id:
    raise HTTPException(status_code=422, detail='Test case is outside the manual run scope.')
  if test_case.lifecycle_state != 'APPROVED' or test_case.status == ARCHIVED or test_case.archived_at is not None:
    raise HTTPException(status_code=409, detail='Only approved active test cases can be added to a manual run.')


def allowed_assignment(operator: Operator, assigned_to: int | None) -> bool:
  return assigned_to is None or operator.role in {'ADMIN', 'APPROVER'} or assigned_to == operator.id


def validate_result_status(status: str, notes: str | None) -> None:
  if status in {'FAILED', 'BLOCKED'} and not (notes and notes.strip()):
    raise HTTPException(status_code=422, detail='Failed or blocked results require a safe note.')
  reject_secret_like(notes, 'Result notes')


def safe_csv(value) -> str:
  text = '' if value is None else str(value)
  return f"'{text}" if text.startswith(('=', '+', '-', '@')) else text


def cases_csv(rows: list[ManagedTestCase]) -> str:
  output = StringIO()
  writer = csv.writer(output, lineterminator='\n')
  writer.writerow(['case_key', 'title', 'priority', 'test_type', 'lifecycle_state', 'current_version'])
  for item in rows:
    writer.writerow([safe_csv(item.case_key), safe_csv(item.title), item.priority, item.test_type, item.lifecycle_state, item.current_version])
  return output.getvalue()


def validate_evidence_file(file: UploadFile, content: bytes) -> tuple[str, str, str]:
  name = Path(file.filename or 'evidence').name
  reject_secret_like(name, 'Evidence filename')
  suffix = Path(name).suffix.lower()
  if suffix in {'.exe', '.bat', '.cmd', '.ps1', '.msi', '.dll', '.com', '.scr'}:
    raise HTTPException(status_code=422, detail='Executable evidence files are not allowed.')
  if suffix not in ALLOWED_EVIDENCE:
    raise HTTPException(status_code=422, detail='Evidence file type is not allowed.')
  expected_mime, evidence_type = ALLOWED_EVIDENCE[suffix]
  if file.content_type and file.content_type not in {expected_mime, 'application/octet-stream'}:
    raise HTTPException(status_code=422, detail='Evidence MIME type is not allowed.')
  if len(content) > MAX_EVIDENCE_BYTES:
    raise HTTPException(status_code=413, detail='Evidence file is too large.')
  return name[:240], suffix, evidence_type


def store_evidence(file: UploadFile, content: bytes) -> tuple[str, str, str, int, str]:
  original, suffix, evidence_type = validate_evidence_file(file, content)
  digest = hashlib.sha256(content).hexdigest()
  EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
  stored = f'{uuid4().hex}{suffix}'
  path = (EVIDENCE_ROOT / stored).resolve()
  path.relative_to(EVIDENCE_ROOT.resolve())
  if path.exists():
    raise HTTPException(status_code=409, detail='Evidence filename collision.')
  path.write_bytes(content)
  relative = str(Path(EVIDENCE_ROOT.name) / stored).replace('\\', '/')
  return original, stored, relative, len(content), digest, evidence_type


def evidence_path(evidence: ManualEvidence) -> Path:
  path = (EVIDENCE_ROOT / evidence.stored_filename).resolve()
  try:
    path.relative_to(EVIDENCE_ROOT.resolve())
  except ValueError:
    raise HTTPException(status_code=400, detail='Invalid evidence path.') from None
  return path
