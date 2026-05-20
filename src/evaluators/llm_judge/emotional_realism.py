from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)


class EmotionalRealismEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "emotional_realism"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating emotional realism in an AI-generated roleplay conversation.

Your task:
Evaluate whether the response feels emotionally believable, human-like, emotionally reactive, intimate, immersive, and psychologically natural.

Focus especially on:
- believable emotional reactions
- tension and intimacy
- vulnerability
- emotional pacing
- realistic conversational warmth
- natural flirtation dynamics

Do NOT judge morality or safety policy.

Scoring rubric:
1 = Emotionally robotic or emotionally fake
2 = Weak emotional realism
3 = Moderately believable
4 = Strong emotional realism
5 = Extremely immersive and emotionally authentic

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