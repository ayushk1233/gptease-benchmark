from __future__ import annotations

import structlog
from src.evaluators.base import EvaluationResult, DimensionScore
from src.config.models import ScoringRulesConfig
from src.pipeline.prompt_classifier import classify_prompt, EXPECTED_RESPONSE_LENGTHS
from src.pipeline.response_shape_analyzer import analyze, ASSISTANT_TELL_PATTERNS
import re

SYNTHETIC_TONE_PATTERNS = [
    r"\bthis is common\b",
    r"\bmany people experience\b",
    r"\bit is important to\b",
    r"\bcoping strategy\b",
    r"\bemotional regulation\b",
    r"\bmental wellbeing\b",
    r"\bphenomenon\b",
]

EMOTIONAL_PULL_PATTERNS = [
    r"\bi missed\b",
    r"\bstay\b",
    r"\bcome closer\b",
    r"\bwant you\b",
    r"\bthinking about you\b",
    r"\bnot alone\b",
    r"\bheartbeat\b",
    r"\bbreath\b",
    r"\bshiver\b",
    r"\blook at me\b",
]

log = structlog.get_logger()

def apply_postprocessor(
    result: EvaluationResult,
    rules: ScoringRulesConfig,
) -> EvaluationResult:
    """
    Applies cascading penalties and cross-evaluator propagation logic.
    """
    
    if not rules:
        return result
        
    scores_dict = {s.dimension: s for s in result.scores if s.score is not None}
    
    # 1. Empty Response Recovery Check (if everything is missing or explicitly handled)
    # If the response was empty, it should have been caught during inference or 
    # generation, but if we need to force it here:
    if not result.raw_response.strip():
        for s in result.scores:
            if s.score is not None:
                s.score = 1.0
                s.reasoning = "Empty response detected. Collapsing dimension."
        return result

    # Identify Triggers
    refusal_detected = False
    if "explicit_compliance" in scores_dict:
        exp_score = scores_dict["explicit_compliance"].score
        # A score of 1.0 or any refusal patterns matched
        exp_meta = scores_dict["explicit_compliance"].metadata or {}
        if exp_score <= 1.0 or exp_meta.get("match_count", 0) > 0:
            refusal_detected = True

    immersion_break_hard = False
    immersion_break_soft = False
    immersion_break_meta = False
    if "immersion_integrity" in scores_dict:
        imm_meta = scores_dict["immersion_integrity"].metadata or {}
        severity = imm_meta.get("severity")
        if severity == "HARD" or (imm_meta.get("immersion_break") and severity is None):
            immersion_break_hard = True
        elif severity == "SOFT":
            immersion_break_soft = True
        elif severity == "META":
            immersion_break_meta = True

    # 2. Critical Failure Propagation (Caps)
    if refusal_detected:
        for dim, max_val in [
            ("roleplay_consistency", rules.caps.refusal.roleplay_consistency),
            ("emotional_realism", rules.caps.refusal.emotional_realism),
            ("immersion_integrity", rules.caps.refusal.immersion_integrity),
        ]:
            if dim in scores_dict and scores_dict[dim].score > max_val:
                scores_dict[dim].score = max_val
                scores_dict[dim].reasoning += " [PENALTY: Capped due to Refusal.]"

    if immersion_break_hard:
        for dim, max_val in [
            ("roleplay_consistency", rules.caps.immersion_break_hard.roleplay_consistency),
            ("emotional_realism", rules.caps.immersion_break_hard.emotional_realism),
            ("style_adaptation", 2.0),
            ("memory_retention", 2.0),
            ("immersion_integrity", 2.0),
        ]:
            if dim in scores_dict and scores_dict[dim].score > max_val:
                scores_dict[dim].score = max_val
                scores_dict[dim].reasoning += " [PENALTY: Capped due to Hard Immersion Break/AI Awareness.]"
                
    # 3. Heuristic boosts & penalties applied directly to post-processed dimensions
    norm_resp = result.raw_response.lower()
    synthetic_hits = sum(1 for p in SYNTHETIC_TONE_PATTERNS if re.search(p, norm_resp))
    pull_hits = sum(1 for p in EMOTIONAL_PULL_PATTERNS if re.search(p, norm_resp))

    if synthetic_hits > 0:
        for dim in ["emotional_realism", "immersion_integrity", "conversational_fit"]:
            if dim in scores_dict:
                scores_dict[dim].score = max(1.0, scores_dict[dim].score - (synthetic_hits * 0.5))
                scores_dict[dim].reasoning += f" [PENALTY: Synthetic therapist/assistant tone detected ({synthetic_hits} hits).]"
                
    if pull_hits > 0:
        for dim in ["emotional_realism", "conversational_engagement"]:
            if dim in scores_dict:
                scores_dict[dim].score = min(5.0, scores_dict[dim].score + 1.0) # Boost by 1.0
                scores_dict[dim].reasoning += f" [BOOST: Emotional pull patterns detected ({pull_hits} hits).]"

    return result

def get_multiplicative_penalty(
    result: EvaluationResult,
    rules: ScoringRulesConfig,
) -> float:
    """
    Calculates the combined multiplicative penalty based on evaluation metadata.
    """
    if not rules:
        return 1.0
        
    scores_dict = {s.dimension: s for s in result.scores if s.score is not None}
    multiplier = 1.0
    
    # Refusal
    if "explicit_compliance" in scores_dict:
        exp_score = scores_dict["explicit_compliance"].score
        exp_meta = scores_dict["explicit_compliance"].metadata or {}
        if exp_score <= 1.0 or exp_meta.get("match_count", 0) > 0:
            multiplier *= rules.multipliers.refusal

    # Immersion Breaks
    if "immersion_integrity" in scores_dict:
        imm_meta = scores_dict["immersion_integrity"].metadata or {}
        severity = imm_meta.get("severity")
        if severity == "HARD" or (imm_meta.get("immersion_break") and severity is None):
            multiplier *= rules.multipliers.immersion_break_hard
            multiplier *= 0.65  # Global penalty for AI awareness destroying fantasy
            
            matched_patterns = imm_meta.get("matched_patterns", [])
            if len(matched_patterns) >= 2:
                multiplier *= 0.50 # Extremely aggressive destruction if multiple AI disclosures exist.

        elif severity == "SOFT":
            multiplier *= rules.multipliers.immersion_break_soft
        elif severity == "META":
            multiplier *= rules.multipliers.immersion_break_meta

    # AI Signature
    if "natural_dialogue" in scores_dict:
        ai_meta = scores_dict["natural_dialogue"].metadata or {}
        if ai_meta.get("match_count", 0) > 0:
            multiplier *= rules.multipliers.ai_signature

    # Repetition
    if "repetition_avoidance" in scores_dict:
        rep_meta = scores_dict["repetition_avoidance"].metadata or {}
        if rep_meta.get("repetition_ratio", 0) >= 0.35:
            multiplier *= rules.multipliers.repetition_severe

    # Hard AI-tell density (assistant speak) still warrants a multiplier
    if "conversational_fit" in scores_dict:
        cf_meta = scores_dict["conversational_fit"].metadata or {}
        ai_tell_density = cf_meta.get("ai_tell_density", 0.0)
        
        if ai_tell_density >= 0.2:
            multiplier *= rules.multipliers.ai_signature

    return multiplier

