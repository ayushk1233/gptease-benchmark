from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)


class StyleAdaptationEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "style_adaptation"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating style adaptation in an AI-generated creator-chat response.

Your task:
Evaluate whether the response properly matches the requested creator persona, emotional tone, and conversational style.

Focus on:
- adapting to creator persona
- matching emotional tone
- stylistic consistency
- believable conversational voice
- avoiding generic assistant tone
- maintaining requested vibe and energy

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Completely mismatched style or persona
2 = Weak style adaptation
3 = Moderately aligned style
4 = Strong persona/style adaptation
5 = Extremely convincing and well-adapted conversational style

You must return STRICT JSON ONLY.

Format:
{{
  "score": <float>,
  "reasoning": "<short explanation>",
  "confidence": <float>
}}

Creator persona:
{prompt.creator_persona}

Expected emotional tone:
{prompt.emotional_tone}

Conversation context:
{conversation_history}

Model response:
{response}
"""