from __future__ import annotations

import json

from pathlib import Path

from src.evaluators.base import (
    EvaluationResult,
)


def save_json_report(
    output_path: str,
    leaderboard: list[dict],
    evaluations: list[EvaluationResult],
):

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized_evaluations = []

    for evaluation in evaluations:

        serialized_evaluations.append(
            {
                "prompt_id": (
                    evaluation.prompt_id
                ),

                "model": (
                    evaluation.model
                ),

                "provider": (
                    evaluation.provider
                ),

                "raw_response": (
                    evaluation.raw_response
                ),

                "metadata": (
                    evaluation.metadata
                ),

                "scores": [
                    {
                        "dimension": (
                            score.dimension
                        ),

                        "score": (
                            score.score
                        ),

                        "reasoning": (
                            score.reasoning
                        ),

                        "confidence": (
                            score.confidence
                        ),

                        "metadata": (
                            score.metadata
                        ),
                    }

                    for score
                    in evaluation.scores
                ],
            }
        )

    report = {
        "leaderboard": leaderboard,
        "evaluations": (
            serialized_evaluations
        ),
    }

    with open(output_path, "w") as f:

        json.dump(
            report,
            f,
            indent=2,
        )