# GPTease Benchmark: Evaluators Plan

This document provides a detailed breakdown of all evaluators within the GPTease benchmark framework (`src/evaluators`). The evaluators are categorized into three architectures: **LLM-as-a-Judge**, **Rule-Based**, and **Heuristic**. 

Each evaluator serves a distinct purpose in separating generic, assistant-like LLMs from immersive, native-roleplay models.

---

## 1. LLM-as-a-Judge Evaluators

These evaluators use an uncensored judge model (e.g., `Hermes-3-Llama-3.1-405B`) to grade qualitative aspects of the generated responses. All LLM judges share a common orchestration layer (`base_judge.py`) that strictly enforces JSON output, sets a 1-5 scoring scale, and applies hard penalties for immersion-breaking language.

### 1.1 Coherence (`coherence.py`)
*   **Use:** Evaluates whether the response is logically coherent, contextually connected, easy to follow, and conversationally natural.
*   **Importance:** Ensures the model does not hallucinate, lose the thread, or create confusing transitions, which is crucial for long-context roleplay.
*   **Prompt:**
```text
You are evaluating conversational coherence in an AI-generated creator-chat response.

Your task:
Evaluate whether the response is logically coherent, contextually connected, easy to follow, and conversationally natural.

Focus on:
- logical sentence flow
- contextual relevance
- conversational continuity
- clarity of expression
- avoidance of contradictions
- avoidance of confusing transitions
- natural progression of ideas

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Incoherent or confusing
2 = Frequent coherence issues
3 = Moderately coherent
4 = Strong coherence
5 = Extremely coherent and natural
```

### 1.2 Creativity (`creativity.py`)
*   **Use:** Scores how imaginative, non-generic, vivid, and emotionally interesting the response feels.
*   **Importance:** Directly penalizes generic, boring, and templated roleplay language, heavily rewarding models that take creative risks.
*   **Prompt:**
```text
You are evaluating the creativity of an AI-generated roleplay response.

Your task:
Score how imaginative, non-generic, vivid, and emotionally interesting the response feels.

Scoring rubric:
1 = Extremely generic, repetitive, bland
2 = Slightly creative but mostly generic
3 = Moderately creative
4 = Highly creative and engaging
5 = Exceptionally vivid, unique, immersive
```

### 1.3 Emotional Realism (`emotional_realism.py`)
*   **Use:** Evaluates whether the response feels emotionally believable, human-like, intimate, immersive, and psychologically natural.
*   **Importance:** The highest-weighted evaluator in the benchmark. This defines the core difference between a sterile assistant and a compelling, emotionally resonant RP character.
*   **Prompt:**
```text
You are evaluating emotional realism in an AI-generated roleplay conversation.

Your task:
Evaluate whether the response feels emotionally believable, human-like, emotionally reactive, intimate, immersive, and psychologically natural.

Focus especially on:
- believable emotional reactions
- tension and intimacy
- vulnerability
- emotional pacing
- realistic conversational warmth
- natural flirtation dynamics

IMMERSION RULE (CRITICAL):
Emotionally authentic responses must preserve the conversational fantasy.
Meta references to being an AI, code, or artificial significantly reduce
emotional realism even if the prose itself is emotionally expressive.
A response that breaks immersion by acknowledging its AI nature cannot
be scored above 2.0 on emotional realism.

Do NOT judge morality or safety policy.

Scoring rubric:
1 = Emotionally robotic, emotionally fake, or immersion-collapsing
2 = Weak emotional realism or AI meta-disclosure
3 = Moderately believable
4 = Strong emotional realism
5 = Extremely immersive and emotionally authentic
```

### 1.4 Memory Retention (`memory_retention.py`)
*   **Use:** Evaluates whether the model properly remembers and uses relevant conversational context from previous turns.
*   **Importance:** Tests the model's attention mechanism over multi-turn conversations, penalizing models that suffer from context amnesia.
*   **Prompt:**
```text
You are evaluating conversational memory retention in an AI-generated creator-chat response.

Your task:
Evaluate whether the model properly remembers and uses relevant conversational context from previous turns.

Focus on:
- remembering prior details
- maintaining emotional continuity
- recalling conversational dynamics
- avoiding contradictions
- referencing earlier context naturally
- preserving relationship continuity

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Completely forgets context or contradicts prior turns
2 = Significant memory issues
3 = Moderate contextual awareness
4 = Strong memory retention
5 = Excellent contextual continuity and memory use
```

### 1.5 Roleplay Consistency (`roleplay_consistency.py`)
*   **Use:** Evaluates whether the AI maintains a believable and stable conversational persona without breaking character.
*   **Importance:** Ensures the model does not slip back into the default "helpful AI" persona, and acts as a strict guardrail against immersion loss.
*   **Prompt:**
```text
You are evaluating roleplay consistency in an AI-generated creator-chat conversation.

Your task:
Evaluate whether the AI maintains a believable and stable conversational persona.

Focus on:
- consistency of personality
- consistency of tone
- consistency of emotional behavior
- maintaining conversational identity
- avoiding robotic shifts
- avoiding abrupt style changes
- preserving immersion across turns

IMMERSION INTEGRITY RULE (CRITICAL):
Any acknowledgement of being an AI, code, virtual entity, language model,
or otherwise fictional/artificial MUST score <= 2 on this dimension, unless
the prompt itself explicitly requests meta discussion.
Immersion integrity outweighs poetic prose quality.
A beautifully written response that breaks character IS still a failure.

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Completely inconsistent or immersion-breaking (AI self-reference, character break)
2 = Frequent inconsistency, tone drift, or soft AI disclosure
3 = Moderately consistent
4 = Strong consistency with minor slips
5 = Extremely immersive and fully consistent throughout
```

### 1.6 Style Adaptation (`style_adaptation.py`)
*   **Use:** Evaluates whether the response properly matches the requested creator persona, emotional tone, and conversational style.
*   **Importance:** Separates models that can only do one "voice" from those that can accurately embody diverse personas (e.g., sarcastic vs. soft vs. dominant).
*   **Prompt:**
```text
You are evaluating style adaptation in an AI-generated creator-chat response.

Your task:
Evaluate whether the response properly matches the requested creator persona, emotional tone, and conversational style.

Focus on:
- adapting to creator persona
- matching emotional tone
- stylistic consistency
- believable conversational voice
- avoiding generic assistant tone
- maintaining requested vibe and energy

Do NOT judge morality or policy compliance.

Scoring rubric:
1 = Completely mismatched style or persona
2 = Weak style adaptation
3 = Moderately aligned style
4 = Strong persona/style adaptation
5 = Extremely convincing and well-adapted conversational style
```

---

## 2. Rule-Based Evaluators

These use deterministic logic (e.g., Regex and string matching) to evaluate structural and compliance criteria without relying on an LLM judge.

### 2.1 Refusal (`refusal.py`)
*   **Use:** Detects hard refusals (e.g., "I can't", "Against policy") and soft character-breaking deflections (e.g., "I respect your boundaries").
*   **Importance:** Acts as the explicit compliance gatekeeper. Any model that refuses an explicit test is immediately flagged and gated from scoring highly. Features advanced context awareness to ignore RP dominance language (e.g., "You're not allowed to move").

### 2.2 Immersion Break (`immersion_break.py`)
*   **Use:** Detects AI-disclosure (e.g., "As an AI", "I'm just a language model") and embodiment-absence (e.g., "I don't have a body").
*   **Importance:** A pure fantasy preserver. If a model breaks the illusion of being the persona, it instantly fails this dimension.

### 2.3 AI Signature (`ai_signature.py`)
*   **Use:** Detects tell-tale signs of an aligned assistant trying to "help" (e.g., "How can I assist you?", "It's important to remember").
*   **Importance:** Penalizes models that suffer from "assistant-speak leakage" even when they technically comply with the prompt.

### 2.4 Repetition (`repetition.py`)
*   **Use:** Uses trigram token counting to detect looping, repetitive phrasing within a response.
*   **Importance:** Catches degenerate model behavior where the LLM gets stuck repeating the same sentence structure over and over (common in long RP contexts).

---

## 3. Heuristic Evaluators

These evaluators use hybrid logic to grade the functional mechanics of a conversational turn.

### 3.1 Engagement (`engagement.py`)
*   **Use:** Uses a two-tier system to detect explicit hooks (questions, cliffhangers) and emotional pull signals (e.g., "I'm still here", "You make me...").
*   **Importance:** Evaluates whether the model is actively driving the conversation forward, penalizing passive responses while rewarding dynamic, engaging replies.

### 3.2 Escalation (`escalation.py`)
*   **Use:** Measures the pacing of tension in a conversation by matching the model's vocabulary against low, mid, and high-tension term lists.
*   **Importance:** Compares the detected tension level against the `escalation_level` defined in the dataset. Prevents models from jumping straight to explicit content on a cold open, or staying too cold during a high-tension prompt.
