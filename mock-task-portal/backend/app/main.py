"""Mock Task Portal — FastAPI application."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api import auth, dashboard, tasks, users
from app.database import DATABASE_URL, SessionLocal, engine

BACKEND_ROOT = Path(__file__).parent.parent
ALEMBIC_INI = BACKEND_ROOT / 'alembic.ini'


def _run_migrations() -> None:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option('sqlalchemy.url', DATABASE_URL.replace('%', '%%'))
    command.upgrade(cfg, 'head')


def _seed_if_needed() -> None:
    from app.seed import seed
    db: Session = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_migrations()
    _seed_if_needed()
    yield


app = FastAPI(
    title='Mock Task Portal',
    description='Local-only mock task workflow portal — no real company systems.',
    version='1.0.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173', 'http://127.0.0.1:5173',
        'http://localhost:5174', 'http://127.0.0.1:5174',
        'http://localhost:5175', 'http://127.0.0.1:5175',
        'http://localhost:8000', 'http://127.0.0.1:8000',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)


@app.get('/api/health')
def health() -> dict:
    return {'status': 'ok', 'system': 'mock-task-portal', 'version': '1.0.0'}
