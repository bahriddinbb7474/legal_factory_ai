import asyncio
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import func, select

from app.db.base import User
from app.db.session import get_db
from app.main import app
from app.services.auth import verify_password
from fastapi import HTTPException

from app.services.current_user import CurrentUser, get_current_user, require_any_role


ADMIN = {"email": "admin@example.test", "full_name": "Initial Admin", "password": "strong-local-password"}


def test_anonymous_legal_workspace_routes_are_rejected(raw_client) -> None:
    requests = [
        ("GET", "/api/agents", None),
        ("GET", "/api/company-profile", None),
        ("GET", "/api/document-templates", None),
        ("GET", "/api/documents", None),
        ("GET", "/api/chats", None),
        ("POST", "/api/chats", {"title": "Anonymous chat"}),
        ("GET", "/api/chats/1", None),
        ("GET", "/api/chats/1/messages", None),
        ("POST", "/api/chats/1/messages", {"role": "user", "content": "Anonymous message"}),
        ("GET", "/api/chats/1/verdict", None),
        ("GET", "/api/chats/1/costs", None),
        ("GET", "/api/chats/1/approvals", None),
        ("GET", "/api/generated-documents/1", None),
        ("PATCH", "/api/generated-documents/1", {"title": "Anonymous edit"}),
        ("POST", "/api/generated-documents/1/apply-template", {"template_key": "legal_opinion"}),
        ("GET", "/api/generated-documents/1/approvals", None),
    ]

    for method, path, payload in requests:
        response = raw_client.request(method, path, json=payload)
        assert response.status_code == 401, f"{method} {path} must require authentication"


def test_authenticated_user_can_use_normal_workspace(client) -> None:
    created = client.post("/api/chats", json={"title": "Authenticated workspace"})
    assert created.status_code == 201
    assert client.get("/api/chats").status_code == 200
    assert client.get("/api/document-templates").status_code == 200
    assert client.get("/api/agents").status_code == 200


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


def test_bootstrap_initializes_existing_user_without_usable_admin(raw_client) -> None:
    override = app.dependency_overrides[get_db]

    async def create_legacy_user() -> None:
        async for db in override():
            db.add(
                User(
                    email=ADMIN["email"],
                    full_name="Legacy User",
                    role="viewer",
                    password_hash="",
                    is_active=True,
                )
            )
            await db.commit()

    asyncio.run(create_legacy_user())
    response = raw_client.post("/api/auth/bootstrap", json=ADMIN)
    assert response.status_code == 201
    assert response.json()["role"] == "admin"
    assert "password_hash" not in response.json()

    async def check_initialized_user() -> None:
        async for db in override():
            users = list((await db.scalars(select(User))).all())
            assert len(users) == 1
            assert users[0].role == "admin"
            assert users[0].is_active is True
            assert verify_password(ADMIN["password"], users[0].password_hash)

    asyncio.run(check_initialized_user())


def test_concurrent_bootstrap_creates_only_one_usable_admin(raw_client) -> None:
    payloads = [
        ADMIN,
        {"email": "second-admin@example.test", "full_name": "Second Admin", "password": "second-strong-password"},
    ]
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda payload: raw_client.post("/api/auth/bootstrap", json=payload), payloads))

    assert sorted(response.status_code for response in responses) == [201, 409]
    override = app.dependency_overrides[get_db]

    async def count_usable_admins() -> None:
        async for db in override():
            count = await db.scalar(
                select(func.count(User.id)).where(
                    User.role == "admin",
                    User.is_active.is_(True),
                    User.password_hash != "",
                )
            )
            assert count == 1

    asyncio.run(count_usable_admins())


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
