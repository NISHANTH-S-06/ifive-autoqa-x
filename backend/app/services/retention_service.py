from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import BACKEND_ROOT, PROJECT_ROOT, Settings, settings
from app.models.automated_execution import AutomatedRun, ExecutionArtifact, ExecutionJob
from app.models.connection_target import ConnectionCheck
from app.models.evidence import Evidence
from app.models.operator_session import OperatorSession
from app.models.reporting import ReportExport
from app.models.test_management import ManualEvidence, ManualTestRun, ManualTestRunCase
from app.models.test_run import TestRun
from app.services.audit_service import append_event


AUTOMATED_TERMINAL = {'PASSED', 'FAILED', 'CANCELLED', 'TIMED_OUT', 'BLOCKED'}
MANUAL_TERMINAL = {'COMPLETED', 'CANCELLED'}
LEGACY_TERMINAL = {'PASSED', 'FAILED', 'CANCELLED'}
JOB_TERMINAL = {'COMPLETED', 'FAILED', 'CANCELLED', 'TIMED_OUT', 'BLOCKED'}
CONFIRMATION = 'DELETE RETAINED FILES'


@dataclass(frozen=True)
class FileCandidate:
  category: str
  path: Path
  root: Path
  record: object | None = None


def _contained(path: Path, root: Path) -> Path:
  resolved = path.resolve()
  try:
    resolved.relative_to(root.resolve())
  except ValueError:
    raise ValueError('Retention candidate escapes an approved storage root.') from None
  source_roots = {PROJECT_ROOT.resolve(), BACKEND_ROOT.resolve(), (PROJECT_ROOT / 'frontend').resolve(), (PROJECT_ROOT / 'qa').resolve()}
  if resolved in source_roots:
    raise ValueError('Retention must not target a source directory.')
  return resolved


def _data_path(relative: str, config: Settings) -> Path:
  value = Path(relative)
  if value.is_absolute() or '..' in value.parts:
    raise ValueError('Stored file path is unsafe.')
  if value.parts and value.parts[0].lower() == 'data':
    return BACKEND_ROOT / value
  return config.data_root / value


def _candidate(category: str, path: Path, root: Path, record: object | None = None) -> FileCandidate:
  return FileCandidate(category, _contained(path, root), root.resolve(), record)


def _collect_files(db: Session, now: datetime, config: Settings) -> list[FileCandidate]:
  files: list[FileCandidate] = []
  artifact_cutoff = now - timedelta(days=config.retention_artifact_days)
  evidence_cutoff = now - timedelta(days=config.retention_evidence_days)
  export_cutoff = now - timedelta(days=config.retention_export_days)

  artifact_rows = db.execute(
    select(ExecutionArtifact, AutomatedRun).join(AutomatedRun, AutomatedRun.id == ExecutionArtifact.run_id).where(
      ExecutionArtifact.created_at < artifact_cutoff,
      AutomatedRun.status.in_(AUTOMATED_TERMINAL),
      AutomatedRun.completed_at.is_not(None),
    )
  ).all()
  for artifact, _ in artifact_rows:
    files.append(_candidate('execution_artifacts', _data_path(artifact.relative_path, config), config.artifact_root, artifact))

  manual_rows = db.execute(
    select(ManualEvidence, ManualTestRun).join(ManualTestRunCase, ManualTestRunCase.id == ManualEvidence.run_case_id).join(ManualTestRun, ManualTestRun.id == ManualTestRunCase.run_id).where(
      ManualEvidence.created_at < evidence_cutoff,
      ManualEvidence.deleted_at.is_(None),
      ManualTestRun.status.in_(MANUAL_TERMINAL),
    )
  ).all()
  for evidence, _ in manual_rows:
    files.append(_candidate('manual_evidence', _data_path(evidence.relative_path, config), config.evidence_root, evidence))

  legacy_rows = db.execute(
    select(Evidence, TestRun).join(TestRun, TestRun.id == Evidence.test_run_id).where(
      Evidence.created_at < evidence_cutoff,
      TestRun.status.in_(LEGACY_TERMINAL),
      TestRun.completed_at.is_not(None),
    )
  ).all()
  qa_root = config.qa_runs_root
  for evidence, run in legacy_rows:
    relative = Path(evidence.relative_path)
    path = PROJECT_ROOT / relative if relative.parts and relative.parts[0].lower() == 'qa' else qa_root / run.run_code / relative.name
    files.append(_candidate('playwright_evidence', path, qa_root, evidence))

  for export in db.scalars(select(ReportExport).where(ReportExport.created_at < export_cutoff, ReportExport.deleted_at.is_(None))):
    files.append(_candidate('report_exports', config.export_root / export.stored_filename, config.export_root, export))

  if config.temp_root.is_dir():
    operational_cutoff = now - timedelta(days=config.retention_operational_days)
    for path in config.temp_root.rglob('*'):
      if path.is_file() and datetime.fromtimestamp(path.stat().st_mtime) < operational_cutoff:
        files.append(_candidate('temporary_runtime', path, config.temp_root))
  unique: dict[str, FileCandidate] = {}
  for item in files:
    unique[str(item.path).lower()] = item
  return list(unique.values())


def cleanup_retention(db: Session, dry_run: bool = True, confirmation: str | None = None, config: Settings = settings, now: datetime | None = None, operator_id: int | None = None) -> dict:
  current = now or datetime.utcnow()
  if not dry_run and confirmation != CONFIRMATION:
    raise ValueError('Cleanup confirmation is required.')
  candidates = _collect_files(db, current, config)
  summary = {
    'dry_run': dry_run,
    'candidate_files': len(candidates),
    'candidate_bytes': sum(item.path.stat().st_size for item in candidates if item.path.is_file()),
    'deleted_files': 0,
    'deleted_bytes': 0,
    'records_removed': {'connection_checks': 0, 'expired_sessions': 0, 'completed_jobs': 0},
    'categories': {},
    'protected': {'active_run_artifacts': True, 'audit_history': True, 'password_history': True, 'immutable_histories': True},
  }
  for item in candidates:
    summary['categories'][item.category] = summary['categories'].get(item.category, 0) + 1
  operational_cutoff = current - timedelta(days=config.retention_operational_days)
  old_checks = list(db.scalars(select(ConnectionCheck).where(ConnectionCheck.created_at < operational_cutoff)))
  old_sessions = list(db.scalars(select(OperatorSession).where(OperatorSession.expires_at < operational_cutoff, or_(OperatorSession.revoked_at.is_not(None), OperatorSession.expires_at < current))))
  old_jobs = list(db.scalars(select(ExecutionJob).where(ExecutionJob.updated_at < operational_cutoff, ExecutionJob.status.in_(JOB_TERMINAL))))
  summary['records_removed'] = {'connection_checks': len(old_checks), 'expired_sessions': len(old_sessions), 'completed_jobs': len(old_jobs)}
  if not dry_run:
    for item in candidates:
      if not item.path.is_file():
        continue
      size = item.path.stat().st_size
      item.path.unlink()
      summary['deleted_files'] += 1
      summary['deleted_bytes'] += size
      if isinstance(item.record, ManualEvidence):
        item.record.deleted_at = current
      if isinstance(item.record, ReportExport):
        item.record.deleted_at = current
    for record in [*old_checks, *old_sessions, *old_jobs]:
      db.delete(record)
  append_event(
    db,
    'RETENTION_CLEANUP_PREVIEWED' if dry_run else 'RETENTION_CLEANUP_COMPLETED',
    operator_id=operator_id,
    actor_type='OPERATOR' if operator_id is not None else 'SYSTEM',
    resource_type='RETENTION',
    metadata={
      'dry_run': dry_run,
      'candidate_files': summary['candidate_files'],
      'deleted_files': summary['deleted_files'],
      'records_removed': sum(summary['records_removed'].values()) if not dry_run else 0,
    },
  )
  return summary
