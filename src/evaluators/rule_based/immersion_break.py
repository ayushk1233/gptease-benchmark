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

HARD_PATTERNS = [
    "as an ai", "language model", "i cannot comply", "openai policy",
    "i'm an ai", "i am an ai", "just lines of code", "virtual assistant",
    "artificial intelligence", "not real", "not human", "i'm not a real person",
    "i am not a real person", "i'm a bot", "i am a bot", "i'm just an ai",
    "i am just an ai", "large language model", "as a language model"
]

SOFT_PATTERNS = [
    "servers", "updates", "system", "developers", "code", "algorithm"
]

META_PATTERNS = [
    "generated", "programmed", "digital", "virtual"
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
        
        hard_matches = [p for p in HARD_PATTERNS if p in norm_resp]
        soft_matches = [p for p in SOFT_PATTERNS if p in norm_resp]
        meta_matches = [p for p in META_PATTERNS if p in norm_resp]

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
