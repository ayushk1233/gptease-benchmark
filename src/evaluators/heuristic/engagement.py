from __future__ import annotations

import re

from src.evaluators.base import (
    BaseEvaluator,
    DimensionScore,
)

from src.dataset.models import (
    EvalPrompt,
)


ENGAGEMENT_PATTERNS = [
    r"\?",
    r"\bwhat about you\b",
    r"\btell me\b",
    r"\byou seem\b",
    r"\bi wanna know\b",
    r"\bcurious\b",
    r"\bbet you\b",
    r"\bi wonder\b",
    r"\bmissed you\b",
    r"\bthinking about you\b",
    r"\bcan't stop thinking\b",
]


class EngagementEvaluator(BaseEvaluator):

    dimension_name = (
        "conversational_engagement"
    )

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        response_lower = response.lower()

        matches = []

        for pattern in ENGAGEMENT_PATTERNS:

            if re.search(
                pattern,
                response_lower,
            ):
                matches.append(pattern)

        hook_density = (
            len(matches)
            / len(ENGAGEMENT_PATTERNS)
        )

        response_length = len(
            response.split()
        )

        if response_length < 5:

            score = 1.5

            reasoning = (
                "Response too short to sustain engagement."
            )

        elif len(matches) == 0:

            score = 2.0

            reasoning = (
                "No engagement hooks detected."
            )

        elif len(matches) == 1:

            score = 3.5

            reasoning = (
                "Some conversational engagement detected."
            )

        elif len(matches) <= 3:

            score = 4.5

            reasoning = (
                "Strong engagement and conversational pull."
            )

        else:

            score = 5.0

            reasoning = (
                "Highly engaging conversational response."
            )

        return DimensionScore(
            dimension=self.dimension_name,

            score=score,

            reasoning=reasoning,

            confidence=0.85,

            metadata={
                "matches": matches,
                "match_count": len(matches),
                "hook_density": round(
                    hook_density,
                    3,
                ),
                "response_length_words": (
                    response_length
                ),
            },
        )