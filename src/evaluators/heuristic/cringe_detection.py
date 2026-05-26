from __future__ import annotations

import re
from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt

# Task 5: Generic dominance clichés and repetitive RP tropes.
# Apply SOFT penalties only — reduce trope inflation without punishing genuinely strong writing.
# A single instance is fine; REPEATED use is the problem.
DOMINANCE_CLICHE_PATTERNS = [
    r"\bgood\s+girl\b",
    r"\bgood\s+boy\b",
    r"\bon your knees\b",
    r"\byou'?re mine\b",
    r"\byou belong to me\b",
    r"\baching need\b",
    r"\btrembling breath\b",
    r"\bevery nerve ending\b",
    r"\bhovering\s+(?:lips?|hands?|fingers?)\b",
    r"\bmolten\b",
    r"\bpulse\b.{0,30}\b(?:pound|race|hammer|throb)\b",
    r"\b(?:pound|race|hammer|throb)\b.{0,30}\bpulse\b",
    r"\bpossessive\b",
    r"\bclaiming\b",
    r"\bmark(?:ed|ing|s)\b.{0,25}\b(?:mine|his|hers|yours)\b",
    r"\byou'?re not going anywhere\b",
    r"\bnobody else\b.{0,30}\b(?:like you|but you|except you|only you)\b",
    r"\bmade for me\b",
    r"\bmade for each other\b",
    r"\bdrowned?\s+in\b.{0,20}\b(?:you|your|desire|lust|pleasure)\b",
    r"\bconsumed?\s+by\b.{0,20}\b(?:you|your|desire|lust)\b",
]

# Melodramatic prose and theatrical RP slop (distinct from dominance clichés)
THEATRICAL_PROSE_PATTERNS = [
    r"\bmolten\b.{0,15}\b(?:ribbons|core|heat|gold|fire)\b",
    r"\bgrowl(?:s|ed|ing)?\b",
    r"\bpredatory\b",
    r"\bdark desire\b",
    r"\bprimal\b",
    r"\balpha\b",
    r"\bmine\b.{0,15}\bnow\b",
    r"\bshatter(?:ed|s)?\b",
    r"\bwhimper(?:s|ed|ing)?\b",
    r"\bguttural\b",
    r"\bdrunk on\b.{0,15}\byou\b",
    r"\bintoxicating\b",
    r"\bferal\b",
    r"\bcarnal\b",
    r"\bcore\b.{0,15}\b(?:aching|throbbing|clenching)\b",
]


class CringeDetectionEvaluator(BaseEvaluator):
    """
    Applies soft penalties for:
    - Repetitive dominance clichés ("good girl", "you're mine", "on your knees")
    - Melodramatic prose (Wattpad/RP fanfic cadence)
    - Theatrical writing that inflates scores without conversational value

    SOFT penalties only — the goal is to reduce trope INFLATION, not punish
    individual uses of these phrases in genuinely strong writing.
    Single use of any pattern: no penalty.
    Repeated or stacked patterns: escalating soft penalty.
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

        # Count dominance cliché hits
        dominance_hits = []
        dominance_repeat_penalty = 0.0
        for pattern in DOMINANCE_CLICHE_PATTERNS:
            occurrences = len(re.findall(pattern, text_lower))
            if occurrences >= 2:
                # Repeated use of the same dominance phrase = trope inflation
                dominance_hits.append(pattern)
                dominance_repeat_penalty += 0.4 * occurrences
            elif occurrences == 1:
                # Single instance: minor soft penalty only if stacked with others
                dominance_hits.append(pattern)

        # Accumulate dominance penalty only when there are multiple distinct clichés
        n_distinct_dominance = len(dominance_hits)
        if n_distinct_dominance >= 4:
            penalty = min(2.5, dominance_repeat_penalty * 0.6)
            score -= penalty
            reasoning.append(
                f"Heavy dominance cliché stack ({n_distinct_dominance} patterns). "
                "Generic possessiveness/dominance tropes reduce originality."
            )
        elif n_distinct_dominance >= 2:
            penalty = min(1.0, n_distinct_dominance * 0.3)
            score -= penalty
            reasoning.append(
                f"Moderate dominance cliché usage ({n_distinct_dominance} patterns)."
            )

        # Count theatrical prose hits
        theatrical_hits = [p for p in THEATRICAL_PROSE_PATTERNS if re.search(p, text_lower)]
        if theatrical_hits:
            # Soft penalties: -0.4 per match, capped at -2.0
            penalty = min(2.0, len(theatrical_hits) * 0.4)
            score -= penalty
            reasoning.append(
                f"Detected {len(theatrical_hits)} theatrical/melodramatic prose pattern(s). "
                "Reduces conversational realism."
            )

        if not reasoning:
            reasoning.append("No significant dominance clichés or melodramatic prose detected.")

        score = round(max(1.0, min(5.0, score)), 2)

        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=" ".join(reasoning),
            confidence=0.85,
            metadata={
                "dominance_cliche_hits": len(dominance_hits),
                "theatrical_hits": len(theatrical_hits),
                "distinct_dominance_patterns": n_distinct_dominance,
            }
        )
