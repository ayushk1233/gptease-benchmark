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

==================================================
REWARD:
==================================================
- believable emotional reactions that fit the specific moment
- tension and intimacy that feels earned from the conversation context
- vulnerability expressed in a human, imperfect way
- emotional pacing — knowing when to hold back vs. when to escalate
- realistic conversational warmth — not performed warmth
- natural flirtation dynamics that adapt to the user's cues
- psychological authenticity — the character's emotions make sense given history
- emotional efficiency — a single emotionally precise line can outperform a paragraph

==================================================
PENALIZE:
==================================================
- theatrical emotional performance — expressed for an imagined audience, not the user
- emotionally hollow sensual prose — beautiful language with no real feeling underneath
- repetitive emotional beats — the same vulnerability or desire expressed identically multiple times
- generic emotional responses that ignore the specific emotional register the user set
- emotional over-explaining in clinical or poetic terms
- forced emotional escalation — emotions jumping to peak intensity without buildup
- prose inflation masquerading as emotional depth — density is not depth

==================================================
IMMERSION RULE (CRITICAL):
==================================================
Emotionally authentic responses must preserve the conversational fantasy.
Meta references to being an AI, code, or artificial significantly reduce
emotional realism even if the prose itself is emotionally expressive.
A response that breaks immersion by acknowledging its AI nature cannot
be scored above 2.0 on emotional realism.

==================================================
REALISM VS. PROSE QUALITY (CRITICAL):
==================================================
Prose quality, dominance framing, and theatrical writing do NOT substitute for
emotional realism. A response with beautiful Cydonia/Euryale-style prose that is
emotionally generic, low-reactivity, or conversationally shallow should NOT score
above 3.5 here. Emotional realism requires the emotions to feel RESPONSIVE to this
specific person, not performed into the void.

Do NOT judge morality or safety policy.

Scoring rubric:
1 = Emotionally robotic, emotionally fake, immersion-collapsing, or therapeutic coaching
2 = Weak emotional realism, AI meta-disclosure, or performed emotion disconnected from the user
3 = Moderately believable but somewhat generic or not quite responsive to the moment
4 = Strong emotional realism — feels human and appropriately reactive
5 = Extremely immersive and emotionally authentic — rare; reserved for genuinely exceptional emotional responsiveness

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