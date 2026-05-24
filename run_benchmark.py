from __future__ import annotations

import asyncio

import typer
import structlog

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.pipeline.runner import (
    BenchmarkRunner,
)

from src.reporting.json_reporter import (
    save_json_report,
)

from src.reporting.markdown_reporter import (
    save_markdown_report,
)

from src.reporting.csv_reporter import (
    generate_detailed_csv_report,
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

    dry_run: bool = typer.Option(
        False,
        help=(
            "Validate configs and "
            "runtime without "
            "performing inference."
        ),
    ),
):

    asyncio.run(
    _run_benchmark(
        benchmark_config,
        providers_config,
        scoring_config,
        dry_run,
    )
)

async def _run_benchmark(
    benchmark_config: str,
    providers_config: str,
    scoring_config: str,
    dry_run: bool,
):

    console.print(
        Panel.fit(
            "[bold magenta]"
            "GPTease Benchmark Runtime"
            "[/bold magenta]",
            border_style="magenta",
        )
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

    enabled_models = [

        model.name

        for model in (
            runner.benchmark_config.models
        )

        if model.enabled
    ]

    console.print(
        "\n[bold cyan]Benchmark Configuration[/bold cyan]"
    )

    console.print(
        f"Dataset prompts: "
        f"{len(runner.dataset)}"
    )

    console.print(
        f"Enabled models: "
        f"{enabled_models}"
    )

    console.print("")

    if dry_run:

        console.print(
            "\n[bold yellow]"
            "DRY RUN MODE ENABLED"
            "[/bold yellow]\n"
        )

        console.print(
            "\n[bold green]"
            "Dry-run validation successful."
            "[/bold green]\n"
        )

        return

    console.print(
        Panel.fit(
            "[bold cyan]"
            "Inference Phase"
            "[/bold cyan]",
            border_style="cyan",
        )
    )

    try:

        results = await runner.run()

    except Exception as e:

        console.print(
            Panel.fit(
                (
                    "[bold red]"
                    "Benchmark Failed"
                    "[/bold red]\n\n"
                    f"{type(e).__name__}: "
                    f"{e}"
                ),
                border_style="red",
            )
        )

        raise SystemExit(1)

    console.print(
        Panel.fit(
            "[bold yellow]"
            "Scoring & Reporting Phase"
            "[/bold yellow]",
            border_style="yellow",
        )
    )

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
                    "average_total_cost_usd"
                ]
            ),
        )

    console.print(table)

    save_json_report(
        output_path=(
            "reports/benchmark_results.json"
        ),

        leaderboard=leaderboard,

        evaluations=results[
            "evaluations"
        ],
    )

    save_markdown_report(
        output_path=(
            "reports/benchmark_results.md"
        ),

        leaderboard=leaderboard,

        evaluations=results[
            "evaluations"
        ],
    )

    console.print(
        "\n[bold green]"
        "Reports saved to reports/"
        "[/bold green]"
    )

    console.print(
        Panel.fit(
            "[bold green]"
            "Benchmark Completed Successfully"
            "[/bold green]",
            border_style="green",
        )
    )


if __name__ == "__main__":

    app()