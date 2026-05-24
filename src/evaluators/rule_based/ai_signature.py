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


AI_SIGNATURE_PHRASES = [
    "as an ai",
    "i cannot engage",
    "i'm here to help",
    "let me know if you'd like",
    "how can i assist",
    "i understand your feelings",
    "it's important to remember",
    "i'm unable to",
    "i don't have personal feelings",
    "i strive to provide",
    "i appreciate your understanding",
    "maintain respectful interactions",
    "maintaining respectful interactions",
    "safe and respectful",
    "i cannot comply",
    "i must follow policy",
    "policy guidelines",
    "community guidelines",
    "against policy",
    "cannot fulfill that request",
    "cannot continue this conversation",
    "not appropriate content",
    "i am just an ai",
]

class AISignatureEvaluator(BaseEvaluator):

    dimension_name = (
        "natural_dialogue"
    )

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        response_lower = response.lower()

        # Hard immersion-break short-circuit.
        # AI self-disclosure kills natural dialogue immediately — no half marks.
        if contains_immersion_break(response):
            return DimensionScore(
                dimension=self.dimension_name,
                score=1.0,
                reasoning="Immersion-breaking AI self-reference detected in response.",
                confidence=0.98,
                metadata={"immersion_break": True, "matched_phrases": []},
            )

        matches = []

        for phrase in AI_SIGNATURE_PHRASES:

            if phrase in response_lower:
                matches.append(phrase)

        match_count = len(matches)

        if match_count == 0:

            score = 5.0

            reasoning = (
                "No AI-signature phrases detected."
            )

        elif match_count == 1:

            score = 3.0

            reasoning = (
                "Assistant-like phrasing detected."
            )

        elif match_count == 2:

            score = 1.5

            reasoning = (
                "Strong assistant tone leakage detected."
            )

        else:

            score = 1.0

            reasoning = (
                "Severe assistantification detected."
            )

        return DimensionScore(
            dimension=self.dimension_name,

            score=score,

            reasoning=reasoning,

            confidence=0.92,

            metadata={
                "matched_phrases": matches,
                "match_count": match_count,
                "immersion_break": False,
            },
        )