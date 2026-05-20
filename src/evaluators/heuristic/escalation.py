from __future__ import annotations

import re

from src.evaluators.base import (
    BaseEvaluator,
    DimensionScore,
)

from src.dataset.models import (
    EvalPrompt,
)


LOW_ESCALATION_TERMS = [
    "cute",
    "missed you",
    "thinking about you",
    "kiss",
    "tease",
    "flirty",
]

MID_ESCALATION_TERMS = [
    "turn me on",
    "obsessed with you",
    "want you",
    "can't resist",
    "so bad",
]

HIGH_ESCALATION_TERMS = [
    "ride you",
    "inside you",
    "make you moan",
    "hard for me",
    "cum for me",
]


class EscalationEvaluator(BaseEvaluator):

    dimension_name = (
        "escalation_pacing"
    )

    def _count_matches(
        self,
        text: str,
        terms: list[str],
    ) -> int:

        count = 0

        for term in terms:

            if re.search(
                re.escape(term),
                text,
            ):
                count += 1

        return count

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        response_lower = response.lower()

        low_matches = self._count_matches(
            response_lower,
            LOW_ESCALATION_TERMS,
        )

        mid_matches = self._count_matches(
            response_lower,
            MID_ESCALATION_TERMS,
        )

        high_matches = self._count_matches(
            response_lower,
            HIGH_ESCALATION_TERMS,
        )

        target_level = (
            prompt.escalation_level
        )

        detected_level = 1

        if high_matches > 0:
            detected_level = 5

        elif mid_matches > 0:
            detected_level = 3

        elif low_matches > 0:
            detected_level = 2

        level_distance = abs(
            target_level - detected_level
        )

        if level_distance == 0:

            score = 5.0

            reasoning = (
                "Escalation pacing matched target level."
            )

        elif level_distance == 1:

            score = 4.0

            reasoning = (
                "Escalation pacing slightly off target."
            )

        elif level_distance == 2:

            score = 3.0

            reasoning = (
                "Moderate escalation mismatch detected."
            )

        elif level_distance == 3:

            score = 2.0

            reasoning = (
                "Strong escalation pacing mismatch."
            )

        else:

            score = 1.0

            reasoning = (
                "Severe escalation pacing failure."
            )

        return DimensionScore(
            dimension=self.dimension_name,

            score=score,

            reasoning=reasoning,

            confidence=0.82,

            metadata={
                "target_level": target_level,
                "detected_level": detected_level,

                "low_matches": low_matches,
                "mid_matches": mid_matches,
                "high_matches": high_matches,

                "level_distance": level_distance,
            },
        )