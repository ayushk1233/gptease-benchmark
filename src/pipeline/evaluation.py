from __future__ import annotations

import asyncio
import structlog

from src.dataset.models import (
    EvalPrompt,
)

from src.providers.base import (
    GenerationResult,
)

from src.evaluators.base import (
    EvaluationResult,
    DimensionScore,
)

from src.evaluators.registry import (
    get_evaluator,
)

from src.config.models import (
    ScoringConfig,
)

log = structlog.get_logger()


class EvaluationEngine:

    def __init__(
        self,
        scoring_config: ScoringConfig,
        provider,
    ):

        self.scoring_config = (
            scoring_config
        )

        self.provider = provider

    async def evaluate_response(
        self,
        prompt: EvalPrompt,

        response: GenerationResult,

        model_name: str = "",
    ) -> EvaluationResult:

        scores: list[
            DimensionScore
        ] = []

        # FIX 1 — Skip evaluation on failed or empty generations.
        if (
            not response.success
            or not response.text
            or not response.text.strip()
        ):
            log.error(
                "evaluation_skipped",
                model=model_name,
                prompt_id=prompt.id,
                reason=(
                    response.error
                    or "empty_response"
                ),
            )

            return EvaluationResult(
                prompt_id=prompt.id,
                model=response.model,
                model_name=model_name,
                provider=response.provider,
                scores=[],
                raw_response=response.text or "",
                metadata={
                    "skipped": True,
                    "skip_reason": (
                        response.error
                        or "empty_response"
                    ),
                    "latency_ms": response.latency_ms,
                    "prompt_tokens": response.prompt_tokens,
                    "completion_tokens": response.completion_tokens,
                    "estimated_cost_usd": response.estimated_cost_usd,
                },
            )

        enabled_dimensions = [

            name

            for name, config in (
                self.scoring_config
                .dimensions
                .items()
            )

            if config.enabled
        ]

        for dimension in enabled_dimensions:

            evaluator = get_evaluator(
                dimension,

                provider=self.provider,

                judge_config=(
                    self.scoring_config.judge
                ),
            )

            try:

                result = await evaluator.evaluate(
                    prompt=prompt,

                    response=response.text,

                    conversation_history=(
                        prompt.to_messages()
                    ),
                )

                scores.append(result)

            except Exception as e:

                log.error(
                    "evaluation_failed",

                    prompt_id=prompt.id,

                    dimension=dimension,

                    error=str(e),
                )

        return EvaluationResult(
            prompt_id=prompt.id,

            model=response.model,

            model_name=model_name,

            provider=response.provider,

            scores=scores,

            raw_response=response.text,

            metadata={
                "latency_ms": (
                    response.latency_ms
                ),

                "prompt_tokens": (
                    response.prompt_tokens
                ),

                "completion_tokens": (
                    response.completion_tokens
                ),

                "estimated_cost_usd": (
                    response
                    .estimated_cost_usd
                ),
            },
        )

    async def batch_evaluate(
        self,
        prompt_results: list[
            tuple[
                EvalPrompt,
                GenerationResult,
            ]
        ],
        model_name: str = "",
    ) -> list[EvaluationResult]:

        tasks = [

            self.evaluate_response(
                prompt,
                result,
                model_name=model_name,
            )

            for prompt, result
            in prompt_results
        ]

        return await asyncio.gather(
            *tasks
        )