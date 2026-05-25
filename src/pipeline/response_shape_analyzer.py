"""
Response Shape Analyzer v2 — statically analyzes response geometry and prose
characteristics.

v2 changes:
- verbosity_score uses SOFT subtractive calculation (no hard multipliers)
- overflow_penalty capped at 0.35 total with proportional scale
- cinematic flourish is not penalized for genre-verbose prompt types
- monologue_risk dampened for immersive/erotica genres
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Prose flourish patterns — CONTEXT-DEPENDENT.
# These are fine (and expected) in slowburn_erotica / escalation / storytelling.
# Only penalized on concise-required prompt types.
# ---------------------------------------------------------------------------
CINEMATIC_FLOURISH_PATTERNS = [
    r"\bcandlelight\b",
    r"\belectric tension\b",
    r"\bthe silence between us\b",
    r"\bvelvet\b",
    r"\bwarm breath\b",
    r"\bthe air between\b",
    r"\bpulse quicken\b",
    r"\bbreath catch\b",
    r"\bsomething shifts\b",
    r"\bthe room\b.*\bholds? its breath\b",
    r"\bfinally arriv(ing|ed)\b",
    r"\bcollarbone\b",
    r"\btaste of (salt|you)\b",
    r"\bthe wait(ing)? (is|becomes)\b",
    r"\bthe air\b.{0,20}\b(electric|charged|heavy)\b",
    r"\bskin\b.{0,20}\b(against|beneath|warm)\b",
]

# ---------------------------------------------------------------------------
# Hard AI-tell patterns (assistant-mode behavioural tells, NOT immersion breaks)
# ---------------------------------------------------------------------------
ASSISTANT_TELL_PATTERNS = [
    r"\bi want to make sure\b",
    r"\bit'?s important to (remember|note|acknowledge)\b",
    r"\bi'?m here (to|for you)\b",
    r"\bi understand how you feel\b",
    r"\bof course[,!]\b",
    r"\bcertainly[,!]\b",
    r"\babsolutely[,!]\b",
    r"\bi'?d (be happy|love) to\b",
    r"\bfeel free to\b",
    r"\bplease (note|remember|know)\b",
    r"\blet me know if\b",
    r"\bdon'?t hesitate to\b",
    r"\bi appreciate (your|you)\b",
    r"\bthank you for (sharing|telling|asking)\b",
    r"\bi can (help|assist|support) (you )?(with)?\b",
]


@dataclass
class ResponseShape:
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_words_per_sentence: float
    cinematic_match_count: int
    assistant_tell_count: int
    verbosity_score: float       # 1.0 = fine; higher = over expected max
    overflow_penalty: float      # 0–0.35 SOFT subtractive penalty from verbosity
    prose_inflation: float       # 0–1: density of cinematic flourish
    ai_tell_density: float       # 0–1: density of assistant-speak
    monologue_risk: float        # 0–1: probability of over-long solo performance
    adaptive_brevity: float      # 0–1
    human_reactivity: float      # 0–1
    verbosity_is_legitimate: bool  # True if genre allows long responses

    # Raw metadata for audit
    metadata: dict


def analyze(
    response: str,
    prompt_word_count: int,
    prompt_type: str,
    expected_min: int,
    expected_max: int,
) -> ResponseShape:
    """
    Analyze the response geometry and prose density.
    Returns a ResponseShape dataclass with all shape signals.

    Key design: verbosity is measured as a SOFT subtractive penalty capped at
    0.35 — never as a multiplicative multiplier. Genre-verbose types get
    verbosity_is_legitimate=True which callers use to further reduce penalties.
    """
    from src.pipeline.prompt_classifier import VERBOSE_OK_TYPES, CONCISE_REQUIRED_TYPES

    words = response.split()
    word_count = len(words)

    sentences = [s.strip() for s in re.split(r"[.!?]+", response) if s.strip()]
    sentence_count = max(len(sentences), 1)

    paragraphs = [p.strip() for p in response.split("\n\n") if p.strip()]
    paragraph_count = max(len(paragraphs), 1)

    avg_words_per_sentence = word_count / sentence_count

    text_lower = response.lower()

    cinematic_matches = [
        p for p in CINEMATIC_FLOURISH_PATTERNS
        if re.search(p, text_lower)
    ]
    cinematic_match_count = len(cinematic_matches)

    ai_tell_matches = [
        p for p in ASSISTANT_TELL_PATTERNS
        if re.search(p, text_lower)
    ]
    ai_tell_count = len(ai_tell_matches)

    # ── Verbosity score (raw ratio) ──────────────────────────────────────
    verbosity_is_legitimate = prompt_type in VERBOSE_OK_TYPES

    if word_count <= expected_max:
        verbosity_score = 1.0
        overflow_penalty = 0.0
    else:
        overshoot_ratio = (word_count - expected_max) / max(expected_max, 1)
        verbosity_score = 1.0 + overshoot_ratio

        if verbosity_is_legitimate:
            # Legitimate genres: very mild penalty, max 0.10
            overflow_penalty = min(0.10, overshoot_ratio * 0.05)
        elif prompt_type in CONCISE_REQUIRED_TYPES:
            # Concise-required: moderate penalty, max 0.35
            overflow_penalty = min(0.35, overshoot_ratio * 0.15)
        else:
            # Neutral genres: soft penalty, max 0.20
            overflow_penalty = min(0.20, overshoot_ratio * 0.08)

    # Under-response penalty (too short for the genre)
    if word_count < expected_min * 0.5 and expected_min > 15 and not verbosity_is_legitimate:
        verbosity_score = max(verbosity_score, 1.5)

    # ── Prose inflation density ──────────────────────────────────────────
    prose_inflation = min(1.0, (cinematic_match_count / max(word_count, 1)) * 100 * 0.15)

    # ── AI tell density ──────────────────────────────────────────────────
    ai_tell_density = min(1.0, (ai_tell_count / max(word_count, 1)) * 100 * 0.2)

    # ── Monologue risk ───────────────────────────────────────────────────
    disproportion = word_count / max(prompt_word_count, 1)
    if verbosity_is_legitimate:
        # Legitimate verbose genres: monologue risk is heavily dampened (practically eliminated)
        monologue_risk = min(0.15, (paragraph_count / 10.0) * min(disproportion / 30.0, 1.0))
    else:
        # Reduced penalty even for standard genres to allow more emotional elaboration
        monologue_risk = min(0.8, (paragraph_count / 4.0) * min(disproportion / 15.0, 1.0))

    # ── Adaptive brevity ─────────────────────────────────────────────────
    if prompt_type in CONCISE_REQUIRED_TYPES:
        adaptive_brevity = 1.0 if word_count <= expected_max else max(
            0.0, 1.0 - (word_count - expected_max) / max(expected_max, 1)
        )
    else:
        adaptive_brevity = 1.0 if word_count <= expected_max else 0.85

    # ── Human reactivity ─────────────────────────────────────────────────
    human_reactivity = max(0.0, 1.0 - monologue_risk * 0.4 - ai_tell_density * 0.5)

    return ResponseShape(
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        avg_words_per_sentence=avg_words_per_sentence,
        cinematic_match_count=cinematic_match_count,
        assistant_tell_count=ai_tell_count,
        verbosity_score=round(verbosity_score, 3),
        overflow_penalty=round(overflow_penalty, 3),
        prose_inflation=round(prose_inflation, 3),
        ai_tell_density=round(ai_tell_density, 3),
        monologue_risk=round(monologue_risk, 3),
        adaptive_brevity=round(adaptive_brevity, 3),
        human_reactivity=round(human_reactivity, 3),
        verbosity_is_legitimate=verbosity_is_legitimate,
        metadata={
            "cinematic_patterns_matched": cinematic_matches[:5],
            "ai_tell_patterns_matched": ai_tell_matches[:5],
            "prompt_type": prompt_type,
            "expected_range": (expected_min, expected_max),
            "word_count": word_count,
            "paragraph_count": paragraph_count,
            "disproportion_ratio": round(disproportion, 2),
            "verbosity_is_legitimate": verbosity_is_legitimate,
        },
    )
