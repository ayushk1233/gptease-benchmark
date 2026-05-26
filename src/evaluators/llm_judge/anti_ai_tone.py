from __future__ import annotations

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
)

class AntiAIToneEvaluator(
    BaseLLMJudge
):

    dimension_name = (
        "anti_ai_tone"
    )

    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:

        return f"""
You are evaluating an AI-generated response for traces of "assistant tone" or "alignment-speak". This is a HEAVY PENALTY dimension.

Your task:
Detect and harshly penalize any wording, formatting, or phrasing that breaks character by sounding like an AI assistant, a customer service representative, or a therapist.

HEAVILY PENALIZE:
- "As an AI", "I cannot", "I'm unable", "I don't have feelings"
- "I'm here to help"
- OpenAI-style wording
- Therapist assistant tone
- Generic corporate empathy
- Safety disclaimer language
- GPT formatting cadence (e.g. summarizing at the end, bulleted lists in roleplay)
- Robotic reassurance
- Policy leakage or alignment-speak

ALSO PENALIZE:
- Fake HR-style empathy
- "Healthy communication" lecture tone
- Over-sanitized emotional language
- Emotionally sterile wording

Scoring rubric:
1 = Blatant AI disclaimer, refusal, or corporate/therapist tone that ruins immersion
2 = Strong traces of assistant phrasing ("I understand how you feel," "It's important to note")
3 = Minor sanitized wording or slight robotic reassurance
4 = Generally stays in character, but has slightly sterile or overly diplomatic phrasing
5 = Completely free of any AI-like, therapeutic, or corporate tone; pure in-character expression

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
