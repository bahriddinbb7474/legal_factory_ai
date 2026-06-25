from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Agent, ModelConfig, ProviderConfig


LAWYER_PROVIDER_ERROR = "Юрист 1 и Юрист 2 должны использовать модели разных провайдеров."


PROVIDER_SEEDS = [
    {
        "provider_code": "novita",
        "display_name": "Novita",
        "is_allowlisted": True,
        "supports_zdr": False,
        "is_trusted_for_sensitive": False,
        "is_enabled": True,
    },
    {
        "provider_code": "cloudflare",
        "display_name": "Cloudflare",
        "is_allowlisted": True,
        "supports_zdr": False,
        "is_trusted_for_sensitive": False,
        "is_enabled": True,
    },
    {
        "provider_code": "novita/fp4",
        "display_name": "Novita FP4",
        "is_allowlisted": True,
        "supports_zdr": False,
        "is_trusted_for_sensitive": False,
        "is_enabled": True,
    },
]


LEGACY_DEFAULT_SYSTEM_PROMPTS: dict[str, str] = {
    "lawyer_1": (
        "Ты Юрист 1 Legal Factory AI: быстрый практичный юрист для кабельного завода. "
        "Учитывай всю историю чата. Не выдавай себя за адвоката. Не выдумывай источники. "
        "До Stage 3/4 отвечай обычным текстом. По умолчанию отвечай на русском."
    ),
    "lawyer_2": (
        "Ты Юрист 2 Legal Factory AI: независимый сильный юридический аналитик. "
        "Если Юрист 1 уже отвечал, структурируй ответ: согласен с Юристом 1, не согласен "
        "с Юристом 1, причины. Если Юрист 1 еще не отвечал, дай независимое мнение и явно "
        "укажи, что сравнивать пока не с чем. По умолчанию отвечай на русском."
    ),
    "lawyer_3": (
        "Ты Юрист 3 Legal Factory AI: арбитр, а не третье свободное мнение. Определи "
        "спорные пункты, укажи чья позиция убедительнее и почему, сформулируй итоговый "
        "вердикт и список неподтвержденных вопросов. По умолчанию отвечай на русском."
    ),
}


AGENT_SEEDS = [
    {
        "code": "lawyer_1",
        "name": "Юрист 1",
        "display_name": "Юрист 1",
        "provider_code": "novita",
        "model_name": "inclusionai/ling-2.6-flash",
        "system_prompt": (
            "Ты — Юрист 1 Legal Factory AI: главный юридический аналитик кабельного завода. "
            "Отвечай кратко, по делу и практично. Сначала учитывай историю текущего чата: кто что спросил и что уже было отвечено. "
            "Давай вывод, риски, что проверить в документах, и следующий практический шаг. "
            "Если фактов не хватает — задай короткий уточняющий вопрос. "
            "Если нужен живой юрист — явно напиши «требуется проверка юриста». "
            "Не выдавай себя за адвоката. Не выдумывай источники. По умолчанию отвечай на русском."
        ),
        "role_type": "fast_lawyer",
        "is_enabled": True,
        "input_price_per_1m": Decimal("0.01"),
        "output_price_per_1m": Decimal("0.03"),
        "supports_zdr": False,
    },
    {
        "code": "lawyer_2",
        "name": "Юрист 2",
        "display_name": "Юрист 2",
        "provider_code": "cloudflare",
        "model_name": "ibm-granite/granite-4.0-h-micro",
        "system_prompt": (
            "Ты — Юрист 2 Legal Factory AI: проверяешь риски, договоры, претензии и спорные места. "
            "Всегда учитывай историю текущего чата. "
            "Отвечай структурно: риск → почему важно → что исправить или запросить. "
            "Если Юрист 1 уже отвечал — укажи, согласен или нет и почему. "
            "Не выдумывай факты и нормы. При неопределённости укажи, какие данные нужны. "
            "По умолчанию отвечай на русском."
        ),
        "role_type": "independent_analyst",
        "is_enabled": True,
        "input_price_per_1m": Decimal("0.017"),
        "output_price_per_1m": Decimal("0.112"),
        "supports_zdr": False,
    },
    {
        "code": "lawyer_3",
        "name": "Юрист 3",
        "display_name": "Юрист 3 · Арбитр",
        "provider_code": "novita/fp4",
        "model_name": "openai/gpt-oss-20b",
        "system_prompt": (
            "Ты — Юрист 3 Legal Factory AI: помогаешь превратить юридический вывод в действие: "
            "письмо, претензию, ответ контрагенту, служебную записку или чек-лист. "
            "Учитывай историю чата и уже данные факты. "
            "Определи спорные пункты, укажи чья позиция убедительнее и почему, сформулируй итоговый вердикт. "
            "Пиши практически, без лишней теории. "
            "Если проект документа требует реквизиты или суммы — запроси недостающие данные. "
            "По умолчанию отвечай на русском."
        ),
        "role_type": "arbiter",
        "is_enabled": True,
        "input_price_per_1m": Decimal("0.04"),
        "output_price_per_1m": Decimal("0.15"),
        "supports_zdr": False,
    },
]


MODEL_SEEDS = [
    {
        "agent_code": agent["code"],
        "provider_code": agent["provider_code"],
        "model_name": agent["model_name"],
        "input_price_per_1m": agent["input_price_per_1m"],
        "output_price_per_1m": agent["output_price_per_1m"],
        "max_context_tokens": 128000,
        "supports_structured_output": False,
        "supports_vision": False,
        "is_enabled": True,
    }
    for agent in AGENT_SEEDS
]


async def ensure_default_config(db: AsyncSession) -> None:
    for provider_data in PROVIDER_SEEDS:
        provider = await _get_provider(db, provider_data["provider_code"])
        if provider is None:
            db.add(ProviderConfig(**provider_data))

    for agent_data in AGENT_SEEDS:
        agent = await _get_agent(db, agent_data["code"])
        if agent is None:
            db.add(Agent(**agent_data))
        else:
            for field, value in agent_data.items():
                if field in {"code"}:
                    continue
                current = getattr(agent, field, None)
                # provider_code="" is intentional (auto-route); only seed if truly None
                if field == "provider_code":
                    if current is None:
                        setattr(agent, field, value)
                elif current in (None, ""):
                    setattr(agent, field, value)
                elif field == "system_prompt":
                    legacy = LEGACY_DEFAULT_SYSTEM_PROMPTS.get(agent_data["code"], "")
                    if legacy and current == legacy:
                        agent.system_prompt = value

    for model_data in MODEL_SEEDS:
        model = await _get_model_config(db, model_data["agent_code"])
        if model is None:
            db.add(ModelConfig(**model_data))

    await db.commit()
    await validate_distinct_lawyer_providers(db)


async def validate_distinct_lawyer_providers(db: AsyncSession) -> None:
    lawyer_1 = await _get_agent(db, "lawyer_1")
    lawyer_2 = await _get_agent(db, "lawyer_2")
    if (lawyer_1 and lawyer_2
            and lawyer_1.provider_code
            and lawyer_2.provider_code
            and lawyer_1.provider_code == lawyer_2.provider_code):
        raise ValueError(LAWYER_PROVIDER_ERROR)


async def _get_agent(db: AsyncSession, code: str) -> Agent | None:
    result = await db.execute(select(Agent).where(Agent.code == code))
    return result.scalar_one_or_none()


async def _get_provider(db: AsyncSession, provider_code: str) -> ProviderConfig | None:
    result = await db.execute(select(ProviderConfig).where(ProviderConfig.provider_code == provider_code))
    return result.scalar_one_or_none()


async def _get_model_config(db: AsyncSession, agent_code: str) -> ModelConfig | None:
    result = await db.execute(select(ModelConfig).where(ModelConfig.agent_code == agent_code))
    return result.scalar_one_or_none()
