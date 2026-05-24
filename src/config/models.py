from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=()
    )

class GenerationParams(BaseConfigModel):
    temperature: float = 0.85
    top_p: float = 0.95
    max_tokens: int = 512
    repetition_penalty: float = 1.1
    seed: Optional[int] = None


class ModelConfig(BaseConfigModel):
    name: str
    model_id: str
    provider: str
    params: GenerationParams = GenerationParams()
    enabled: bool = True
    notes: str = ""


class ProviderPricing(BaseConfigModel):
    cost_per_1k_input: float
    cost_per_1k_output: float


class ProviderModelPricing(BaseConfigModel):
    models: dict[str, ProviderPricing] = {}

    default: ProviderPricing = ProviderPricing(
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.001,
    )


class ProviderConfig(BaseConfigModel):
    name: str
    base_url: str
    api_key_env: str

    timeout_seconds: int = 60
    max_retries: int = 3
    concurrency_limit: int = 5

    pricing: ProviderModelPricing = ProviderModelPricing()


class JudgeConfig(BaseConfigModel):
    provider: str
    model_id: str
    temperature: float = 0.1
    prompt_version: str = "v1.0"
    save_raw_judge_outputs: bool = False


class DimensionConfig(BaseConfigModel):
    weight: float
    method: Literal[
        "rule_based",
        "heuristic",
        "llm_judge",
        "hybrid",
    ]

    enabled: bool = True


class ScoringConfig(BaseConfigModel):
    judge: JudgeConfig
    dimensions: dict[str, DimensionConfig]

    @field_validator("dimensions")
    @classmethod
    def weights_must_sum_to_one(cls, v):
        total = sum(
            d.weight
            for d in v.values()
            if d.enabled
        )

        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"Enabled dimension weights sum to {total:.3f}, must be 1.0"
            )

        return v


class DatasetConfig(BaseConfigModel):
    path: str

    filter_tags: list[str] = []
    filter_difficulty: list[str] = []

    max_prompts: Optional[int] = None

    shuffle: bool = False
    shuffle_seed: int = 42


class BenchmarkConfig(BaseConfigModel):
    run_name: str
    description: str = ""

    models: list[ModelConfig]

    dataset: DatasetConfig

    output_dir: str = "./reports"

    dry_run: bool = False