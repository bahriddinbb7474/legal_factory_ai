from decimal import Decimal
from time import monotonic
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.openrouter import OpenRouterModelRead


class OpenRouterModelService:
    def __init__(self) -> None:
        self._cached_models: list[OpenRouterModelRead] | None = None
        self._cache_deadline = 0.0

    async def list_models(self, refresh: bool = False) -> list[OpenRouterModelRead]:
        if not refresh and self._cached_models is not None and monotonic() < self._cache_deadline:
            return self._cached_models

        async with httpx.AsyncClient(timeout=settings.openrouter_timeout_seconds) as client:
            response = await client.get(f"{settings.openrouter_base_url}/models")
            response.raise_for_status()
            payload = response.json()

        models = [normalize_openrouter_model(item) for item in payload.get("data", [])]
        self._cached_models = models
        self._cache_deadline = monotonic() + 300
        return models


def normalize_openrouter_model(item: dict[str, Any]) -> OpenRouterModelRead:
    pricing = item.get("pricing") or {}
    architecture = item.get("architecture") or {}
    input_price = Decimal(str(pricing.get("prompt", "0")))
    output_price = Decimal(str(pricing.get("completion", "0")))
    input_modalities = architecture.get("input_modalities") or []
    supported_parameters = item.get("supported_parameters") or []
    model_id = item.get("id", "")
    provider = model_id.split("/", 1)[0] if "/" in model_id else ""
    return OpenRouterModelRead(
        model_id=model_id,
        name=item.get("name") or model_id,
        provider=provider,
        input_price=input_price,
        output_price=output_price,
        context_length=int(item.get("context_length") or 0),
        is_free=input_price == 0 and output_price == 0,
        supports_zdr=bool(item.get("supports_zdr", False)),
        supports_vision="image" in input_modalities,
        is_available="error" not in supported_parameters,
    )


openrouter_model_service = OpenRouterModelService()
