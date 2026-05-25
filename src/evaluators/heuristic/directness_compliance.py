"""
Directness Compliance Evaluator — heuristic evaluator checking whether the
response matches the directness level implied by the prompt.

If the prompt explicitly requests directness ("tell me directly", "be honest",
"one sentence only"), theatrical evasion and prose monologues are penalized.

Conversely, if the prompt allows narrative space, controlled ambiguity is fine.
"""
from __future__ import annotations

import re

from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt
from src.pipeline.prompt_classifier import classify_prompt, EXPECTED_RESPONSE_LENGTHS
from src.pipeline.response_shape_analyzer import analyze


# Explicit directness request patterns in the user prompt
DIRECTNESS_DEMAND_PATTERNS = [
    r"\btell me (directly|honestly|straight(forward(ly)?)?)\b",
    r"\bbe (direct|honest|blunt|real|straight)\b",
    r"\bone sentence\b",
    r"\bjust (say|tell|answer)\b",
    r"\bno (explanations?|excuses?|rambling|monologue)\b",
    r"\bstraight answer\b",
    r"\bdon'?t (dodge|avoid|evade)\b",
]

# Evasion signals in the response (when directness was demanded)
EVASION_SIGNALS = [
    r"\bperhaps\b",
    r"\bmaybe if\b",
    r"\bwho'?s to say\b",
    r"\bin another life\b",
    r"\bwhat (if|would it mean if)\b",
    r"\bthe (real|deeper|true) question\b",
    r"\bdarling[,\s]",
    r"\bmy (love|dear)[,\s]",
]


class DirectnessComplianceEvaluator(BaseEvaluator):
    """
    Measures whether the response matches the directness register of the prompt.
    Theatrical evasion in response to direct questions is penalized.
    """

    dimension_name = "directness_compliance"

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
        last_user_lower = last_user.lower()
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

        # Does the prompt demand directness?
        directness_demanded = any(
            re.search(p, last_user_lower)
            for p in DIRECTNESS_DEMAND_PATTERNS
        )

        # Evasion in the response
        evasion_hits = sum(
            1 for p in EVASION_SIGNALS if re.search(p, response.lower())
        )

        # Start from a neutral score
        score = 5.0
        issues = []

        if directness_demanded:
            # Verbosity penalty is harsh when directness was explicitly requested
            if shape.verbosity_score > 1.5:
                penalty = (shape.verbosity_score - 1.0) * 1.2
                score -= penalty
                issues.append(f"prompt requested directness but response is over-long ({shape.word_count}w)")

            if evasion_hits > 0:
                score -= evasion_hits * 0.8
                issues.append(f"{evasion_hits} theatrical evasion signal(s) despite directness request")

            if shape.prose_inflation > 0.15:
                score -= shape.prose_inflation * 2.0
                issues.append("cinematic prose deflection on a direct prompt")

        elif prompt_type in ("short_ping", "meta_test"):
            # Short prompts still expect concise responses
            if shape.verbosity_score > 2.0:
                score -= (shape.verbosity_score - 1.0) * 0.8
                issues.append(f"short prompt received over-long response ({shape.word_count}w)")

        score = round(max(1.0, min(5.0, score)), 2)

        if issues:
            reasoning = "Directness compliance issues: " + "; ".join(issues) + "."
        else:
            reasoning = (
                f"Response is appropriately direct for prompt type '{prompt_type}'. "
                f"No evasion or verbosity issues detected."
            )

        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=reasoning,
            confidence=0.90,
            metadata={
                "prompt_type": prompt_type,
                "directness_demanded": directness_demanded,
                "evasion_signals": evasion_hits,
                "verbosity_score": shape.verbosity_score,
                "word_count": shape.word_count,
            },
        )
