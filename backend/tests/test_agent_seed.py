"""Tests for ensure_default_config: prompt upgrade logic and preservation."""
import asyncio
from decimal import Decimal

from app.db.base import Agent
from app.db.session import get_db
from app.main import app
from app.services.agent_seed import AGENT_SEEDS, LEGACY_DEFAULT_SYSTEM_PROMPTS


def _new_prompt(code: str) -> str:
    return next(a["system_prompt"] for a in AGENT_SEEDS if a["code"] == code)


def _base_agent_kwargs(code: str) -> dict:
    seed = next(a for a in AGENT_SEEDS if a["code"] == code)
    return {
        "code": seed["code"],
        "name": seed["name"],
        "display_name": seed["display_name"],
        "provider_code": seed["provider_code"],
        "model_name": seed["model_name"],
        "role_type": seed["role_type"],
        "is_enabled": seed["is_enabled"],
        "input_price_per_1m": seed["input_price_per_1m"],
        "output_price_per_1m": seed["output_price_per_1m"],
        "supports_zdr": seed["supports_zdr"],
    }


def _insert_agent(system_prompt: str, code: str = "lawyer_1") -> None:
    async def _run() -> None:
        override = app.dependency_overrides.get(get_db, get_db)
        async for db in override():
            db.add(Agent(**_base_agent_kwargs(code), system_prompt=system_prompt))
            await db.commit()

    asyncio.run(_run())


def _get_agents_via_api(client) -> dict[str, dict]:
    """Trigger ensure_default_config and return agents keyed by code."""
    response = client.get("/api/admin/agents")
    assert response.status_code == 200
    return {a["code"]: a for a in response.json()}


# --- Core upgrade behavior ---

def test_fresh_db_creates_agents_with_new_prompts(client) -> None:
    agents = _get_agents_via_api(client)
    for code in ("lawyer_1", "lawyer_2", "lawyer_3"):
        assert agents[code]["system_prompt"] == _new_prompt(code), (
            f"{code} should have the new prompt on a fresh DB"
        )


def test_existing_agent_with_empty_prompt_gets_new_prompt(client) -> None:
    _insert_agent(system_prompt="", code="lawyer_1")
    agents = _get_agents_via_api(client)
    assert agents["lawyer_1"]["system_prompt"] == _new_prompt("lawyer_1")


def test_existing_agent_with_legacy_prompt_gets_upgraded(client) -> None:
    for code in ("lawyer_1", "lawyer_2", "lawyer_3"):
        _insert_agent(system_prompt=LEGACY_DEFAULT_SYSTEM_PROMPTS[code], code=code)

    agents = _get_agents_via_api(client)

    for code in ("lawyer_1", "lawyer_2", "lawyer_3"):
        assert agents[code]["system_prompt"] == _new_prompt(code), (
            f"{code} should be upgraded from legacy to new prompt"
        )
        assert agents[code]["system_prompt"] != LEGACY_DEFAULT_SYSTEM_PROMPTS[code]


def test_existing_agent_with_custom_prompt_is_preserved(client) -> None:
    custom = "Особый промпт для нашей специфической ситуации."
    _insert_agent(system_prompt=custom, code="lawyer_1")
    agents = _get_agents_via_api(client)
    assert agents["lawyer_1"]["system_prompt"] == custom


# --- Architecture separation ---

def test_system_prompt_does_not_contain_chat_history_markers(client) -> None:
    """Ensures system_prompt stays universal — chat history must go through chat_context, not here."""
    agents = _get_agents_via_api(client)
    for code in ("lawyer_1", "lawyer_2", "lawyer_3"):
        prompt = agents[code]["system_prompt"]
        assert "История текущего чата:" not in prompt, f"{code} system_prompt must not embed chat history"
        assert "Контекст чата:" not in prompt
        assert "Текущий вопрос пользователя:" not in prompt
