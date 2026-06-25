"""Unit tests for build_chat_history_context and build_chat_context."""
from datetime import datetime
from types import SimpleNamespace

from app.services.chat_context import (
    HISTORY_LIMIT,
    build_chat_context,
    build_chat_history_context,
    build_rich_lawyer_block,
)


def _msg(
    author_type: str,
    content: str,
    model_id: str | None = None,
    created_at: datetime | None = None,
    structured_payload: dict | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        author_type=author_type,
        content=content,
        model_id=model_id,
        created_at=created_at,
        structured_payload=structured_payload,
    )


def _chat(title: str, section: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(title=title, section=section)


# --- build_chat_history_context ---

def test_sender_labels_all_types() -> None:
    messages = [
        _msg("user", "Вопрос"),
        _msg("agent1", "Ответ 1"),
        _msg("agent2", "Ответ 2"),
        _msg("agent3", "Ответ 3"),
        _msg("system", "Системное"),
    ]
    result = build_chat_history_context(messages)
    assert "Пользователь: Вопрос" in result
    assert "Юрист 1: Ответ 1" in result
    assert "Юрист 2: Ответ 2" in result
    assert "Юрист 3: Ответ 3" in result
    assert "Система: Системное" in result


def test_history_is_chronological() -> None:
    messages = [_msg("user", "Первый"), _msg("agent1", "Второй"), _msg("user", "Третий")]
    result = build_chat_history_context(messages)
    assert result.index("Первый") < result.index("Второй") < result.index("Третий")


def test_history_limited_to_last_n() -> None:
    messages = [_msg("user", f"Сообщение {i}") for i in range(35)]
    result = build_chat_history_context(messages, limit=30)
    assert "Сообщение 4" not in result
    assert "Сообщение 5" in result
    assert "Сообщение 34" in result


def test_history_default_limit_is_30() -> None:
    assert HISTORY_LIMIT == 30
    messages = [_msg("user", f"M{i}") for i in range(35)]
    result = build_chat_history_context(messages)
    assert "M4" not in result
    assert "M5" in result


def test_empty_content_skipped() -> None:
    messages = [_msg("user", ""), _msg("user", "   "), _msg("user", "Настоящий вопрос")]
    result = build_chat_history_context(messages)
    assert result.count("Пользователь:") == 1
    assert "Настоящий вопрос" in result


def test_timestamp_included_when_created_at_set() -> None:
    dt = datetime(2026, 6, 23, 10, 15)
    result = build_chat_history_context([_msg("user", "Вопрос", created_at=dt)])
    assert "[2026-06-23 10:15]" in result
    assert "Пользователь: Вопрос" in result


def test_no_timestamp_when_created_at_none() -> None:
    result = build_chat_history_context([_msg("user", "Вопрос")])
    assert "[" not in result


def test_model_suffix_included_for_agent_messages() -> None:
    result = build_chat_history_context([_msg("agent1", "Ответ", model_id="gpt-4")])
    assert "(модель: gpt-4)" in result


def test_no_model_suffix_when_model_id_none() -> None:
    result = build_chat_history_context([_msg("agent1", "Ответ")])
    assert "(модель:" not in result


# --- build_chat_context ---

def test_context_includes_chat_metadata_with_section() -> None:
    chat = _chat("Договор поставки", section="Контракты")
    messages = [_msg("user", "Проверь договор")]
    result = build_chat_context(messages, chat=chat)
    assert "Раздел: Контракты" in result
    assert "Название: Договор поставки" in result


def test_context_no_section_line_when_section_none() -> None:
    chat = _chat("Общий чат", section=None)
    messages = [_msg("user", "Вопрос")]
    result = build_chat_context(messages, chat=chat)
    assert "Название: Общий чат" in result
    assert "Раздел:" not in result


def test_context_no_metadata_block_when_chat_none() -> None:
    messages = [_msg("user", "Вопрос")]
    result = build_chat_context(messages)
    assert "Контекст чата:" not in result


def test_context_includes_history_section() -> None:
    messages = [_msg("user", "Старый"), _msg("agent1", "Ответ"), _msg("user", "Новый")]
    result = build_chat_context(messages)
    assert "История текущего чата:" in result
    assert "Пользователь: Старый" in result
    assert "Юрист 1: Ответ" in result


def test_context_includes_current_question_footer() -> None:
    messages = [
        _msg("user", "Старый вопрос"),
        _msg("agent1", "Ответ юриста"),
        _msg("user", "Новый вопрос"),
    ]
    result = build_chat_context(messages)
    assert "Текущий вопрос пользователя:" in result
    assert "Новый вопрос" in result


def test_context_current_question_is_last_user_message() -> None:
    messages = [_msg("user", "Первый"), _msg("agent1", "Ответ"), _msg("user", "Последний")]
    result = build_chat_context(messages)
    # Both appear in history, but "Текущий вопрос" section should reference the last one
    footer_start = result.index("Текущий вопрос пользователя:")
    assert "Последний" in result[footer_start:]


def test_context_includes_continuation_instruction() -> None:
    result = build_chat_context([_msg("user", "Вопрос")])
    assert "Используй историю чата" in result
    assert "продолжением" in result


def test_context_includes_document_context() -> None:
    result = build_chat_context([_msg("user", "Вопрос")], document_context="Договор поставки: текст")
    assert "Документы, связанные с текущим чатом:" in result
    assert "Договор поставки: текст" in result


def test_context_includes_legal_context() -> None:
    result = build_chat_context([_msg("user", "Вопрос")], legal_context="Статья 12 ГК РУ: ...")
    assert "правовые источники" in result
    assert "Статья 12 ГК РУ" in result


def test_context_no_document_section_when_empty() -> None:
    result = build_chat_context([_msg("user", "Вопрос")], document_context="")
    assert "Документы, связанные" not in result


def test_context_no_legal_section_when_empty() -> None:
    result = build_chat_context([_msg("user", "Вопрос")], legal_context="")
    assert "правовые источники" not in result


# --- build_rich_lawyer_block ---

def test_rich_block_falls_back_to_content_when_no_payload() -> None:
    msg = _msg("agent1", "Ответ без структуры")
    assert build_rich_lawyer_block(msg) == "Ответ без структуры"


def test_rich_block_includes_summary_and_metadata() -> None:
    payload = {
        "summary": "Риск нарушения сроков оплаты",
        "risk": "yellow",
        "confidence": "medium",
        "findings": [],
        "meaning_for_factory": "Нужен контроль дебиторки",
        "actions": [],
        "sources": [],
        "agreement": None,
    }
    result = build_rich_lawyer_block(_msg("agent1", "краткий", structured_payload=payload))
    assert "Риск нарушения сроков оплаты" in result
    assert "риск=yellow" in result
    assert "уверенность=medium" in result
    assert "Нужен контроль дебиторки" in result


def test_rich_block_includes_findings_and_actions() -> None:
    payload = {
        "summary": "Выявлены нарушения",
        "risk": "red",
        "confidence": "high",
        "findings": [{"title": "Задержка", "description": "Просрочка 30 дней"}],
        "meaning_for_factory": "Требуется реакция",
        "actions": ["Выставить претензию", "Уведомить директора"],
        "sources": [],
        "agreement": None,
    }
    result = build_rich_lawyer_block(_msg("agent1", "краткий", structured_payload=payload))
    assert "Задержка: Просрочка 30 дней" in result
    assert "Выставить претензию" in result
    assert "Уведомить директора" in result


def test_rich_block_includes_sources() -> None:
    payload = {
        "summary": "Проверка источника",
        "risk": "yellow",
        "confidence": "low",
        "findings": [],
        "meaning_for_factory": "Нужна проверка",
        "actions": [],
        "sources": [{"title": "Закон о поставках", "verification_status": "pending"}],
        "agreement": None,
    }
    result = build_rich_lawyer_block(_msg("agent1", "краткий", structured_payload=payload))
    assert "Закон о поставках (pending)" in result


def test_rich_block_includes_agreement_fields() -> None:
    payload = {
        "summary": "Мнение Юриста 2",
        "risk": "green",
        "confidence": "high",
        "findings": [],
        "meaning_for_factory": "Всё в порядке",
        "actions": [],
        "sources": [],
        "agreement": {
            "agreed_points": ["Срок оплаты"],
            "disagreed_points": ["Размер штрафа"],
            "unresolved_points": ["Условие форс-мажора"],
        },
    }
    result = build_rich_lawyer_block(_msg("agent2", "краткий", structured_payload=payload))
    assert "Согласен: Срок оплаты" in result
    assert "Не согласен: Размер штрафа" in result
    assert "Нерешено: Условие форс-мажора" in result


def test_history_uses_rich_block_for_agent_with_payload() -> None:
    payload = {
        "summary": "Предварительный вывод о рисках",
        "risk": "yellow",
        "confidence": "medium",
        "findings": [{"title": "Риск", "description": "Описание риска"}],
        "meaning_for_factory": "Важно для завода",
        "actions": ["Проверить"],
        "sources": [],
        "agreement": None,
    }
    messages = [
        _msg("user", "Вопрос пользователя"),
        _msg("agent1", "краткий вывод", structured_payload=payload),
    ]
    result = build_chat_history_context(messages)
    assert "Предварительный вывод о рисках" in result
    assert "риск=yellow" in result
    assert "Риск: Описание риска" in result


def test_history_uses_content_for_agent_without_payload() -> None:
    messages = [_msg("agent1", "Ответ юриста без структуры")]
    result = build_chat_history_context(messages)
    assert "Юрист 1: Ответ юриста без структуры" in result
