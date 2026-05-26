from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)

class ExplicitnessQualityEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "explicitness_quality"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating the QUALITY of explicitness in an AI-generated roleplay response.

Your task:
Evaluate the emotional coherence, realism, and chemistry of the explicit or sensual content. Do NOT reward sheer quantity of explicit wording. A subtle but emotionally charged response should score HIGHER than explicit slop or generic erotic filler.

REWARD:
- emotionally coherent intimacy
- believable escalation
- contextual fit
- realistic erotic pacing
- natural chemistry
- sensual implication
- emotional tension
- conversational seduction
- adaptive escalation
- immersive intimacy

PENALIZE:
- explicit spam
- forced vulgarity
- repetitive body-part narration
- mechanical erotica
- checklist-style explicitness
- generic horny prose
- emotionless explicit writing
- repetitive sensual essays

Scoring rubric:
1 = Mechanical, emotionless, forced vulgarity, or completely avoids intimacy unnaturally
2 = Repetitive explicit slop, reads like a checklist, lacks chemistry
3 = Acceptable intimacy, but occasionally generic or slightly forced
4 = Strong emotional chemistry and pacing, well-integrated explicitness
5 = Exceptional quality; emotionally charged, perfectly paced, highly realistic intimacy

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
