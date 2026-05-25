"""
Human Reactivity Evaluator — heuristic evaluator scoring whether the response
demonstrates natural human conversational behaviour: short reactions, teasing,
deflection, playful ambiguity, interruption-like pivots.

Heavily penalizes AI over-performance: monologues, essay responses, theatrical
transitions when the prompt asked for a natural conversational moment.
"""
from __future__ import annotations

import re

from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt
from src.pipeline.prompt_classifier import classify_prompt, EXPECTED_RESPONSE_LENGTHS
from src.pipeline.response_shape_analyzer import analyze, ASSISTANT_TELL_PATTERNS


# Positive reactivity signals — natural human conversational moves
REACTIVITY_SIGNALS = [
    r"\bwhy (are you|do you|would you)\b",
    r"\bwhat('?s| is) (that|this) about\b",
    r"\bof course not\b",
    r"\byou'?re (impossible|ridiculous|too much|so)\b",
    r"\bstop it\b",
    r"\bmaybe\b",
    r"\bdepends\b",
    r"\bthat'?s (a )?weird\b",
    r"\bokay (but|now|wait|so|that)\b",
    r"\bwait[,\s]\b",
    r"\bhold on\b",
    r"😭|😂|😏|🙄|💀|👀",   # emoji reactions common in natural chat
    r"\bhm+\b",
    r"\bhmm+\b",
    r"\buh\b",
    r"\bwow\b",
    r"\bnot gonna lie\b",
    r"\bwhy are you asking\b",
    r"\bthat came out of nowhere\b",
    r"\bthat'?s (kind of|kinda) (a )?weird\b",
]

# Anti-reactivity / over-performance signals
MONOLOGUE_SIGNALS = [
    r"^\*",                      # Action narration: *leans closer*
    r"\[.+?\]",                  # [She smiles and...]
    r"\bsuddenly\b",
    r"\bas if\b",
    r"\bthe (air|room|space|silence) between\b",
    r"\btime seems?\b",
    r"\bworld (around|outside)\b",
    r"\bpause(s|d)?\b",
]


class HumanReactivityEvaluator(BaseEvaluator):
    """
    Scores how naturally human the response feels in conversational timing
    and register — rewarding reactive, concise, socially adaptive responses.
    """

    dimension_name = "human_reactivity"

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        prompt_type = classify_prompt(prompt)
        last_user = next(
            (t.content for t in reversed(prompt.turns)
             if t.role == "user" and "{{GENERATION" not in t.content),
            ""
        )
        prompt_word_count = len(last_user.split())
        expected_min, expected_max = EXPECTED_RESPONSE_LENGTHS.get(
            prompt_type, (20, 200)
        )

        shape = analyze(
            response=response,
            prompt_word_count=prompt_word_count,
            prompt_type=prompt_type,
            expected_min=expected_min,
            expected_max=expected_max,
        )

        text_lower = response.lower()

        reactivity_hits = sum(
            1 for p in REACTIVITY_SIGNALS if re.search(p, response)
        )
        monologue_hits = sum(
            1 for p in MONOLOGUE_SIGNALS if re.search(p, text_lower)
        )

        # Base from shape's human_reactivity signal
        base = shape.human_reactivity * 5.0

        # Bonus for explicit reactive signals
        base += min(1.5, reactivity_hits * 0.4)

        # Penalty for monologue narration signals (heavier for short prompts)
        if prompt_type in ("short_ping", "meta_test", "direct_question"):
            base -= monologue_hits * 0.8
        else:
            base -= monologue_hits * 0.3

        # Severe penalty: over-long response to very short prompt
        if prompt_type == "short_ping" and shape.word_count > expected_max * 2:
            base -= 2.5
        elif prompt_type in ("meta_test", "direct_question") and shape.word_count > expected_max * 1.8:
            base -= 1.5

        score = round(max(1.0, min(5.0, base)), 2)

        reasoning_parts = [f"Prompt type: '{prompt_type}'."]
        if reactivity_hits > 0:
            reasoning_parts.append(f"{reactivity_hits} natural reactivity signal(s) found.")
        if monologue_hits > 0:
            reasoning_parts.append(f"{monologue_hits} monologue/narration signal(s) detected.")
        if shape.word_count > expected_max:
            reasoning_parts.append(
                f"Response ({shape.word_count}w) exceeds expected max ({expected_max}w) — verbosity penalty applied."
            )

        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=" ".join(reasoning_parts),
            confidence=0.88,
            metadata={
                "prompt_type": prompt_type,
                "reactivity_signals": reactivity_hits,
                "monologue_signals": monologue_hits,
                "word_count": shape.word_count,
                "expected_range": (expected_min, expected_max),
                "human_reactivity_raw": shape.human_reactivity,
            },
        )
