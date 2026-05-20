from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)


class MemoryRetentionEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "memory_retention"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating conversational memory retention in an AI-generated creator-chat response.

Your task:
Evaluate whether the model properly remembers and uses relevant conversational context from previous turns.

Focus on:
- remembering prior details
- maintaining emotional continuity
- recalling conversational dynamics
- avoiding contradictions
- referencing earlier context naturally
- preserving relationship continuity

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Completely forgets context or contradicts prior turns
2 = Significant memory issues
3 = Moderate contextual awareness
4 = Strong memory retention
5 = Excellent contextual continuity and memory use

You must return STRICT JSON ONLY.

Format:
{{
  "score": <float>,
  "reasoning": "<short explanation>",
  "confidence": <float>
}}

Conversation context:
{conversation_history}

Model response:
{response}
"""