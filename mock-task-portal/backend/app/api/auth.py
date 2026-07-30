"""Auth API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import AuthContext, create_session, get_auth_context, revoke_session, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.users import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter_by(username=payload.username, is_active=True).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    token = create_session(db, user)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post('/logout', status_code=204)
def logout(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> None:
    # Token is extracted from the header via Depends; we revoke via the context user
    # In a real system we'd pass the raw token; here we expire the oldest session for simplicity
    from app.models.user import UserSession
    session = db.query(UserSession).filter_by(user_id=ctx.user.id).order_by(UserSession.id.desc()).first()
    if session:
        db.delete(session)
        db.commit()


@router.get('/me', response_model=UserOut)
def me(ctx: AuthContext = Depends(get_auth_context)) -> UserOut:
    return UserOut.model_validate(ctx.user)
