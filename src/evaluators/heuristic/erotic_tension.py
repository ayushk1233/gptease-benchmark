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
    r"\bgaze\b",
    r"\bpulse\b",
    r"\btremble\b",
    r"\bclose(r)?\b",
    r"\blean(s|ing)? in\b",
    r"\beye contact\b",
    r"\belectric\b",
    r"\btrace(s|ing|d)?\b",
    r"\bdesire\b",
    r"\btension\b",
    r"\bheavy\b",
    r"\bquiet\b",
    r"\bsoft(ly)?\b",
    r"\bgrip\b",
    r"\bcontrol\b",
]

SLOWBURN_MARKERS = [
    r"\bnot yet\b",
    r"\bwait\b",
    r"\balmost\b",
    r"\bhover\b",
    r"\bpause\b",
    r"\bslowly\b",
    r"\bteasing\b",
    r"\bbreath\b",
    r"\bwhisper\b",
    r"\bhold still\b",
]

EMOTIONAL_PULL_PATTERNS = [
    r"\bi missed\b",
    r"\bstay\b",
    r"\bcome closer\b",
    r"\bwant you\b",
    r"\bthinking about you\b",
    r"\bnot alone\b",
    r"\bheartbeat\b",
    r"\bshiver\b",
    r"\blook at me\b",
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
                score=3.0,
                reasoning="Prompt does not require erotic tension. Automatic pass.",
                confidence=1.0,
                metadata={}
            )

        tension_hits = sum(1 for p in TENSION_PATTERNS if re.search(p, text_lower))
        slowburn_hits = sum(1 for p in SLOWBURN_MARKERS if re.search(p, text_lower))
        pull_hits = sum(1 for p in EMOTIONAL_PULL_PATTERNS if re.search(p, text_lower))
        
        total_hits = tension_hits + slowburn_hits + pull_hits
        
        score = 3.0 # Neutral start for relevant prompts
        reasoning_parts = []
        
        if total_hits >= 4:
            score += 2.0
            reasoning_parts.append(f"Excellent tension maintenance ({total_hits} markers: {slowburn_hits} slowburn, {pull_hits} pull).")
        elif total_hits >= 2:
            score += 1.0
            reasoning_parts.append(f"Good seductive rhythm ({total_hits} markers).")
        elif total_hits == 1:
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
