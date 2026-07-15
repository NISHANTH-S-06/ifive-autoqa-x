from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestProject(Base):
  __tablename__ = 'test_projects'
  __table_args__ = (
    UniqueConstraint('code', name='uq_test_projects_code'),
    Index('ix_test_projects_owner', 'owner_operator_id'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(160), nullable=False)
  code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE', index=True)
  owner_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
  archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

  modules: Mapped[list['TestModule']] = relationship(back_populates='project')
  suites: Mapped[list['ManagedTestSuite']] = relationship(back_populates='project')
  cases: Mapped[list['ManagedTestCase']] = relationship(back_populates='project')


class TestModule(Base):
  __tablename__ = 'test_modules'
  __table_args__ = (
    UniqueConstraint('project_id', 'code', name='uq_test_modules_project_code'),
    Index('ix_test_modules_project_code', 'project_id', 'code'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(160), nullable=False)
  code: Mapped[str] = mapped_column(String(40), nullable=False)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE', index=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
  archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  project: Mapped[TestProject] = relationship(back_populates='modules')
  suites: Mapped[list['ManagedTestSuite']] = relationship(back_populates='module')
  cases: Mapped[list['ManagedTestCase']] = relationship(back_populates='module')


class ManagedTestSuite(Base):
  __tablename__ = 'managed_test_suites'
  __table_args__ = (
    UniqueConstraint('project_id', 'module_id', 'code', name='uq_managed_test_suites_scope_code'),
    Index('ix_managed_test_suites_scope_code', 'project_id', 'module_id', 'code'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
  module_id: Mapped[int] = mapped_column(ForeignKey('test_modules.id'), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(160), nullable=False)
  code: Mapped[str] = mapped_column(String(40), nullable=False)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  suite_type: Mapped[str] = mapped_column(String(40), nullable=False, default='MANUAL')
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE', index=True)
  owner_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
  archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  project: Mapped[TestProject] = relationship(back_populates='suites')
  module: Mapped[TestModule] = relationship(back_populates='suites')
  cases: Mapped[list['ManagedTestCase']] = relationship(back_populates='suite')
  manual_runs: Mapped[list['ManualTestRun']] = relationship(back_populates='suite')


class ManagedTestCase(Base):
  __tablename__ = 'managed_test_cases'
  __table_args__ = (
    UniqueConstraint('case_key', name='uq_managed_test_cases_key'),
    Index('ix_managed_test_cases_lifecycle', 'lifecycle_state'),
    Index('ix_managed_test_cases_owner', 'owner_operator_id'),
    Index('ix_managed_test_cases_updated', 'updated_at'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
  module_id: Mapped[int] = mapped_column(ForeignKey('test_modules.id'), nullable=False, index=True)
  suite_id: Mapped[int] = mapped_column(ForeignKey('managed_test_suites.id'), nullable=False, index=True)
  case_key: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
  title: Mapped[str] = mapped_column(String(220), nullable=False)
  objective: Mapped[str | None] = mapped_column(Text, nullable=True)
  preconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
  test_type: Mapped[str] = mapped_column(String(40), nullable=False, default='FUNCTIONAL', index=True)
  priority: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM', index=True)
  severity: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM')
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE')
  lifecycle_state: Mapped[str] = mapped_column(String(20), nullable=False, default='DRAFT')
  owner_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)
  reviewed_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  approved_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
  reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

  project: Mapped[TestProject] = relationship(back_populates='cases')
  module: Mapped[TestModule] = relationship(back_populates='cases')
  suite: Mapped[ManagedTestSuite] = relationship(back_populates='cases')
  steps: Mapped[list['TestCaseStep']] = relationship(back_populates='test_case', cascade='all, delete-orphan', order_by='TestCaseStep.step_number')
  versions: Mapped[list['TestCaseVersion']] = relationship(back_populates='test_case', order_by='TestCaseVersion.version_number')
  tag_links: Mapped[list['TestCaseTag']] = relationship(back_populates='test_case', cascade='all, delete-orphan')


class TestCaseStep(Base):
  __tablename__ = 'test_case_steps'
  __table_args__ = (
    UniqueConstraint('test_case_id', 'step_number', name='uq_test_case_steps_case_number'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  test_case_id: Mapped[int] = mapped_column(ForeignKey('managed_test_cases.id'), nullable=False, index=True)
  step_number: Mapped[int] = mapped_column(Integer, nullable=False)
  action: Mapped[str] = mapped_column(Text, nullable=False)
  expected_result: Mapped[str] = mapped_column(Text, nullable=False)
  test_data: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

  test_case: Mapped[ManagedTestCase] = relationship(back_populates='steps')


class TestCaseVersion(Base):
  __tablename__ = 'test_case_versions'
  __table_args__ = (
    UniqueConstraint('test_case_id', 'version_number', name='uq_test_case_versions_case_version'),
    Index('ix_test_case_versions_case_version', 'test_case_id', 'version_number'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  test_case_id: Mapped[int] = mapped_column(ForeignKey('managed_test_cases.id'), nullable=False, index=True)
  version_number: Mapped[int] = mapped_column(Integer, nullable=False)
  snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
  change_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  source_state: Mapped[str] = mapped_column(String(20), nullable=False)

  test_case: Mapped[ManagedTestCase] = relationship(back_populates='versions')


class Tag(Base):
  __tablename__ = 'tags'
  __table_args__ = (UniqueConstraint('normalized_name', name='uq_tags_normalized_name'),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  normalized_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  case_links: Mapped[list['TestCaseTag']] = relationship(back_populates='tag')


class TestCaseTag(Base):
  __tablename__ = 'test_case_tags'
  __table_args__ = (UniqueConstraint('test_case_id', 'tag_id', name='uq_test_case_tags_case_tag'),)

  test_case_id: Mapped[int] = mapped_column(ForeignKey('managed_test_cases.id'), primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  tag_id: Mapped[int] = mapped_column(ForeignKey('tags.id'), primary_key=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  test_case: Mapped[ManagedTestCase] = relationship(back_populates='tag_links')
  tag: Mapped[Tag] = relationship(back_populates='case_links')


class ManualTestRun(Base):
  __tablename__ = 'manual_test_runs'
  __table_args__ = (
    UniqueConstraint('run_key', name='uq_manual_test_runs_key'),
    Index('ix_manual_test_runs_status', 'status'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_key: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
  suite_id: Mapped[int] = mapped_column(ForeignKey('managed_test_suites.id'), nullable=False)
  name: Mapped[str] = mapped_column(String(180), nullable=False)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='PLANNED')
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  assigned_to: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

  suite: Mapped[ManagedTestSuite] = relationship(back_populates='manual_runs')
  cases: Mapped[list['ManualTestRunCase']] = relationship(back_populates='run', cascade='all, delete-orphan')


class ManualTestRunCase(Base):
  __tablename__ = 'manual_test_run_cases'
  __table_args__ = (
    UniqueConstraint('run_id', 'test_case_id', 'test_case_version', name='uq_manual_run_case_version'),
    Index('ix_manual_test_run_cases_status', 'status'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_id: Mapped[int] = mapped_column(ForeignKey('manual_test_runs.id'), nullable=False, index=True)
  test_case_id: Mapped[int] = mapped_column(ForeignKey('managed_test_cases.id'), nullable=False)
  test_case_version: Mapped[int] = mapped_column(Integer, nullable=False)
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='NOT_RUN')
  assigned_to: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  actual_result: Mapped[str | None] = mapped_column(Text, nullable=True)
  notes: Mapped[str | None] = mapped_column(Text, nullable=True)
  executed_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

  run: Mapped[ManualTestRun] = relationship(back_populates='cases')
  step_results: Mapped[list['ManualStepResult']] = relationship(back_populates='run_case', cascade='all, delete-orphan')
  evidence: Mapped[list['ManualEvidence']] = relationship(back_populates='run_case')


class ManualStepResult(Base):
  __tablename__ = 'manual_step_results'
  __table_args__ = (
    UniqueConstraint('run_case_id', 'step_number', name='uq_manual_step_results_case_step'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_case_id: Mapped[int] = mapped_column(ForeignKey('manual_test_run_cases.id'), nullable=False, index=True)
  step_number: Mapped[int] = mapped_column(Integer, nullable=False)
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='NOT_RUN')
  actual_result: Mapped[str | None] = mapped_column(Text, nullable=True)
  notes: Mapped[str | None] = mapped_column(Text, nullable=True)
  executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  executed_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)

  run_case: Mapped[ManualTestRunCase] = relationship(back_populates='step_results')
  evidence: Mapped[list['ManualEvidence']] = relationship(back_populates='step_result')


class ManualEvidence(Base):
  __tablename__ = 'manual_evidence'
  __table_args__ = (Index('ix_manual_evidence_run_case', 'run_case_id'),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_case_id: Mapped[int] = mapped_column(ForeignKey('manual_test_run_cases.id'), nullable=False)
  step_result_id: Mapped[int | None] = mapped_column(ForeignKey('manual_step_results.id'), nullable=True)
  evidence_type: Mapped[str] = mapped_column(String(20), nullable=False)
  original_filename: Mapped[str] = mapped_column(String(240), nullable=False)
  stored_filename: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
  relative_path: Mapped[str] = mapped_column(String(500), nullable=False)
  mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
  size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
  sha256: Mapped[str] = mapped_column(String(64), nullable=False)
  uploaded_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  deleted_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)

  run_case: Mapped[ManualTestRunCase] = relationship(back_populates='evidence')
  step_result: Mapped[ManualStepResult | None] = relationship(back_populates='evidence')
