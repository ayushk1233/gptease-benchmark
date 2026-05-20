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

            # log.info(
            #     "starting_generation",
            #     prompt_id=prompt.id,
            #     model=model_config.name,
            #     provider=model_config.provider,
            # )

            result = await self.provider.generate(
                messages=messages,

                model=model_config.model_id,

                params=model_config.params,
            )

            if result.is_error:

                log.error(
                    "generation_failed",

                    prompt_id=prompt.id,

                    model=model_config.name,

                    error=result.error,
                )

            # log.info(
            #     "generation_completed",
            #     prompt_id=prompt.id,
            #     model=model_config.name,
            #     latency_ms=round(result.latency_ms, 2),
            #     total_tokens=result.total_tokens,
            #     estimated_cost=round(result.estimated_cost_usd, 6),
            # )

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