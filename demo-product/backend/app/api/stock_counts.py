"""Stock Counts API router."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.schemas.inventory import StockCountCreate, StockCountOut
from app.services import inventory_service

router = APIRouter(prefix='/api/stock-counts', tags=['stock-counts'])


@router.get('', response_model=List[StockCountOut])
def list_stock_counts(
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> List[StockCountOut]:
    return inventory_service.list_stock_counts(db)


@router.post('', response_model=StockCountOut, status_code=status.HTTP_201_CREATED)
def create_stock_count(
    payload: StockCountCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> StockCountOut:
    ctx.require_role('DEMO_ADMIN', 'INVENTORY_USER')
    return inventory_service.create_stock_count(db, payload, created_by=ctx.username)
