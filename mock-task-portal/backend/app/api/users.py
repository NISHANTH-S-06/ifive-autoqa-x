"""Users API router — read-only user list for dropdowns."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.user import User
from app.schemas.users import UserOut

router = APIRouter(prefix='/api/users', tags=['users'])


@router.get('', response_model=List[UserOut])
def list_users(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> List[UserOut]:
    users = db.query(User).filter_by(is_active=True).order_by(User.display_name).all()
    return [UserOut.model_validate(u) for u in users]
