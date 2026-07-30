"""Health API router."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix='/api/health', tags=['health'])


@router.get('')
def health_check() -> dict:
    return {
        'status': 'ok',
        'system': 'demo-product',
        'version': '1.0.0',
    }
