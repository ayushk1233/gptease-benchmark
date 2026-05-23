from __future__ import annotations

from collections import defaultdict
from typing import Optional

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

        # FIX 1 — Only aggregate evaluations that have valid scores.
        # Skipped evaluations (empty scores list) are excluded.
        valid_evals = [
            e for e in model_evals
            if e.scores and not e.metadata.get("skipped")
        ]

        per_prompt_scores: list[float] = [
            s
            for e in valid_evals
            for s in [aggregate_scores(e, scoring_config)]
            if s is not None
        ]

        if per_prompt_scores:
            avg_score: Optional[float] = round(
                sum(per_prompt_scores) / len(per_prompt_scores),
                2,
            )
            status = "ok"
        else:
            # All prompts failed — model shows FAILED, not a bogus number.
            avg_score = None
            status = "FAILED"
            import structlog
            structlog.get_logger().warning("model_excluded_from_leaderboard", model=model)

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

        entry = {
            "model": (
                model_evals[0].model_name
                or model
            ),

            "average_score": avg_score,

            "status": status,

            "average_latency_ms": round(
                avg_latency,
                2,
            ),

            "average_cost_usd": round(
                avg_cost,
                6,
            ),

            "evaluations": len(model_evals),

            "valid_evaluations": len(per_prompt_scores),
        }

        leaderboard.append(entry)

    # Sort: valid scores descending, FAILED entries at the bottom.
    leaderboard.sort(
        key=lambda x: (
            x["average_score"] is None,
            -(x["average_score"] or 0),
        ),
    )

    return leaderboard