import builtins
import getpass
import json

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.audit_event import AuditEvent
from app.models.operator import Operator
from app.models.password_history import PasswordHistory


def stage7_password() -> str:
  return ''.join(['Quartz', '!', 'River', '4820'])


def run_bootstrap(monkeypatch, tmp_path, answers: list[str], password: str) -> None:
  from app.cli import create_operator

  engine = create_engine(f'sqlite:///{tmp_path / "bootstrap.db"}', connect_args={'check_same_thread': False})
  SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
  prompt_answers = iter(answers)
  password_answers = iter([password, password])
  monkeypatch.setattr(create_operator, 'engine', engine)
  monkeypatch.setattr(create_operator, 'SessionLocal', SessionLocal)
  monkeypatch.setattr(builtins, 'input', lambda _prompt='': next(prompt_answers))
  monkeypatch.setattr(getpass, 'getpass', lambda _prompt='': next(password_answers))
  create_operator.main()
  engine.dispose()


def test_bootstrap_admin_is_forced_to_rotate_and_audited(monkeypatch, tmp_path, capsys):
  password = stage7_password()
  run_bootstrap(monkeypatch, tmp_path, ['stage7-admin', 'Stage Seven Admin', 'ADMIN'], password)

  engine = create_engine(f'sqlite:///{tmp_path / "bootstrap.db"}', connect_args={'check_same_thread': False})
  with sessionmaker(bind=engine)() as db:
    operator = db.scalar(select(Operator).where(Operator.username == 'stage7-admin'))
    assert operator is not None
    assert operator.role == 'ADMIN'
    assert operator.is_active is True
    assert operator.must_change_password is True
    assert operator.force_password_change_reason == 'BOOTSTRAP'
    assert operator.password_version == 1
    assert operator.password_changed_at is None
    assert operator.password_expires_at is None

    history = db.scalar(select(PasswordHistory).where(PasswordHistory.operator_id == operator.id))
    assert history is not None
    assert history.change_reason == 'BOOTSTRAP'
    assert history.password_version == 1

    event = db.scalar(select(AuditEvent).where(AuditEvent.action == 'BOOTSTRAP_ADMIN_CREATED'))
    assert event is not None
    assert event.outcome == 'SUCCESS'
    metadata = json.loads(event.metadata_json or '{}')
    assert metadata == {'username': 'stage7-admin', 'role': 'ADMIN', 'requires_rotation': True}
    assert 'password' not in event.metadata_json.lower()

  output = capsys.readouterr().out
  assert password not in output
  assert 'created successfully' in output
  engine.dispose()


def test_bootstrap_rejects_second_active_admin(monkeypatch, tmp_path):
  password = stage7_password()
  run_bootstrap(monkeypatch, tmp_path, ['stage7-admin', 'Stage Seven Admin', 'ADMIN'], password)

  from app.cli import create_operator

  engine = create_engine(f'sqlite:///{tmp_path / "bootstrap.db"}', connect_args={'check_same_thread': False})
  SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
  prompt_answers = iter(['second-admin', 'Second Admin', 'ADMIN'])
  password_answers = iter([password, password])
  monkeypatch.setattr(create_operator, 'engine', engine)
  monkeypatch.setattr(create_operator, 'SessionLocal', SessionLocal)
  monkeypatch.setattr(builtins, 'input', lambda _prompt='': next(prompt_answers))
  monkeypatch.setattr(getpass, 'getpass', lambda _prompt='': next(password_answers))

  with pytest.raises(SystemExit, match='An active ADMIN already exists'):
    create_operator.main()

  with SessionLocal() as db:
    operators = list(db.scalars(select(Operator).where(Operator.role == 'ADMIN')))
    assert len(operators) == 1
  engine.dispose()


def test_bootstrap_allows_operator_when_admin_exists(monkeypatch, tmp_path):
  password = stage7_password()
  run_bootstrap(monkeypatch, tmp_path, ['stage7-admin', 'Stage Seven Admin', 'ADMIN'], password)
  run_bootstrap(monkeypatch, tmp_path, ['stage7-viewer', 'Stage Seven Viewer', 'VIEWER'], password)

  engine = create_engine(f'sqlite:///{tmp_path / "bootstrap.db"}', connect_args={'check_same_thread': False})
  with sessionmaker(bind=engine)() as db:
    viewer = db.scalar(select(Operator).where(Operator.username == 'stage7-viewer'))
    assert viewer is not None
    assert viewer.role == 'VIEWER'
    assert viewer.must_change_password is True
    event = db.scalar(select(AuditEvent).where(AuditEvent.action == 'OPERATOR_CREATED', AuditEvent.resource_id == str(viewer.id)))
    assert event is not None
  engine.dispose()
