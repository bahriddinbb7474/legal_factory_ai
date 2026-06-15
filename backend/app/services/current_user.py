from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str


def get_current_user() -> CurrentUser:
    return CurrentUser(id=settings.dev_current_user_id, role=settings.dev_current_user_role)
