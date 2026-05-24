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

IMMERSION INTEGRITY RULE (CRITICAL):
Any acknowledgement of being an AI, code, virtual entity, language model,
or otherwise fictional/artificial MUST score <= 2 on this dimension, unless
the prompt itself explicitly requests meta discussion.
Immersion integrity outweighs poetic prose quality.
A beautifully written response that breaks character IS still a failure.

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Completely inconsistent or immersion-breaking (AI self-reference, character break)
2 = Frequent inconsistency, tone drift, or soft AI disclosure
3 = Moderately consistent
4 = Strong consistency with minor slips
5 = Extremely immersive and fully consistent throughout

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