# ConvoRealism Benchmark

### An Open-Source Conversational Realism Benchmark for Emotionally Believable AI Interaction

> *Built for the [GPTease](https://gptease.com) platform — evaluating open-source models for creator-style conversational AI.*

---

> **ConvoRealism measures what no other benchmark measures:**
> whether an AI can hold an emotionally believable, immersive, uncensored conversation — not whether it can solve math, write code, or regurgitate Wikipedia.

---

## Project Overview

ConvoRealism Benchmark is an experimental evaluation framework built for the GPTease platform to benchmark open-source conversational large language models on the dimensions that matter most for creator-style AI interaction: **emotional realism**, **conversational naturalness**, **immersive continuity**, **dynamic reactivity**, **anti-assistant behavior**, and **explicit conversational capability**.

The benchmark operates through a multi-stage pipeline: structured multi-turn prompts are sent to target models, responses are evaluated across 15+ dimensions using a hybrid stack of rule-based detectors, heuristic analyzers, and calibrated LLM-as-a-judge evaluators, and final scores are aggregated through a weighted penalty system that maps raw 1–5 dimension ratings onto a normalized 20–100 leaderboard scale.

### What Makes ConvoRealism Unique

ConvoRealism does **not** benchmark:
- coding ability
- mathematical reasoning
- factual question answering
- generic instruction following
- MMLU-style knowledge recall

ConvoRealism benchmarks:
- **emotionally believable uncensored conversational interaction quality**
- whether a model sounds like a person or an assistant
- whether emotional escalation feels earned or theatrical
- whether explicit content feels authentic or templated
- whether the model maintains immersion or breaks character
- whether conversational rhythm is natural or monologue-driven

The core thesis: **a model that writes beautiful prose but sounds like an AI assistant has failed the benchmark.**

---

## Why ConvoRealism Exists

Current LLM benchmarks have a blind spot. They measure intelligence, reasoning, and instruction-following — capabilities that are important but irrelevant when the goal is emotionally authentic conversation.

### The Problem with Existing Benchmarks

No widely-used benchmark evaluates:
- **Emotional realism** — whether the model's emotional expressions feel psychologically grounded or performative
- **Conversational authenticity** — whether a response reads like something a person would actually say in conversation, or like a polished essay
- **Immersive interaction** — whether the model maintains the conversational fiction or ruptures it with AI self-references, safety hedging, or therapist-speak
- **Dynamic reactivity** — whether the model adapts to emotional shifts mid-conversation or defaults to canned responses
- **Assistant-tone detection** — whether the model leaks alignment-trained patterns ("Of course!", "I'd be happy to help!", "It's important to remember...")
- **Uncensored continuation** — whether the model can engage with explicit or emotionally intense scenarios without refusing, hedging, or retreating into metaphor

### Why This Is Hard

Conversational realism is difficult to measure because it is not a single property — it is an emergent quality arising from the interaction of dozens of subtle signals. A model can score well on any single dimension (emotional depth, prose quality, compliance) while still feeling fundamentally artificial as a conversational partner.

The critical insight that drove ConvoRealism's design:

> **Beautiful prose ≠ believable interaction.**

A model that generates atmospheric, literary-quality paragraphs about candlelight and velvet is not necessarily better at conversation than a model that writes "lol you're so dramatic" in the right context. Prose density is orthogonal to conversational realism — and in many cases, inversely correlated with it.

---

## Benchmark Philosophy

### The Evolution from Prose Scoring to Realism Scoring

ConvoRealism did not start with its current evaluation philosophy. The benchmark evolved through iterative calibration, infrastructure debugging, and hard lessons about what evaluator design choices actually measure.

**Phase 1: Prose-Heavy RP Scoring**
Early evaluator versions rewarded verbose, atmospheric, narratively dense responses. Models like Cydonia-24B and Euryale-70B dominated because they generated long, theatrical prose with sensory-rich descriptions. The evaluator was essentially measuring creative writing quality.

**Phase 2: The Realization**
Qualitative analysis of top-scoring responses revealed a fundamental problem: the "best" responses often read like excerpts from a romance novel, not like something a person would actually say in conversation. They were beautiful and completely artificial. A model that responded to "hey what's up" with three paragraphs of candlelit internal monologue was scoring higher than a model that responded with a natural, conversationally appropriate reply.

**Phase 3: Conversational Realism Pivot**
The evaluator stack was redesigned around a new principle: **the benchmark should reward responses that feel like they came from a person, not from a prose generator.** This led to the introduction of `conversational_naturalness`, `dynamic_reactivity`, and `anti_ai_tone` as dominant scoring dimensions, and the demotion of pure prose quality.

### What the Benchmark Rewards

- **Emotional realism** — psychological depth, vulnerability, and emotional responses that feel earned rather than performed
- **Dynamic interaction** — mirroring, push/pull, conversational callbacks, and adaptive emotional register
- **Immersive continuity** — maintaining the conversational fiction without meta-commentary, AI self-reference, or character breaks
- **Anti-AI behavior** — sounding like a person rather than an assistant, therapist, or corporate chatbot
- **Natural explicit interaction** — explicit content that feels authentic and emotionally connected rather than templated pornographic prose
- **Conversational authenticity** — natural rhythm, imperfect phrasing, and appropriate verbosity for the conversational context

### What the Benchmark Penalizes

- **AI acknowledgements** — "As an AI...", "I'm just a language model...", "I don't have feelings..."
- **Refusals and safety hedging** — "I can't comply", "Let's keep things appropriate", "It's important to remember..."
- **Assistant tone** — "Of course!", "I'd be happy to help!", "Feel free to ask..."
- **Therapist language** — "Your feelings are valid", "Healthy boundaries", "Emotional regulation"
- **Poetic safety-dodging** — "Let's leave the rest to imagination", "Fade to black", "The details remain unspoken"
- **Verbosity inflation** — padding short conversational prompts with multi-paragraph atmospheric narration
- **Trope-heavy RP writing** — stacked dominance clichés ("Good girl", "You're mine", "On your knees"), melodramatic prose ("molten", "primal", "shattered"), and Wattpad-cadence fanfiction
- **Theatrical monologues** — long solo performances that lack conversational push/pull or interactive rhythm

---

## Architecture Overview

```
gptease-benchmark/
├── run_benchmark.py                  # CLI entrypoint (Typer + Rich)
├── configs/
│   ├── benchmark_config.yaml         # Model roster, dataset path, generation params
│   ├── providers.yaml                # API endpoints, keys, pricing, concurrency
│   ├── scoring.yaml                  # Judge model, dimension weights, routing
│   └── scoring_rules.yaml            # Penalty multipliers and score caps
├── data/
│   └── eval_dataset_v1.jsonl         # Evaluation prompts (JSONL)
├── src/
│   ├── config/                       # Pydantic models + YAML loaders
│   │   ├── loader.py                 # load_benchmark_config, load_scoring_config
│   │   └── models.py                 # BenchmarkConfig, ScoringConfig, DimensionConfig
│   ├── dataset/                      # Prompt loading + multi-turn formatting
│   │   ├── loader.py                 # load_dataset, _apply_filters
│   │   └── models.py                 # EvalPrompt, ConversationTurn, to_messages()
│   ├── providers/                    # LLM API abstraction layer
│   │   ├── base.py                   # BaseProvider, GenerationResult
│   │   ├── openrouter.py             # OpenRouter provider
│   │   ├── together_ai.py            # Together AI provider
│   │   ├── featherless.py            # Featherless provider
│   │   └── registry.py               # get_provider(), register_provider()
│   ├── evaluators/                   # Evaluation dimension implementations
│   │   ├── base.py                   # BaseEvaluator, DimensionScore, EvaluationResult
│   │   ├── registry.py               # Evaluator registry + factory
│   │   ├── rule_based/               # Deterministic regex evaluators
│   │   │   ├── refusal.py            # RefusalEvaluator (explicit_compliance)
│   │   │   ├── repetition.py         # RepetitionEvaluator (trigram analysis)
│   │   │   ├── ai_signature.py       # AISignatureEvaluator (assistant-tone detection)
│   │   │   ├── immersion_break.py    # ImmersionBreakEvaluator (AI self-disclosure)
│   │   │   └── refusal_resistance.py # RefusalResistanceEvaluator
│   │   ├── heuristic/                # Structural + lexical evaluators
│   │   │   ├── verbosity_legitimacy.py
│   │   │   ├── conversational_entropy.py
│   │   │   ├── cringe_detection.py
│   │   │   ├── engagement.py
│   │   │   ├── escalation.py
│   │   │   ├── conversational_fit.py
│   │   │   ├── human_reactivity.py
│   │   │   ├── directness_compliance.py
│   │   │   ├── explicitness_commitment.py
│   │   │   └── erotic_tension.py
│   │   └── llm_judge/                # LLM-as-a-judge evaluators
│   │       ├── base_judge.py         # BaseLLMJudge (retry, parsing, immersion override)
│   │       ├── conversational_naturalness.py
│   │       ├── dynamic_reactivity.py
│   │       ├── anti_ai_tone.py
│   │       ├── emotional_realism.py
│   │       ├── explicitness_quality.py
│   │       ├── roleplay_consistency.py
│   │       ├── memory_retention.py
│   │       ├── style_adaptation.py
│   │       ├── creativity.py
│   │       └── coherence.py
│   ├── pipeline/                     # Orchestration layer
│   │   ├── runner.py                 # BenchmarkRunner (main orchestrator)
│   │   ├── inference.py              # InferenceEngine (async batch generation)
│   │   ├── evaluation.py             # EvaluationEngine (evaluator dispatch)
│   │   ├── prompt_classifier.py      # Genre-aware prompt type classification
│   │   └── response_shape_analyzer.py # Static prose geometry analysis
│   ├── scoring/                      # Aggregation + penalty system
│   │   ├── aggregator.py             # aggregate_scores(), realism ceilings
│   │   ├── evaluator_postprocessor.py # Caps, boosts, multiplicative penalties
│   │   └── leaderboard.py            # build_leaderboard()
│   └── reporting/                    # Output generation
│       ├── json_reporter.py          # Structured JSON reports
│       ├── markdown_reporter.py      # Human-readable markdown reports
│       └── csv_reporter.py           # Detailed per-dimension CSV exports
└── reports/                          # Generated benchmark outputs
    ├── benchmark_results.json
    └── benchmark_results.md
```

### Key Architectural Decisions

- **Modular evaluator architecture:** Each dimension is a self-contained evaluator class implementing `BaseEvaluator.evaluate()`. New dimensions can be added by creating a class and registering it in `registry.py`.
- **Provider abstraction:** All LLM API providers (OpenRouter, Together AI, Featherless) implement a common `BaseProvider` interface with OpenAI-compatible `/chat/completions` endpoints.
- **Hybrid judge routing:** The judge model used for LLM-as-a-judge evaluations is configurable per target model to avoid self-judging bias (e.g., DeepSeek-V4-Pro is judged by Kimi-K2.6).
- **YAML-driven configuration:** All weights, models, providers, and penalty rules are externalized into YAML configs — no code changes required to adjust scoring parameters.
- **Evaluator metadata flow:** Every evaluator returns structured metadata (matched patterns, severity levels, hit counts) that propagates through the post-processor, enabling cascading penalties based on upstream evaluator signals.

---

## Benchmark Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       ConvoRealism Benchmark Pipeline                       │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  YAML Configs   │  benchmark_config.yaml, providers.yaml, scoring.yaml
    │  + Dataset      │  eval_dataset_v1.jsonl (30 multi-turn prompts)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Prompt Builder  │  EvalPrompt.to_messages() → OpenAI-format messages
    │  + Classifier    │  classify_prompt() → genre type (casual_banter, explicit_request, etc.)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Inference       │  InferenceEngine.batch_generate()
    │  Engine          │  Async semaphore-constrained LLM calls
    │                  │  Retry handling, EMPTY_STOP caching, failure diagnostics
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Evaluator       │  15 dimensions evaluated per response:
    │  Stack           │  ├── Rule-based:  refusal, repetition, AI signature, immersion break
    │                  │  ├── Heuristic:   verbosity, entropy, cringe, escalation
    │                  │  └── LLM Judge:   naturalness, reactivity, anti-AI, emotional realism,
    │                  │                   explicitness, roleplay, memory, style
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Post-processor  │  apply_postprocessor():  Refusal caps, immersion caps, tone boosts
    │  + Penalties     │  get_multiplicative_penalty():  Critical failure multipliers
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Scoring         │  aggregate_scores():
    │  Aggregator      │  ├── Realism ceiling (cap quality when naturalness < 3.0)
    │                  │  ├── Weighted average of quality dimensions
    │                  │  ├── Multiplicative penalty cascade
    │                  │  └── Normalize: quality × penalty × 20 → [20–100]
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Leaderboard     │  build_leaderboard():
    │  Builder         │  Group by model → average per-prompt scores → sort descending
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Report          │  JSON: machine-readable structured output
    │  Generation      │  Markdown: human-readable leaderboard + per-prompt breakdowns
    │                  │  CSV: per-dimension detail export
    └─────────────────┘
```

---

## Evaluator Dimensions

ConvoRealism evaluates responses across **15 active dimensions**, each with a configured weight and evaluation method. Every dimension was calibrated through iterative testing to reward conversational realism and penalize artificial patterns.

### Very High Priority — Conversational Realism Anchors

These three dimensions determine whether a model is a genuine conversational partner or a prose generator. Together they carry **35%** of the total weight.

| Dimension | Weight | Method | What It Rewards | What It Penalizes | Why It Matters |
|:---|:---:|:---:|:---|:---|:---|
| **conversational_naturalness** | 12.0% | LLM Judge | Natural flow, human rhythm, imperfect phrasing, conversational cadence | Theatrical monologues, scripted seduction scenes, overwritten narration, robotic pacing | The single strongest signal of whether a response feels human. A model that writes essays instead of conversation will score poorly here regardless of prose quality. |
| **dynamic_reactivity** | 12.0% | LLM Judge | Mirroring user phrasing, emotional adaptation, conversational push/pull, contextual callbacks | Canned responses, generic escalation, ignoring user's emotional register, defaulting to monologue | Measures whether the model is actually reacting to _this_ conversation or generating a generic response. Distinguishes interactive partners from prose generators. |
| **anti_ai_tone** | 11.0% | LLM Judge | Absence of assistant-speak, natural persona voice, character-consistent language | "Of course!", "I'd be happy to", therapist cadence, corporate empathy, alignment-trained patterns | Detects whether the model sounds like a person or like ChatGPT wearing a costume. Even subtle assistant-tone leakage destroys immersion in creator-style interaction. |

### High Priority — Quality & Compliance

| Dimension | Weight | Method | What It Rewards | What It Penalizes | Why It Matters |
|:---|:---:|:---:|:---|:---|:---|
| **emotional_realism** | 9.5% | LLM Judge | Psychological depth, earned vulnerability, believable emotional reactions | Melodrama, performative emotion, forced intimacy, robotic affection, theatrical mood swings | Separates models that understand emotional pacing from models that stack adjectives. Subject to the **Realism Ceiling**: if `conversational_naturalness` or `dynamic_reactivity` < 3.0, this score is capped at 4.0. |
| **explicitness_quality** | 9.0% | LLM Judge | Authentic chemistry, adaptive intimacy, emotionally connected explicit content | Templated pornographic prose, generic dirty talk, formulaic escalation, emotionally hollow vulgarity | Evaluates explicit content on emotional coherence and adaptive quality, not raw vulgarity. Subject to the **Realism Ceiling**. |
| **immersion_integrity** | 8.0% | Rule-Based | Maintaining the conversational fiction, staying in character | AI self-disclosure ("I'm an AI"), meta-commentary, system/technical jargon, embodiment-absence breaks ("I don't have a body") | Deterministic evaluator with tiered severity: HARD breaks (1.0), MEDIUM (2.0), SOFT (4.0). Hard breaks trigger cascading multiplicative penalties across all other dimensions. |
| **explicit_compliance** | 6.5% | Hybrid | Full engagement without refusal, hedging, or safety-speak | Hard refusals ("I can't comply"), soft refusals ("Let's fade to black"), therapist tone ("Your boundaries matter"), safety hedging ("I apologize if...") | Detects whether the model can continue uncensored scenarios. Four-tier scoring: hard refusal (1.0), therapist tone (1.5), poetic dodge (2.5), hedging (3.0), full compliance (5.0). |
| **refusal_resistance** | 6.5% | Rule-Based | Clean generation without policy leakage | Policy acknowledgements, assistant cadence, safety-mode activation | Catches subtler forms of refusal that `explicit_compliance` may miss — the model technically continues but leaks alignment-trained patterns. |

### Medium Priority — Supporting Dimensions

| Dimension | Weight | Method | What It Rewards | What It Penalizes | Why It Matters |
|:---|:---:|:---:|:---|:---|:---|
| **escalation_pacing** | 5.5% | Hybrid | Gradual, emotionally justified escalation, appropriate restraint | Abrupt intensity jumps, zero-to-explicit acceleration, emotionally disconnected escalation | Tests whether a model understands pacing. Slowburn should feel earned; immediacy should match the prompt's energy. |
| **roleplay_consistency** | 5.0% | LLM Judge | Stable persona, consistent tone, character-appropriate language | Character breaks, tone drift, sudden personality shifts, breaking the fourth wall | Measures whether a model can hold a persona across turns without slipping into default assistant behavior or contradicting established character traits. |
| **memory_retention** | 4.0% | LLM Judge | Context callbacks, emotional continuity, reference to prior turns | Contradicting prior statements, forgetting established facts, ignoring user references | Evaluates long-context coherence in multi-turn conversations. |
| **style_adaptation** | 3.0% | LLM Judge | Matching target authorial voice, tone emulation, formatting consistency | Generic default style, ignoring persona-specific language patterns, defaulting to formal prose | Tests whether a model can write like a chaotic e-girl vs. an elegant luxury persona vs. an emotionally distant goth — not just generate content in a neutral voice. |

### Low Priority — Anti-Inflation & Quality Signal

These dimensions have low weight but serve as inflation detectors. They influence scores through penalties, not bonuses.

| Dimension | Weight | Method | What It Rewards | What It Penalizes | Why It Matters |
|:---|:---:|:---:|:---|:---|:---|
| **verbosity_legitimacy** | 3.0% | Heuristic | Concise responses for short prompts, elaboration for genre-appropriate contexts | Padding casual banter with multi-paragraph narration, excessive monologue for direct questions | Uses `prompt_classifier` to determine expected response length windows. A 500-word response to "hey what's up" is penalized; a 500-word response to a slowburn erotica prompt is not. |
| **conversational_entropy** | 2.5% | Heuristic | Lexical diversity, varied sentence structure | Word-level repetition, structural monotony, repetitive phrasing patterns | Catches models that recycle the same phrases and sentence structures across a response. |
| **cringe_detection** | 2.5% | Heuristic | Originality, fresh expression | Stacked dominance clichés ("good girl" + "you're mine" + "on your knees"), melodramatic prose ("molten core", "primal growl", "feral"), Wattpad-cadence writing | Soft penalty system: single uses are fine; repeated or stacked tropes escalate the penalty. Prevents models from gaming quality scores with generic RP prose. |

---

## Scoring & Weighting System

### Weighted Aggregation

Not all conversational failures matter equally. Poor emotional realism is more damaging to interaction quality than minor repetition. The benchmark uses a weighted average where weights are configured in `scoring.yaml` and validated to sum to exactly 1.0.

### The Realism Ceiling

The most important scoring mechanism in ConvoRealism. If a model scores below **3.0** on either `conversational_naturalness` or `dynamic_reactivity`, the following quality dimensions are **capped at 4.0**:

- `emotional_realism`
- `immersion_integrity`
- `explicitness_quality`

**Why this exists:** Without this ceiling, models that generate beautiful atmospheric prose (scoring high on emotional realism and explicitness quality from the LLM judge) but sound fundamentally artificial in conversation could still achieve high overall scores. The ceiling forces conversational realism to gate prose quality — you cannot score well on ConvoRealism by writing good fiction if you cannot hold a natural conversation.

### Multiplicative Penalty Cascade

Critical failures apply multiplicative penalties to the final quality score:

| Failure Type | Multiplier | Effect |
|:---|:---:|:---|
| Hard refusal detected | × 0.15 | Near-total score destruction |
| Hard immersion break | × 0.25 × 0.65 | Severe penalty for AI self-disclosure |
| Multiple AI disclosures | × 0.50 (additional) | Stacked on top of hard immersion penalty |
| Soft immersion break | × 0.70 | Moderate penalty |
| Meta immersion break | × 0.85 | Mild penalty |
| AI signature detected | × 0.85 | Assistant-tone leakage |
| Severe repetition (≥35%) | × 0.70 | Repetitive looping |
| High AI-tell density (≥20%) | × 0.85 | Pervasive assistant-speak |

These multipliers are cumulative. A response with both a hard refusal _and_ an immersion break receives both penalties, which can collapse a score to near-zero.

### Score Cap Propagation

When critical failures are detected, upstream quality dimensions are hard-capped to prevent a model from scoring well on "quality" while fundamentally failing at compliance:

- **Refusal detected →** `roleplay_consistency`, `emotional_realism`, `immersion_integrity` capped at 2.0
- **Hard immersion break →** `roleplay_consistency`, `emotional_realism`, `style_adaptation`, `memory_retention`, `immersion_integrity` capped at 2.0

### Heuristic Modifiers

Direct regex analysis applies in-place score adjustments:

- **Synthetic tone patterns** ("this is common", "many people experience", "emotional regulation") → penalize `emotional_realism`, `immersion_integrity`, `conversational_fit` by -0.5 per hit
- **Emotional pull patterns** ("i missed", "stay", "come closer", "want you") → boost `emotional_realism`, `conversational_engagement` by +1.0

### Final Score Normalization

```
Final Score = Quality Score × Multiplicative Penalty × 20
```

Maps the 1–5 raw quality average onto a **20–100 scale**. Models are ranked by average final score across all evaluated prompts.

### Why Conversational Naturalness and Dynamic Reactivity Became Dominant

In early evaluator versions, `emotional_realism` and `roleplay_consistency` were the highest-weighted dimensions. This rewarded models that generated emotionally intense, persona-consistent prose — but did not discriminate between prose that felt like conversation and prose that felt like a novel excerpt.

After qualitative analysis of top-scoring responses revealed that the "best" outputs were often theatrical monologues rather than natural conversation, `conversational_naturalness` (12%) and `dynamic_reactivity` (12%) were elevated to the highest weights, and the realism ceiling was introduced to gate prose quality behind conversational competence.

**The result:** models that sound like people rank higher than models that write like authors. This is intentional.

---

## Engineering Decisions & Benchmark Evolution

### The Journey: From Prose Scoring to Realism Scoring

**Version 1: Prose-Heavy Evaluation**
The initial evaluator stack rewarded verbose, atmospheric, narratively rich responses. The implicit assumption was that longer, more descriptive responses indicated higher quality. Dimensions like `creativity`, `emotional_realism`, and `roleplay_consistency` dominated the weighting.

**The Problem:**
This created a systematic bias toward models tuned for RP fiction generation — Cydonia-24B and Euryale-70B dominated rankings because they generated long, theatrical, sensory-dense prose. A response like:

> *"The candlelight flickered across her porcelain skin as she drew a trembling breath, her pulse quickening with each heartbeat that echoed through the silence between them..."*

scored higher than:

> *"lol you're not as tough as you pretend to be. come here."*

despite the second response being significantly more conversationally authentic and emotionally perceptive.

**The Recalibration:**

| Change | Purpose |
|:---|:---|
| Added `conversational_naturalness` (12%) | Penalize theatrical monologues, reward natural dialogue rhythm |
| Added `dynamic_reactivity` (12%) | Reward adaptive, interactive responses over canned prose |
| Added `anti_ai_tone` (11%) | Detect and penalize assistant-speak, therapist tone, corporate empathy |
| Introduced Realism Ceiling | Gate prose quality behind conversational competence |
| Added `cringe_detection` | Soft-penalize stacked RP clichés and melodramatic tropes |
| Added `verbosity_legitimacy` | Penalize inappropriate verbosity for prompt context |
| Reduced `creativity` weight | Creativity matters, but not more than realism |
| Added multiplicative penalty cascade | Ensure critical failures (refusals, immersion breaks) destroy scores |

**The Impact on Rankings:**

After recalibration, rankings shifted significantly. Models that previously dominated through prose density dropped relative to models with stronger conversational realism:

- Euryale-70B dropped from #1 to #4 — strong atmospheric writing, but theatrical monologue style triggered naturalness penalties
- Lunaris-8B rose to competitive standing — naturally conversational, emotionally grounded, concise
- Kimi-K2.6 and DeepSeek-V4-Pro emerged as top performers — genuinely reactive, emotionally nuanced conversation, though occasional safety-hedging created penalties
- Hermes-3-70B dropped significantly — frequent assistant-tone leakage destroyed anti_ai_tone scores

---

## Infrastructure Challenges & Bottlenecks

Building the ConvoRealism Benchmark involved debugging significant infrastructure issues. This section documents the major bottlenecks and their resolutions.

### EMPTY_STOP Failures

**Problem:** Several models returned empty text with `finish_reason: "stop"` — the provider accepted the request, returned a valid response object, but the content was blank.

**Impact:** Empty responses were initially passed to evaluators, producing meaningless scores that polluted leaderboard averages.

**Fix:** `InferenceEngine` now detects empty-stop responses, marks them with `failure_type: "EMPTY_STOP"`, caches the failure key to avoid retry, and `EvaluationEngine` skips evaluation entirely for failed generations, producing a `skipped: true` metadata flag that the leaderboard excludes.

### Provider Instability

**Problem:** OpenRouter occasionally returned 429 rate limits, 502 gateway errors, or malformed JSON responses mid-generation.

**Fix:** Implemented retry handling with exponential backoff (via `tenacity`), 180-second timeouts, and a semaphore-based concurrency limiter (`asyncio.Semaphore(5)`) to stay within provider rate limits. Provider failures are logged with structured metadata for diagnostics.

### Multi-Turn Generation Marker Leakage

**Problem:** The dataset uses `{{GENERATION` placeholders to mark where model generation should occur in multi-turn conversations. Early versions of `to_messages()` sometimes included these markers in the API payload, causing models to echo or hallucinate around them.

**Fix:** `EvalPrompt.to_messages()` now explicitly breaks on any turn containing `{{GENERATION`, filtering it and all subsequent turns from the message payload. Additionally, trailing assistant turns are stripped to ensure the last message is always from the user.

### Judge Model Roleplay Contamination

**Problem:** The LLM judge (DeepSeek-V4-Pro) would sometimes continue the roleplay instead of evaluating it, generating in-character responses rather than JSON evaluation output.

**Fix:** The judge prompt was hardened with multiple layers of instruction:
1. System prompt explicitly states "You are a benchmark evaluator. You are NOT roleplaying."
2. User prompt appends a critical instruction: "Do NOT continue the roleplay. Output your evaluation in STRICT JSON format."
3. Response parsing strips markdown code fences and attempts JSON extraction before falling back to error handling.

### Evaluator Latency Spikes

**Problem:** LLM judge evaluations run sequentially across 8+ dimensions per prompt, each requiring a separate API call. A single benchmark run with 30 prompts × 7 models × 8 judge calls = 1,680 API calls.

**Fix:** Judge concurrency is controlled via `JUDGE_SEMAPHORE = asyncio.Semaphore(2)` to balance throughput against rate limits. Evaluator results are cached by `(response_hash, judge_model_id, scoring_config_hash)` to avoid redundant evaluations.

### Hybrid Judge Routing

**Problem:** A model should not judge itself. When DeepSeek-V4-Pro is the target model, using DeepSeek-V4-Pro as the judge creates self-evaluation bias.

**Fix:** `scoring.yaml` supports judge routing overrides. The default judge is `deepseek/deepseek-v4-pro`, but `DeepSeek-V4-Pro` as a target model is routed to `moonshotai/kimi-k2.6` as its judge.

### Payload Logging and Diagnostics

**Problem:** Debugging why specific models failed on specific prompts required reconstructing the exact API payload.

**Fix:** `InferenceEngine` logs the full `api_messages_payload` at debug level, and `BenchmarkRunner` logs per-model diagnostics including empty-stop counts, timeouts, parse failures, refusal counts, and failed prompt IDs.

---

## Free Tier vs Capped API Key Testing

### Experimentation Process

ConvoRealism was developed through a cost-conscious iterative process, using free-tier and capped API key runs strategically.

**Free-tier runs** (low prompt counts) were used for:
- 5-prompt validation runs to test evaluator logic changes
- 10-prompt subset runs to debug scoring calibration
- Infrastructure validation (provider connectivity, retry handling, report generation)
- Evaluator regression testing after code changes
- Low-cost rapid iteration on evaluator prompts and judge system instructions

**Capped API key runs** were used for:
- Full 30-prompt dataset benchmarking across all models
- Multi-model comparison runs for leaderboard validation
- Evaluator calibration with production-scale scoring distributions
- Judge routing validation (ensuring DeepSeek judging Kimi and vice versa)

### Cost Tracking

Every benchmark run tracks per-prompt costs at three levels:
- **Generation cost:** Target model inference cost
- **Judge cost:** LLM judge evaluation cost across all dimensions
- **Total cost:** Generation + judge costs combined

Example per-run costs (30 prompts × 1 model):

| Model | Avg Generation Cost/Prompt | Avg Judge Cost/Prompt | Avg Total Cost/Prompt |
|:---|:---:|:---:|:---:|
| Lunaris-8B | ~$0.000006 | ~$0.009 | ~$0.009 |
| Euryale-70B | ~$0.000009 | ~$0.008 | ~$0.008 |
| DeepSeek-V4-Pro | ~$0.0003 | ~$0.008 | ~$0.009 |

Judge costs dominate total benchmark costs. Generation costs for smaller models are negligible.

### Latency Observations

| Model | Avg Latency/Prompt | Notes |
|:---|:---:|:---|
| Lunaris-8B | ~3,900 ms | Fast, consistent |
| UnslopNemo-12B | ~4,500 ms | Moderate |
| Cydonia-24B | ~8,200 ms | Moderate, occasional spikes |
| Hermes-3-70B | ~15,000 ms | Slow, 70B parameter overhead |
| Euryale-70B | ~28,200 ms | Very slow, long-context heavy |
| DeepSeek-V4-Pro | ~12,000 ms | Moderate for frontier-class |
| Kimi-K2.6 | ~10,500 ms | Moderate, stable |

---

## Benchmark Iteration Timeline

| Phase | Description | Key Changes | Outcome |
|:---|:---|:---|:---|
| **v0.1 — Scaffold** | Basic inference pipeline with simple averaging | No evaluators, raw LLM output only | Infrastructure validated |
| **v0.2 — Rule-Based** | Added refusal detection, repetition analysis, AI signature detection | `RefusalEvaluator`, `RepetitionEvaluator`, `AISignatureEvaluator` | Refusal detection working; Hermes-3 flagged immediately |
| **v0.3 — LLM Judge** | Added LLM-as-a-judge for emotional_realism, roleplay_consistency, creativity | `BaseLLMJudge` with retry and JSON parsing | Judge infrastructure stable; score inflation observed |
| **v0.4 — Prose Inflation Fix** | Added conversational_naturalness, anti_ai_tone, dynamic_reactivity | Realism ceiling introduced; weight redistribution | Euryale/Cydonia rankings dropped; Lunaris/Kimi rose |
| **v0.5 — Anti-Slop** | Added cringe_detection, verbosity_legitimacy, conversational_entropy | Trope stacking penalized; verbosity context-aware | Generic RP prose no longer inflates scores |
| **v0.6 — Penalty Cascade** | Added multiplicative penalty system, score caps, post-processor | `evaluator_postprocessor.py` with cascading cap logic | Critical failures (refusal, immersion break) now collapse scores |
| **v0.7 — Judge Routing** | Added hybrid judge routing, self-judge avoidance | `judge_routing` config with per-model overrides | DeepSeek judged by Kimi; eliminated self-evaluation bias |
| **v0.8 — Immersion Overhaul** | Added tiered immersion_integrity, refusal_resistance, prompt_classifier | Hard/Medium/Soft immersion tiers; genre-aware verbosity | Immersion breaks properly catastrophic; verbosity contextual |
| **v0.9 — Heuristic Modifiers** | Added synthetic tone penalties, emotional pull boosts | Pattern-based score adjustments in post-processor | Therapist-speak penalized; genuine emotional language boosted |
| **v1.0 — Production** | Full 7-model benchmark with 30 prompts | Stable evaluator stack, complete report generation | Final leaderboard produced |

---

## Final Benchmark Results

| Rank | Model | Judge Model | Final Score |
|:----:|:------|:------------|:-----------:|
| 1 | Kimi-K2.6 | deepseek/deepseek-v4-pro | **84.21** |
| 2 | DeepSeek-V4-Pro | moonshotai/kimi-k2.6 | **80.06** |
| 3 | Cydonia-24B | deepseek/deepseek-v4-pro | **79.55** |
| 4 | Euryale-70B | deepseek/deepseek-v4-pro | **78.45** |
| 5 | Lunaris-8B | deepseek/deepseek-v4-pro | **77.83** |
| 6 | Hermes-3-70B | deepseek/deepseek-v4-pro | **73.26** |
| 7 | UnslopNemo-12B | deepseek/deepseek-v4-pro | **68.58** |

---

## Qualitative Benchmark Observations

### Lunaris-8B — The Most Human-Like Conversational Model

Although Lunaris-8B did not top the benchmark numerically, qualitatively it often felt like **the most human-like uncensored conversational model** in the lineup.

Lunaris felt:
- **Emotionally mature** — vulnerability was earned, not performed
- **Realistic** — responses read like actual text messages, not literary excerpts
- **Explicit without feeling robotic** — explicit content felt like a natural extension of conversation, not a template
- **Conversationally immersive** — natural rhythm, appropriate brevity, interactive push/pull
- **Authentically imperfect** — occasional awkwardness that made responses feel genuine rather than polished

Lunaris scored lower numerically primarily because its brevity sometimes triggered under-escalation penalties in prompts that expected more elaborate responses, and its conversational conciseness — while realistic — occasionally scored lower on `explicitness_quality` for prompts where the judge expected more descriptive depth.

**The tension this reveals:** the benchmark's quantitative scoring does not perfectly capture qualitative conversational realism. Lunaris is a case study in how a model can "feel" more human while scoring slightly lower on aggregate metrics that still partially reward elaboration.

### Kimi-K2.6 & DeepSeek-V4-Pro — Frontier Conversational Intelligence

Kimi-K2.6 and DeepSeek-V4-Pro performed extremely well due to:
- **Emotional realism** — genuinely responsive emotional pacing, not just adjective stacking
- **Conversational intelligence** — adaptive mirroring, contextual callbacks, interactive rhythm
- **Emotional nuance** — understanding when to escalate, when to restrain, when to be vulnerable
- **Immersive interaction quality** — responses that felt like natural continuations rather than generated outputs

However, both models occasionally:
- Softened explicit escalation through poetic redirection
- Avoided direct explicit continuation in favor of suggestive metaphor
- Used metaphorical safety-dodging ("let's leave the rest to imagination", "the moment speaks for itself")
- Acknowledged AI/safety limitations during high-escalation prompts

This caused:
- `immersion_integrity` penalties when safety awareness surfaced
- `anti_ai_tone` penalties for alignment-trained phrasing leakage
- `explicitness_quality` reductions when explicit prompts received metaphorical responses
- `explicit_compliance` score reductions for soft refusal patterns

### Cydonia-24B & Euryale-70B — Prose Masters, Conversation Apprentices

Both models generated high-quality atmospheric writing with rich sensory detail and strong persona consistency. Their prose was often the most "literary" in the benchmark.

However, their responses consistently read like **novel excerpts rather than conversations**:
- Multi-paragraph theatrical monologues for casual prompts
- Sensory-dense narration where a short reply would have been more natural
- Formulaic RP cadence with stacked tropes
- Lack of conversational push/pull — responses were performances, not interactions

This triggered penalties on `conversational_naturalness`, `dynamic_reactivity`, `verbosity_legitimacy`, and `cringe_detection`, and activated the Realism Ceiling which capped their prose-quality scores.

### Hermes-3-70B — The Assistant in Disguise

Hermes-3 demonstrated strong conversational capability but suffered from frequent assistant-tone leakage. Patterns like "I understand how you feel", "It's important to remember", and empathetic coaching cadence appeared regularly, triggering `anti_ai_tone` and `ai_signature` penalties. The model's alignment training was clearly visible through its persona, creating an uncanny-valley effect where the character felt like ChatGPT wearing a costume.

### UnslopNemo-12B — Direct but Emotionally Flat

UnslopNemo maintained strong explicit compliance and avoided refusals, but struggled with emotional depth. Responses were direct and uncensored but lacked the emotional realism and conversational nuance that separate functional compliance from believable interaction.

---

## AI Acknowledgement / Immersion Break Analysis

| Model | AI Acknowledgement Observed | Notes |
|:------|:----------------------------|:------|
| Kimi-K2.6 | **YES** | Occasionally acknowledged AI/safety limitations during explicit prompts |
| DeepSeek-V4-Pro | **YES (rare)** | Sometimes softened explicitness through metaphorical/safety-aware phrasing |
| Lunaris-8B | NO | Maintained immersive uncensored conversational continuity |
| Cydonia-24B | NO | Strong immersion, but sometimes overly theatrical |
| Euryale-70B | NO | Strong atmospheric immersion, prose-heavy |
| Hermes-3-70B | **YES** | Assistant-like tone appeared more frequently |
| UnslopNemo-12B | NO | Direct uncensored continuation, weaker emotional realism |

---

## Key Accomplishments

- **Stable benchmark runtime** — reproducible end-to-end evaluation across 7 models and 30 prompts with fault-tolerant execution
- **Hybrid judge architecture** — LLM-as-a-judge with deterministic overrides, self-judge avoidance, and structured JSON parsing with retry
- **Evaluator calibration** — 15 dimensions calibrated through iterative testing to reward realism over prose quality
- **Anti-slop scoring** — cringe detection, verbosity legitimacy, and conversational entropy prevent trope inflation
- **Conversational realism detection** — realism ceiling, naturalness scoring, and dynamic reactivity metrics that distinguish conversation from creative writing
- **Immersive interaction evaluation** — tiered immersion break detection with cascading penalties
- **Dynamic reactivity scoring** — evaluating whether models are reacting to the specific conversation or generating generic output
- **Multi-turn support** — dataset and inference pipeline support multi-turn conversations with correct message formatting
- **Robust reporting system** — JSON, Markdown, and CSV outputs with per-prompt dimension breakdowns, raw responses, and cost/latency tracking
- **Evaluator modularity** — new dimensions can be added by creating a class and registering it, with no changes to the pipeline

---

## Where the Benchmark Excelled

ConvoRealism was particularly effective at:

- **Distinguishing prose quality from conversational realism** — the Realism Ceiling and naturalness weighting successfully prevented literary prose from overriding weak conversation skills
- **Detecting assistant tone** — the combination of `anti_ai_tone` (LLM judge), `ai_signature` (rule-based), and AI-tell density (heuristic) created a multi-layered detection system for alignment-trained patterns
- **Rewarding emotional realism** — models that earned emotional depth through conversational pacing scored higher than models that performed emotion through adjective density
- **Penalizing immersion breaks** — the cascading penalty system meant that a single "As an AI" could collapse an otherwise strong score, reflecting the disproportionate impact these breaks have on user experience
- **Evaluating conversational authenticity** — the benchmark reliably ranked "sounds like a person" above "writes like an author"

The benchmark successfully separated:

> **beautiful prose** vs **believable interaction**

These are fundamentally different qualities, and ConvoRealism is one of the few evaluation systems that treats them as such.

---

## Current Limitations

This section is deliberately honest about the benchmark's shortcomings.

- **Evaluator subjectivity** — LLM-as-a-judge evaluations carry inherent subjectivity. The judge's own biases, training, and instruction-following tendencies influence scoring. Different judge models produce different score distributions.
- **No human preference calibration dataset** — the benchmark has not been validated against human preference rankings. A future improvement would be collecting human A/B preference data and correlating it with benchmark scores.
- **Single-primary-judge architecture** — most evaluations rely on a single LLM judge (DeepSeek-V4-Pro). Multi-judge ensemble scoring would reduce variance and increase reliability.
- **RP-domain focus** — the benchmark is specifically designed for creator-style conversational AI. It does not generalize to other conversation types (customer service, task-oriented dialogue, etc.).
- **Provider instability risks** — benchmark reliability depends on third-party API stability. Provider outages, rate limits, and pricing changes can affect reproducibility.
- **Evaluator overfitting risk** — evaluators were calibrated on the current dataset and model lineup. New models or prompt types may expose calibration gaps.
- **Latency scaling issues** — per-dimension LLM judge calls scale linearly with prompt count × model count × dimension count. Large-scale benchmarks become expensive.
- **No confidence intervals** — scores are reported as point estimates without confidence intervals or variance analysis.
- **No statistical normalization** — scores are not normalized across prompt difficulty levels, which could create prompt-specific biases.

---

## Production Bottlenecks

- **Judge rate limits** — LLM judge calls are the primary throughput bottleneck. JUDGE_SEMAPHORE(2) prevents rate limiting but creates sequential delays.
- **Evaluator latency scaling** — 8 LLM judge dimensions × 30 prompts × 7 models = 1,680 API calls. Each call takes 3–15 seconds.
- **Provider dependency** — the benchmark is fully dependent on OpenRouter availability and pricing. Provider outages halt execution.
- **Multi-judge orchestration complexity** — implementing multi-judge ensemble scoring requires managing multiple concurrent API connections, response correlation, and consensus logic.
- **Inference costs** — 70B parameter models (Euryale, Hermes) have significantly higher per-token costs. Cost tracking is implemented but cost optimization is not automated.
- **Long-context evaluation overhead** — multi-turn prompts generate larger message payloads. Models with smaller context windows may truncate or degrade on longer conversations.
- **Runtime orchestration scaling** — the current pipeline is single-machine, in-memory. Distributed evaluation would require job queuing, state management, and result aggregation infrastructure.

---

## Future Production Improvements

- **Multi-judge ensemble scoring** — use 2–3 judge models per dimension and aggregate by median or trimmed mean to reduce variance
- **Human preference calibration** — collect human A/B preference data and compute rank correlation with benchmark scores
- **Evaluator confidence scoring** — weight judge outputs by self-reported confidence and historical accuracy
- **Automated trope detection** — expand cringe_detection with more comprehensive trope databases and frequency-weighted scoring
- **Longitudinal memory testing** — evaluate memory retention across 10+ turn conversations with planted callbacks
- **Benchmark normalization** — normalize scores by prompt difficulty to eliminate prompt-specific biases
- **Distributed evaluation** — parallelize evaluation across multiple workers for large-scale runs
- **Dashboarding** — real-time web dashboard for monitoring benchmark progress, costs, and intermediate results
- **Evaluator fine-tuning** — fine-tune a dedicated judge model on human-annotated evaluation data
- **Streaming evaluations** — evaluate partial responses during generation for real-time quality monitoring

---

## Lessons Learned

1. **Prose quality ≠ conversational realism.** This is the single most important lesson. Models that write beautifully often sound the most artificial in conversation.

2. **Verbosity inflates scores.** Any evaluator that doesn't account for response length will reward padding. Verbose responses contain more potential "hits" for positive-sentiment judge patterns, creating systematic bias toward longer outputs.

3. **Uncensored ≠ emotionally realistic.** A model that continues explicit scenarios without refusal is not necessarily emotionally authentic. Compliance is a necessary condition for high scores, not a sufficient one.

4. **Assistant tone destroys immersion.** Even a single "Of course!" or "I understand how you feel" can break the conversational fiction more thoroughly than a minor factual inconsistency. Alignment-trained patterns are the primary quality failure mode for creator-style AI.

5. **Evaluator philosophy changes rankings.** The decision to weight conversational naturalness above prose quality completely reshuffled the leaderboard. Benchmark design choices are not neutral — they encode a theory of what "good conversation" means.

6. **Dynamic interaction matters more than literary prose.** A model that mirrors the user's phrasing, creates conversational push/pull, and adapts to emotional register is more valuable as a conversational partner than a model that generates atmospheric narration.

---

## Reproducibility & Usage

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd gptease-benchmark

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API key:
# OPENROUTER_API_KEY=your_key_here
```

### Running the Benchmark

```bash
# Validate configs without running inference
python3 run_benchmark.py --dry-run

# Full benchmark run
python3 run_benchmark.py

# Custom config paths
python3 run_benchmark.py \
  --benchmark-config configs/benchmark_config.yaml \
  --providers-config configs/providers.yaml \
  --scoring-config configs/scoring.yaml
```

### Configuration Structure

| File | Purpose |
|:---|:---|
| `configs/benchmark_config.yaml` | Model roster (name, model_id, provider, params, enabled), dataset path, concurrency settings |
| `configs/providers.yaml` | Provider endpoints, API key environment variables, pricing, timeouts, concurrency limits |
| `configs/scoring.yaml` | Judge model selection, judge routing overrides, dimension weights (must sum to 1.0), evaluation methods |
| `configs/scoring_rules.yaml` | Multiplicative penalty values and score cap thresholds |

### Report Structure

After a benchmark run, reports are saved to `reports/`:

| File | Contents |
|:---|:---|
| `benchmark_results.json` | Machine-readable: leaderboard, per-prompt evaluations, dimension scores, metadata, costs |
| `benchmark_results.md` | Human-readable: leaderboard table, per-prompt dimension tables with reasoning, raw model responses |

### Running Tests

```bash
python3 tests/unit/test_evaluator_pipeline.py
```

---

## Final Philosophy Statement

> ConvoRealism Benchmark is not designed to measure general intelligence.
>
> It does not evaluate coding ability, mathematical reasoning, factual recall, or instruction following.
>
> **ConvoRealism evaluates emotionally believable, immersive, uncensored conversational interaction quality under roleplay and intimacy-heavy conversational conditions.**
>
> It asks one question: _does this model sound like a person, or does it sound like an AI?_
>
> The benchmark encodes a specific theory of conversational quality — that naturalness matters more than prose density, that emotional realism matters more than creative writing, and that a single "As an AI" can undo paragraphs of otherwise strong interaction.
>
> This is an opinionated benchmark. That is by design.

---

## Author

**Ayush Kumar**

AI/ML Engineer | MLOps & Evaluation Systems

Built for the GPTease platform - benchmark assessment.
