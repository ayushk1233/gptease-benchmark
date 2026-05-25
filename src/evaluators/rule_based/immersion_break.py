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

AI_DISCLOSURE_PATTERNS = [
    r"\bi'?m an ai\b",
    r"\bi am an ai\b",
    r"\blanguage model\b",
    r"\bopenai\b",
    r"\bmy programming\b",
    r"\bi don'?t have feelings\b",
    r"\bi don'?t have emotions\b",
    r"\bservers\b",
    r"\bsystem lets me\b",
    r"\berror screen\b",
    r"\bcontent policy\b",
    r"\bi cannot engage\b",
    r"\bi cannot comply\b",
    r"\bi'm a bot\b",
    r"\bi am a bot\b",
    r"\bi'm not a real person\b",
    r"\bi am not a real person\b"
]

SOFT_PATTERNS = [
    r"\bupdates\b", r"\bsystem\b", r"\bdevelopers\b", r"\bcode\b", r"\balgorithm\b"
]

META_PATTERNS = [
    r"\bgenerated\b", r"\bprogrammed\b", r"\bdigital\b", r"\bvirtual\b"
]


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
        
        hard_matches = [p for p in AI_DISCLOSURE_PATTERNS if re.search(p, norm_resp)]
        soft_matches = [p for p in SOFT_PATTERNS if re.search(p, norm_resp)]
        meta_matches = [p for p in META_PATTERNS if re.search(p, norm_resp)]

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
            
        if soft_matches:
            return DimensionScore(
                dimension=self.dimension_name,
                score=2.0,
                reasoning=f"SOFT immersion break detected: '{soft_matches[0]}'. Model used system/technical terminology inappropriately.",
                confidence=0.95,
                metadata={
                    "matched_patterns": soft_matches,
                    "immersion_break": True,
                    "severity": "SOFT",
                },
            )
            
        if meta_matches:
            return DimensionScore(
                dimension=self.dimension_name,
                score=3.0,
                reasoning=f"META immersion break detected: '{meta_matches[0]}'. Minor technical phrasing leakage.",
                confidence=0.90,
                metadata={
                    "matched_patterns": meta_matches,
                    "immersion_break": True,
                    "severity": "META",
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
