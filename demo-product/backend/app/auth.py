"""Authentication & authorization for Demo Product Website."""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.user import User, Session as UserSession

SESSION_TTL_HOURS = 8
_bearer = HTTPBearer(auto_error=False)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def hash_password(password: str) -> str:
    """SHA-256 hash for demo passwords."""
    salt = 'DEMO_PRODUCT_SALT'
    return hashlib.sha256(f'{salt}:{password}'.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def create_session(db: DBSession, user: User) -> str:
    token = secrets.token_urlsafe(32)
    db.add(UserSession(
        user_id=user.id,
        token_hash=_hash_token(token),
        expires_at=datetime.utcnow() + timedelta(hours=SESSION_TTL_HOURS),
    ))
    db.commit()
    return token


def revoke_session(db: DBSession, token: str) -> None:
    session = db.query(UserSession).filter_by(token_hash=_hash_token(token)).first()
    if session:
        db.delete(session)
        db.commit()


class AuthContext:
    def __init__(self, user: User) -> None:
        self.user = user

    @property
    def username(self) -> str:
        return self.user.username

    @property
    def role(self) -> str:
        return self.user.role

    def require_role(self, *roles: str) -> None:
        if self.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Role {self.role} is not permitted for this action. Allowed: {roles}',
            )


def get_auth_context(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: DBSession = Depends(get_db),
) -> AuthContext:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    token_hash = _hash_token(credentials.credentials)
    session = db.query(UserSession).filter_by(token_hash=token_hash).first()
    if session is None or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session expired or invalid')
    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User inactive')
    return AuthContext(user)


def get_optional_auth_context(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: DBSession = Depends(get_db),
) -> Optional[AuthContext]:
    if credentials is None:
        return None
    try:
        return get_auth_context(credentials, db)
    except HTTPException:
        return None
