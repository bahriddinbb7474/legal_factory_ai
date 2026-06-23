from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.services.current_user import CurrentUser
from app.services.document_access import DocumentAccessError, document_access_service


VIEWER = {
    "email": "viewer@example.test",
    "full_name": "Read Only Viewer",
    "role": "viewer",
    "password": "viewer-password-12",
}
SALES = {
    "email": "sales@example.test",
    "full_name": "Sales Writer",
    "role": "sales",
    "password": "sales-password-123",
}


def _login_as_created_user(client: TestClient, payload: dict[str, str]) -> None:
    created = client.post("/api/admin/users", json=payload)
    assert created.status_code == 201
    assert client.post("/api/auth/logout").status_code == 204
    login = client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200


def test_anonymous_mutations_still_require_auth_and_registration_is_absent(raw_client: TestClient) -> None:
    assert raw_client.post("/api/chats", json={"title": "Anonymous"}).status_code == 401
    assert raw_client.get("/api/generated-documents/1/download.docx").status_code == 401
    assert raw_client.post("/api/auth/register", json=VIEWER).status_code == 404
    assert raw_client.post("/api/auth/signup", json=VIEWER).status_code == 404


def test_viewer_can_use_representative_read_endpoints(client: TestClient) -> None:
    chat_id = client.post("/api/chats", json={"title": "Existing chat"}).json()["id"]
    _login_as_created_user(client, VIEWER)

    assert client.get("/api/chats").status_code == 200
    assert client.get(f"/api/chats/{chat_id}").status_code == 200
    assert client.get(f"/api/chats/{chat_id}/messages").status_code == 200
    assert client.get("/api/agents").status_code == 200
    assert client.get("/api/document-templates").status_code == 200
    assert client.get("/api/documents").status_code == 200
    assert client.get("/api/generated-documents/999").status_code == 404


def test_viewer_workspace_mutations_are_forbidden_without_db_changes(client: TestClient) -> None:
    chat_id = client.post("/api/chats", json={"title": "Protected chat"}).json()["id"]
    initial_chats = client.get("/api/chats").json()
    _login_as_created_user(client, VIEWER)

    requests = [
        ("POST", "/api/chats", {"title": "Viewer chat"}),
        ("POST", f"/api/chats/{chat_id}/messages", {"role": "user", "content": "Viewer message"}),
        ("POST", f"/api/chats/{chat_id}/messages/1/mark-verdict", None),
        ("DELETE", f"/api/chats/{chat_id}/verdict", None),
        (
            "POST",
            f"/api/chats/{chat_id}/documents/generate-from-verdict",
            {"agent_code": "lawyer_1", "document_type": "letter", "title": "Viewer document"},
        ),
        ("POST", f"/api/chats/{chat_id}/invoke", {"agent_code": "lawyer_1"}),
        ("POST", f"/api/chats/{chat_id}/request-approval", None),
        ("POST", f"/api/chats/{chat_id}/approve", None),
        ("POST", f"/api/chats/{chat_id}/reject", None),
        ("DELETE", "/api/documents/1", None),
        ("POST", f"/api/chats/{chat_id}/documents/1", None),
        ("DELETE", f"/api/chats/{chat_id}/documents/1", None),
        ("PATCH", "/api/generated-documents/1", {"title": "Viewer edit"}),
        ("GET", "/api/generated-documents/1/download.docx", None),
        ("GET", "/api/generated-documents/1/download.pdf", None),
        ("POST", "/api/generated-documents/1/send-to-chat", None),
        ("POST", "/api/generated-documents/1/apply-template", {"template_key": "legal_opinion"}),
        ("POST", "/api/generated-documents/1/request-approval", None),
        ("POST", "/api/generated-documents/1/approve", None),
        ("POST", "/api/generated-documents/1/reject", None),
    ]

    for method, path, payload in requests:
        response = client.request(method, path, json=payload)
        assert response.status_code == 403, f"{method} {path} must reject viewer mutations"

    upload = client.post(
        "/api/documents/upload",
        files={"file": ("viewer.txt", b"read only", "text/plain")},
    )
    assert upload.status_code == 403
    assert client.get("/api/chats").json() == []
    assert client.get(f"/api/chats/{chat_id}/messages").json() == []


def test_non_viewer_workspace_writer_can_still_mutate(client: TestClient) -> None:
    _login_as_created_user(client, SALES)
    chat = client.post("/api/chats", json={"title": "Sales chat"})
    assert chat.status_code == 201
    message = client.post(
        f"/api/chats/{chat.json()['id']}/messages",
        json={"role": "user", "content": "Sales message"},
    )
    assert message.status_code == 201


def test_document_policy_uses_current_supply_and_accountant_role_names() -> None:
    import_contract = SimpleNamespace(category="import_contract")
    tax_letter = SimpleNamespace(category="tax_letter")

    document_access_service.assert_can_access(CurrentUser(id=1, role="supply"), import_contract, "view")
    document_access_service.assert_can_access(CurrentUser(id=2, role="accountant"), tax_letter, "view")

    with pytest.raises(DocumentAccessError):
        document_access_service.assert_can_access(CurrentUser(id=3, role="accountant"), import_contract, "view")
    with pytest.raises(DocumentAccessError):
        document_access_service.assert_can_access(CurrentUser(id=4, role="supply"), tax_letter, "view")
