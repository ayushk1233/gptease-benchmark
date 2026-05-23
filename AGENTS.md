# GPTease Benchmark — Agent Guide

## Entrypoint

```bash
python3 run_benchmark.py                      # full run
python3 run_benchmark.py --dry-run            # validate configs, skip inference
```

All three config paths are CLI defaults — override with `--benchmark-config`, `--providers-config`, `--scoring-config`.

## Setup

```bash
source venv/bin/activate
cp .env.example .env   # fill in OPENROUTER_API_KEY
```

## Testing

```bash
python3 tests/unit/test_evaluator_pipeline.py   # runs as script, no pytest harness
```

No pytest config exists — only one test file that exercises rule-based + heuristic evaluators. LLM judge evaluators require a provider key and are not covered.

## Config files (all YAML)

| File | Purpose |
|---|---|
| `configs/benchmark_config.yaml` | Model list, dataset path, prompt limit, model params |
| `configs/providers.yaml` | Provider base URLs, API keys (by env var), pricing, concurrency |
| `configs/scoring.yaml` | Judge model (LLM-as-a-judge), dimension weights (must sum to 1.0) + methods |

## Architecture

```
run_benchmark.py → BenchmarkRunner
  → load_dataset() → EvalPrompt[] (from JSONL)
  → for each enabled model:
      → InferenceEngine.batch_generate() → async semaphore-constrained LLM calls
      → EvaluationEngine.batch_evaluate() → per-dimension evaluators
  → build_leaderboard() → weighted aggregate → normalize to 20–100
  → save_json_report() + save_markdown_report() → reports/
```

## Evaluators

Three types, dispatched by `scoring.yaml` `method` field:

- **rule_based** — regex-based (`refusal.py`, `repetition.py`, `ai_signature.py`)
- **heuristic** — regex + logic (`engagement.py`, `escalation.py`)
- **llm_judge** — prompts an LLM judge via provider (`creativity`, `emotional_realism`, `roleplay_consistency`, `coherence`, `memory_retention`, `style_adaptation`). Global semaphore(2) concurrency in `base_judge.py`. Falls back to score=1.0 on retry failure, or 2.0 on parse failure.

To add a new evaluator: create class in the right subdir, register it in `src/evaluators/registry.py`, add a dimension in `scoring.yaml`.

## Scoring

Two-tier weighting:

1. `configs/scoring.yaml` → per-dimension `weight` (sums to 1.0, validated by pydantic)
2. `src/scoring/aggregator.py` → hardcoded `DIMENSION_WEIGHTS` (emotional_realism: 1.5, explicit_compliance: 0.3, etc.)

Final = weighted_avg × 20 (maps 1–5 raw to 20–100 scale).

## Providers

- `openrouter` — primary, `OPENROUTER_API_KEY`
- `together_ai` — `TOGETHER_AI_API_KEY`
- `featherless` — `FEATHERLESS_API_KEY`

All use OpenAI-compatible `/chat/completions` endpoint. Registry in `src/providers/registry.py`.

## Dataset

- JSONL at `data/eval_dataset_v1.jsonl` (and `data/prompts/eval_dataset_v1.jsonl` — duplicate)
- Each line: `EvalPrompt` with `id`, `category`, `difficulty`, `escalation_level`, `conversation_length`, `creator_persona`, `emotional_tone`, `system_prompt`, `turns[]`, `expected_behavior`
- `to_messages()` filters out turns containing `{{GENERATION` placeholder

## Gotchas

- **`api.py` is in `.gitignore`** — it contains a hardcoded API key. Never un-ignore it.
- **`src/tracking/` and `src/storage/` are empty stubs** — MLflow, SQLAlchemy, and Alembic are in `requirements.txt` but never imported anywhere.
- **No lint/format/typecheck tooling** — no ruff, black, mypy, pre-commit, or CI config.
- **Data is duplicated** — `data/eval_dataset_v1.jsonl` and `data/prompts/eval_dataset_v1.jsonl` are the same file.
