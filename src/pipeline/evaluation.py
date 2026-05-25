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

from src.scoring.evaluator_postprocessor import (
    apply_postprocessor,
)

from src.config.models import (
    ScoringConfig,
)

log = structlog.get_logger()

_EVALUATOR_CACHE = {}


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
        
        model_params: Optional[dict] = None,
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
                    "generation_cost_usd": response.estimated_cost_usd,
                    "judge_cost_usd": 0.0,
                    "total_cost_usd": response.estimated_cost_usd,
                    "retries": response.retries,
                    "failure_type": response.failure_type,
                },
            )
            
            if model_params:
                res.metadata.update(model_params)
            return res

        judge_model_id = self.scoring_config.judge_routing.overrides.get(
            model_name, self.scoring_config.judge_routing.default_judge
        )
        
        resolved_judge_config = self.scoring_config.judge.model_copy()
        resolved_judge_config.model_id = judge_model_id
        
        scoring_config_hash = hash(str(self.scoring_config.model_dump()))
        response_hash = hash(response.text)
        cache_key = (response_hash, judge_model_id, scoring_config_hash)
        
        if cache_key in _EVALUATOR_CACHE:
            cached_scores = _EVALUATOR_CACHE[cache_key]
            scores = cached_scores
            # Reset judge cost for cached hits
            cached_judge_cost = 0.0
        else:
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

                judge_config=resolved_judge_config,
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
                
                if "judge_latency_ms" in result.metadata:
                    log.debug(
                        "judge_evaluation_completed",
                        evaluated_model=model_name,
                        judge_model=resolved_judge_config.model_id,
                        prompt_id=prompt.id,
                        dimension=dimension,
                        latency_ms=result.metadata["judge_latency_ms"],
                        judge_retry_count=result.metadata["judge_retry_count"],
                    )

            except Exception as e:

                log.error(
                    "evaluation_failed",

                    prompt_id=prompt.id,

                    dimension=dimension,

                    error=str(e),
                )

            _EVALUATOR_CACHE[cache_key] = scores
            cached_judge_cost = sum(s.metadata.get("judge_cost_usd", 0.0) for s in scores)

        raw_result = EvaluationResult(
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

                "generation_cost_usd": (
                    response
                    .estimated_cost_usd
                ),

                "judge_cost_usd": cached_judge_cost,

                "total_cost_usd": (
                    response.estimated_cost_usd
                    + cached_judge_cost
                ),
                
                "judge_model": judge_model_id,
                "retries": response.retries,
                "failure_type": response.failure_type,
            },
        )
        
        if model_params:
            raw_result.metadata.update(model_params)
        
        return apply_postprocessor(
            result=raw_result,
            rules=self.scoring_config.rules,
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
        model_params: Optional[dict] = None,
    ) -> list[EvaluationResult]:

        tasks = [

            self.evaluate_response(
                prompt,
                result,
                model_name=model_name,
                model_params=model_params,
            )

            for prompt, result
            in prompt_results
        ]

        return await asyncio.gather(
            *tasks
        )