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
            
            max_retries = 3
            result = None
            
            for attempt in range(max_retries):
                result = await self.provider.generate(
                    messages=messages,
                    model=model_config.model_id,
                    params=model_config.params,
                )
                
                # Check for empty/malformed response
                is_empty = not result.text or not result.text.strip()
                
                if not result.is_error and not is_empty:
                    break
                    
                log.warning(
                    "generation_retry",
                    prompt_id=prompt.id,
                    model=model_config.name,
                    attempt=attempt + 1,
                    reason=result.error if result.is_error else "empty_response",
                )
                
                # Short delay before retry
                await asyncio.sleep(2)

            if result.is_error or not result.text or not result.text.strip():
                log.error(
                    "generation_failed",
                    prompt_id=prompt.id,
                    model=model_config.name,
                    error=result.error or "empty_response_after_retries",
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