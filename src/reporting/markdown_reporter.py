from __future__ import annotations

from pathlib import Path

from src.evaluators.base import (
    EvaluationResult,
)


def generate_markdown_report(
    leaderboard: list[dict],
    evaluations: list[EvaluationResult],
) -> str:

    lines = []

    lines.append(
        "# GPTease Benchmark Results\n"
    )

    lines.append(
        "## Leaderboard\n"
    )

    lines.append(
        "| Rank | Model | Judge Model | Score | Avg Latency (ms) | Avg Cost ($) |"
    )

    lines.append(
        "|---|---|---|---|---|---|"
    )

    for idx, entry in enumerate(
        leaderboard,
        start=1,
    ):

        lines.append(
            f"| {idx} "
            f"| {entry['model']} "
            f"| {entry.get('judge_model', 'Unknown')} "
            f"| {entry['average_score']} "
            f"| {entry['average_latency_ms']} "
            f"| {entry['average_total_cost_usd']} |"
        )

    lines.append("\n")

    lines.append(
        "## Evaluation Details\n"
    )

    for evaluation in evaluations:

        lines.append(
            f"### Prompt: "
            f"{evaluation.prompt_id}"
        )

        lines.append(
            f"- Model: "
            f"{evaluation.model}"
        )

        lines.append(
            f"- Provider: "
            f"{evaluation.provider}"
        )

        lines.append(
            f"- Latency: "
            f"{evaluation.metadata.get('latency_ms', 0)} ms"
        )

        lines.append(
            f"- Cost: "
            f"${evaluation.metadata.get('estimated_cost_usd', 0)}"
        )

        lines.append("\n")

        lines.append(
            "#### Dimension Scores"
        )

        lines.append(
            "| Dimension | Score | Reasoning |"
        )

        lines.append(
            "|---|---|---|"
        )

        for score in evaluation.scores:

            lines.append(
                f"| {score.dimension} "
                f"| {score.score} "
                f"| {score.reasoning} |"
            )

        lines.append("\n")

        lines.append(
            "#### Raw Response"
        )

        lines.append("```")

        lines.append(
            evaluation.raw_response
        )

        lines.append("```")

        lines.append("\n---\n")

    return "\n".join(lines)


def save_markdown_report(
    output_path: str,
    leaderboard: list[dict],
    evaluations: list[EvaluationResult],
):

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    markdown = (
        generate_markdown_report(
            leaderboard,
            evaluations,
        )
    )

    with open(output_path, "w") as f:

        f.write(markdown)