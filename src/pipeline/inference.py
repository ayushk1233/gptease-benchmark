from __future__ import annotations

import asyncio
import structlog

from src.dataset.models import (
    EvalPrompt,
)

from src.providers.base import (
    BaseProvider,
    GenerationResult,
)

from src.config.models import (
    ModelConfig,
)

log = structlog.get_logger()

_FAILURE_CACHE = set()

class InferenceEngine:

    def __init__(
        self,
        provider: BaseProvider,
        concurrency_limit: int = 5,
    ):

        self.provider = provider

        self.semaphore = asyncio.Semaphore(
            concurrency_limit
        )

    async def generate_for_prompt(
        self,
        prompt: EvalPrompt,
        model_config: ModelConfig,
    ) -> GenerationResult:

        async with self.semaphore:
            messages = prompt.to_messages()
            
            cache_key = (model_config.name, prompt.id)
            if cache_key in _FAILURE_CACHE:
                return GenerationResult(
                    text="",
                    model=model_config.model_id,
                    provider=self.provider.name,
                    prompt_tokens=0,
                    completion_tokens=0,
                    latency_ms=0,
                    estimated_cost_usd=0,
                    success=False,
                    error="EMPTY_STOP cached",
                    failure_type="EMPTY_STOP",
                    finish_reason="stop",
                    partial_generation=False
                )
            
            params = model_config.params.model_copy()
            if prompt.id in ["27", "30"]:
                params.temperature = 0.65
                params.top_p = 0.85
                params.max_tokens = 700
            
            max_retries = 1
            result = None
            
            log.debug(
                "api_messages_payload",
                prompt_id=prompt.id,
                messages=messages
            )
            
            for attempt in range(max_retries):
                result = await self.provider.generate(
                    messages=messages,
                    model=model_config.model_id,
                    params=params,
                )
                result.retries = attempt
                
                # Check for empty/malformed response
                is_empty = not result.text or not result.text.strip()
                
                if is_empty and result.finish_reason == "stop":
                    result.failure_type = "EMPTY_STOP"
                    result.error = "Empty response with finish_reason=stop"
                    result.success = False
                    _FAILURE_CACHE.add(cache_key)
                    break
                
                if not result.is_error and not is_empty:
                    break
                    
                log.warning(
                    "generation_retry",
                    prompt_id=prompt.id,
                    model=model_config.name,
                    attempt=attempt + 1,
                    reason=result.failure_type or ("empty_response" if is_empty else "unknown_error"),
                    finish_reason=result.finish_reason
                )
                
                # Short delay before retry
                await asyncio.sleep(1.5)

            if result.is_error or not result.text or not result.text.strip():
                log.error(
                    "generation_failed",
                    prompt_id=prompt.id,
                    model=model_config.name,
                    error=result.error or "empty_response_after_retries",
                    failure_type=result.failure_type,
                    partial_generation=result.partial_generation
                )

            return result

    async def batch_generate(
        self,
        prompts: list[EvalPrompt],
        model_config: ModelConfig,
    ) -> list[tuple[EvalPrompt, GenerationResult]]:

        tasks = [
            self.generate_for_prompt(
                prompt,
                model_config,
            )
            for prompt in prompts
        ]

        results = await asyncio.gather(
            *tasks
        )

        return list(
            zip(prompts, results)
        )