import asyncio

from sqlalchemy import select

from app.db.base import User
from app.db.session import get_db
from app.main import app
from app.services.auth import verify_password
from fastapi import HTTPException

from app.services.current_user import CurrentUser, get_current_user, require_any_role


ADMIN = {"email": "admin@example.test", "full_name": "Initial Admin", "password": "strong-local-password"}


def test_bootstrap_login_me_and_password_hash(raw_client) -> None:
    bootstrap = raw_client.post("/api/auth/bootstrap", json=ADMIN)
    assert bootstrap.status_code == 201
    assert bootstrap.json()["role"] == "admin"
    assert "password_hash" not in bootstrap.json()
    assert raw_client.post("/api/auth/bootstrap", json=ADMIN).status_code == 409

    raw_client.post("/api/auth/logout")
    assert raw_client.get("/api/auth/me").status_code == 401
    assert raw_client.post("/api/auth/login", json={"email": ADMIN["email"], "password": "wrong-password"}).status_code == 401

    login = raw_client.post("/api/auth/login", json={"email": ADMIN["email"], "password": ADMIN["password"]})
    assert login.status_code == 200
    me = raw_client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == ADMIN["email"]
    assert "password_hash" not in me.json()

    override = app.dependency_overrides[get_db]

    async def check_hash() -> None:
        async for db in override():
            user = await db.scalar(select(User).where(User.email == ADMIN["email"]))
            assert user.password_hash != ADMIN["password"]
            assert verify_password(ADMIN["password"], user.password_hash)

    asyncio.run(check_hash())


def test_inactive_user_cannot_login(raw_client) -> None:
    raw_client.post("/api/auth/bootstrap", json=ADMIN)
    raw_client.post("/api/auth/logout")
    override = app.dependency_overrides[get_db]

    async def deactivate() -> None:
        async for db in override():
            user = await db.scalar(select(User).where(User.email == ADMIN["email"]))
            user.is_active = False
            await db.commit()

    asyncio.run(deactivate())
    response = raw_client.post("/api/auth/login", json={"email": ADMIN["email"], "password": ADMIN["password"]})
    assert response.status_code == 403


def test_protected_company_profile_and_role_helper(raw_client) -> None:
    payload = {"full_name": "Factory LLC", "short_name": "Factory"}
    assert raw_client.put("/api/company-profile", json=payload).status_code == 401

    raw_client.post("/api/auth/bootstrap", json=ADMIN)
    assert raw_client.put("/api/company-profile", json=payload).status_code == 200

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=2, role="viewer")
    assert raw_client.put("/api/company-profile", json=payload).status_code == 403

    dependency = require_any_role("admin", "director")
    assert asyncio.run(dependency(CurrentUser(id=1, role="director"))).role == "director"
    try:
        asyncio.run(dependency(CurrentUser(id=2, role="viewer")))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("viewer role must be rejected")
