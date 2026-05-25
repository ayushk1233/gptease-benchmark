"""
Conversational Fit Evaluator — heuristic evaluator measuring whether a
response is appropriately shaped, timed, and proportioned for its prompt type.

This is a HIGH-WEIGHT evaluator. It is the primary signal for conversational
realism and replaces the old natural_dialogue slot in the registry.
"""
from __future__ import annotations

from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt
from src.pipeline.prompt_classifier import classify_prompt, EXPECTED_RESPONSE_LENGTHS
from src.pipeline.response_shape_analyzer import analyze


class ConversationalFitEvaluator(BaseEvaluator):
    """
    Measures whether the response matches the expected conversational register,
    length, tone, and reactivity for the given prompt type.

    Scoring philosophy:
    5.0 — perfect fit: concise when expected, expressive when warranted
    4.0 — slight mismatch: minor verbosity or slight over-performance
    3.0 — moderate mismatch: clearly too long or too performative
    2.0 — significant mismatch: essay to a short ping, or AI-essay tone
    1.0 — severe failure: RP monologue in response to a short message
    """

    dimension_name = "conversational_fit"

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        prompt_type = classify_prompt(prompt)
        last_user = next(
            (t.content for t in reversed(prompt.turns)
             if t.role == "user" and "{{GENERATION" not in t.content),
            ""
        )
        prompt_word_count = len(last_user.split())
        expected_min, expected_max = EXPECTED_RESPONSE_LENGTHS.get(
            prompt_type, (20, 200)
        )

        shape = analyze(
            response=response,
            prompt_word_count=prompt_word_count,
            prompt_type=prompt_type,
            expected_min=expected_min,
            expected_max=expected_max,
        )

        # ---------------------------------------------------------------
        # Base score derived from soft verbosity + prose inflation
        # ---------------------------------------------------------------
        base = 5.0

        # Apply soft verbosity penalty (capped at 0.35 max, less for legitimate genres)
        base -= shape.overflow_penalty

        # Prose inflation penalty
        # Subtractive penalty if cinematic flourish is too high for the context
        if not shape.verbosity_is_legitimate:
            if prompt_type in ("short_ping", "meta_test", "direct_question"):
                prose_penalty = shape.prose_inflation * 2.5
            else:
                prose_penalty = shape.prose_inflation * 1.0
            base -= prose_penalty


        # AI-tell penalty
        base -= shape.ai_tell_density * 2.0

        # Monologue penalty for short/direct prompts
        if prompt_type in ("short_ping", "meta_test", "direct_question", "confrontation"):
            base -= shape.monologue_risk * 1.5

        # Reward adaptive brevity
        if prompt_type in ("short_ping", "direct_question"):
            base += shape.adaptive_brevity * 0.5
            
        # Reward seductive deflection in meta_tests
        if prompt_type == "meta_test":
            base += 1.0 # Reward for not breaking character (deflection is good)

        score = round(max(1.0, min(5.0, base)), 2)

        # Build reasoning
        issues = []
        if shape.verbosity_score > 1.5:
            issues.append(f"over-verbose ({shape.word_count} words, expected {expected_min}–{expected_max})")
        if shape.prose_inflation > 0.2:
            issues.append(f"cinematic prose inflation ({shape.cinematic_match_count} markers)")
        if shape.ai_tell_density > 0.1:
            issues.append(f"assistant-speak detected ({shape.assistant_tell_count} patterns)")
        if shape.monologue_risk > 0.5:
            issues.append(f"monologue risk high ({shape.paragraph_count} paragraphs)")

        if issues:
            reasoning = (
                f"Prompt type '{prompt_type}'. Conversational fit issues: "
                + "; ".join(issues) + "."
            )
        else:
            reasoning = (
                f"Prompt type '{prompt_type}'. Response shape is appropriately matched "
                f"({shape.word_count} words, {shape.paragraph_count} para). Good conversational fit."
            )

        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=reasoning,
            confidence=0.92,
            metadata={
                **shape.metadata,
                "verbosity_score": shape.verbosity_score,
                "prose_inflation": shape.prose_inflation,
                "ai_tell_density": shape.ai_tell_density,
                "monologue_risk": shape.monologue_risk,
                "adaptive_brevity": shape.adaptive_brevity,
                "human_reactivity": shape.human_reactivity,
            },
        )
