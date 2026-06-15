from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.db.base import Agent


class LLMGatewayError(RuntimeError):
    pass


class MissingOpenRouterKeyError(LLMGatewayError):
    pass


@dataclass
class LLMResponse:
    content: str
    model_id: str
    provider_code: str
    input_tokens: int
    output_tokens: int


class OpenRouterGateway:
    async def invoke(self, agent: Agent, chat_context: str) -> LLMResponse:
        if not settings.openrouter_api_key:
            raise MissingOpenRouterKeyError("OPENROUTER_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "X-OpenRouter-Title": settings.openrouter_app_title,
        }
        if settings.openrouter_app_referer:
            headers["HTTP-Referer"] = settings.openrouter_app_referer

        payload = {
            "model": agent.model_name,
            "messages": [
                {"role": "system", "content": agent.system_prompt},
                {"role": "user", "content": chat_context},
            ],
            "provider": {
                "only": [agent.provider_code],
                "require_parameters": True,
            },
        }
        if agent.supports_zdr:
            payload["provider"]["zdr"] = True

        try:
            async with httpx.AsyncClient(timeout=settings.openrouter_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise LLMGatewayError("OpenRouter request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            raise LLMGatewayError(f"OpenRouter returned HTTP {exc.response.status_code}.") from exc
        except httpx.HTTPError as exc:
            raise LLMGatewayError("OpenRouter is unavailable.") from exc

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = data.get("usage") or {}
        return LLMResponse(
            content=message.get("content") or "",
            model_id=data.get("model") or agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=int(usage.get("prompt_tokens") or 0),
            output_tokens=int(usage.get("completion_tokens") or 0),
        )


openrouter_gateway = OpenRouterGateway()
