from datetime import datetime

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import AuthSession, User
from app.db.session import get_db
from app.schemas.users import BootstrapAdminRequest, LoginRequest, UserRead, UserRole
from app.services.auth import create_session, hash_password, hash_session_token, verify_password
from app.services.current_user import CurrentUser, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _read_user(user: User) -> UserRead:
    return UserRead(id=user.id, email=user.email, full_name=user.full_name, role=user.role, is_active=user.is_active, last_login_at=user.last_login_at, created_at=user.created_at, updated_at=user.updated_at)


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie("legal_factory_session", token, max_age=settings.auth_session_days * 86400, httponly=True, samesite="lax", secure=settings.auth_cookie_secure, path="/")


@router.post("/bootstrap", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def bootstrap_admin(payload: BootstrapAdminRequest, response: Response, db: AsyncSession = Depends(get_db)) -> UserRead:
    if (await db.scalar(select(func.count(User.id)))) != 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bootstrap is already disabled")
    user = User(email=payload.email.strip().lower(), full_name=payload.full_name.strip(), role=UserRole.admin.value, password_hash=hash_password(payload.password), is_active=True)
    db.add(user)
    await db.flush()
    token = await create_session(db, user)
    await db.commit()
    await db.refresh(user)
    _set_cookie(response, token)
    return _read_user(user)


@router.post("/login", response_model=UserRead)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)) -> UserRead:
    user = await db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    user.last_login_at = datetime.utcnow()
    token = await create_session(db, user)
    await db.commit()
    await db.refresh(user)
    _set_cookie(response, token)
    return _read_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, legal_factory_session: str | None = Cookie(default=None), db: AsyncSession = Depends(get_db)) -> None:
    if legal_factory_session:
        await db.execute(delete(AuthSession).where(AuthSession.token_hash == hash_session_token(legal_factory_session)))
        await db.commit()
    response.delete_cookie("legal_factory_session", path="/")


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserRead:
    user = await db.get(User, current_user.id)
    return _read_user(user)
