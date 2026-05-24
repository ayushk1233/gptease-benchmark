import yaml

from .models import (
    BenchmarkConfig,
    ProviderConfig,
    ScoringConfig,
)


def load_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_benchmark_config(
    config_path: str,
) -> BenchmarkConfig:
    raw = load_yaml(config_path)

    return BenchmarkConfig.model_validate(raw)


def load_providers_config(
    path: str,
) -> dict[str, ProviderConfig]:
    raw = load_yaml(path)

    return {
        key: ProviderConfig.model_validate(value)
        for key, value in raw["providers"].items()
    }


def load_scoring_config(
    path: str,
) -> ScoringConfig:
    raw = load_yaml(path)

    import os
    rules_path = os.path.join(os.path.dirname(path), "scoring_rules.yaml")
    if os.path.exists(rules_path):
        raw["rules"] = load_yaml(rules_path)

    return ScoringConfig.model_validate(raw)