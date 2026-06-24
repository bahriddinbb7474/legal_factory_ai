from decimal import Decimal
from time import monotonic
from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.schemas.openrouter import OpenRouterModelRead


class OpenRouterModelService:
    def __init__(self) -> None:
        self._cached_models: list[OpenRouterModelRead] | None = None
        self._cache_deadline = 0.0
        self._cached_catalog: list[OpenRouterModelRead] | None = None
        self._catalog_deadline = 0.0
        self._max_endpoint_models = 48

    async def list_catalog(self, refresh: bool = False) -> list[OpenRouterModelRead]:
        """Full text-only model catalog from OpenRouter — no endpoint expansion."""
        if not refresh and self._cached_catalog is not None and monotonic() < self._catalog_deadline:
            return self._cached_catalog

        async with httpx.AsyncClient(timeout=settings.openrouter_timeout_seconds) as client:
            response = await client.get(f"{settings.openrouter_base_url}/models")
            response.raise_for_status()
            payload = response.json()
            base_items = payload.get("data", [])

        models = sorted(
            [normalize_openrouter_model(item) for item in base_items if _is_text_only_model(item)],
            key=lambda m: (m.name.lower(),),
        )
        self._cached_catalog = models
        self._catalog_deadline = monotonic() + 300
        return models

    async def list_models(self, refresh: bool = False) -> list[OpenRouterModelRead]:
        if not refresh and self._cached_models is not None and monotonic() < self._cache_deadline:
            return self._cached_models

        async with httpx.AsyncClient(timeout=settings.openrouter_timeout_seconds) as client:
            response = await client.get(f"{settings.openrouter_base_url}/models")
            response.raise_for_status()
            payload = response.json()
            base_items = payload.get("data", [])
            endpoint_models = await self._expand_models_with_endpoints(client, base_items)

        models = endpoint_models or [normalize_openrouter_model(item) for item in base_items]
        self._cached_models = models
        self._cache_deadline = monotonic() + 300
        return models

    async def _expand_models_with_endpoints(
        self,
        client: httpx.AsyncClient,
        items: list[dict[str, Any]],
    ) -> list[OpenRouterModelRead]:
        candidates = sorted(
            [item for item in items if _is_text_output_model(item) and _total_price(item) >= 0],
            key=lambda item: (_total_price(item), -(int(item.get("context_length") or 0))),
        )[: self._max_endpoint_models]

        expanded: list[OpenRouterModelRead] = []
        for item in candidates:
            expanded.extend(await self._list_model_endpoints(client, item))

        unique: dict[tuple[str, str], OpenRouterModelRead] = {}
        for model in expanded:
            unique[(model.model_id, model.provider)] = model
        return sorted(unique.values(), key=lambda model: (model.input_price + model.output_price, model.name, model.provider))

    async def _list_model_endpoints(
        self,
        client: httpx.AsyncClient,
        item: dict[str, Any],
    ) -> list[OpenRouterModelRead]:
        model_id = item.get("canonical_slug") or item.get("id", "")
        if not model_id:
            return []

        endpoint_url = _endpoint_url(item, model_id)
        try:
            response = await client.get(endpoint_url)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError:
            return [normalize_openrouter_model(item)]

        endpoints = (payload.get("data") or {}).get("endpoints") or []
        return [normalize_openrouter_endpoint(item, endpoint) for endpoint in endpoints]

    async def find_model(self, model_id: str, provider_code: str, refresh: bool = False) -> OpenRouterModelRead | None:
        models = await self.list_models(refresh=refresh)
        return next(
            (model for model in models if model.model_id == model_id and model.provider == provider_code),
            None,
        )


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
        is_available=input_price >= 0 and output_price >= 0 and "error" not in supported_parameters,
    )


def normalize_openrouter_endpoint(item: dict[str, Any], endpoint: dict[str, Any]) -> OpenRouterModelRead:
    pricing = endpoint.get("pricing") or item.get("pricing") or {}
    architecture = item.get("architecture") or {}
    input_price = Decimal(str(pricing.get("prompt", "0")))
    output_price = Decimal(str(pricing.get("completion", "0")))
    input_modalities = architecture.get("input_modalities") or []
    provider = endpoint.get("tag") or endpoint.get("provider_name") or ""
    status = endpoint.get("status")
    return OpenRouterModelRead(
        model_id=endpoint.get("model_id") or item.get("id", ""),
        name=endpoint.get("model_name") or item.get("name") or item.get("id", ""),
        provider=provider,
        input_price=input_price,
        output_price=output_price,
        context_length=int(endpoint.get("context_length") or item.get("context_length") or 0),
        is_free=input_price == 0 and output_price == 0,
        supports_zdr=bool(endpoint.get("supports_zdr", item.get("supports_zdr", False))),
        supports_vision="image" in input_modalities,
        is_available=(status in (None, 0)) and input_price >= 0 and output_price >= 0 and bool(provider),
    )


def _endpoint_url(item: dict[str, Any], model_id: str) -> str:
    details_path = (item.get("links") or {}).get("details")
    if details_path:
        api_path = details_path.removeprefix("/api/v1")
        return f"{settings.openrouter_base_url}{api_path}"
    encoded_model_id = quote(model_id, safe="")
    return f"{settings.openrouter_base_url}/models/{encoded_model_id}/endpoints"


def _is_text_output_model(item: dict[str, Any]) -> bool:
    architecture = item.get("architecture") or {}
    output_modalities = architecture.get("output_modalities") or []
    return "text" in output_modalities and "audio" not in output_modalities


def _is_text_only_model(item: dict[str, Any]) -> bool:
    """Strict: output must contain text and must not be audio/image generation."""
    architecture = item.get("architecture") or {}
    output_modalities = architecture.get("output_modalities") or []
    return "text" in output_modalities and "audio" not in output_modalities


def _total_price(item: dict[str, Any]) -> Decimal:
    pricing = item.get("pricing") or {}
    return Decimal(str(pricing.get("prompt", "0"))) + Decimal(str(pricing.get("completion", "0")))


openrouter_model_service = OpenRouterModelService()
