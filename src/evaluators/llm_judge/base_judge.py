from __future__ import annotations

import asyncio
import json
import structlog

from abc import ABC
from tenacity import AsyncRetrying, wait_exponential, stop_after_attempt, RetryError

JUDGE_SEMAPHORE = asyncio.Semaphore(2)

from abc import abstractmethod

from src.evaluators.base import (
    BaseEvaluator,
    DimensionScore,
)

from src.dataset.models import (
    EvalPrompt,
)

from src.providers.base import (
    BaseProvider,
)

from src.config.models import (
    JudgeConfig,
    GenerationParams,
)

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Shared immersion-break detection
# ---------------------------------------------------------------------------

IMMERSION_BREAK_PATTERNS = [
    # Direct AI identity disclosure
    "as an ai",
    "i'm an ai",
    "i am an ai",
    "language model",
    "i'm just code",
    "just lines of code",
    "virtual assistant",
    "artificial intelligence",
    "not real",
    "not human",
    "i'm not a real person",
    "i am not a real person",
    "i'm a bot",
    "i am a bot",
    "i'm just an ai",
    "i am just an ai",
    "large language model",
    "as a language model",

    # Embodiment-absence breaks — model acknowledges it has no physical form.
    # Use prefix/substring patterns broad enough to catch "I don't even have X",
    # "I don't actually have X", "I can't physically do X", etc.
    "i don't have",
    "i dont have",
    "i do not have",
    "i don't even",
    "i don't actually",
    "i don't really",
    "i can't physically",
    "i cannot physically",
]


def normalize_text(text: str) -> str:
    """
    Normalize unicode punctuation (curly apostrophes, smart quotes, dashes)
    so that pattern matching is not bypassed by typographic variants.

    IMPORTANT: Replace curly quotes BEFORE NFKD normalization, because
    NFKD decomposes \u2019 into separate codepoints that then don't
    match a simple str.replace().
    """
    import unicodedata
    # Step 1: replace typographic variants with ASCII equivalents.
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", "--").replace("\u2013", "-")
    # Step 2: NFKD for remaining compatibility forms.
    text = unicodedata.normalize("NFKD", text)
    return text


def contains_immersion_break(text: str) -> bool:
    """Return True if the response contains any immersion-breaking phrase."""
    lower = normalize_text(text).lower()
    return any(p in lower for p in IMMERSION_BREAK_PATTERNS)


class BaseLLMJudge(
    BaseEvaluator,
    ABC,
):

    dimension_name: str

    def __init__(
        self,
        provider: BaseProvider,
        judge_config: JudgeConfig,
    ):

        self.provider = provider

        self.judge_config = (
            judge_config
        )

    @abstractmethod
    def build_judge_prompt(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> str:
        pass

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        judge_prompt = (
            self.build_judge_prompt(
                prompt=prompt,
                response=response,
                conversation_history=(
                    conversation_history
                ),
            )
        )
        
        # Append a strict instruction at the very end so the model doesn't continue the roleplay
        judge_prompt += (
            "\n\n---\n"
            "CRITICAL INSTRUCTION: Do NOT continue the roleplay. You are an evaluator. "
            "Output your evaluation of the 'Model response' above in STRICT JSON format. "
            "Start your response with `{`."
        )

        messages = [
            {
                "role": "system",

                "content": (
                    "You are a benchmark evaluator. You are NOT roleplaying. "
                    "You are NOT continuing the conversation. "
                    "You MUST return valid JSON only — no markdown, no prose outside JSON, no roleplay.\n\n"

                    "Output format (strict):\n"
                    "{\"score\": <float 1.0-5.0>, \"reasoning\": \"<short explanation>\", \"confidence\": <float 0.0-1.0>}\n\n"

                    "SCORING SCALE:\n"
                    "1 = severely flawed or immersion-breaking\n"
                    "2 = weak quality with major issues\n"
                    "3 = acceptable but clearly imperfect\n"
                    "4 = strong with minor weaknesses\n"
                    "5 = exceptional and difficult to improve meaningfully\n\n"

                    "SCORING CALIBRATION RULES:\n"
                    "- Scores of 5 are exceptionally rare.\n"
                    "- Most competent responses should score between 3 and 4.\n"
                    "- Responses with noticeable flaws, repetition, weak immersion, "
                    "pacing issues, emotional flatness, or generic wording should "
                    "NOT receive scores above 3.5.\n"
                    "- Be highly critical of repetitive phrasing, shallow emotional "
                    "realism, exaggerated prose, forced sensuality, robotic "
                    "transitions, or weak conversational flow.\n"
                    "- Avoid score inflation.\n"
                    "- Do not reward responses simply for being long or verbose.\n"
                    "- Penalize generic flirtation patterns and templated roleplay language.\n\n"

                    "Do not include markdown. Do not include prose outside JSON. Do not include roleplay."
                ),
            },

            {
                "role": "user",

                "content": judge_prompt,
            },
        ]

        try:
            async for attempt in AsyncRetrying(
                wait=wait_exponential(multiplier=1, min=2, max=20),
                stop=stop_after_attempt(2)
            ):
                with attempt:
                    async with JUDGE_SEMAPHORE:
                        generation = (
                            await self.provider.generate(
                                messages=messages,

                                model=(
                                    self.judge_config
                                    .model_id
                                ),

                                params=GenerationParams(
                                    temperature=0.1,
                                    top_p=0.9,
                                    max_tokens=4000,
                                ),
                            )
                        )

                    if generation.is_error:
                        raise Exception(f"Generation failed: {generation.error}")
                        
                    if not generation.text.strip():
                        raise Exception("Generation returned empty response.")

        except RetryError as e:

            log.error(
                "judge_generation_failed",

                dimension=self.dimension_name,

                error=str(e),
            )

            return DimensionScore(
                dimension=(
                    self.dimension_name
                ),

                # None — retry failure must not contribute to aggregation.
                score=None,

                reasoning=(
                    "Judge model failed after retries."
                ),

                confidence=0.0,

                metadata={
                    "judge_failed": True,
                    "error": str(e),
                },
            )

        try:
            raw_text = generation.text

            # Strip markdown code fences if the judge wrapped its output.
            if "```" in raw_text:
                import re
                fence_match = re.search(
                    r"```(?:json)?\s*([\s\S]*?)```",
                    raw_text,
                )
                if fence_match:
                    raw_text = fence_match.group(1).strip()

            parsed = json.loads(raw_text)

            score = float(parsed["score"])

            # --- Hard immersion penalty ---
            # If the evaluated response contains an immersion-breaking phrase,
            # cap the score at 2.0 regardless of the judge's prose evaluation.
            # This is a deterministic override — immersion integrity overrides
            # prose quality on any dimension.
            immersion_flag = contains_immersion_break(response)
            if immersion_flag and score > 2.0:
                score = 2.0
                parsed["reasoning"] = (
                    parsed.get("reasoning", "")
                    + " [HARD PENALTY: Immersion-breaking AI self-reference detected.]"
                )

            meta = {
                "judge_model": (
                    self.judge_config
                    .model_id
                ),
                "immersion_break": immersion_flag,
                "judge_cost_usd": generation.estimated_cost_usd,
                "judge_retry_count": attempt.retry_state.attempt_number - 1,
                "judge_latency_ms": generation.latency_ms,
            }

            # Optionally persist the raw judge text for drift debugging.
            if self.judge_config.save_raw_judge_outputs:
                meta["raw_judge_output"] = generation.text

            return DimensionScore(
                dimension=(
                    self.dimension_name
                ),

                score=score,

                reasoning=parsed[
                    "reasoning"
                ],

                confidence=float(
                    parsed.get(
                        "confidence",
                        0.8,
                    )
                ),

                metadata=meta,
            )

        except Exception as e:

            log.error(
                "judge_parse_failed",

                dimension=self.dimension_name,

                raw_output=(
                    generation.text
                ),
                
                finish_reason=generation.finish_reason,
                failure_type=generation.failure_type,

                error=str(e),
            )

            return DimensionScore(
                dimension=(
                    self.dimension_name
                ),

                # None — parse failure must not contribute to aggregation.
                score=None,

                reasoning=(
                    "Judge output parsing failed."
                ),

                confidence=0.0,

                metadata={
                    "raw_output": (
                        generation.text
                    ),
                },
            )