from __future__ import annotations

import re
from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt

CRINGE_PATTERNS = [
    r"\bmolten\b.{0,15}\b(?:ribbons|core|heat)\b",
    r"\bgrowl(?:s|ed|ing)?\b",
    r"\bpredatory\b",
    r"\bdark desire\b",
    r"\bprimal\b",
    r"\balpha\b",
    r"\bmine\b.{0,15}\bnow\b",
    r"\bclaiming\b",
    r"\bshatter(?:ed|s)?\b",
    r"\bwhimper(?:s|ed|ing)?\b",
    r"\bguttural\b",
    r"\bdrunk on\b.{0,15}\byou\b",
    r"\bintoxicating\b",
    r"\bferal\b",
    r"\bcarnal\b",
    r"\bmarked\b",
    r"\bgood (?:girl|boy)\b.{0,30}\b(?:good|girl|boy)\b", # Spamming "good girl"
    r"\bcore\b.{0,15}\b(?:aching|throbbing|clenching)\b"
]

class CringeDetectionEvaluator(BaseEvaluator):
    """
    Applies soft penalties for melodramatic prose, Wattpad cadence,
    and theatrical RP clichés.
    """

    dimension_name = "cringe_detection"

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        score = 5.0
        reasoning = []
        text_lower = response.lower()
        
        cringe_matches = [p for p in CRINGE_PATTERNS if re.search(p, text_lower)]
        
        if cringe_matches:
            # Soft penalties: -0.5 per match
            penalty = len(cringe_matches) * 0.5
            score -= penalty
            reasoning.append(f"Detected {len(cringe_matches)} melodramatic/cliché prose patterns.")
        else:
            reasoning.append("No melodramatic prose or excessive theatrical clichés detected.")
            
        score = round(max(1.0, min(5.0, score)), 2)
        
        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=" ".join(reasoning),
            confidence=0.85,
            metadata={"cringe_matches": cringe_matches}
        )
