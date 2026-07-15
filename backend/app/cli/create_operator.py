import getpass
from datetime import datetime

from app.database import Base, SessionLocal, engine
from app.migrations import install_audit_protection, migrate_stage4_schema, migrate_stage6_schema
from app.models import operator_session, password_history
from app.models.operator import Operator
from app.repositories.operator_repository import OperatorRepository
from app.services.operator_security import add_password_history, password_expiry_from
from app.services.audit_service import append_event
from app.services.password_service import hash_password, normalize_username, validate_password


def main() -> None:
  print('Local AutoQA bootstrap administrative action. No default credentials are created.')
  username = normalize_username(input('Username: '))
  display_name = input('Display name: ').strip()
  role = input('Role [VIEWER/TESTER/APPROVER/ADMIN]: ').strip().upper()
  if role not in {'VIEWER', 'TESTER', 'APPROVER', 'ADMIN'}: raise SystemExit('Invalid role.')
  password = getpass.getpass('Password: '); confirmation = getpass.getpass('Confirm password: ')
  if password != confirmation: raise SystemExit('Passwords do not match.')
  validate_password(password, username, display_name)
  migrate_stage4_schema(engine); migrate_stage6_schema(engine); Base.metadata.create_all(engine); install_audit_protection(engine)
  with SessionLocal() as db:
    repository = OperatorRepository(db)
    if repository.by_username(username): raise SystemExit('Operator already exists.')
    if role == 'ADMIN' and repository.active_admin_count() > 0: raise SystemExit('An active ADMIN already exists. Use ADMIN operator management for additional accounts.')
    now = datetime.utcnow()
    operator = Operator(username=username, display_name=display_name, password_hash=hash_password(password), role=role, is_active=True, must_change_password=True, password_version=1, force_password_change_reason='BOOTSTRAP', credentials_updated_at=now, password_expires_at=password_expiry_from(now))
    db.add(operator); db.flush(); add_password_history(db, operator, None, 'BOOTSTRAP', now); append_event(db, 'BOOTSTRAP_ADMIN_CREATED' if role == 'ADMIN' else 'OPERATOR_CREATED', actor_type='SYSTEM', resource_type='OPERATOR', resource_id=str(operator.id), metadata={'username': username, 'role': role, 'requires_rotation': True}); db.commit()
  print(f'Local {role} operator created successfully.')


if __name__ == '__main__': main()
