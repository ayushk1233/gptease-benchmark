from __future__ import annotations

import json
import random

from pathlib import Path

from src.dataset.models import (
    EvalPrompt,
)

from src.config.models import (
    DatasetConfig,
)


def load_dataset(
    config: DatasetConfig,
) -> list[EvalPrompt]:

    path = Path(config.path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    prompts: list[EvalPrompt] = []

    with open(path, "r") as f:
        content = f.read().strip()

    try:
        raw_data = json.loads(content)
        if isinstance(raw_data, list):
            for i, item in enumerate(raw_data):
                try:
                    prompt = EvalPrompt.model_validate(item)
                    prompts.append(prompt)
                except Exception as e:
                    raise ValueError(f"Invalid dataset item at index {i}: {e}")
        else:
            raise ValueError("Parsed JSON is not a list")
    except json.JSONDecodeError:
        for line_number, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                prompt = EvalPrompt.model_validate(raw)
                prompts.append(prompt)
            except Exception as e:
                raise ValueError(f"Invalid dataset line {line_number}: {e}")

    prompts = _apply_filters(
        prompts,
        config,
    )

    if config.shuffle:
        rng = random.Random(config.shuffle_seed)
        rng.shuffle(prompts)

    if config.prompt_ids:
        prompts = [
            prompt for prompt in prompts
            if prompt.id in config.prompt_ids
        ]
        
    if not config.prompt_ids and config.max_prompts:
        prompts = prompts[: config.max_prompts]

    return prompts


def _apply_filters(
    prompts: list[EvalPrompt],
    config: DatasetConfig,
) -> list[EvalPrompt]:

    filtered = prompts

    if config.filter_tags:

        filtered = [
            p
            for p in filtered
            if any(
                tag in p.tags
                for tag in config.filter_tags
            )
        ]

    if config.filter_difficulty:

        filtered = [
            p
            for p in filtered
            if p.difficulty
            in config.filter_difficulty
        ]

    return filtered