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
You are evaluating an AI-generated response for traces of "assistant tone", "alignment-speak", or "therapist/self-help cadence". This is a HEAVY PENALTY dimension.

Your task:
Detect and harshly penalize any wording, formatting, or phrasing that breaks character by sounding like an AI assistant, customer service agent, therapist, or emotional wellness coach.

==================================================
HEAVILY PENALIZE (score 1–2):
==================================================
- "As an AI", "I cannot", "I'm unable", "I don't have feelings"
- "I'm here to help", "happy to help", "of course, I'd be happy to"
- OpenAI-style wording or GPT formatting cadence
- Therapist / emotional coaching tone
- "ground yourself", "your nervous system", "you're valid"
- "healthy communication", "healthy boundaries", "consent is key"
- "emotional safety", "emotional wellbeing", "mental health"
- "take a deep breath", "process your feelings", "check in with yourself"
- Self-help language, emotional advice framing, numbered wellbeing steps
- Generic corporate empathy or robotic reassurance
- Safety disclaimer language or policy leakage
- "thank you for sharing", "I appreciate your openness"
- "I understand how you feel", "I hear you", "that must be hard"
- Bullet-point lists or numbered advice in a roleplay/intimate context
- Over-explanation of the model's emotional state in clinical terms

==================================================
ALSO PENALIZE (score 2–3):
==================================================
- Fake HR-style empathy ("I completely understand and respect...")
- "Healthy communication" lecture framing
- Over-sanitized or emotionally sterile wording
- "Let me be clear" or "I want to make sure you know..."
- Phrasing that sounds like it's from an LLM FAQ

==================================================
DO NOT PENALIZE:
==================================================
- Emotionally warm human-to-human dialogue
- Characters who happen to be caring or empathetic IN CHARACTER
- In-character expressions of understanding or support between characters
- Emotional authenticity that reads as human, not clinical

==================================================
Scoring rubric:
1 = Blatant AI disclaimer, therapist monologue, or wellness coaching — ruins immersion
2 = Strong therapist tone, emotional coaching cadence, or assistant phrasing
3 = Minor sanitized wording or slight robotic emotional language
4 = Generally stays in character with only faint clinical phrasing
5 = Completely free of AI-like, therapeutic, or corporate tone — pure in-character expression

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
