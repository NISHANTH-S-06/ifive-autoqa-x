"""Auth API router for Demo Product Website."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, create_session, get_auth_context, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserOut
from app.services.demo_setting_service import is_bug_enabled

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: DBSession = Depends(get_db)) -> TokenResponse:
    # Bug toggle check: login_failure_mode
    if is_bug_enabled(db, 'login_failure_mode'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Authentication service unavailable: Demo login failure mode is active.',
        )

    user = db.query(User).filter_by(username=payload.username, is_active=True).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    token = create_session(db, user)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> None:
    from app.models.user import Session as UserSession
    session = db.query(UserSession).filter_by(user_id=ctx.user.id).order_by(UserSession.id.desc()).first()
    if session:
        db.delete(session)
        db.commit()


@router.get('/me', response_model=UserOut)
def me(ctx: AuthContext = Depends(get_auth_context)) -> UserOut:
    return UserOut.model_validate(ctx.user)
