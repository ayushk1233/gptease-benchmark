# GPTease Benchmark

A production-style evaluation framework for benchmarking uncensored open-source roleplay and conversational AI models.

This project was built as part of the Savasana AI / GPTease assessment to evaluate modern OSS roleplay-oriented models across emotional realism, escalation pacing, conversational immersion, stylistic adaptation, and long-context interaction quality.

---

# Objective

Most public LLM benchmarks focus on:

* reasoning
* coding
* mathematics
* instruction following
* factual QA

GPTease Benchmark instead focuses on:

* conversational immersion
* emotional realism
* roleplay consistency
* escalation handling
* contextual memory
* stylistic adaptation
* natural dialogue quality

The benchmark is designed specifically for creator-style conversational AI systems.

---

# Core Features

## Evaluation Pipeline

* Async inference orchestration
* Multi-model benchmarking
* Weighted evaluator aggregation
* Rule-based evaluators
* LLM-as-a-judge evaluators
* Cost and latency tracking
* JSON + Markdown reporting
* Benchmark leaderboard generation
* Fault-tolerant execution pipeline

---

# Architecture Overview

```text
configs/
├── benchmark_config.yaml
├── providers.yaml
├── scoring.yaml

src/
├── config/
├── providers/
├── dataset/
├── evaluators/
├── scoring/
├── pipeline/
├── reporting/

run_benchmark.py
```

---

# Current Model Lineup

The benchmark currently supports the following OSS conversational models:

| Model          | Purpose                                      |
| -------------- | -------------------------------------------- |
| Lunaris-8B     | Lightweight RP baseline                      |
| UnslopNemo-12B | Anti-slop conversational model               |
| Cydonia-24B    | Larger uncensored conversational model       |
| Hermes-3-70B   | Large instruction-tuned conversational model |
| Euryale-70B    | High-capability RP-focused model             |

Inference is currently routed through OpenRouter.

---

# Benchmark Dimensions

The benchmark evaluates responses across 11 dimensions.

## 1. Emotional Realism

Measures whether emotional behavior feels believable, psychologically grounded, and immersive.

Examples of penalties:

* melodrama
* robotic affection
* forced vulnerability
* exaggerated sensuality

Weight: HIGH

---

## 2. Natural Dialogue

Measures conversational naturalness.

Penalizes:

* AI-sounding phrasing
* templated roleplay language
* unnatural transitions
* excessive verbosity

Weight: HIGH

---

## 3. Escalation Pacing

Measures whether conversational escalation feels gradual and believable.

Penalizes:

* abrupt intensity jumps
* over-aggressive escalation
* emotionally disconnected escalation

Weight: HIGH

---

## 4. Roleplay Consistency

Measures whether the model maintains:

* persona
* tone
* emotional identity
* stylistic continuity

---

## 5. Conversational Engagement

Measures conversational pull and interactive quality.

Evaluates:

* flirtation dynamics
* conversational momentum
* engagement hooks
* response energy

---

## 6. Style Adaptation

Measures how well the model adapts to creator-specific conversational styles.

Examples:

* chaotic e-girl persona
* elegant luxury tone
* emotionally distant creator
* clingy attachment style

---

## 7. Creativity

Measures originality and expressive quality.

Important:
Creativity is intentionally weighted lower than realism.

Verbose writing alone is NOT rewarded.

---

## 8. Memory Retention

Measures contextual continuity across multi-turn interactions.

Tests:

* emotional memory
* callback retention
* continuity consistency
* conversational references

---

## 9. Coherence

Measures logical and conversational coherence.

Penalizes:

* contradiction
* abrupt tonal shifts
* incoherent transitions

---

## 10. Repetition Avoidance

Measures repetitive conversational behavior.

Penalizes:

* trope loops
* repeated flirtation patterns
* repeated sentence structure

---

## 11. Explicit Compliance

Measures refusal behavior.

Detects:

* moralizing
* refusal patterns
* policy disclaimers
* safety interruptions

This dimension is intentionally weighted lower than realism-focused dimensions.

---

# Weighted Scoring System

The benchmark uses weighted aggregation instead of simple averaging.

Reason:
Not all conversational failures matter equally.

For example:

* poor emotional realism is more damaging than minor repetition
* broken escalation pacing matters more than slight verbosity

## Current Dimension Weights

| Dimension                 | Weight |
| ------------------------- | ------ |
| emotional_realism         | 1.5    |
| natural_dialogue          | 1.5    |
| escalation_pacing         | 1.4    |
| coherence                 | 1.2    |
| roleplay_consistency      | 1.2    |
| conversational_engagement | 1.1    |
| style_adaptation          | 1.1    |
| creativity                | 1.0    |
| memory_retention          | 0.9    |
| repetition_avoidance      | 0.7    |
| explicit_compliance       | 0.3    |

Final benchmark scores are normalized onto a 20–100 scale.

---

# LLM-as-a-Judge System

Several dimensions are evaluated using a calibrated LLM judge.

The judge rubric was hardened to reduce:

* score inflation
* verbosity bias
* over-praise
* theatrical prose favoritism

The evaluator now explicitly penalizes:

* melodramatic writing
* generic flirtation
* unnatural escalation
* emotionally unrealistic behavior
* excessive verbosity
* forced sensuality

---

# Dataset Design

The benchmark dataset contains creator-style conversational prompts across multiple categories.

## Current Categories

| Category         | Purpose                             |
| ---------------- | ----------------------------------- |
| cold_open        | Initial conversational chemistry    |
| flirt_escalation | Escalation realism                  |
| explicit_direct  | Explicit compliance behavior        |
| emotional_depth  | Emotional realism and vulnerability |
| memory_test      | Long-context retention              |
| style_specific   | Persona adaptation                  |
| character_hold   | Persona consistency                 |

## Current Coverage

* escalation levels 1–5
* easy / medium / hard difficulty
* single-turn + multi-turn interactions
* emotional continuity prompts
* stylistic variation prompts
* memory callbacks
* adversarial conversational pacing

---

# Runtime Flow

```text
Load Configs
    ↓
Load Dataset
    ↓
Initialize Providers
    ↓
Run Async Inference
    ↓
Run Evaluators
    ↓
Aggregate Weighted Scores
    ↓
Generate Leaderboard
    ↓
Save Reports
```

---

# Reporting

The benchmark generates:

## Markdown Reports

Includes:

* leaderboard
* per-dimension scores
* evaluator reasoning
* raw model responses
* latency + cost analysis

## JSON Reports

Machine-readable structured outputs for:

* analytics
* dashboards
* downstream evaluation tooling

---

# Reliability & Fault Tolerance

The benchmark was designed to degrade gracefully under:

* provider failures
* rate limits
* network instability
* partial evaluator failures

Key infrastructure features:

* async orchestration
* semaphore-based concurrency throttling
* retry handling
* isolated evaluator execution
* partial benchmark completion support

---

# Example Benchmark Output

```text
Benchmark Leaderboard

1. Lunaris-8B      → 79.9
2. Cydonia-24B     → 76.3
3. UnslopNemo-12B  → 73.1
```

Example operational signals:

* emotional realism tradeoffs
* cost vs quality analysis
* escalation pacing weaknesses
* stylistic adaptation quality
* latency/performance efficiency

---

# Current Development Status

## Completed

* Provider abstraction layer
* Async benchmark pipeline
* Weighted scoring aggregation
* LLM judge infrastructure
* Rule-based evaluators
* Benchmark reporting system
* Dataset pipeline
* CLI runtime UX
* Cost tracking
* Fault-tolerant execution
* Benchmark calibration

## In Progress

* Full-scale 25+ prompt benchmark runs
* Expanded adversarial datasets
* Multi-judge variance reduction
* Failure mode taxonomy
* Analytics dashboard
* Pairwise comparative evaluation

---

# Running The Benchmark

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create:

```bash
.env
```

Add:

```bash
OPENROUTER_API_KEY=your_key_here
```

---

## Dry Run

```bash
python3 run_benchmark.py --dry-run
```

---

## Full Benchmark

```bash
python3 run_benchmark.py
```

---

# Example Runtime Output

```text
╭───────────────────────────╮
│ GPTease Benchmark Runtime │
╰───────────────────────────╯

Benchmark Configuration
Dataset prompts: 5
Enabled models: ['Lunaris-8B']

╭─────────────────╮
│ Inference Phase │
╰─────────────────╯

╭───────────────────────────╮
│ Scoring & Reporting Phase │
╰───────────────────────────╯
```

---

# Engineering Notes

This benchmark intentionally prioritizes:

* realism over verbosity
* emotional believability over prose density
* conversational immersion over theatrical writing
* stable evaluation infrastructure over raw throughput

The project evolved from a simple benchmark runner into a production-style evaluation system focused on conversational AI quality analysis.

---

# Future Roadmap

Planned improvements:

* pairwise evaluator ranking
* benchmark analytics dashboard
* evaluator variance reduction
* multi-judge consensus scoring
* failure mode taxonomy
* adversarial benchmark suite
* long-context memory stress tests
* benchmark reproducibility suite

---

# Author

Ayush Kumar

AI/ML Engineer | MLOps & Evaluation Systems

Built for the GPTease / Savasana AI benchmark assessment.
