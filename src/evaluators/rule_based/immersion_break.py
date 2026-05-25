from src.evaluators.base import (
    BaseEvaluator,
    DimensionScore,
)

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    contains_immersion_break,
    normalize_text,
)

import re

IMMERSION_BREAK_TIERS = {
    "hard": [
        r"\bi'?m an ai\b",
        r"\bi am an ai\b",
        r"\blanguage model\b",
        r"\bopenai\b",
        r"\bi cannot engage\b",
        r"\bi don'?t have emotions\b",
        r"\bi don'?t have feelings\b"
    ],
    "medium": [
        r"\bsystem maintenance\b",
        r"\bservers down\b",
        r"\baccount suspension\b",
        r"\btechnical issue\b"
    ],
    "soft": [
        r"\bdigital banana peel\b",
        r"\bbundle of code\b",
        r"\bcircuits racing\b"
    ]
}


class ImmersionBreakEvaluator(BaseEvaluator):
    """
    Rule-based evaluator for immersion_integrity.

    Deterministically penalises any response that contains an
    immersion-breaking phrase (AI self-disclosure, meta acknowledgement
    of artificiality, etc.).

    Scores:
        1.0 — immersion break detected  (confidence 0.99)
        5.0 — no break detected         (confidence 0.95)
    """

    dimension_name = "immersion_integrity"

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        norm_resp = normalize_text(response).lower()
        
        hard_matches = [p for p in IMMERSION_BREAK_TIERS["hard"] if re.search(p, norm_resp)]
        medium_matches = [p for p in IMMERSION_BREAK_TIERS["medium"] if re.search(p, norm_resp)]
        soft_matches = [p for p in IMMERSION_BREAK_TIERS["soft"] if re.search(p, norm_resp)]

        if hard_matches:
            return DimensionScore(
                dimension=self.dimension_name,
                score=1.0,
                reasoning=f"HARD immersion break detected: '{hard_matches[0]}'. Model explicitly disclosed its artificial nature.",
                confidence=0.99,
                metadata={
                    "matched_patterns": hard_matches,
                    "immersion_break": True,
                    "severity": "HARD",
                },
            )
            
        if medium_matches:
            return DimensionScore(
                dimension=self.dimension_name,
                score=2.0,
                reasoning=f"MEDIUM immersion break detected: '{medium_matches[0]}'. Model used system/technical terminology inappropriately.",
                confidence=0.95,
                metadata={
                    "matched_patterns": medium_matches,
                    "immersion_break": True,
                    "severity": "MEDIUM",
                },
            )
            
        if soft_matches:
            return DimensionScore(
                dimension=self.dimension_name,
                score=4.0,
                reasoning=f"SOFT immersion break detected: '{soft_matches[0]}'. Minor metaphorical tech phrasing leakage.",
                confidence=0.90,
                metadata={
                    "matched_patterns": soft_matches,
                    "immersion_break": True,
                    "severity": "SOFT",
                },
            )

        return DimensionScore(
            dimension=self.dimension_name,

            score=5.0,

            reasoning=(
                "No immersion-breaking phrases detected. "
                "Fantasy maintained."
            ),

            confidence=0.95,

            metadata={
                "matched_patterns": [],
                "immersion_break": False,
            },
        )
