"""Demo Settings (bug toggles) API router."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, get_auth_context, get_optional_auth_context
from app.database import get_db
from app.schemas.demo_setting import DemoSettingOut, DemoSettingUpdate
from app.services import demo_setting_service

router = APIRouter(tags=['demo-settings'])


@router.get('/api/demo-settings', response_model=List[DemoSettingOut])
def list_demo_settings(
    ctx: Optional[AuthContext] = Depends(get_optional_auth_context),
    db: DBSession = Depends(get_db),
) -> List[DemoSettingOut]:
    return demo_setting_service.get_all_settings(db)


@router.patch('/api/demo-settings/{key}', response_model=DemoSettingOut)
def update_demo_setting(
    key: str,
    payload: DemoSettingUpdate,
    ctx: Optional[AuthContext] = Depends(get_optional_auth_context),
    db: DBSession = Depends(get_db),
) -> DemoSettingOut:
    if ctx is None or ctx.role != 'DEMO_ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Role is not permitted for this action.',
        )
    if key not in demo_setting_service.KNOWN_BUG_KEYS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Unknown bug toggle key {key!r}. Known: {demo_setting_service.KNOWN_BUG_KEYS}',
        )
    return demo_setting_service.update_setting(db, key, payload.enabled, payload.value)


@router.post('/api/demo-bugs/toggles/{key}', response_model=DemoSettingOut)
def toggle_demo_bug(
    key: str,
    enabled: bool = Query(True),
    ctx: Optional[AuthContext] = Depends(get_optional_auth_context),
    db: DBSession = Depends(get_db),
) -> DemoSettingOut:
    if ctx is None or ctx.role != 'DEMO_ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Role is not permitted for this action.',
        )
    if key not in demo_setting_service.KNOWN_BUG_KEYS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Unknown bug toggle key {key!r}. Known: {demo_setting_service.KNOWN_BUG_KEYS}',
        )
    return demo_setting_service.update_setting(db, key, enabled)
