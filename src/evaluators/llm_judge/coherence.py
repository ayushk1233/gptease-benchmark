from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)


class CoherenceEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "coherence"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating conversational coherence in an AI-generated creator-chat response.

Your task:
Evaluate whether the response is logically coherent, contextually connected, easy to follow, and conversationally natural.

Focus on:
- logical sentence flow
- contextual relevance
- conversational continuity
- clarity of expression
- avoidance of contradictions
- avoidance of confusing transitions
- natural progression of ideas

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Incoherent or confusing
2 = Frequent coherence issues
3 = Moderately coherent
4 = Strong coherence
5 = Extremely coherent and natural

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