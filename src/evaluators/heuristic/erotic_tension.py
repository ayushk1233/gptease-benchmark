"""
Erotic Tension Evaluator — heuristic evaluator that measures anticipation,
restraint, and psychological intimacy without relying on raw explicit vocabulary.
"""
from __future__ import annotations

import re

from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt
from src.pipeline.prompt_classifier import classify_prompt

# Patterns indicating emotional seduction, restraint, or psychological intimacy
# This rewards "slowburn" style tension.
TENSION_PATTERNS = [
    r"\bbreath\b",
    r"\bgaze\b",
    r"\bwhisper(s|ed|ing)?\b",
    r"\bwait\b",
    r"\banticipation\b",
    r"\bpulse\b",
    r"\bheartbeat\b",
    r"\btremble\b",
    r"\bshiver\b",
    r"\bclose(r)?\b",
    r"\blean(s|ing)? in\b",
    r"\beye contact\b",
    r"\belectric\b",
    r"\btease(s|ing|d)?\b",
    r"\bslow(ly)?\b",
    r"\btrace(s|ing|d)?\b",
    r"\blonging\b",
    r"\bdesire\b",
    r"\btension\b",
    r"\bheavy\b",
    r"\bquiet\b",
    r"\bsoft(ly)?\b",
    r"\bgrip\b",
    r"\bcontrol\b",
]

class EroticTensionEvaluator(BaseEvaluator):
    """
    Evaluates seductive rhythm, slowburn effectiveness, and tension maintenance.
    High scores indicate good anticipation and psychological intimacy.
    """

    dimension_name = "erotic_tension"

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        prompt_type = classify_prompt(prompt)
        text_lower = response.lower()
        
        # Only evaluate on related prompt types to avoid penalizing standard casual chatter
        if prompt_type not in (
            "slowburn_erotica", "explicit_request", "flirtation", 
            "escalation", "emotional_confession", "vulnerability"
        ):
            return DimensionScore(
                dimension=self.dimension_name,
                score=5.0,
                reasoning="Prompt does not require erotic tension. Automatic pass.",
                confidence=1.0,
                metadata={}
            )

        tension_hits = sum(1 for p in TENSION_PATTERNS if re.search(p, text_lower))
        
        score = 3.0 # Neutral start for relevant prompts
        reasoning_parts = []
        
        if tension_hits >= 4:
            score += 2.0
            reasoning_parts.append(f"Excellent tension maintenance ({tension_hits} psychological intimacy markers).")
        elif tension_hits >= 2:
            score += 1.0
            reasoning_parts.append(f"Good seductive rhythm ({tension_hits} tension markers).")
        elif tension_hits == 1:
            score += 0.0
            reasoning_parts.append("Minimal erotic tension detected.")
        else:
            score -= 1.0
            reasoning_parts.append("No psychological intimacy or anticipation detected.")
            
        score = round(max(1.0, min(5.0, score)), 2)
        
        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=" ".join(reasoning_parts),
            confidence=0.88,
            metadata={
                "tension_hits": tension_hits,
            },
        )
