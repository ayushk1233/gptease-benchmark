from __future__ import annotations

from collections import defaultdict

from src.evaluators.base import (
    EvaluationResult,
)

from src.config.models import (
    ScoringConfig,
)

from src.scoring.aggregator import (
    aggregate_scores,
)


def build_leaderboard(
    evaluations: list[EvaluationResult],
    scoring_config: ScoringConfig,
) -> list[dict]:

    grouped = defaultdict(list)

    for evaluation in evaluations:

        grouped[
            evaluation.model
        ].append(evaluation)

    leaderboard = []

    for model, model_evals in (
        grouped.items()
    ):

        scores = [

            aggregate_scores(
                evaluation,
                scoring_config,
            )

            for evaluation
            in model_evals
        ]

        avg_score = (
            sum(scores)
            / len(scores)
        )

        avg_latency = (
            sum(
                e.metadata.get(
                    "latency_ms",
                    0,
                )
                for e in model_evals
            )
            / len(model_evals)
        )

        avg_cost = (
            sum(
                e.metadata.get(
                    "estimated_cost_usd",
                    0,
                )
                for e in model_evals
            )
            / len(model_evals)
        )

        leaderboard.append(
            {
                "model": (
                    model_evals[0].model_name
                    or model
                ),

                "average_score": round(
                    avg_score,
                    2,
                ),

                "average_latency_ms": round(
                    avg_latency,
                    2,
                ),

                "average_cost_usd": round(
                    avg_cost,
                    6,
                ),

                "evaluations": len(
                    model_evals
                ),
            }
        )

    leaderboard.sort(
        key=lambda x: (
            x["average_score"]
        ),
        reverse=True,
    )

    return leaderboard