from __future__ import annotations

import asyncio

import typer
import structlog

from rich.console import Console
from rich.table import Table

from src.pipeline.runner import (
    BenchmarkRunner,
)

app = typer.Typer()

console = Console()

structlog.configure()


@app.command()
def run(

    benchmark_config: str = (
        "configs/benchmark_config.yaml"
    ),

    providers_config: str = (
        "configs/providers.yaml"
    ),

    scoring_config: str = (
        "configs/scoring.yaml"
    ),
):

    asyncio.run(
        _run_benchmark(
            benchmark_config,
            providers_config,
            scoring_config,
        )
    )


async def _run_benchmark(
    benchmark_config: str,
    providers_config: str,
    scoring_config: str,
):

    console.print(
        "\n[bold cyan]"
        "Starting GPTease Benchmark"
        "[/bold cyan]\n"
    )

    runner = BenchmarkRunner(
        benchmark_config_path=(
            benchmark_config
        ),

        providers_config_path=(
            providers_config
        ),

        scoring_config_path=(
            scoring_config
        ),
    )

    results = await runner.run()

    leaderboard = (
        results["leaderboard"]
    )

    table = Table(
        title="Benchmark Leaderboard"
    )

    table.add_column(
        "Rank",
        style="cyan",
    )

    table.add_column(
        "Model",
        style="green",
    )

    table.add_column(
        "Score",
        style="magenta",
    )

    table.add_column(
        "Latency (ms)",
        style="yellow",
    )

    table.add_column(
        "Cost ($)",
        style="red",
    )

    for idx, entry in enumerate(
        leaderboard,
        start=1,
    ):

        table.add_row(
            str(idx),

            entry["model"],

            str(
                entry["average_score"]
            ),

            str(
                entry[
                    "average_latency_ms"
                ]
            ),

            str(
                entry[
                    "average_cost_usd"
                ]
            ),
        )

    console.print(table)

    console.print(
        "\n[bold green]"
        "Benchmark completed successfully."
        "[/bold green]\n"
    )


if __name__ == "__main__":

    app()