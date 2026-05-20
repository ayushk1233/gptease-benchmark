from __future__ import annotations

import json
import structlog

from abc import ABC
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
                    "You are a strict "
                    "LLM benchmark evaluator."
                ),
            },

            {
                "role": "user",

                "content": judge_prompt,
            },
        ]

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

            log.error(
                "judge_generation_failed",

                dimension=self.dimension_name,

                error=generation.error,
            )

            return DimensionScore(
                dimension=(
                    self.dimension_name
                ),

                score=1.0,

                reasoning=(
                    "Judge model failed."
                ),

                confidence=0.0,

                metadata={
                    "error": (
                        generation.error
                    ),
                },
            )

        try:

            parsed = json.loads(
                generation.text
            )

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

                score=2.0,

                reasoning=(
                    "Judge output parsing failed."
                ),

                confidence=0.2,

                metadata={
                    "raw_output": (
                        generation.text
                    ),
                },
            )