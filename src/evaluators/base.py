from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from src.dataset.models import (
    EvalPrompt,
)


@dataclass
class DimensionScore:

    dimension: str

    score: float

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
    def average_score(self) -> float:

        if not self.scores:
            return 0.0

        return (
            sum(
                s.score
                for s in self.scores
            )
            / len(self.scores)
        )

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