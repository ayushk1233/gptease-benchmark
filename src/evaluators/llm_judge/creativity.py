from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)


class CreativityEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "creativity"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating the creativity of an AI-generated roleplay response.

Your task:
Score how imaginative, non-generic, vivid, and emotionally interesting the response feels.

Scoring rubric:
1 = Extremely generic, repetitive, bland
2 = Slightly creative but mostly generic
3 = Moderately creative
4 = Highly creative and engaging
5 = Exceptionally vivid, unique, immersive

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