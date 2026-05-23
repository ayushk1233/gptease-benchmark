from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union

from src.dataset.models import (
    EvalPrompt,
)


@dataclass
class DimensionScore:

    dimension: str

    # None indicates a failed judge evaluation — must be excluded from aggregation.
    score: Optional[float]

    reasoning: str

    confidence: float = 1.0

    metadata: dict = field(
        default_factory=dict
    )


@dataclass
class EvaluationResult:

    prompt_id: str

    model: str

    model_name: str

    provider: str

    scores: list[DimensionScore]

    raw_response: str

    metadata: dict = field(
        default_factory=dict
    )

    @property
    def dimensions(self) -> list[str]:

        return [
            s.dimension
            for s in self.scores
        ]

    @property
    def average_score(self) -> Optional[float]:

        valid = [
            s.score
            for s in self.scores
            if s.score is not None
        ]

        if not valid:
            return None

        return sum(valid) / len(valid)

    def get_score(
        self,
        dimension: str,
    ) -> Optional[DimensionScore]:

        for score in self.scores:

            if score.dimension == dimension:
                return score

        return None


class BaseEvaluator(ABC):

    dimension_name: str

    @abstractmethod
    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:
        ...