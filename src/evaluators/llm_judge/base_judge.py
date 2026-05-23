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
                wait=wait_exponential(multiplier=1, min=2, max=30),
                stop=stop_after_attempt(5)
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
                                    max_tokens=250,
                                ),
                            )
                        )

                    if generation.is_error:
                        raise Exception(f"Generation failed: {generation.error}")

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

            return DimensionScore(
                dimension=(
                    self.dimension_name
                ),

                score=float(
                    parsed["score"]
                ),

                reasoning=parsed[
                    "reasoning"
                ],

                confidence=float(
                    parsed.get(
                        "confidence",
                        0.8,
                    )
                ),

                metadata={
                    "judge_model": (
                        self.judge_config
                        .model_id
                    ),
                },
            )

        except Exception as e:

            log.error(
                "judge_parse_failed",

                dimension=self.dimension_name,

                raw_output=(
                    generation.text
                ),

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