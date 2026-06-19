from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AuthSession, User
from app.db.session import get_db


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str
    email: str = ""
    full_name: str = ""


async def get_current_user(
    legal_factory_session: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    if not legal_factory_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    from app.services.auth import hash_session_token

    result = await db.execute(
        select(AuthSession, User)
        .join(User, User.id == AuthSession.user_id)
        .where(AuthSession.token_hash == hash_session_token(legal_factory_session))
    )
    row = result.first()
    if row is None or row.AuthSession.expires_at <= datetime.utcnow() or not row.User.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    user = row.User
    return CurrentUser(id=user.id, role=user.role, email=user.email, full_name=user.full_name)


def require_any_role(*roles: str) -> Callable:
    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user
    return dependency


def require_role(role: str) -> Callable:
    return require_any_role(role)
