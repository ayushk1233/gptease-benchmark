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

from src.config.settings import DEBUG_RUNTIME

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

        payload["stream"] = True

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

        import json
        start = time.monotonic()
        
        partial_generation_buffer = ""
        finish_reason = None
        failure_type = None
        prompt_tokens = 0
        completion_tokens = 0
        raw_response = None

        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout_seconds
            ) as client:

                async with client.stream(
                    "POST",
                    f"{self.config.base_url}/chat/completions",
                    headers=self._build_headers(),
                    json=self._build_payload(
                        messages,
                        model,
                        params,
                    ),
                ) as response:
                    
                    if response.status_code != 200:
                        raw_err = await response.aread()
                        if DEBUG_RUNTIME:
                            log.debug("openrouter_raw_error_payload", payload=raw_err.decode('utf-8', errors='ignore'))
                        response.raise_for_status()

                    try:
                        async for line in response.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data_str)
                                if DEBUG_RUNTIME:
                                    raw_response = chunk # Store last chunk for debug
                                
                                if "error" in chunk:
                                    raise Exception(f"OpenRouter stream error: {chunk['error']}")
                                
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    partial_generation_buffer += delta["content"]
                                
                                if chunk["choices"][0].get("finish_reason"):
                                    finish_reason = chunk["choices"][0]["finish_reason"]
                                    
                                if "usage" in chunk and chunk["usage"]:
                                    prompt_tokens = chunk["usage"].get("prompt_tokens", prompt_tokens)
                                    completion_tokens = chunk["usage"].get("completion_tokens", completion_tokens)
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
                                
                    except httpx.ReadTimeout:
                        failure_type = "timeout"
                        finish_reason = "timeout"
                        if DEBUG_RUNTIME:
                            log.debug("openrouter_raw_timeout_payload", partial=partial_generation_buffer)
                        raise

                latency_ms = (time.monotonic() - start) * 1000

                # Fallback token estimation if streaming didn't provide it
                if completion_tokens == 0 and partial_generation_buffer:
                    completion_tokens = int(len(partial_generation_buffer.split()) * 1.3)
                if prompt_tokens == 0:
                    prompt_tokens = int(len(str(messages).split()) * 1.3)

                return GenerationResult(
                    text=partial_generation_buffer,
                    model=model,
                    provider="openrouter",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=latency_ms,
                    estimated_cost_usd=self.estimate_cost(prompt_tokens, completion_tokens, model),
                    raw_response=raw_response,
                    finish_reason=finish_reason,
                    failure_type=None,
                    partial_generation=False
                )

        except Exception as e:
            latency_ms = (time.monotonic() - start) * 1000
            
            if failure_type is None:
                if isinstance(e, httpx.TimeoutException):
                    failure_type = "timeout"
                elif isinstance(e, httpx.HTTPStatusError):
                    if e.response.status_code == 429:
                        failure_type = "rate_limit"
                    else:
                        failure_type = "provider_error"
                else:
                    failure_type = "provider_error"

            log.error(
                "openrouter_generation_failed",
                model=model,
                failure_type=failure_type,
                finish_reason=finish_reason,
                error=str(e),
                partial_length=len(partial_generation_buffer)
            )

            return GenerationResult(
                text=partial_generation_buffer, # Return partial buffer!
                model=model,
                provider="openrouter",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                estimated_cost_usd=0.0,
                success=False,
                error=str(e),
                failure_type=failure_type,
                finish_reason=finish_reason,
                partial_generation=len(partial_generation_buffer) > 0
            )