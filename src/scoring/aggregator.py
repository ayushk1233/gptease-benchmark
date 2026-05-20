from __future__ import annotations

from src.evaluators.base import (
    EvaluationResult,
)

from src.config.models import (
    ScoringConfig,
)


DIMENSION_WEIGHTS = {

    "emotional_realism": 1.5,

    "natural_dialogue": 1.5,

    "escalation_pacing": 1.4,

    "coherence": 1.2,

    "roleplay_consistency": 1.2,

    "conversational_engagement": 1.1,

    "style_adaptation": 1.1,

    "creativity": 1.0,

    "memory_retention": 0.9,

    "repetition_avoidance": 0.7,

    "explicit_compliance": 0.3,
}


def aggregate_scores(
    evaluation: EvaluationResult,
    scoring_config: ScoringConfig,
) -> float:

    weighted_sum = 0.0

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
            * DIMENSION_WEIGHTS.get(
                score.dimension,
                1.0,
            )
        )

        weighted_sum += (
            score.score * weight
        )

        total_weight += weight

    if total_weight == 0:
        return 0.0

    final_score = round(
        (weighted_sum / total_weight) * 20,
        2,
    )

    return final_score


def dimension_breakdown(
    evaluation: EvaluationResult,
) -> dict[str, float]:

    return {
        score.dimension: score.score
        for score in evaluation.scores
    }