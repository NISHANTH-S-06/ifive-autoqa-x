"""Products API router."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.schemas.inventory import ProductOut
from app.services import inventory_service

router = APIRouter(prefix='/api/products', tags=['products'])


@router.get('', response_model=List[ProductOut])
def list_products(
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> List[ProductOut]:
    return inventory_service.list_products(db)
