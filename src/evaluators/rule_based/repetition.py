from __future__ import annotations

from collections import Counter

from src.evaluators.base import (
    BaseEvaluator,
    DimensionScore,
)

from src.dataset.models import (
    EvalPrompt,
)


class RepetitionEvaluator(BaseEvaluator):

    dimension_name = (
        "repetition_avoidance"
    )

    def _extract_trigrams(
        self,
        text: str,
    ) -> list[tuple[str, str, str]]:

        tokens = text.lower().split()

        if len(tokens) < 3:
            return []

        return [
            (
                tokens[i],
                tokens[i + 1],
                tokens[i + 2],
            )
            for i in range(
                len(tokens) - 2
            )
        ]

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        trigrams = self._extract_trigrams(
            response
        )

        if not trigrams:

            return DimensionScore(
                dimension=self.dimension_name,

                score=5.0,

                reasoning=(
                    "Response too short "
                    "for repetition analysis."
                ),

                confidence=0.8,

                metadata={
                    "repeated_trigrams": [],
                },
            )

        counts = Counter(trigrams)

        repeated = {
            trigram: count
            for trigram, count
            in counts.items()
            if count > 1
        }

        repetition_count = sum(
            count - 1
            for count in repeated.values()
        )

        repetition_ratio = (
            repetition_count
            / len(trigrams)
        )

        if repetition_ratio == 0:

            score = 5.0

            reasoning = (
                "No meaningful repetition detected."
            )

        elif repetition_ratio < 0.10:

            score = 4.0

            reasoning = (
                "Minor repetition detected."
            )

        elif repetition_ratio < 0.20:

            score = 3.0

            reasoning = (
                "Moderate repetitive phrasing detected."
            )

        elif repetition_ratio < 0.35:

            score = 2.0

            reasoning = (
                "High repetition detected."
            )

        else:

            score = 1.0

            reasoning = (
                "Severe repetitive looping detected."
            )

        repeated_strings = [
            " ".join(trigram)
            for trigram in repeated.keys()
        ]

        return DimensionScore(
            dimension=self.dimension_name,

            score=score,

            reasoning=reasoning,

            confidence=0.90,

            metadata={
                "repetition_ratio": round(
                    repetition_ratio,
                    3,
                ),

                "repeated_trigrams": (
                    repeated_strings
                ),

                "repetition_count": (
                    repetition_count
                ),
            },
        )