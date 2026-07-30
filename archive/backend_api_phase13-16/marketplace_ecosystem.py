"""Phase 13 – Marketplace Ecosystem API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.marketplace_ecosystem import MarketplaceEcosystemService

router = APIRouter(prefix='/marketplace', tags=['Phase13-Marketplace'])


@router.post('/seed')
def seed_marketplace(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MarketplaceEcosystemService(db).seed_marketplace()


@router.get('/plugins')
def list_plugins(
    category: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_auth_context),
):
    return MarketplaceEcosystemService(db).list_plugins(category=category, search=search)


@router.post('/plugins/{plugin_id}/install')
def install_plugin(plugin_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MarketplaceEcosystemService(db).install_plugin(plugin_id)


@router.post('/plugins/{plugin_id}/uninstall')
def uninstall_plugin(plugin_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MarketplaceEcosystemService(db).uninstall_plugin(plugin_id)


@router.get('/categories')
def get_categories(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MarketplaceEcosystemService(db).get_categories()
