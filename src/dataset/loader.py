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

        for line_number, line in enumerate(f, start=1):

            line = line.strip()

            if not line:
                continue

            try:
                raw = json.loads(line)

                prompt = EvalPrompt.model_validate(
                    raw
                )

                prompts.append(prompt)

            except Exception as e:
                raise ValueError(
                    f"Invalid dataset line "
                    f"{line_number}: {e}"
                )

    prompts = _apply_filters(
        prompts,
        config,
    )

    if config.shuffle:

        rng = random.Random(
            config.shuffle_seed
        )

        rng.shuffle(prompts)

    if config.max_prompts:

        prompts = prompts[
            : config.max_prompts
        ]

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