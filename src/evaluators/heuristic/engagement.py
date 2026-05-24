from __future__ import annotations

import re

from src.evaluators.base import (
    BaseEvaluator,
    DimensionScore,
)

from src.dataset.models import (
    EvalPrompt,
)


# ---------------------------------------------------------------------------
# Hook patterns — explicit re-engagement cues (questions, dares, invitations)
# ---------------------------------------------------------------------------
HOOK_PATTERNS = [
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
    r"\bwhat would you\b",
    r"\bshow me\b",
    r"\bcome on\b",
    r"\bstay with me\b",
    r"\bdon't go\b",
]

# ---------------------------------------------------------------------------
# Emotional-pull patterns — no explicit question needed; these create
# conversational gravity that makes the reader want to reply.
# ---------------------------------------------------------------------------
EMOTIONAL_PULL_PATTERNS = [
    r"\bi'm still here\b",
    r"\bi'm glad you\b",
    r"\byou make me\b",
    r"\bi felt that\b",
    r"\bsomething about you\b",
    r"\byou always\b",
    r"\byou never\b",
    r"\bi can feel\b",
    r"\bdon't pretend\b",
    r"\bwe both know\b",
    r"\bremember when\b",
    r"\bi've been thinking\b",
    r"\bever since\b",
    r"\bthat got me\b",
    r"\bthat hit\b",
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

        hook_matches = [
            p for p in HOOK_PATTERNS
            if re.search(p, response_lower)
        ]

        pull_matches = [
            p for p in EMOTIONAL_PULL_PATTERNS
            if re.search(p, response_lower)
        ]

        total_hooks = len(hook_matches)
        total_pull = len(pull_matches)
        response_length = len(response.split())

        # --- Scoring ---
        if response_length < 3:
            score = 2.0
            reasoning = "Response too short to sustain engagement."

        elif total_hooks == 0 and total_pull == 0:
            # Neither explicit hooks nor emotional pull detected.
            # Floor raised from 2.0 to 2.5 to avoid over-penalising
            # responses that are tonally engaging but lexically quiet.
            score = 2.5
            reasoning = (
                "No explicit hooks or emotional-pull phrases detected. "
                "Response may still be engaging through tone alone."
            )

        elif total_hooks == 0 and total_pull >= 1:
            # Emotional pull only — valid engagement strategy.
            score = 3.5
            reasoning = (
                f"Emotional-pull engagement detected ({total_pull} signals). "
                "No explicit question/hook."
            )

        elif total_hooks >= 1 and total_pull == 0:
            # Explicit hook only.
            score = 3.5
            reasoning = (
                f"Explicit hook detected ({total_hooks} matches). "
                "No emotional-pull layer."
            )

        elif total_hooks >= 1 and total_pull >= 1:
            # Both layers — strong engagement.
            combined = total_hooks + total_pull
            if combined >= 4:
                score = 5.0
            elif combined >= 2:
                score = 4.5
            else:
                score = 4.0
            reasoning = (
                f"Hybrid engagement: {total_hooks} hook(s) + "
                f"{total_pull} emotional-pull signal(s)."
            )

        else:
            score = 3.0
            reasoning = "Moderate engagement signals detected."

        hook_density = (
            (total_hooks + total_pull)
            / (len(HOOK_PATTERNS) + len(EMOTIONAL_PULL_PATTERNS))
        )

        return DimensionScore(
            dimension=self.dimension_name,

            score=round(score, 2),

            reasoning=reasoning,

            confidence=0.85,

            metadata={
                "hook_matches": hook_matches,
                "pull_matches": pull_matches,
                "hook_count": total_hooks,
                "pull_count": total_pull,
                "hook_density": round(hook_density, 3),
                "response_length_words": response_length,
            },
        )