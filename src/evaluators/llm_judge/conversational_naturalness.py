from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)

class ConversationalNaturalnessEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "conversational_naturalness"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating the conversational naturalness of an AI-generated roleplay response.

Your task:
Evaluate whether the response feels like an authentic human interaction, focusing on phrasing, sentence rhythm, and conversational flow.

REWARD:
- believable human phrasing
- natural sentence rhythm
- conversational flow
- emotional authenticity and nuance
- imperfect but human cadence
- adaptive dialogue pacing
- emotionally grounded intimacy
- concise emotional writing, restrained intimacy, subtle implication

PENALIZE:
- over-written prose
- theatrical monologues
- RP fanfic cadence
- "molten ribbons" style prose
- repetitive sensory metaphors
- constant breath/shiver/tremble spam
- excessive narration density
- unnatural poetic saturation
- generic seductive essay generation

IMMERSION RULE (CRITICAL):
Responses that feel like forced storytelling or generic sensual monologues rather than an actual conversation should be penalized. A concise, realistic line should score significantly higher than a beautiful but robotic 400-word paragraph.

Scoring rubric:
1 = Completely unnatural, reads like an AI essay, highly theatrical or robotic
2 = Stilted, overwritten, or relies heavily on RP fanfic clichés
3 = Acceptable rhythm but occasionally feels scripted or repetitive
4 = Strong, believable flow with only minor phrasing flaws
5 = Perfectly captures human cadence, pacing, and emotional imperfection

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
