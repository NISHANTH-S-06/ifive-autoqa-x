"""FastAPI Application for Demo Product Website."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession

from app.api import auth, demo_settings, departments, employees, health, products, stock_counts
from app.database import DATABASE_URL, SessionLocal
from app.services.demo_setting_service import is_bug_enabled

BACKEND_ROOT = Path(__file__).parent.parent
ALEMBIC_INI = BACKEND_ROOT / 'alembic.ini'


def _run_migrations() -> None:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option('sqlalchemy.url', DATABASE_URL.replace('%', '%%'))
    command.upgrade(cfg, 'head')


def _seed_if_needed() -> None:
    from app.seed import seed
    db: DBSession = SessionLocal()
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
    title='Demo Product Website API',
    description='Local ERP Demo Target System for AutoQA testing.',
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


@app.middleware('http')
async def api_delay_middleware(request: Request, call_next):
    # Check if api_delay bug toggle is enabled
    # Skip delay for health and demo-settings so admin toggles remain responsive
    if not request.url.path.startswith('/api/health') and not request.url.path.startswith('/api/demo-settings'):
        print(f"API REQUEST: {request.method} {request.url.path}")
        try:
            db: DBSession = SessionLocal()
            try:
                if is_bug_enabled(db, 'api_delay'):
                    time.sleep(3)
            finally:
                db.close()
        except Exception:
            # Handle uninitialized database or test environment gracefully
            pass
    return await call_next(request)


app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(products.router)
app.include_router(stock_counts.router)
app.include_router(demo_settings.router)
app.include_router(health.router)
