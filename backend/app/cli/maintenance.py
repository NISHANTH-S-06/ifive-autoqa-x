import argparse
from pathlib import Path

from app import main as _model_registry
from app.config import settings
from app.database import SessionLocal, engine
from app.services.audit_service import append_event
from app.services.backup_service import create_backup, restore_backup, validate_backup
from app.services.retention_service import CONFIRMATION, cleanup_retention


def run() -> None:
  parser = argparse.ArgumentParser(description='Explicit local AutoQA backup, restore, and retention operations.')
  subparsers = parser.add_subparsers(dest='command', required=True)
  subparsers.add_parser('backup')
  validate_parser = subparsers.add_parser('validate')
  validate_parser.add_argument('backup_id')
  restore_parser = subparsers.add_parser('restore')
  restore_parser.add_argument('backup_id')
  cleanup_parser = subparsers.add_parser('cleanup')
  cleanup_parser.add_argument('--apply', action='store_true')
  args = parser.parse_args()
  settings.prepare_directories()
  if args.command == 'backup':
    answer = input('Type CREATE LOCAL BACKUP to continue: ')
    if answer != 'CREATE LOCAL BACKUP':
      raise SystemExit('Backup cancelled.')
    result = create_backup()
    with SessionLocal() as db:
      append_event(db, 'LOCAL_BACKUP_CREATED', actor_type='SYSTEM', resource_type='BACKUP', resource_id=result['backup_id'], metadata={'file_count': result['file_count']})
      db.commit()
    print(f"Backup created: {result['backup_id']} ({result['file_count']} files)")
  elif args.command == 'validate':
    result = validate_backup(settings.backup_root / args.backup_id)
    print(f"Backup valid: {result['backup_id']} ({result['file_count']} files)")
  elif args.command == 'restore':
    confirmation = input(f'Type RESTORE {args.backup_id} to continue: ')
    engine.dispose()
    result = restore_backup(settings.backup_root / args.backup_id, confirmation)
    with SessionLocal() as db:
      append_event(db, 'LOCAL_BACKUP_RESTORED', actor_type='SYSTEM', resource_type='BACKUP', resource_id=result['backup_id'], metadata={'pre_restore_backup_id': result['pre_restore_backup_id'], 'restored_items': result['restored_items']})
      db.commit()
    print(f"Backup restored: {result['backup_id']}; safety backup: {result['pre_restore_backup_id']}")
  else:
    confirmation = None
    if args.apply:
      confirmation = input(f'Type {CONFIRMATION} to continue: ')
    with SessionLocal() as db:
      result = cleanup_retention(db, dry_run=not args.apply, confirmation=confirmation)
      db.commit()
    label = 'completed' if args.apply else 'preview'
    print(f"Cleanup {label}: {result['candidate_files']} files, {sum(result['records_removed'].values())} operational records")


if __name__ == '__main__':
  run()

