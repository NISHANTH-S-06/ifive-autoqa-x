from datetime import datetime
import json

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.test_management import (
  ManagedTestCase,
  ManagedTestSuite,
  ManualEvidence,
  ManualStepResult,
  ManualTestRun,
  ManualTestRunCase,
  Tag,
  TestCaseTag,
  TestCaseVersion,
  TestModule,
  TestProject,
)
from app.schemas.test_management import (
  LifecycleReason,
  ManualEvidenceRead,
  ManualResultStatus,
  ManualRunCaseAdd,
  ManualRunCaseRead,
  ManualRunCaseUpdate,
  ManualRunCreate,
  ManualRunRead,
  ManualStepResultRead,
  ManualStepResultUpdate,
  Page,
  TestCaseCreate,
  TestCaseList,
  TestCaseRead,
  TestCaseUpdate,
  TestCaseVersionRead,
  TestModuleCreate,
  TestModuleRead,
  TestModuleUpdate,
  TestProjectCreate,
  TestProjectList,
  TestProjectRead,
  TestProjectUpdate,
  TestSuiteCreate,
  TestSuiteRead,
  TestSuiteUpdate,
)
from app.services.audit_service import append_event
from app.services.test_management import (
  ACTIVE,
  ARCHIVED,
  EDITABLE_STATES,
  RESULT_TERMINAL,
  SORT_COLUMNS,
  allowed_assignment,
  apply_case_steps,
  case_read,
  cases_csv,
  create_version,
  ensure_case_approved_for_run,
  evidence_path,
  next_run_key,
  normalize_code,
  reject_secret_like,
  require_module_active,
  require_project_active,
  require_suite_active,
  set_case_tags,
  store_evidence,
  validate_operator,
  validate_result_status,
  validate_steps,
)

router = APIRouter(tags=['test-management'], dependencies=[Depends(get_auth_context)])


def _can_manage_structure(context: AuthContext) -> bool:
  return context.operator.role == 'ADMIN'


def _can_author(context: AuthContext) -> bool:
  return context.operator.role in {'TESTER', 'ADMIN'}


def _can_review(context: AuthContext) -> bool:
  return context.operator.role in {'APPROVER', 'ADMIN'}


def _can_execute_manual(context: AuthContext, assigned_to: int | None) -> bool:
  return context.operator.role in {'TESTER', 'ADMIN'} and (assigned_to is None or assigned_to == context.operator.id or context.operator.role == 'ADMIN')


def _require_manage(context: AuthContext) -> None:
  if not _can_manage_structure(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')


def _require_author(context: AuthContext) -> None:
  if not _can_author(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')


def _page(limit: int, offset: int, total: int) -> Page:
  return Page(limit=limit, offset=offset, total=total)


def _get_case(db: Session, case_id: int) -> ManagedTestCase:
  item = db.scalar(select(ManagedTestCase).options(selectinload(ManagedTestCase.steps), selectinload(ManagedTestCase.tag_links).selectinload(TestCaseTag.tag)).where(ManagedTestCase.id == case_id))
  if item is None:
    raise HTTPException(status_code=404, detail='Test case not found.')
  return item


def _case_query():
  return select(ManagedTestCase).options(selectinload(ManagedTestCase.steps), selectinload(ManagedTestCase.tag_links).selectinload(TestCaseTag.tag))


@router.get('/test-projects', response_model=TestProjectList)
def list_test_projects(search: str | None = None, status: str | None = None, owner_id: int | None = None, include_archived: bool = False, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
  statement = select(TestProject)
  count_statement = select(func.count(TestProject.id))
  filters = []
  if not include_archived:
    filters.append(TestProject.status != ARCHIVED)
  if search:
    term = f'%{search.strip().lower()}%'
    filters.append(func.lower(TestProject.name).like(term) | func.lower(TestProject.code).like(term))
  if status:
    filters.append(TestProject.status == status.upper())
  if owner_id is not None:
    filters.append(TestProject.owner_operator_id == owner_id)
  for item in filters:
    statement = statement.where(item)
    count_statement = count_statement.where(item)
  total = db.scalar(count_statement) or 0
  items = list(db.scalars(statement.order_by(TestProject.updated_at.desc(), TestProject.id.desc()).offset(offset).limit(limit)))
  return TestProjectList(items=items, page=_page(limit, offset, total))


@router.post('/test-projects', response_model=TestProjectRead, status_code=201)
def create_test_project(payload: TestProjectCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  validate_operator(db, payload.owner_operator_id)
  item = TestProject(name=payload.name.strip(), code=normalize_code(payload.code), description=payload.description, owner_operator_id=payload.owner_operator_id, created_by=context.operator.id)
  db.add(item)
  try:
    db.flush()
  except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=409, detail='Project code already exists.') from None
  append_event(db, 'test_project_created', operator_id=context.operator.id, resource_type='TEST_PROJECT', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.get('/test-projects/{project_id}', response_model=TestProjectRead)
def get_test_project(project_id: int, db: Session = Depends(get_db)):
  item = db.get(TestProject, project_id)
  if item is None:
    raise HTTPException(status_code=404, detail='Test project not found.')
  return item


@router.patch('/test-projects/{project_id}', response_model=TestProjectRead)
def update_test_project(project_id: int, payload: TestProjectUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  item = require_project_active(db.get(TestProject, project_id))
  if payload.version is not None and payload.version != item.version:
    raise HTTPException(status_code=409, detail='Project version conflict.')
  validate_operator(db, payload.owner_operator_id)
  for key, value in payload.model_dump(exclude_unset=True, exclude={'version'}).items():
    setattr(item, key, value.strip() if isinstance(value, str) else value)
  item.version += 1
  append_event(db, 'test_project_updated', operator_id=context.operator.id, resource_type='TEST_PROJECT', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.post('/test-projects/{project_id}/archive', response_model=TestProjectRead)
def archive_test_project(project_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  item = require_project_active(db.get(TestProject, project_id))
  item.status = ARCHIVED; item.archived_at = datetime.utcnow(); item.version += 1
  append_event(db, 'test_project_archived', operator_id=context.operator.id, resource_type='TEST_PROJECT', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.get('/test-modules', response_model=list[TestModuleRead])
def list_test_modules(project_id: int | None = None, include_archived: bool = False, db: Session = Depends(get_db)):
  statement = select(TestModule)
  if project_id is not None:
    statement = statement.where(TestModule.project_id == project_id)
  if not include_archived:
    statement = statement.where(TestModule.status != ARCHIVED)
  return list(db.scalars(statement.order_by(TestModule.project_id, TestModule.sort_order, TestModule.name)))


@router.post('/test-modules', response_model=TestModuleRead, status_code=201)
def create_test_module(payload: TestModuleCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  require_project_active(db.get(TestProject, payload.project_id))
  item = TestModule(project_id=payload.project_id, name=payload.name.strip(), code=normalize_code(payload.code), description=payload.description, sort_order=payload.sort_order, created_by=context.operator.id)
  db.add(item)
  try: db.flush()
  except IntegrityError:
    db.rollback(); raise HTTPException(status_code=409, detail='Module code already exists for this project.') from None
  append_event(db, 'test_module_created', operator_id=context.operator.id, resource_type='TEST_MODULE', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.patch('/test-modules/{module_id}', response_model=TestModuleRead)
def update_test_module(module_id: int, payload: TestModuleUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  item = require_module_active(db.get(TestModule, module_id))
  for key, value in payload.model_dump(exclude_unset=True).items():
    setattr(item, key, value.strip() if isinstance(value, str) else value)
  append_event(db, 'test_module_updated', operator_id=context.operator.id, resource_type='TEST_MODULE', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.post('/test-modules/{module_id}/archive', response_model=TestModuleRead)
def archive_test_module(module_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  item = require_module_active(db.get(TestModule, module_id))
  item.status = ARCHIVED; item.archived_at = datetime.utcnow()
  append_event(db, 'test_module_archived', operator_id=context.operator.id, resource_type='TEST_MODULE', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.get('/test-suites', response_model=list[TestSuiteRead])
def list_test_suites(project_id: int | None = None, module_id: int | None = None, include_archived: bool = False, db: Session = Depends(get_db)):
  statement = select(ManagedTestSuite)
  if project_id is not None:
    statement = statement.where(ManagedTestSuite.project_id == project_id)
  if module_id is not None:
    statement = statement.where(ManagedTestSuite.module_id == module_id)
  if not include_archived:
    statement = statement.where(ManagedTestSuite.status != ARCHIVED)
  return list(db.scalars(statement.order_by(ManagedTestSuite.project_id, ManagedTestSuite.name)))


@router.post('/test-suites', response_model=TestSuiteRead, status_code=201)
def create_test_suite(payload: TestSuiteCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  require_project_active(db.get(TestProject, payload.project_id))
  require_module_active(db.get(TestModule, payload.module_id), payload.project_id)
  validate_operator(db, payload.owner_operator_id)
  item = ManagedTestSuite(project_id=payload.project_id, module_id=payload.module_id, name=payload.name.strip(), code=normalize_code(payload.code), description=payload.description, suite_type=payload.suite_type.strip().upper(), owner_operator_id=payload.owner_operator_id, created_by=context.operator.id)
  db.add(item)
  try: db.flush()
  except IntegrityError:
    db.rollback(); raise HTTPException(status_code=409, detail='Suite code already exists for this scope.') from None
  append_event(db, 'test_suite_created', operator_id=context.operator.id, resource_type='TEST_SUITE', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.patch('/test-suites/{suite_id}', response_model=TestSuiteRead)
def update_test_suite(suite_id: int, payload: TestSuiteUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  item = require_suite_active(db.get(ManagedTestSuite, suite_id))
  validate_operator(db, payload.owner_operator_id)
  for key, value in payload.model_dump(exclude_unset=True).items():
    setattr(item, key, value.strip() if isinstance(value, str) else value)
  append_event(db, 'test_suite_updated', operator_id=context.operator.id, resource_type='TEST_SUITE', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.post('/test-suites/{suite_id}/archive', response_model=TestSuiteRead)
def archive_test_suite(suite_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_manage(context)
  item = require_suite_active(db.get(ManagedTestSuite, suite_id))
  item.status = ARCHIVED; item.archived_at = datetime.utcnow()
  append_event(db, 'test_suite_archived', operator_id=context.operator.id, resource_type='TEST_SUITE', resource_id=str(item.id), metadata={'code': item.code})
  db.commit(); db.refresh(item); return item


@router.get('/test-cases/export')
def export_test_cases(format: str = Query('csv', pattern='^(csv|json)$'), limit: int = Query(200, ge=1, le=1000), context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  rows = list(db.scalars(_case_query().where(ManagedTestCase.status != ARCHIVED).order_by(ManagedTestCase.updated_at.desc()).limit(limit)))
  append_event(db, 'test_export_created', operator_id=context.operator.id, resource_type='TEST_CASE', metadata={'format': format, 'rows': len(rows)})
  db.commit()
  if format == 'json':
    return JSONResponse([case_read(item) for item in rows])
  return PlainTextResponse(cases_csv(rows), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename="test-cases.csv"'})


@router.get('/test-cases', response_model=TestCaseList)
def list_test_cases(project_id: int | None = None, module_id: int | None = None, suite_id: int | None = None, lifecycle_state: str | None = None, priority: str | None = None, test_type: str | None = None, owner_id: int | None = None, creator_id: int | None = None, tag: str | None = None, search: str | None = None, sort: str = 'updated_at', direction: str = 'desc', limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
  statement = _case_query()
  count_statement = select(func.count(ManagedTestCase.id))
  filters = [ManagedTestCase.status != ARCHIVED]
  if project_id is not None: filters.append(ManagedTestCase.project_id == project_id)
  if module_id is not None: filters.append(ManagedTestCase.module_id == module_id)
  if suite_id is not None: filters.append(ManagedTestCase.suite_id == suite_id)
  if lifecycle_state: filters.append(ManagedTestCase.lifecycle_state == lifecycle_state.upper())
  if priority: filters.append(ManagedTestCase.priority == priority.upper())
  if test_type: filters.append(ManagedTestCase.test_type == test_type.upper())
  if owner_id is not None: filters.append(ManagedTestCase.owner_operator_id == owner_id)
  if creator_id is not None: filters.append(ManagedTestCase.created_by == creator_id)
  if search:
    term = f'%{search.strip().lower()}%'
    filters.append(func.lower(ManagedTestCase.title).like(term) | func.lower(ManagedTestCase.case_key).like(term))
  for item in filters:
    statement = statement.where(item)
    count_statement = count_statement.where(item)
  if tag:
    from app.models.test_management import Tag, TestCaseTag
    key = tag.strip().lower()
    statement = statement.join(TestCaseTag).join(Tag).where(Tag.normalized_name == key)
    count_statement = count_statement.join(TestCaseTag, TestCaseTag.test_case_id == ManagedTestCase.id).join(Tag, Tag.id == TestCaseTag.tag_id).where(Tag.normalized_name == key)
  sort_column = SORT_COLUMNS.get(sort)
  if sort_column is None:
    raise HTTPException(status_code=422, detail='Unsupported sort column.')
  order = sort_column.asc() if direction.lower() == 'asc' else sort_column.desc()
  total = db.scalar(count_statement) or 0
  rows = list(db.scalars(statement.order_by(order, ManagedTestCase.id.desc()).offset(offset).limit(limit)))
  return TestCaseList(items=[case_read(item) for item in rows], page=_page(limit, offset, total))


@router.post('/test-cases', response_model=TestCaseRead, status_code=201)
def create_test_case(payload: TestCaseCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_author(context)
  require_project_active(db.get(TestProject, payload.project_id))
  require_module_active(db.get(TestModule, payload.module_id), payload.project_id)
  require_suite_active(db.get(ManagedTestSuite, payload.suite_id), payload.project_id, payload.module_id)
  validate_operator(db, payload.owner_operator_id)
  validate_steps(payload.steps)
  item = ManagedTestCase(project_id=payload.project_id, module_id=payload.module_id, suite_id=payload.suite_id, case_key=normalize_code(payload.case_key), title=payload.title.strip(), objective=payload.objective, preconditions=payload.preconditions, test_type=payload.test_type.value, priority=payload.priority.value, severity=payload.severity.value, owner_operator_id=payload.owner_operator_id, created_by=context.operator.id)
  apply_case_steps(item, payload.steps)
  db.add(item)
  try:
    db.flush()
    set_case_tags(db, item, payload.tags)
    create_version(db, item, context.operator.id, 'Initial draft', 'DRAFT')
  except IntegrityError:
    db.rollback(); raise HTTPException(status_code=409, detail='Test case key already exists.') from None
  append_event(db, 'test_case_created', operator_id=context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'case_key': item.case_key})
  db.commit(); db.refresh(item); return case_read(_get_case(db, item.id))


@router.get('/test-cases/{case_id}', response_model=TestCaseRead)
def get_test_case(case_id: int, db: Session = Depends(get_db)):
  return case_read(_get_case(db, case_id))


@router.patch('/test-cases/{case_id}', response_model=TestCaseRead)
def update_test_case(case_id: int, payload: TestCaseUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  item = _get_case(db, case_id)
  if item.lifecycle_state not in EDITABLE_STATES:
    raise HTTPException(status_code=409, detail='Only draft or rejected test cases can be edited directly.')
  if context.operator.role != 'ADMIN' and item.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can edit this draft.')
  if payload.steps is not None:
    validate_steps(payload.steps)
    apply_case_steps(item, payload.steps)
  for key, value in payload.model_dump(exclude_unset=True, exclude={'steps', 'tags'}).items():
    setattr(item, key, value.value if hasattr(value, 'value') else value)
  if payload.tags is not None:
    set_case_tags(db, item, payload.tags)
  item.updated_at = datetime.utcnow()
  create_version(db, item, context.operator.id, 'Draft updated', item.lifecycle_state)
  append_event(db, 'test_case_updated', operator_id=context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'case_key': item.case_key})
  db.commit(); return case_read(_get_case(db, case_id))


@router.post('/test-cases/{case_id}/submit', response_model=TestCaseRead)
def submit_test_case(case_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  item = _get_case(db, case_id)
  if item.lifecycle_state not in {'DRAFT', 'REJECTED'}:
    raise HTTPException(status_code=409, detail='Only draft or rejected cases can be submitted.')
  if context.operator.role != 'ADMIN' and item.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can submit this case.')
  item.lifecycle_state = 'IN_REVIEW'; item.reviewed_by = None; item.reviewed_at = None; item.updated_at = datetime.utcnow()
  create_version(db, item, context.operator.id, 'Submitted for review', 'IN_REVIEW')
  append_event(db, 'test_case_submitted', operator_id=context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'case_key': item.case_key})
  db.commit(); return case_read(_get_case(db, case_id))


@router.post('/test-cases/{case_id}/approve', response_model=TestCaseRead)
def approve_test_case(case_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  item = _get_case(db, case_id)
  if item.lifecycle_state != 'IN_REVIEW':
    raise HTTPException(status_code=409, detail='Only cases in review can be approved.')
  if item.created_by == context.operator.id:
    append_event(db, 'test_case_approval_denied', 'DENIED', context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'reason': 'creator_separation'})
    db.commit()
    raise HTTPException(status_code=400, detail='Creators cannot approve their own test cases.')
  now = datetime.utcnow()
  item.lifecycle_state = 'APPROVED'; item.reviewed_by = context.operator.id; item.approved_by = context.operator.id; item.reviewed_at = now; item.approved_at = now; item.updated_at = now
  create_version(db, item, context.operator.id, 'Approved', 'APPROVED')
  append_event(db, 'test_case_approved', operator_id=context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'case_key': item.case_key, 'version': item.current_version})
  db.commit(); return case_read(_get_case(db, case_id))


@router.post('/test-cases/{case_id}/reject', response_model=TestCaseRead)
def reject_test_case(case_id: int, payload: LifecycleReason, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if not payload.reason or not payload.reason.strip():
    raise HTTPException(status_code=422, detail='Rejection reason is required.')
  reject_secret_like(payload.reason, 'Rejection reason')
  item = _get_case(db, case_id)
  if item.lifecycle_state != 'IN_REVIEW':
    raise HTTPException(status_code=409, detail='Only cases in review can be rejected.')
  if item.created_by == context.operator.id:
    raise HTTPException(status_code=400, detail='Creators cannot review their own test cases.')
  item.lifecycle_state = 'REJECTED'; item.reviewed_by = context.operator.id; item.reviewed_at = datetime.utcnow(); item.updated_at = datetime.utcnow()
  create_version(db, item, context.operator.id, payload.reason, 'REJECTED')
  append_event(db, 'test_case_rejected', operator_id=context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'case_key': item.case_key})
  db.commit(); return case_read(_get_case(db, case_id))


@router.post('/test-cases/{case_id}/revision', response_model=TestCaseRead)
def revise_test_case(case_id: int, payload: LifecycleReason, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  item = _get_case(db, case_id)
  if item.lifecycle_state != 'APPROVED':
    raise HTTPException(status_code=409, detail='Only approved cases can create a controlled draft revision.')
  if context.operator.role != 'ADMIN' and item.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can revise this case.')
  item.lifecycle_state = 'DRAFT'; item.approved_by = None; item.approved_at = None; item.reviewed_by = None; item.reviewed_at = None; item.updated_at = datetime.utcnow()
  create_version(db, item, context.operator.id, payload.reason or 'Revision draft created', 'DRAFT')
  append_event(db, 'test_case_revision_created', operator_id=context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'case_key': item.case_key, 'version': item.current_version})
  db.commit(); return case_read(_get_case(db, case_id))


@router.post('/test-cases/{case_id}/archive', response_model=TestCaseRead)
def archive_test_case(case_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  item = _get_case(db, case_id)
  if context.operator.role != 'ADMIN' and item.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can archive this case.')
  item.status = ARCHIVED; item.lifecycle_state = 'ARCHIVED'; item.archived_at = datetime.utcnow(); item.updated_at = datetime.utcnow()
  create_version(db, item, context.operator.id, 'Archived', 'ARCHIVED')
  append_event(db, 'test_case_archived', operator_id=context.operator.id, resource_type='TEST_CASE', resource_id=str(item.id), metadata={'case_key': item.case_key})
  db.commit(); return case_read(_get_case(db, case_id))


@router.get('/test-cases/{case_id}/versions', response_model=list[TestCaseVersionRead])
def list_test_case_versions(case_id: int, db: Session = Depends(get_db)):
  _get_case(db, case_id)
  return list(db.scalars(select(TestCaseVersion).where(TestCaseVersion.test_case_id == case_id).order_by(TestCaseVersion.version_number)))


@router.get('/test-cases/{case_id}/versions/{version_number}', response_model=TestCaseVersionRead)
def get_test_case_version(case_id: int, version_number: int, db: Session = Depends(get_db)):
  version = db.scalar(select(TestCaseVersion).where(TestCaseVersion.test_case_id == case_id, TestCaseVersion.version_number == version_number))
  if version is None:
    raise HTTPException(status_code=404, detail='Test case version not found.')
  return version


@router.get('/manual-test-runs', response_model=list[ManualRunRead])
def list_manual_runs(status: str | None = None, db: Session = Depends(get_db)):
  statement = select(ManualTestRun)
  if status:
    statement = statement.where(ManualTestRun.status == status.upper())
  rows = list(db.scalars(statement.order_by(ManualTestRun.created_at.desc())))
  for row in rows:
    total = len(row.cases)
    done = sum(case.status in RESULT_TERMINAL for case in row.cases)
    row.progress = f'{done}/{total}' if total else '0/0'
  return rows


@router.post('/manual-test-runs', response_model=ManualRunRead, status_code=201)
def create_manual_run(payload: ManualRunCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_author(context)
  require_project_active(db.get(TestProject, payload.project_id))
  require_suite_active(db.get(ManagedTestSuite, payload.suite_id), payload.project_id)
  if not allowed_assignment(context.operator, payload.assigned_to):
    raise HTTPException(status_code=403, detail='Assignment is not allowed for this operator.')
  validate_operator(db, payload.assigned_to)
  run = ManualTestRun(run_key=next_run_key(db), project_id=payload.project_id, suite_id=payload.suite_id, name=payload.name.strip(), description=payload.description, assigned_to=payload.assigned_to, created_by=context.operator.id)
  db.add(run); db.flush()
  seen = set()
  for case_id in payload.case_ids:
    if case_id in seen:
      raise HTTPException(status_code=422, detail='Duplicate cases are not allowed in a manual run.')
    seen.add(case_id)
    test_case = _get_case(db, case_id)
    ensure_case_approved_for_run(test_case, run)
    run.cases.append(ManualTestRunCase(test_case_id=test_case.id, test_case_version=test_case.current_version, assigned_to=payload.assigned_to))
  append_event(db, 'test_run_created', operator_id=context.operator.id, resource_type='MANUAL_TEST_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit(); db.refresh(run); run.progress = f'0/{len(run.cases)}'; return run


@router.get('/manual-test-runs/{run_id}', response_model=ManualRunRead)
def get_manual_run(run_id: int, db: Session = Depends(get_db)):
  run = db.get(ManualTestRun, run_id)
  if run is None:
    raise HTTPException(status_code=404, detail='Manual run not found.')
  total = len(run.cases); done = sum(case.status in RESULT_TERMINAL for case in run.cases); run.progress = f'{done}/{total}'
  return run


@router.post('/manual-test-runs/{run_id}/start', response_model=ManualRunRead)
def start_manual_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run = db.get(ManualTestRun, run_id)
  if run is None: raise HTTPException(status_code=404, detail='Manual run not found.')
  if not _can_execute_manual(context, run.assigned_to): raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if run.status != 'PLANNED': raise HTTPException(status_code=409, detail='Only planned runs can be started.')
  run.status = 'IN_PROGRESS'; run.started_at = datetime.utcnow()
  append_event(db, 'test_run_started', operator_id=context.operator.id, resource_type='MANUAL_TEST_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit(); db.refresh(run); return run


@router.post('/manual-test-runs/{run_id}/complete', response_model=ManualRunRead)
def complete_manual_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run = db.get(ManualTestRun, run_id)
  if run is None: raise HTTPException(status_code=404, detail='Manual run not found.')
  if not _can_execute_manual(context, run.assigned_to): raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if run.status != 'IN_PROGRESS': raise HTTPException(status_code=409, detail='Only in-progress runs can be completed.')
  if any(case.status in {'NOT_RUN', 'IN_PROGRESS'} for case in run.cases):
    raise HTTPException(status_code=409, detail='All run cases must have a terminal result before completion.')
  run.status = 'COMPLETED'; run.completed_at = datetime.utcnow()
  append_event(db, 'test_run_completed', operator_id=context.operator.id, resource_type='MANUAL_TEST_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit(); db.refresh(run); return run


@router.post('/manual-test-runs/{run_id}/cancel', response_model=ManualRunRead)
def cancel_manual_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run = db.get(ManualTestRun, run_id)
  if run is None: raise HTTPException(status_code=404, detail='Manual run not found.')
  if context.operator.role not in {'ADMIN', 'TESTER'}: raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if run.status in {'COMPLETED', 'CANCELLED'}: raise HTTPException(status_code=409, detail='Terminal manual runs cannot be cancelled.')
  run.status = 'CANCELLED'; run.completed_at = datetime.utcnow()
  append_event(db, 'test_run_cancelled', operator_id=context.operator.id, resource_type='MANUAL_TEST_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit(); db.refresh(run); return run


@router.get('/manual-test-runs/{run_id}/cases', response_model=list[ManualRunCaseRead])
def list_manual_run_cases(run_id: int, db: Session = Depends(get_db)):
  run = db.get(ManualTestRun, run_id)
  if run is None: raise HTTPException(status_code=404, detail='Manual run not found.')
  return run.cases


@router.post('/manual-test-runs/{run_id}/cases', response_model=list[ManualRunCaseRead], status_code=201)
def add_manual_run_cases(run_id: int, payload: ManualRunCaseAdd, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run = db.get(ManualTestRun, run_id)
  if run is None: raise HTTPException(status_code=404, detail='Manual run not found.')
  if run.status != 'PLANNED': raise HTTPException(status_code=409, detail='Cases can only be added to planned runs.')
  if not _can_author(context): raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if not allowed_assignment(context.operator, payload.assigned_to): raise HTTPException(status_code=403, detail='Assignment is not allowed for this operator.')
  validate_operator(db, payload.assigned_to)
  existing = {(item.test_case_id, item.test_case_version) for item in run.cases}
  added: list[ManualTestRunCase] = []
  for case_id in payload.case_ids:
    test_case = _get_case(db, case_id)
    ensure_case_approved_for_run(test_case, run)
    key = (test_case.id, test_case.current_version)
    if key in existing:
      raise HTTPException(status_code=409, detail='Case/version is already in this manual run.')
    row = ManualTestRunCase(run_id=run.id, test_case_id=test_case.id, test_case_version=test_case.current_version, assigned_to=payload.assigned_to)
    db.add(row); added.append(row); existing.add(key)
  append_event(db, 'test_run_cases_added', operator_id=context.operator.id, resource_type='MANUAL_TEST_RUN', resource_id=str(run.id), metadata={'added_count': len(added)})
  db.commit()
  return run.cases


@router.patch('/manual-test-runs/{run_id}/cases/{run_case_id}', response_model=ManualRunCaseRead)
def update_manual_run_case(run_id: int, run_case_id: int, payload: ManualRunCaseUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run_case = db.get(ManualTestRunCase, run_case_id)
  if run_case is None or run_case.run_id != run_id: raise HTTPException(status_code=404, detail='Manual run case not found.')
  if not _can_execute_manual(context, run_case.assigned_to): raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  validate_result_status(payload.status.value, payload.notes)
  now = datetime.utcnow()
  run_case.status = payload.status.value; run_case.actual_result = payload.actual_result; run_case.notes = payload.notes; run_case.executed_by = context.operator.id; run_case.updated_at = now
  if payload.status.value == 'IN_PROGRESS' and run_case.started_at is None: run_case.started_at = now
  if payload.status.value in RESULT_TERMINAL: run_case.completed_at = now
  append_event(db, 'manual_result_updated', operator_id=context.operator.id, resource_type='MANUAL_RUN_CASE', resource_id=str(run_case.id), metadata={'status': run_case.status})
  db.commit(); db.refresh(run_case); return run_case


@router.patch('/manual-test-runs/{run_id}/cases/{run_case_id}/steps/{step_number}', response_model=ManualStepResultRead)
def update_step_result(run_id: int, run_case_id: int, step_number: int, payload: ManualStepResultUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run_case = db.get(ManualTestRunCase, run_case_id)
  if run_case is None or run_case.run_id != run_id: raise HTTPException(status_code=404, detail='Manual run case not found.')
  if not _can_execute_manual(context, run_case.assigned_to): raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  version = db.scalar(select(TestCaseVersion).where(TestCaseVersion.test_case_id == run_case.test_case_id, TestCaseVersion.version_number == run_case.test_case_version))
  snapshot = json.loads(version.snapshot_json if version else '{}')
  valid_steps = {step['step_number'] for step in snapshot.get('steps', [])}
  if step_number not in valid_steps: raise HTTPException(status_code=422, detail='Step number is not part of the frozen case version.')
  validate_result_status(payload.status.value, payload.notes)
  item = db.scalar(select(ManualStepResult).where(ManualStepResult.run_case_id == run_case_id, ManualStepResult.step_number == step_number))
  if item is None:
    item = ManualStepResult(run_case_id=run_case_id, step_number=step_number)
    db.add(item)
  item.status = payload.status.value; item.actual_result = payload.actual_result; item.notes = payload.notes; item.executed_at = datetime.utcnow(); item.executed_by = context.operator.id
  append_event(db, 'manual_step_result_updated', operator_id=context.operator.id, resource_type='MANUAL_STEP_RESULT', resource_id=str(run_case_id), metadata={'step_number': step_number, 'status': item.status})
  db.commit(); db.refresh(item); return item


@router.post('/manual-test-runs/{run_id}/cases/{run_case_id}/evidence', response_model=ManualEvidenceRead, status_code=201)
async def upload_manual_evidence(run_id: int, run_case_id: int, request: Request, filename: str = Query(..., min_length=1, max_length=240), x_csrf_token: str | None = Header(default=None, alias='X-CSRF-Token'), context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run_case = db.get(ManualTestRunCase, run_case_id)
  if run_case is None or run_case.run_id != run_id: raise HTTPException(status_code=404, detail='Manual run case not found.')
  if not _can_execute_manual(context, run_case.assigned_to): raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  content = await request.body()
  class EvidenceFile:
    def __init__(self, name: str, content_type: str | None):
      self.filename = name
      self.content_type = content_type
  original, stored, relative, size, digest, evidence_type = store_evidence(EvidenceFile(filename, request.headers.get('content-type')), content)
  item = ManualEvidence(run_case_id=run_case_id, evidence_type=evidence_type, original_filename=original, stored_filename=stored, relative_path=relative, mime_type=request.headers.get('content-type') or 'application/octet-stream', size_bytes=size, sha256=digest, uploaded_by=context.operator.id)
  db.add(item)
  append_event(db, 'evidence_uploaded', operator_id=context.operator.id, resource_type='MANUAL_EVIDENCE', metadata={'run_case_id': run_case_id, 'size_bytes': size, 'evidence_type': evidence_type})
  db.commit(); db.refresh(item); return item


@router.get('/manual-test-runs/{run_id}/cases/{run_case_id}/evidence', response_model=list[ManualEvidenceRead])
def list_manual_evidence(run_id: int, run_case_id: int, db: Session = Depends(get_db)):
  run_case = db.get(ManualTestRunCase, run_case_id)
  if run_case is None or run_case.run_id != run_id: raise HTTPException(status_code=404, detail='Manual run case not found.')
  return list(db.scalars(select(ManualEvidence).where(ManualEvidence.run_case_id == run_case_id, ManualEvidence.deleted_at.is_(None)).order_by(ManualEvidence.created_at.desc())))


@router.get('/manual-evidence/{evidence_id}/download')
def download_manual_evidence(evidence_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  item = db.get(ManualEvidence, evidence_id)
  if item is None or item.deleted_at is not None: raise HTTPException(status_code=404, detail='Evidence not found.')
  path = evidence_path(item)
  if not path.is_file(): raise HTTPException(status_code=404, detail='Evidence file is unavailable.')
  append_event(db, 'evidence_downloaded', operator_id=context.operator.id, resource_type='MANUAL_EVIDENCE', resource_id=str(item.id)); db.commit()
  return FileResponse(path, media_type=item.mime_type, filename=item.original_filename)


@router.delete('/manual-evidence/{evidence_id}', status_code=204)
def delete_manual_evidence(evidence_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in {'ADMIN', 'TESTER'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  item = db.get(ManualEvidence, evidence_id)
  if item is None or item.deleted_at is not None: raise HTTPException(status_code=404, detail='Evidence not found.')
  item.deleted_at = datetime.utcnow(); item.deleted_by = context.operator.id
  append_event(db, 'evidence_deleted', operator_id=context.operator.id, resource_type='MANUAL_EVIDENCE', resource_id=str(item.id))
  db.commit()
  return Response(status_code=204)


@router.get('/manual-test-runs/{run_id}/export')
def export_manual_run(run_id: int, format: str = Query('csv', pattern='^(csv|json)$'), context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  run = db.get(ManualTestRun, run_id)
  if run is None: raise HTTPException(status_code=404, detail='Manual run not found.')
  rows = [{'run_key': run.run_key, 'case_id': case.test_case_id, 'version': case.test_case_version, 'status': case.status, 'executed_by': case.executed_by} for case in run.cases]
  append_event(db, 'test_export_created', operator_id=context.operator.id, resource_type='MANUAL_TEST_RUN', resource_id=str(run.id), metadata={'format': format, 'rows': len(rows)})
  db.commit()
  if format == 'json':
    return JSONResponse(rows)
  import csv
  from io import StringIO
  from app.services.test_management import safe_csv
  output = StringIO(); writer = csv.writer(output, lineterminator='\n'); writer.writerow(['run_key', 'case_id', 'version', 'status', 'executed_by'])
  for row in rows: writer.writerow([safe_csv(row['run_key']), row['case_id'], row['version'], row['status'], row['executed_by']])
  return PlainTextResponse(output.getvalue(), media_type='text/csv', headers={'Content-Disposition': f'attachment; filename="{run.run_key}.csv"'})
