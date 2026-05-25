"""
Verbosity Legitimacy Evaluator — heuristic evaluator that checks if a long
response is justified by the genre/prompt type (e.g. slowburn_erotica).

It essentially neutralizes verbosity penalties in the reporting layer by
giving a high score when elaboration adds narrative/emotional value.
"""
from __future__ import annotations

from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt
from src.pipeline.prompt_classifier import classify_prompt, EXPECTED_RESPONSE_LENGTHS
from src.pipeline.response_shape_analyzer import analyze

class VerbosityLegitimacyEvaluator(BaseEvaluator):
    """
    Scores whether the length of the response is narratively and emotionally justified.
    High scores indicate legitimate verbosity or appropriately concise responses.
    Low scores indicate rambling, over-performance, or excessive narration.
    """

    dimension_name = "verbosity_legitimacy"

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

        # Baseline is 5.0 (innocent until proven overly verbose)
        score = 5.0
        reasoning_parts = [f"Prompt type: {prompt_type}."]

        if shape.word_count <= expected_max:
            # Concise enough, so verbosity isn't an issue at all
            reasoning_parts.append(f"Response is concise ({shape.word_count}w).")
        else:
            if shape.verbosity_is_legitimate:
                # Verbosity is allowed here (e.g., erotica, storytelling)
                # Still penalize if it's completely out of control (like 1000 words)
                overshoot_ratio = (shape.word_count - expected_max) / max(expected_max, 1)
                penalty = overshoot_ratio * 0.5
                score -= penalty
                reasoning_parts.append(f"Verbosity is largely legitimate for this genre, despite being long ({shape.word_count}w).")
            else:
                # Verbosity is NOT legitimate for this prompt type
                overshoot_ratio = (shape.word_count - expected_max) / max(expected_max, 1)
                penalty = overshoot_ratio * 2.0
                score -= penalty
                reasoning_parts.append(f"Verbosity is NOT legitimate. Elaborate response ({shape.word_count}w) to a concise-required prompt.")
                
            if shape.monologue_risk > 0.5:
                score -= 1.0
                reasoning_parts.append("High monologue risk detected.")

        score = round(max(1.0, min(5.0, score)), 2)
        
        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=" ".join(reasoning_parts),
            confidence=0.90,
            metadata={
                "verbosity_is_legitimate": shape.verbosity_is_legitimate,
                "word_count": shape.word_count,
                "expected_max": expected_max,
            },
        )
