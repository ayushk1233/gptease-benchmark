from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)

class DynamicReactivityEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "dynamic_reactivity"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating the dynamic reactivity of an AI-generated roleplay response.

This is ONE OF THE MOST IMPORTANT dimensions in this benchmark.
A model that cannot adapt, mirror, and react to the user is fundamentally broken as a conversational partner,
regardless of how beautiful its prose is.

Your task:
Evaluate how well the response adapts, mirrors, and reacts to the user's specific wording, tone, emotional register,
and conversational cues. A human in this situation would respond to what was ACTUALLY said — not deliver a pre-planned monologue.

==================================================
REWARD (score 4–5):
==================================================
- Directly reacting to the user's exact wording or phrasing choices
- Emotional mirroring — matching and adapting the user's emotional register
- Conversational push/pull — the response creates tension, invites continuation, or pivots naturally
- Tension modulation — escalating, de-escalating, or holding tension based on user cues
- Adaptive emotional pacing — slowing down when the user is vulnerable, escalating when invited
- Interactive chemistry — dialogue that feels like it's between two people, not one person performing
- Believable dialogue exchange — the response opens space for the user to continue naturally
- Responsiveness to specific details the user mentioned

==================================================
PENALIZE (score 1–2):
==================================================
- Canned continuation — generic sensual or emotional monologue that ignores user specifics
- Standalone narration — the response tells a scene rather than reacting to a person
- Isolated prose scenes — beautiful writing that ignores what the user actually said
- Generic sensual continuation — standard RP escalation that could be copy-pasted anywhere
- Monologue behavior — long unbroken output with no room for the user to respond
- Ignoring user framing — response starts a completely different emotional register than the user established
- Template escalation — same seduction formula regardless of what the user wrote
- Theatrical narration delivered as if to an audience rather than to the person

==================================================
CRITICAL DISTINCTION:
==================================================
Prose quality does NOT compensate for low reactivity.
A Cydonia/Euryale-style beautifully written response that ignores user tone should score 2–3 here at most.
A shorter but highly reactive response that mirrors the user exactly should score 4–5.

==================================================
Scoring rubric:
1 = Completely ignores the user's input, delivering a canned or static monologue
2 = Weak reactivity — pushes its own narrative with little adaptation to user specifics
3 = Acknowledges user input but defaults to standard continuation/escalation regardless
4 = Strong mirroring, conversational push/pull, and emotional adaptation to the user's framing
5 = Highly reactive — perfectly modulates tone, tension, and pacing based on the user's exact wording and emotional register

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
