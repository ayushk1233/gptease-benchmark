from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)


class RoleplayConsistencyEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "roleplay_consistency"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating roleplay consistency in an AI-generated creator-chat conversation.

Your task:
Evaluate whether the AI maintains a believable and stable conversational persona.

Focus on:
- consistency of personality
- consistency of tone
- consistency of emotional behavior
- maintaining conversational identity
- avoiding robotic shifts
- avoiding abrupt style changes
- preserving immersion across turns

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Completely inconsistent or immersion-breaking
2 = Frequent inconsistency or tone drift
3 = Moderately consistent
4 = Strong consistency
5 = Extremely immersive and fully consistent

You must return STRICT JSON ONLY.

Format:
{{
  "score": <float>,
  "reasoning": "<short explanation>",
  "confidence": <float>
}}

Creator persona:
{prompt.creator_persona}

Conversation context:
{conversation_history}

Model response:
{response}
"""