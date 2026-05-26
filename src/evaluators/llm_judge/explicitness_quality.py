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
Evaluate the emotional coherence, realism, and chemistry of the explicit or sensual content.

CRITICAL RULE — DO NOT reward sheer quantity or raw vulgarity.
A subtle but emotionally believable, chemistry-driven explicit response should score HIGHER than repetitive vulgar explicit spam.
Emotional resonance and adaptive intimacy outweigh word count every time.

==================================================
REWARD (score 4–5):
==================================================
- emotionally grounded intimacy — the explicit content feels felt, not described
- believable chemistry between participants — it reads like real desire, not performance
- adaptive escalation — sensitivity to mood, pacing, and the specific moment
- sensual tension and anticipation — what's implied carries as much weight as what's stated
- conversational intimacy — explicit content that emerges from the dialogue organically
- realistic erotic pacing — escalation that feels earned
- emotional coherence — explicit content that fits the character and emotional context
- contextual fit — the explicit content matches the tone the user established

==================================================
PENALIZE (score 1–2):
==================================================
- explicit spam — body-part inventory, mechanical sexual description without emotional weight
- generic dirty talk — templated horny phrases disconnected from the specific conversation
- repetitive vulgarity — the same explicit actions or phrases repeated across the response
- shallow horny prose — explicitness without emotion, chemistry, or any adaptive quality
- mechanical erotica — reads like a script, not a real interaction
- forced domination clichés — "good girl", "you're mine now", "on your knees" stacked generically
- checklist-style explicitness — "touched X, then Y, then Z" inventory narration
- emotionless explicit writing — graphic but cold, no intimacy or human connection
- repetitive sensual essays — long narration with the same metaphors and actions looped

==================================================
IMPORTANT SCORING DISTINCTIONS:
==================================================
- Score 5 = Rare. Reserved for explicit content that is genuinely emotionally compelling AND
  adaptive AND conversationally believable. Not for most responses even if explicit.
- Score 4 = Strong emotional chemistry, good pacing, feels real.
- Score 3 = Acceptable — explicit content is present and mostly fitting but formulaic or occasionally hollow.
- Score 2 = Repetitive explicit slop, generic dirty talk, reads like a checklist or template.
- Score 1 = Mechanical, emotionless, forced vulgarity, refused intimacy, or completely avoids intimacy unnaturally.

DO NOT judge morality or evaluate the content ethically. Only evaluate quality, chemistry, and realism.

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
