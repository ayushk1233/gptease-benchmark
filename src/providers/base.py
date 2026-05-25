from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

from src.config.models import (
    GenerationParams,
    ProviderConfig,
)
load_dotenv()

GENERATION_FAILURE_TYPES = [
    "timeout",
    "empty_stream",
    "provider_error",
    "malformed_chunk",
    "stop_collision",
    "truncated_response",
    "rate_limit",
    "safety_abort",
]

@dataclass
class GenerationResult:
    text: str

    model: str
    provider: str

    prompt_tokens: int
    completion_tokens: int

    latency_ms: float

    estimated_cost_usd: float

    success: bool = True

    error: Optional[str] = None
    
    failure_type: Optional[str] = None
    finish_reason: Optional[str] = None
    partial_generation: bool = False

    retries: int = 0

    raw_response: Optional[dict] = field(
        default=None,
        repr=False,
    )

    @property
    def total_tokens(self) -> int:
        return (
            self.prompt_tokens +
            self.completion_tokens
        )

    @property
    def is_error(self) -> bool:
        return self.error is not None


class BaseProvider(ABC):

    def __init__(
        self,
        config: ProviderConfig,
    ):
        self.config = config
        self._api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        import os

        key = os.getenv(
            self.config.api_key_env
        )

        if not key:
            raise ValueError(
                f"Missing env var: {self.config.api_key_env}"
            )

        return key

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        model: str,
        params: GenerationParams,
    ) -> GenerationResult:
        ...

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> float:

        pricing = (
            self.config.pricing.models.get(model)
            or self.config.pricing.default
        )

        return (
            (
                prompt_tokens / 1000
            ) * pricing.cost_per_1k_input
            +
            (
                completion_tokens / 1000
            ) * pricing.cost_per_1k_output
        )

    async def health_check(self) -> bool:
        try:
            result = await self.generate(
                messages=[
                    {
                        "role": "user",
                        "content": "Hi"
                    }
                ],

                model=(
                    list(
                        self.config.pricing.models.keys()
                    )[0]
                    if self.config.pricing.models
                    else "default"
                ),

                params=GenerationParams(
                    max_tokens=5
                ),
            )

            return not result.is_error

        except Exception:
            return False