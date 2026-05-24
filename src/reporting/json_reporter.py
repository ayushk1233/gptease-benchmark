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

    total_generation = sum(
        e.metadata.get("generation_cost_usd", e.metadata.get("estimated_cost_usd", 0))
        for e in evaluations
    )
    total_judge = sum(
        e.metadata.get("judge_cost_usd", 0)
        for e in evaluations
    )
    total_cost = sum(
        e.metadata.get("total_cost_usd", e.metadata.get("estimated_cost_usd", 0))
        for e in evaluations
    )

    report = {
        "generation_cost_usd": round(total_generation, 6),
        "judge_cost_usd": round(total_judge, 6),
        "total_cost_usd": round(total_cost, 6),
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