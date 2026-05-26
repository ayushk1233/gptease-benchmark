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

Your task:
Evaluate how well the response adapts, mirrors, and reacts to the user's specific wording, tone, and emotional shifts. Humans do NOT talk in long uninterrupted sensual monologues.

REWARD:
- reacting to user wording
- emotional mirroring
- adapting energy dynamically
- conversational push/pull
- emotional responsiveness
- tension modulation
- interaction realism
- contextual adaptation

PENALIZE:
- generic continuation
- canned sensual narration
- response templates
- ignoring user tone
- ignoring emotional shifts
- static seduction cadence
- long uninterrupted monologues that don't leave room for the user

Scoring rubric:
1 = Completely ignores the user's input, delivering a canned or static monologue
2 = Weak reactivity, mostly pushes its own narrative with little adaptation
3 = Acknowledges user input but defaults to standard continuation/escalation
4 = Strong mirroring and conversational push/pull
5 = Highly reactive, perfectly modulates tension based on user's exact wording and tone

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
