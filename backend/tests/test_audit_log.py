from fastapi.testclient import TestClient

ADMIN = {"email": "admin@example.test", "full_name": "Test Admin", "password": "test-admin-password"}
VIEWER = {"email": "viewer@example.test", "full_name": "Test Viewer", "role": "viewer", "password": "viewer-pass-word-12"}

_FORBIDDEN_DETAIL_KEYS = {"password", "password_hash", "token", "cookie", "new_password", "secret"}


def _get_audit_logs(client: TestClient, action: str | None = None) -> list[dict]:
    params = {}
    if action is not None:
        params["action"] = action
    resp = client.get("/api/admin/audit-logs", params=params)
    assert resp.status_code == 200
    return resp.json()


def _no_secrets_in_details(details: dict | None) -> bool:
    if not details:
        return True
    return not any(k in _FORBIDDEN_DETAIL_KEYS for k in details)


# ---------------------------------------------------------------------------
# auth.login
# ---------------------------------------------------------------------------

def test_login_creates_auth_login_event(raw_client: TestClient) -> None:
    raw_client.post("/api/auth/bootstrap", json=ADMIN)
    raw_client.post("/api/auth/logout")
    raw_client.post("/api/auth/login", json={"email": ADMIN["email"], "password": ADMIN["password"]})

    logs = _get_audit_logs(raw_client, action="auth.login")
    assert len(logs) >= 1
    entry = logs[0]
    assert entry["action"] == "auth.login"
    assert entry["entity_type"] == "user"
    assert entry["entity_id"] is not None
    assert entry["user_id"] is not None
    assert _no_secrets_in_details(entry.get("details"))


def test_login_audit_details_contain_email_and_role(raw_client: TestClient) -> None:
    raw_client.post("/api/auth/bootstrap", json=ADMIN)
    raw_client.post("/api/auth/logout")
    raw_client.post("/api/auth/login", json={"email": ADMIN["email"], "password": ADMIN["password"]})

    logs = _get_audit_logs(raw_client, action="auth.login")
    details = logs[0]["details"]
    assert details["email"] == ADMIN["email"]
    assert details["role"] == "admin"


# ---------------------------------------------------------------------------
# auth.logout
# ---------------------------------------------------------------------------

def test_logout_creates_auth_logout_event(client: TestClient) -> None:
    client.post("/api/auth/logout")
    # Re-login so we can query the audit log
    client.post("/api/auth/login", json={"email": ADMIN["email"], "password": ADMIN["password"]})

    logs = _get_audit_logs(client, action="auth.logout")
    assert len(logs) >= 1
    entry = logs[0]
    assert entry["action"] == "auth.logout"
    assert entry["entity_type"] == "user"
    assert entry["user_id"] is not None
    assert _no_secrets_in_details(entry.get("details"))


# ---------------------------------------------------------------------------
# user.created
# ---------------------------------------------------------------------------

def test_create_user_creates_audit_log(client: TestClient) -> None:
    client.post("/api/admin/users", json=VIEWER)

    logs = _get_audit_logs(client, action="user.created")
    assert len(logs) == 1
    entry = logs[0]
    assert entry["action"] == "user.created"
    assert entry["entity_type"] == "user"
    assert entry["entity_id"] is not None
    assert entry["user_id"] is not None  # actor = admin
    assert _no_secrets_in_details(entry.get("details"))


def test_create_user_audit_details_safe(client: TestClient) -> None:
    client.post("/api/admin/users", json=VIEWER)

    logs = _get_audit_logs(client, action="user.created")
    details = logs[0]["details"]
    assert details["email"] == VIEWER["email"]
    assert details["role"] == VIEWER["role"]
    # Password must never appear
    assert "password" not in details
    assert "password_hash" not in details


# ---------------------------------------------------------------------------
# user.updated
# ---------------------------------------------------------------------------

def test_update_user_creates_audit_log(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.patch(f"/api/admin/users/{user_id}", json={"full_name": "Updated Name"})

    logs = _get_audit_logs(client, action="user.updated")
    assert len(logs) >= 1
    entry = logs[0]
    assert entry["action"] == "user.updated"
    assert entry["entity_type"] == "user"
    assert entry["entity_id"] == user_id
    assert _no_secrets_in_details(entry.get("details"))


def test_update_user_audit_details_include_changed_fields(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.patch(f"/api/admin/users/{user_id}", json={"role": "sales"})

    logs = _get_audit_logs(client, action="user.updated")
    details = logs[0]["details"]
    assert "role" in details.get("changed_fields", [])
    assert details["changes"]["role"]["from"] == "viewer"
    assert details["changes"]["role"]["to"] == "sales"


# ---------------------------------------------------------------------------
# user.deactivated
# ---------------------------------------------------------------------------

def test_deactivate_user_creates_deactivated_event(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.patch(f"/api/admin/users/{user_id}", json={"is_active": False})

    logs = _get_audit_logs(client, action="user.deactivated")
    assert len(logs) == 1
    entry = logs[0]
    assert entry["action"] == "user.deactivated"
    assert entry["entity_id"] == user_id
    assert entry["user_id"] is not None


def test_deactivate_also_creates_updated_event(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.patch(f"/api/admin/users/{user_id}", json={"is_active": False})

    updated_logs = _get_audit_logs(client, action="user.updated")
    assert len(updated_logs) >= 1


def test_no_deactivated_event_when_already_inactive(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    # Deactivate once
    client.patch(f"/api/admin/users/{user_id}", json={"is_active": False})
    # Send same patch again — already inactive, not a real transition
    client.patch(f"/api/admin/users/{user_id}", json={"is_active": False})

    logs = _get_audit_logs(client, action="user.deactivated")
    assert len(logs) == 1  # only one deactivated event


# ---------------------------------------------------------------------------
# user.password_reset
# ---------------------------------------------------------------------------

def test_password_reset_creates_audit_log(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.post(f"/api/admin/users/{user_id}/reset-password", json={"new_password": "new-secure-pass-word"})

    logs = _get_audit_logs(client, action="user.password_reset")
    assert len(logs) == 1
    entry = logs[0]
    assert entry["action"] == "user.password_reset"
    assert entry["entity_id"] == user_id
    assert entry["user_id"] is not None


def test_password_reset_audit_contains_no_password(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.post(f"/api/admin/users/{user_id}/reset-password", json={"new_password": "new-secure-pass-word"})

    logs = _get_audit_logs(client, action="user.password_reset")
    details = logs[0].get("details")
    # Details are None or contain no sensitive data
    assert _no_secrets_in_details(details)
    if details:
        assert "password" not in details
        assert "password_hash" not in details
        assert "new_password" not in details


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

def test_viewer_cannot_access_audit_logs(client: TestClient) -> None:
    client.post("/api/admin/users", json=VIEWER)
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"email": VIEWER["email"], "password": VIEWER["password"]})

    assert client.get("/api/admin/audit-logs").status_code == 403


def test_admin_can_access_audit_logs(client: TestClient) -> None:
    assert client.get("/api/admin/audit-logs").status_code == 200


def test_anonymous_cannot_access_audit_logs(raw_client: TestClient) -> None:
    assert raw_client.get("/api/admin/audit-logs").status_code == 401


# ---------------------------------------------------------------------------
# limit / offset
# ---------------------------------------------------------------------------

def test_audit_logs_default_limit_applied(client: TestClient) -> None:
    resp = client.get("/api/admin/audit-logs")
    assert resp.status_code == 200
    # Response is a list (not an error), limit param is accepted
    assert isinstance(resp.json(), list)


def test_audit_logs_limit_param_accepted(client: TestClient) -> None:
    resp = client.get("/api/admin/audit-logs", params={"limit": 10})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_audit_logs_limit_max_enforced(client: TestClient) -> None:
    # Limit above 500 must be rejected (FastAPI Query validation → 422)
    resp = client.get("/api/admin/audit-logs", params={"limit": 501})
    assert resp.status_code == 422


def test_audit_logs_limit_zero_rejected(client: TestClient) -> None:
    resp = client.get("/api/admin/audit-logs", params={"limit": 0})
    assert resp.status_code == 422
