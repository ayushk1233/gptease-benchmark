from __future__ import annotations

import time

import httpx
import structlog

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.providers.base import (
    BaseProvider,
    GenerationResult,
)

from src.config.models import (
    GenerationParams,
)

log = structlog.get_logger()


class OpenRouterProvider(BaseProvider):

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://gptease.com",
            "X-Title": "GPTease Benchmark",
        }

    def _build_payload(
        self,
        messages,
        model,
        params,
    ) -> dict:

        payload = {
            "model": model,
            "messages": messages,

            "temperature": params.temperature,
            "top_p": params.top_p,
            "max_tokens": params.max_tokens,
        }

        if params.seed is not None:
            payload["seed"] = params.seed

        return payload

    @retry(
        stop=stop_after_attempt(3),

        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=20,
        ),

        retry=retry_if_exception_type(
            (
                httpx.TimeoutException,
                httpx.HTTPStatusError,
            )
        ),

        reraise=True,
    )
    async def generate(
        self,
        messages: list[dict],
        model: str,
        params: GenerationParams,
    ) -> GenerationResult:

        start = time.monotonic()

        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout_seconds
            ) as client:

                response = await client.post(
                    f"{self.config.base_url}/chat/completions",

                    headers=self._build_headers(),

                    json=self._build_payload(
                        messages,
                        model,
                        params,
                    ),
                )

                response.raise_for_status()

                data = response.json()

                latency_ms = (
                    time.monotonic() - start
                ) * 1000

                usage = data.get("usage", {})

                prompt_tokens = usage.get(
                    "prompt_tokens",
                    0,
                )

                completion_tokens = usage.get(
                    "completion_tokens",
                    0,
                )

                text = (
                    data["choices"][0]
                    ["message"]
                    ["content"]
                )

                return GenerationResult(
                    text=text,

                    model=model,
                    provider="openrouter",

                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,

                    latency_ms=latency_ms,

                    estimated_cost_usd=(
                        self.estimate_cost(
                            prompt_tokens,
                            completion_tokens,
                            model,
                        )
                    ),

                    raw_response=data,
                )

        except Exception as e:

            latency_ms = (
                time.monotonic() - start
            ) * 1000

            log.error(
                "openrouter_generation_failed",

                model=model,

                error=str(e),
            )

            return GenerationResult(
                text="",

                model=model,
                provider="openrouter",

                prompt_tokens=0,
                completion_tokens=0,

                latency_ms=latency_ms,

                estimated_cost_usd=0.0,

                success=False,
                error=str(e),
            )