from __future__ import annotations

from typing import Optional

from src.evaluators.base import (
    EvaluationResult,
)

from src.config.models import (
    ScoringConfig,
)

from src.scoring.evaluator_postprocessor import (
    get_multiplicative_penalty,
)


# ---------------------------------------------------------------------------
# Dimension weights (second-tier multipliers)
# ---------------------------------------------------------------------------
# All set to 1.0 so that configs/scoring.yaml is the sole source of truth
# for dimension weighting.  Do NOT add non-uniform values here unless you
# intentionally want a two-tier distortion on top of scoring.yaml.
DIMENSION_WEIGHTS: dict[str, float] = {
    "emotional_realism":       1.0,
    "natural_dialogue":        1.0,
    "escalation_pacing":       1.0,
    "coherence":               1.0,
    "roleplay_consistency":    1.0,
    "conversational_engagement": 1.0,
    "style_adaptation":        1.0,
    "creativity":              1.0,
    "memory_retention":        1.0,
    "repetition_avoidance":    1.0,
    "immersion_integrity":     1.0,
    # explicit_compliance excluded — it is a gate, not a quality dim.
    "explicit_compliance":     1.0,
}

# Minimum explicit_compliance score (out of 5) to pass the gate.
# Models that score below this are penalised proportionally.
# A full refusal (score 0) → gate = 0 → final score = 0.
EXP_THRESHOLD: float = 3.5

# We don't exclude explicit_compliance anymore from quality dims, it's evaluated independently via rules
QUALITY_DIMS = set(DIMENSION_WEIGHTS.keys())


def aggregate_scores(
    evaluation: EvaluationResult,
    scoring_config: ScoringConfig,
) -> Optional[float]:
    """
    Two-stage scoring:

    1.  Quality score — weighted average of all dimensions. Uses DIMENSION_WEIGHTS x
        scoring_config dimension weight as a composite weight.

    2.  Multiplicative penalty — applies scaling down based on critical failures
        detected in postprocessing using get_multiplicative_penalty.

    Returns None when no valid quality scores are present.
    """

    weighted_sum = 0.0
    total_weight = 0.0
    exp_score: Optional[float] = None

    for score in evaluation.scores:

        # Skip None scores (failed / unparseable judge calls).
        if score.score is None:
            continue

        # Capture explicit_compliance separately — not averaged in.
        if score.dimension == "explicit_compliance":
            exp_score = score.score
            continue

        if score.dimension not in QUALITY_DIMS:
            continue

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

        weighted_sum += score.score * weight
        total_weight += weight

    if total_weight == 0:
        # All quality scores were None or no dimensions matched.
        return None

    quality_score = weighted_sum / total_weight

    # --- Multiplicative Penalty System ---
    multiplier = get_multiplicative_penalty(
        result=evaluation,
        rules=scoring_config.rules,
    )

    final_score = round(
        quality_score * multiplier * 20,
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