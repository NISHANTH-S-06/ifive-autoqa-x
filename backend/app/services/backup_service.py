import hashlib
import json
import os
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import PROJECT_ROOT, Settings, settings


BACKUP_FORMAT = 1


def _sha256(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open('rb') as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
      digest.update(chunk)
  return digest.hexdigest()


def _safe_relative(value: str) -> Path:
  candidate = Path(value)
  if candidate.is_absolute() or '..' in candidate.parts or not candidate.parts:
    raise ValueError('Backup manifest contains an unsafe path.')
  return candidate


def _contained(path: Path, root: Path) -> Path:
  resolved = path.resolve()
  try:
    resolved.relative_to(root.resolve())
  except ValueError:
    raise ValueError('Backup path escapes the configured backup directory.') from None
  return resolved


def _copy_tree(source: Path, destination: Path) -> None:
  if not source.is_dir():
    return
  for path in source.rglob('*'):
    if path.is_symlink() or not path.is_file():
      continue
    relative = path.relative_to(source)
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def _configuration_templates() -> list[Path]:
  templates = [PROJECT_ROOT / '.env.example', PROJECT_ROOT / 'backend' / '.env.example', PROJECT_ROOT / 'frontend' / '.env.example', PROJECT_ROOT / 'qa' / '.env.example']
  config_root = PROJECT_ROOT / 'config'
  if config_root.is_dir():
    templates.extend(path for path in config_root.glob('*.example') if path.is_file())
  return templates


def create_backup(config: Settings = settings, database_path: Path | None = None) -> dict:
  config.validate()
  source_db = (database_path or config.database_path).resolve()
  if not source_db.is_file():
    raise FileNotFoundError('Configured SQLite database is unavailable.')
  backup_id = datetime.now(timezone.utc).strftime('AUTOQA-%Y%m%dT%H%M%S-%fZ')
  backup_dir = _contained(config.backup_root / backup_id, config.backup_root)
  if backup_dir.exists():
    raise FileExistsError('Backup destination already exists.')
  backup_dir.mkdir(parents=True)
  try:
    database_target = backup_dir / 'database' / 'autoqa.db'
    database_target.parent.mkdir(parents=True)
    with closing(sqlite3.connect(source_db)) as source, closing(sqlite3.connect(database_target)) as destination:
      source.backup(destination)
      destination.commit()
    sources = {
      'data/stage8_evidence': config.evidence_root,
      'data/stage10_artifacts': config.artifact_root,
      'data/stage13_exports': config.export_root,
      'qa/runs': config.qa_runs_root,
    }
    for relative, source in sources.items():
      _copy_tree(source, backup_dir / relative)
    for source in _configuration_templates():
      if source.is_file():
        target = backup_dir / 'configuration' / source.relative_to(PROJECT_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    entries = []
    for path in sorted(item for item in backup_dir.rglob('*') if item.is_file()):
      relative = path.relative_to(backup_dir).as_posix()
      entries.append({'path': relative, 'size_bytes': path.stat().st_size, 'sha256': _sha256(path)})
    manifest = {
      'format_version': BACKUP_FORMAT,
      'backup_id': backup_id,
      'created_at': datetime.now(timezone.utc).isoformat(),
      'entries': entries,
    }
    manifest_path = backup_dir / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding='utf-8')
    return {
      'backup_id': backup_id,
      'file_count': len(entries),
      'total_bytes': sum(item['size_bytes'] for item in entries),
      'manifest_sha256': _sha256(manifest_path),
    }
  except Exception:
    shutil.rmtree(backup_dir, ignore_errors=True)
    raise


def validate_backup(backup_dir: Path, config: Settings = settings) -> dict:
  root = _contained(backup_dir, config.backup_root)
  manifest_path = root / 'manifest.json'
  if not manifest_path.is_file():
    raise ValueError('Backup manifest is missing.')
  try:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
  except (json.JSONDecodeError, UnicodeDecodeError):
    raise ValueError('Backup manifest is invalid.') from None
  if manifest.get('format_version') != BACKUP_FORMAT or manifest.get('backup_id') != root.name:
    raise ValueError('Backup manifest identity is invalid.')
  entries = manifest.get('entries')
  if not isinstance(entries, list) or not entries:
    raise ValueError('Backup manifest has no files.')
  seen: set[str] = set()
  for entry in entries:
    if not isinstance(entry, dict):
      raise ValueError('Backup manifest entry is invalid.')
    relative = _safe_relative(str(entry.get('path', '')))
    normalized = relative.as_posix()
    if normalized in seen:
      raise ValueError('Backup manifest contains duplicate paths.')
    seen.add(normalized)
    path = _contained(root / relative, root)
    if not path.is_file() or path.stat().st_size != entry.get('size_bytes') or _sha256(path) != entry.get('sha256'):
      raise ValueError(f'Backup checksum validation failed for {normalized}.')
  if 'database/autoqa.db' not in seen:
    raise ValueError('Backup database is missing.')
  try:
    with closing(sqlite3.connect(root / 'database' / 'autoqa.db')) as connection:
      result = connection.execute('PRAGMA integrity_check').fetchone()
    if not result or result[0] != 'ok':
      raise ValueError('Backup database integrity check failed.')
  except sqlite3.DatabaseError:
    raise ValueError('Backup database is invalid.') from None
  return {'backup_id': root.name, 'file_count': len(entries), 'manifest_sha256': _sha256(manifest_path)}


def restore_backup(backup_dir: Path, confirmation: str, config: Settings = settings) -> dict:
  validated = validate_backup(backup_dir, config)
  if confirmation != f'RESTORE {validated["backup_id"]}':
    raise ValueError('Restore confirmation does not match the selected backup.')
  pre_restore = create_backup(config)
  root = _contained(backup_dir, config.backup_root)
  staging = _contained(config.temp_root / f'restore-{uuid4().hex}', config.temp_root)
  rollback = _contained(config.temp_root / f'rollback-{uuid4().hex}', config.temp_root)
  staging.mkdir(parents=True)
  rollback.mkdir(parents=True)
  replacements: list[tuple[Path, Path | None]] = []
  try:
    staged_db = staging / 'autoqa.db'
    shutil.copy2(root / 'database' / 'autoqa.db', staged_db)
    directories = {
      config.evidence_root: root / 'data' / 'stage8_evidence',
      config.artifact_root: root / 'data' / 'stage10_artifacts',
      config.export_root: root / 'data' / 'stage13_exports',
      config.qa_runs_root: root / 'qa' / 'runs',
      config.runtime_root / 'restored-configuration' / validated['backup_id']: root / 'configuration',
    }
    staged_dirs: dict[Path, Path] = {}
    for index, (target, source) in enumerate(directories.items()):
      staged_target = staging / f'directory-{index}'
      staged_target.mkdir()
      _copy_tree(source, staged_target)
      staged_dirs[target] = staged_target
    targets: list[tuple[Path, Path]] = [(config.database_path, staged_db), *staged_dirs.items()]
    for index, (target, staged_source) in enumerate(targets):
      target.parent.mkdir(parents=True, exist_ok=True)
      previous = rollback / f'item-{index}' if target.exists() else None
      if previous:
        target.replace(previous)
      replacements.append((target, previous))
      staged_source.replace(target)
    return {'backup_id': validated['backup_id'], 'pre_restore_backup_id': pre_restore['backup_id'], 'restored_items': len(targets)}
  except Exception:
    for target, previous in reversed(replacements):
      if target.exists():
        if target.is_dir():
          shutil.rmtree(target)
        else:
          target.unlink()
      if previous and previous.exists():
        previous.replace(target)
    raise
  finally:
    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(rollback, ignore_errors=True)
