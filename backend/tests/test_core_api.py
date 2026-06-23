def test_list_agents(client) -> None:
    response = client.get("/api/agents")

    assert response.status_code == 200
    agents = response.json()
    assert [agent["code"] for agent in agents] == ["lawyer_1", "lawyer_2", "lawyer_3"]
    assert agents[0]["provider_code"] != agents[1]["provider_code"]


def test_create_chat(client) -> None:
    response = client.post("/api/chats", json={"title": "Contract review"})

    assert response.status_code == 201
    chat = response.json()
    assert chat["id"] == 1
    assert chat["title"] == "Contract review"
    assert chat["status"] == "draft"


def test_create_and_list_chat_messages(client) -> None:
    chat_response = client.post("/api/chats", json={"title": "Debt question"})
    chat_id = chat_response.json()["id"]

    message_response = client.post(
        f"/api/chats/{chat_id}/messages",
        json={"role": "user", "content": "Check customer debt risk"},
    )
    messages_response = client.get(f"/api/chats/{chat_id}/messages")

    assert message_response.status_code == 201
    assert message_response.json()["content"] == "Check customer debt risk"
    assert messages_response.status_code == 200
    messages = messages_response.json()
    assert len(messages) == 1
    assert messages[0]["author_type"] == "user"
    assert messages[0]["role"] == "user"


def test_list_chat_costs(client) -> None:
    chat_response = client.post("/api/chats", json={"title": "Cost report"})
    chat_id = chat_response.json()["id"]

    response = client.get(f"/api/chats/{chat_id}/costs")

    assert response.status_code == 200
    assert response.json() == []


def test_create_chat_sets_owner_automatically(client) -> None:
    response = client.post("/api/chats", json={"title": "Ownership test"})

    assert response.status_code == 201
    chat = response.json()
    assert chat["owner_user_id"] is not None


def test_create_chat_with_section(client) -> None:
    response = client.post("/api/chats", json={"title": "Debt question", "section": "Долги / претензии"})

    assert response.status_code == 201
    chat = response.json()
    assert chat["section"] == "Долги / претензии"


def test_chat_list_non_admin_sees_only_own_chats(client) -> None:
    client.post("/api/chats", json={"title": "Admin chat"})

    client.post(
        "/api/admin/users",
        json={"email": "sales2@test.test", "full_name": "Sales Two", "role": "sales", "password": "sales-password-xyz"},
    )
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"email": "sales2@test.test", "password": "sales-password-xyz"})

    sales_chat = client.post("/api/chats", json={"title": "Sales own chat"}).json()
    chats = client.get("/api/chats").json()
    chat_ids = [c["id"] for c in chats]

    assert sales_chat["id"] in chat_ids
    assert all(c["owner_user_id"] == sales_chat["owner_user_id"] for c in chats)


def test_chat_list_admin_sees_all_chats(client) -> None:
    client.post("/api/chats", json={"title": "Admin first chat"})

    client.post(
        "/api/admin/users",
        json={"email": "sales3@test.test", "full_name": "Sales Three", "role": "sales", "password": "sales-password-abc"},
    )
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"email": "sales3@test.test", "password": "sales-password-abc"})
    client.post("/api/chats", json={"title": "Sales third chat"})

    client.post("/api/auth/logout")
    client.post(
        "/api/auth/login",
        json={"email": "admin@example.test", "password": "test-admin-password"},
    )

    chats = client.get("/api/chats").json()
    assert len(chats) >= 2
