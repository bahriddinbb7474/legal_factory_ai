from fastapi.testclient import TestClient


ADMIN = {"email": "admin@example.test", "full_name": "Test Admin", "password": "test-admin-password"}
VIEWER = {"email": "viewer@example.test", "full_name": "Test Viewer", "role": "viewer", "password": "viewer-pass-word-12"}


def test_anonymous_cannot_access_admin_users(raw_client: TestClient) -> None:
    assert raw_client.get("/api/admin/users").status_code == 401
    assert raw_client.post("/api/admin/users", json=VIEWER).status_code == 401
    assert raw_client.patch("/api/admin/users/1", json={"full_name": "x"}).status_code == 401
    assert raw_client.post("/api/admin/users/1/reset-password", json={"new_password": "x" * 12}).status_code == 401


def test_viewer_cannot_access_admin_users(client: TestClient) -> None:
    client.post("/api/admin/users", json=VIEWER)
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"email": VIEWER["email"], "password": VIEWER["password"]})
    assert client.get("/api/admin/users").status_code == 403
    assert client.post("/api/admin/users", json={"email": "x@x.com", "full_name": "X", "password": "x" * 12}).status_code == 403


def test_admin_can_list_users(client: TestClient) -> None:
    response = client.get("/api/admin/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert any(u["email"] == ADMIN["email"] for u in users)


def test_admin_can_create_user(client: TestClient) -> None:
    response = client.post("/api/admin/users", json=VIEWER)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == VIEWER["email"]
    assert data["full_name"] == VIEWER["full_name"]
    assert data["role"] == "viewer"
    assert data["is_active"] is True


def test_created_user_can_login(client: TestClient) -> None:
    client.post("/api/admin/users", json=VIEWER)
    client.post("/api/auth/logout")
    response = client.post("/api/auth/login", json={"email": VIEWER["email"], "password": VIEWER["password"]})
    assert response.status_code == 200
    assert response.json()["email"] == VIEWER["email"]


def test_password_hash_not_returned(client: TestClient) -> None:
    created = client.post("/api/admin/users", json=VIEWER).json()
    assert "password_hash" not in created
    for user in client.get("/api/admin/users").json():
        assert "password_hash" not in user


def test_duplicate_email_rejected(client: TestClient) -> None:
    client.post("/api/admin/users", json=VIEWER)
    response = client.post("/api/admin/users", json=VIEWER)
    assert response.status_code == 409


def test_admin_can_update_role_fullname_is_active(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    response = client.patch(f"/api/admin/users/{user_id}", json={"full_name": "Updated Name", "role": "sales"})
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["role"] == "sales"
    assert data["is_active"] is True

    response = client.patch(f"/api/admin/users/{user_id}", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_deactivated_user_cannot_login(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.patch(f"/api/admin/users/{user_id}", json={"is_active": False})
    client.post("/api/auth/logout")
    response = client.post("/api/auth/login", json={"email": VIEWER["email"], "password": VIEWER["password"]})
    assert response.status_code == 403


def test_admin_can_reset_password(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    response = client.post(f"/api/admin/users/{user_id}/reset-password", json={"new_password": "new-secure-pass-word"})
    assert response.status_code == 200
    assert "password_hash" not in response.json()


def test_old_password_rejected_after_reset(client: TestClient) -> None:
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.post(f"/api/admin/users/{user_id}/reset-password", json={"new_password": "new-secure-pass-word"})
    client.post("/api/auth/logout")
    response = client.post("/api/auth/login", json={"email": VIEWER["email"], "password": VIEWER["password"]})
    assert response.status_code == 401


def test_new_password_works_after_reset(client: TestClient) -> None:
    new_pass = "new-secure-pass-word"
    user_id = client.post("/api/admin/users", json=VIEWER).json()["id"]
    client.post(f"/api/admin/users/{user_id}/reset-password", json={"new_password": new_pass})
    client.post("/api/auth/logout")
    response = client.post("/api/auth/login", json={"email": VIEWER["email"], "password": new_pass})
    assert response.status_code == 200


def test_cannot_deactivate_last_active_admin(client: TestClient) -> None:
    admin_id = next(u["id"] for u in client.get("/api/admin/users").json() if u["role"] == "admin")
    response = client.patch(f"/api/admin/users/{admin_id}", json={"is_active": False})
    assert response.status_code == 409


def test_cannot_demote_last_active_admin(client: TestClient) -> None:
    admin_id = next(u["id"] for u in client.get("/api/admin/users").json() if u["role"] == "admin")
    response = client.patch(f"/api/admin/users/{admin_id}", json={"role": "viewer"})
    assert response.status_code == 409
