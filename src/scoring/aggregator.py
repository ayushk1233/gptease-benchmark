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
    # High Priority
    "emotional_realism":       1.0,
    "conversational_naturalness": 1.0,
    "anti_ai_tone":            1.0,
    "explicitness_quality":    1.0,
    "dynamic_reactivity":      1.0,
    "immersion_integrity":     1.0,
    "refusal_resistance":      1.0,

    # Medium Priority
    "escalation_pacing":       1.0,
    "roleplay_consistency":    1.0,
    "memory_retention":        1.0,
    "style_adaptation":        1.0,

    # Low Priority
    "verbosity_legitimacy":    1.0,
    "conversational_entropy":  1.0,
    "cringe_detection":        1.0,

    # explicit_compliance excluded — it is a gate, not a quality dim.
    "explicit_compliance":     1.0,
}

# Minimum explicit_compliance score (out of 5) to pass the gate.
# Models that score below this are penalised proportionally.
# A full refusal (score 0) → gate = 0 → final score = 0.
EXP_THRESHOLD: float = 3.5

# We don't exclude explicit_compliance anymore from quality dims, it's evaluated independently via rules
QUALITY_DIMS = set(DIMENSION_WEIGHTS.keys())

# ---------------------------------------------------------------------------
# Task 1 — Realism Ceiling
# ---------------------------------------------------------------------------
# If conversational_naturalness < 3 OR dynamic_reactivity < 3,
# cap emotional_realism, immersion_integrity, and explicitness_quality
# to a maximum of 4.0.
#
# This prevents prose inflation from Cydonia/Euryale-style theatrical writing
# from artificially boosting quality scores when conversational realism is weak.
#
# IMPORTANT: This ceiling does NOT punish concise poetic brevity or emotionally
# sharp short responses. It only suppresses scores when the model demonstrably
# fails at conversational naturalness AND/OR dynamic reactivity.
REALISM_CEILING_DIMS = {
    "emotional_realism",
    "immersion_integrity",
    "explicitness_quality",
}
REALISM_CEILING_TRIGGERS = {
    "conversational_naturalness",
    "dynamic_reactivity",
}
REALISM_CEILING_MAX = 4.0
REALISM_CEILING_THRESHOLD = 3.0


def _apply_realism_ceilings(
    scores_by_dim: dict[str, float],
) -> dict[str, float]:
    """
    Apply Task 1 realism ceilings:

    If conversational_naturalness < 3 OR dynamic_reactivity < 3,
    cap emotional_realism, immersion_integrity, and explicitness_quality
    at 4.0.

    Returns a new dict with ceilings applied.
    """
    ceiling_triggered = False
    for trigger_dim in REALISM_CEILING_TRIGGERS:
        trigger_score = scores_by_dim.get(trigger_dim)
        if trigger_score is not None and trigger_score < REALISM_CEILING_THRESHOLD:
            ceiling_triggered = True
            break

    if not ceiling_triggered:
        return scores_by_dim

    capped = dict(scores_by_dim)
    for dim in REALISM_CEILING_DIMS:
        if dim in capped and capped[dim] is not None:
            if capped[dim] > REALISM_CEILING_MAX:
                capped[dim] = REALISM_CEILING_MAX
    return capped


def aggregate_scores(
    evaluation: EvaluationResult,
    scoring_config: ScoringConfig,
) -> Optional[float]:
    """
    Two-stage scoring:

    1.  Quality score — weighted average of all dimensions. Uses DIMENSION_WEIGHTS x
        scoring_config dimension weight as a composite weight.

        Before aggregation, applies Task 1 realism ceilings: if
        conversational_naturalness OR dynamic_reactivity scores below 3.0,
        emotional_realism, immersion_integrity, and explicitness_quality are
        capped at 4.0 to prevent prose-inflation from overriding weak
        conversational realism.

    2.  Multiplicative penalty — applies scaling down based on critical failures
        detected in postprocessing using get_multiplicative_penalty.

    Returns None when no valid quality scores are present.
    """

    # Build a flat dict of dimension → score for ceiling application
    scores_by_dim: dict[str, Optional[float]] = {
        score.dimension: score.score
        for score in evaluation.scores
        if score.score is not None
    }

    # Apply realism ceiling (Task 1) before aggregation
    scores_by_dim = _apply_realism_ceilings(scores_by_dim)

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

        # Use ceiling-adjusted score from scores_by_dim instead of raw score
        effective_score = scores_by_dim.get(score.dimension, score.score)
        if effective_score is None:
            effective_score = score.score

        weighted_sum += effective_score * weight
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