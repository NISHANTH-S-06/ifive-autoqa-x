from datetime import datetime
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.test_run import TestRun
from app.schemas.test_run import TestRunRequest, TestRunStatus


class RunRepository:
  def __init__(self, db: Session):
    self.db = db

  def list(self, project_id: int | None = None, status: TestRunStatus | None = None, limit: int = 50, allowed_project_ids: tuple[int, ...] | None = None) -> list[TestRun]:
    statement = select(TestRun).order_by(TestRun.created_at.desc(), TestRun.id.desc()).limit(limit)
    if project_id is not None:
      statement = statement.where(TestRun.project_id == project_id)
    if allowed_project_ids is not None:
      statement = statement.where(TestRun.project_id.in_(allowed_project_ids))
    if status is not None:
      statement = statement.where(TestRun.status == status.value)
    return list(self.db.scalars(statement))

  def get(self, run_id: int) -> TestRun | None:
    return self.db.get(TestRun, run_id)

  def create(self, request: TestRunRequest, run_code: str, created_by_operator_id: int | None = None) -> TestRun:
    record = TestRun(run_code=run_code, status=TestRunStatus.QUEUED.value, created_by_operator_id=created_by_operator_id, **request.model_dump())
    self.db.add(record)
    self.db.commit()
    self.db.refresh(record)
    return record

  def set_status(self, run: TestRun, status: TestRunStatus, **values) -> TestRun:
    run.status = status.value
    for key, value in values.items():
      setattr(run, key, value)
    self.db.commit()
    self.db.refresh(run)
    return run

  def running_count(self, exclude_run_id: int | None = None) -> int:
    statement = select(func.count(TestRun.id)).where(TestRun.status == TestRunStatus.RUNNING.value)
    if exclude_run_id is not None:
      statement = statement.where(TestRun.id != exclude_run_id)
    return self.db.scalar(statement) or 0

  def recover_interrupted(self) -> int:
    statement = update(TestRun).where(TestRun.status == TestRunStatus.RUNNING.value).values(
      status=TestRunStatus.FAILED.value,
      error_summary='Execution interrupted before completion.',
      completed_at=datetime.utcnow(),
    )
    result = self.db.execute(statement)
    self.db.commit()
    return result.rowcount

  def summary_counts(self, project_ids: tuple[int, ...] | None = None) -> dict[str, int | float]:
    statement = select(
      func.count(TestRun.id).label('total_runs'),
      func.sum(func.IF(TestRun.status == TestRunStatus.PASSED.value, 1, 0)).label('passed_runs'),
      func.sum(func.IF(TestRun.status == TestRunStatus.FAILED.value, 1, 0)).label('failed_runs'),
      func.sum(func.IF(TestRun.status == TestRunStatus.QUEUED.value, 1, 0)).label('queued_runs'),
      func.sum(func.IF(TestRun.status == TestRunStatus.RUNNING.value, 1, 0)).label('running_runs'),
      func.sum(TestRun.total_tests).label('total_tests'),
      func.sum(TestRun.duration_seconds).label('total_duration')
    )
    if project_ids is not None:
      statement = statement.where(TestRun.project_id.in_(project_ids))
    result = self.db.execute(statement).first()
    if result is None or result.total_runs == 0:
      return {'total_runs': 0, 'passed_runs': 0, 'failed_runs': 0, 'queued_runs': 0, 'running_runs': 0, 'pass_rate': 0, 'total_tests': 0, 'average_duration_seconds': 0}
    completed = (result.passed_runs or 0) + (result.failed_runs or 0)
    return {
      'total_runs': result.total_runs or 0,
      'passed_runs': result.passed_runs or 0,
      'failed_runs': result.failed_runs or 0,
      'queued_runs': result.queued_runs or 0,
      'running_runs': result.running_runs or 0,
      'pass_rate': round(((result.passed_runs or 0) / completed) * 100, 2) if completed else 0,
      'total_tests': result.total_tests or 0,
      'average_duration_seconds': round((result.total_duration or 0) / result.total_runs, 2) if result.total_runs else 0,
    }
