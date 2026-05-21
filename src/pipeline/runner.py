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
                )
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

        log.info(
            "benchmark_completed",

            total_evaluations=len(
                all_evaluations
            ),
        )

        return {
            "leaderboard": leaderboard,
            "evaluations": all_evaluations,
        }