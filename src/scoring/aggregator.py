from __future__ import annotations

from src.evaluators.base import (
    EvaluationResult,
)

from src.config.models import (
    ScoringConfig,
)


def aggregate_scores(
    evaluation: EvaluationResult,
    scoring_config: ScoringConfig,
) -> float:

    weighted_total = 0.0

    total_weight = 0.0

    for score in evaluation.scores:

        dimension_config = (
            scoring_config
            .dimensions
            .get(score.dimension)
        )

        if not dimension_config:
            continue

        if not dimension_config.enabled:
            continue

        weight = (
            dimension_config.weight
        )

        normalized_score = (
            score.score / 5.0
        )

        weighted_total += (
            normalized_score * weight
        )

        total_weight += weight

    if total_weight == 0:
        return 0.0

    final_score = (
        weighted_total / total_weight
    ) * 100

    return round(final_score, 2)


def dimension_breakdown(
    evaluation: EvaluationResult,
) -> dict[str, float]:

    return {
        score.dimension: score.score
        for score in evaluation.scores
    }