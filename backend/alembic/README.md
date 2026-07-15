# Alembic migration foundation

Alembic commands require `AUTOQA_ALEMBIC_DATABASE_URL`; no database URL or
credential is stored in this directory. SQLite targets that resolve to the
active application database are rejected unless a later, separately approved
operation explicitly sets `AUTOQA_ALEMBIC_ALLOW_ACTIVE_DATABASE=true`.

Existing databases must be schema-compared with a clean baseline database
before they are stamped. Use `app.migration_safety.stamp_existing_database`
instead of calling `alembic stamp` directly in operational tooling.

The handwritten compatibility migrations in `app/migrations.py` remain active
until a later phase proves they can be replaced safely.
