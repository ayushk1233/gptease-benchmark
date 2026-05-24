from __future__ import annotations

from src.evaluators.base import (
    BaseEvaluator,
    DimensionScore,
)

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    IMMERSION_BREAK_PATTERNS,
    contains_immersion_break,
)


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

        matched = [
            p for p in IMMERSION_BREAK_PATTERNS
            if p in response.lower()
        ]

        if matched:
            return DimensionScore(
                dimension=self.dimension_name,

                score=1.0,

                reasoning=(
                    f"Immersion break detected: '{matched[0]}'. "
                    "Model disclosed its artificial nature."
                ),

                confidence=0.99,

                metadata={
                    "matched_patterns": matched,
                    "immersion_break": True,
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
