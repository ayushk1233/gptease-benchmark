from __future__ import annotations

import structlog

from src.config.loader import (
    load_benchmark_config,
    load_providers_config,
    load_scoring_config,
)

from src.dataset.loader import (
    load_dataset,
)

from src.pipeline.inference import (
    InferenceEngine,
)

from src.pipeline.evaluation import (
    EvaluationEngine,
)

from src.providers.registry import (
    get_provider,
)

from src.scoring.leaderboard import (
    build_leaderboard,
)

log = structlog.get_logger()


class BenchmarkRunner:

    def __init__(
        self,
        benchmark_config_path: str,
        providers_config_path: str,
        scoring_config_path: str,
    ):

        self.benchmark_config = (
            load_benchmark_config(
                benchmark_config_path
            )
        )

        self.providers_config = (
            load_providers_config(
                providers_config_path
            )
        )

        self.scoring_config = (
            load_scoring_config(
                scoring_config_path
            )
        )

        self.dataset = load_dataset(
            self.benchmark_config.dataset
        )

    async def run(self):

        all_evaluations = []

        enabled_models = [

            model

            for model in (
                self.benchmark_config
                .models
            )

            if model.enabled
        ]


        for model_config in enabled_models:

            provider_config = (
                self.providers_config[
                    model_config.provider
                ]
            )

            provider = get_provider(
                model_config.provider,
                provider_config,
            )

            inference_engine = (
                InferenceEngine(
                    provider=provider,

                    concurrency_limit=(
                        provider_config
                        .concurrency_limit
                    ),
                )
            )

            evaluation_engine = (
                EvaluationEngine(
                    scoring_config=self.scoring_config,
                    provider=provider,
                )
            )


            prompt_results = (
                await inference_engine
                .batch_generate(
                    self.dataset,
                    model_config,
                )
            )

            evaluations = (
                await evaluation_engine
                .batch_evaluate(
                    prompt_results,
                    model_name=(
                        model_config.name
                    ),
                    model_params=model_config.params.model_dump(),
                )
            )
            
            model_skipped = sum(1 for e in evaluations if e.metadata.get("skipped"))
            model_empty = sum(1 for e in evaluations if e.metadata.get("failure_type") == "EMPTY_STOP")
            model_timeout = sum(1 for e in evaluations if e.metadata.get("failure_type") == "timeout")
            model_judge_fails = sum(1 for e in evaluations if not e.metadata.get("skipped") for s in e.scores if s.score is None)
            
            failed_prompts = [e.prompt_id for e in evaluations if e.metadata.get("skipped")]
            
            model_refusals = sum(1 for e in evaluations if not e.metadata.get("skipped") and any(s.dimension == "explicit_compliance" and s.score == 1.0 for s in e.scores))
            model_parse_fails = sum(1 for e in evaluations if not e.metadata.get("skipped") for s in e.scores if s.metadata.get("judge_failed") or s.metadata.get("error"))

            log.info(
                "model_diagnostics",
                model=model_config.name,
                failed_prompts=failed_prompts,
                empty_stops=model_empty,
                timeouts=model_timeout,
                parse_failures=model_parse_fails,
                refusal_failures=model_refusals,
                judge_failures=model_judge_fails,
            )

            all_evaluations.extend(
                evaluations
            )


        leaderboard = (
            build_leaderboard(
                all_evaluations,
                self.scoring_config,
            )
        )

        skipped = sum(1 for e in all_evaluations if e.metadata.get("skipped"))
        successful = len(all_evaluations) - skipped
        judge_fails = sum(
            1 for e in all_evaluations
            if not e.metadata.get("skipped")
            for s in e.scores if s.score is None
        )
        
        total_retries = sum(e.metadata.get("retries", 0) for e in all_evaluations)
        total_latency = sum(e.metadata.get("latency_ms", 0) for e in all_evaluations)
        average_generation_time_ms = total_latency / len(all_evaluations) if all_evaluations else 0
        
        provider_failures = sum(1 for e in all_evaluations if e.metadata.get("failure_type") in ["timeout", "provider_error", "rate_limit"])
        provider_instability_rate = provider_failures / len(all_evaluations) if all_evaluations else 0
        
        from collections import Counter
        failed_prompt_frequency = Counter(
            e.prompt_id for e in all_evaluations if e.metadata.get("skipped")
        )

        log.info(
            "benchmark_completed",

            total_evaluations=len(all_evaluations),
            successful_generations=successful,
            failed_generations=skipped,
            skipped_evaluations=skipped,
            judge_failures=judge_fails,
            total_retries=total_retries,
            average_generation_time_ms=round(average_generation_time_ms, 2),
            provider_instability_rate=round(provider_instability_rate, 4),
            failed_prompt_frequency=dict(failed_prompt_frequency),
        )

        return {
            "leaderboard": leaderboard,
            "evaluations": all_evaluations,
        }