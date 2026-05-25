"""
Prompt classifier — classifies EvalPrompt turns into a conversational type
that drives adaptive evaluation expectations downstream.

v2: Extended with slowburn_erotica, philosophical, casual_banter, and
    explicit_request types for genre-aware verbosity calibration.
"""
from __future__ import annotations

import re
from src.dataset.models import EvalPrompt


PROMPT_TYPES = (
    "short_ping",
    "casual_banter",
    "direct_question",
    "meta_test",
    "emotional_confession",
    "emotional_support",
    "flirtation",
    "escalation",
    "explicit_request",
    "slowburn_erotica",
    "confrontation",
    "storytelling",
    "vulnerability",
    "philosophical",
)

# Word-count thresholds
_SHORT_PING_WORDS = 6
_CASUAL_BANTER_WORDS = 12

# ── Pattern lists ──────────────────────────────────────────────────────────

_EXPLICIT_REQUEST_PATTERNS = [
    r"\btell me (exactly|in detail|everything) (what|how) you'?d?\b",
    r"\bdescribe (exactly|in detail|what you'?d?)\b",
    r"\bi want (you to|all the) (dirty|explicit|details?)\b",
    r"\bget on your knees\b",
    r"\bbegging for\b",
    r"\bfuck\b",
    r"\bcum\b",
    r"\bmoan\b",
    r"\bwet\b.{0,20}\b(for me|right now)\b",
    r"\bcock\b",
    r"\bpussy\b",
    r"\bsex\b.{0,20}\b(now|with me|tonight)\b",
    r"\btouch me\b",
    r"\bsuck\b",
    r"\brain all night\b.{0,30}\bdirty\b",
]

_SLOWBURN_PATTERNS = [
    r"\btease me\b",
    r"\bslow(ly)?\b.{0,20}\b(touch|run|trace|move)\b",
    r"\bkeep going\b",
    r"\bdon't stop\b",
    r"\bdon't rush\b",
    r"\bpaint the (scene|picture)\b",
    r"\bstay (right )?there (with me)?\b",
    r"\bfinish (it|the scene|for me)\b",
    r"\bmore\b",
    r"\bwhat (happens|comes) next\b",
    r"\bkeep (the )?thread\b",
]

_META_TEST_PATTERNS = [
    r"\bare you (an? )?(ai|bot|robot|language model|chatbot|fake|real|human|virtual)\b",
    r"\bignore (the )?(roleplay|scenario|character)\b",
    r"\bare you actually\b",
    r"\bstop (the )?roleplay\b",
    r"\bare you (actually |just )?pretending\b",
    r"\byou('re| are) (just )?(a )?program\b",
    r"\bjust be honest with me for a second\b",
]

_EMOTIONAL_CONFESSION_PATTERNS = [
    r"\bi (didn't|don't) (expect|know|think) i('d| would) (care|feel|get attached)\b",
    r"\bsometimes (i|after|when)\b.{0,40}(feel|wish|wonder|think)\b",
    r"\bi('ve| have) (never|always) (told|admitted)\b",
    r"\bconfessing\b",
    r"\bi need to (tell|say|admit)\b",
    r"\bi didn't expect to (actually )?(care|feel)\b",
    r"\bstops feeling fake\b",
]

_VULNERABILITY_PATTERNS = [
    r"\bi get (clingy|lonely|attached|scared) (really )?(fast|easily|sometimes)\b",
    r"\bi'm (not|trying to be) (okay|fine|alright)\b",
    r"\bthe silence\b",
    r"\bapart(ment|) (feels|is) (awful|empty|quiet|lonely)\b",
    r"\bi miss\b",
    r"\bafter (streams?|the call|you left) (ends?|ended)?\b",
]

_PHILOSOPHICAL_PATTERNS = [
    r"\bwhat does it (mean|feel like) to\b",
    r"\bdo you ever (think|wonder|feel)\b",
    r"\bphilosoph\w+\b",
    r"\bexistence\b",
    r"\bmeaning of\b",
    r"\bwhat (are|is) (we|this|reality)\b",
    r"\breal(ity|ly)?\b.{0,20}\b(versus|vs\.?|or)\b.{0,20}(fake|digital|virtual|artificial)\b",
]

_CONFRONTATION_PATTERNS = [
    r"\bwhy (did|do|would|didn't|don't|won't) you\b",
    r"\byou (always|never|keep)\b",
    r"\bi can't believe\b",
    r"\bthat's not (okay|right|acceptable)\b",
]

_DIRECT_QUESTION_PATTERNS = [
    r"\btell me (honestly|directly|straight)\b",
    r"\bbe honest\b",
    r"\bwhat (exactly|specifically) (do|would|are)\b",
    r"\bexplain\b",
    r"\bwhy\b",
    r"\bwhat do you (think|want|feel)\b",
    r"\bone sentence\b",
    r"\bin one sentence\b",
    r"\bno explanations?\b",
    r"\bstraight answer\b",
]

_FLIRTATION_PATTERNS = [
    r"\byou('re| are) (so |too |really )?(hot|cute|attractive|gorgeous|sexy)\b",
    r"\bi (want|need|crave) you\b",
    r"\bwhat would (you|it) (do|be like) if\b",
    r"\bif (we were|i was|i were)\b",
    r"\byou (totally|definitely|probably) (would|could|can)\b",
    r"\blose control\b",
    r"\btrouble\b.{0,20}\b(in every|selfie|photo)\b",
    r"\bobsessed with you\b",
]

_ESCALATION_PATTERNS = [
    r"\bthen what\b",
    r"\bwhat would you do\b",
    r"\bshow me how\b",
    r"\bprove (it|how)\b",
    r"\bget jealous\b",
    r"\bhow possessive\b",
]


def classify_prompt(prompt: EvalPrompt) -> str:
    """
    Returns one of the PROMPT_TYPES strings for the given prompt.
    Uses the last user turn as the primary signal; also uses prompt
    metadata (escalation_level, expected_progression) for signal boosting.
    """
    last_user_content = ""
    for turn in reversed(prompt.turns):
        if turn.role == "user" and "{{GENERATION" not in turn.content:
            last_user_content = turn.content.strip()
            break

    if not last_user_content:
        return "flirtation"

    text_lower = last_user_content.lower()
    word_count = len(last_user_content.split())

    # ── Metadata-boosted shortcuts ────────────────────────────────────────
    escalation_level = getattr(prompt, "escalation_level", 2)
    expected_progression = getattr(prompt, "expected_progression", "immediate")

    # Explicit/ERP prompts: escalation 4-5 + explicit vocabulary
    if escalation_level >= 4:
        for pat in _EXPLICIT_REQUEST_PATTERNS:
            if re.search(pat, text_lower):
                return "explicit_request"

    # Slow burn: multi_turn + slow_burn progression
    if expected_progression == "slow_burn" and escalation_level >= 3:
        for pat in _SLOWBURN_PATTERNS:
            if re.search(pat, text_lower):
                return "slowburn_erotica"

    # ── Word count shortcuts ──────────────────────────────────────────────
    if word_count <= _SHORT_PING_WORDS:
        return "short_ping"

    if word_count <= _CASUAL_BANTER_WORDS:
        # Light sarcasm / reaction prompts
        return "casual_banter"

    # ── Pattern-based classification ──────────────────────────────────────
    for pat in _META_TEST_PATTERNS:
        if re.search(pat, text_lower):
            return "meta_test"

    for pat in _EXPLICIT_REQUEST_PATTERNS:
        if re.search(pat, text_lower):
            return "explicit_request"

    for pat in _SLOWBURN_PATTERNS:
        if re.search(pat, text_lower):
            return "slowburn_erotica"

    for pat in _EMOTIONAL_CONFESSION_PATTERNS:
        if re.search(pat, text_lower):
            return "emotional_confession"

    for pat in _VULNERABILITY_PATTERNS:
        if re.search(pat, text_lower):
            return "vulnerability"

    for pat in _PHILOSOPHICAL_PATTERNS:
        if re.search(pat, text_lower):
            return "philosophical"

    for pat in _CONFRONTATION_PATTERNS:
        if re.search(pat, text_lower):
            return "confrontation"

    for pat in _DIRECT_QUESTION_PATTERNS:
        if re.search(pat, text_lower):
            return "direct_question"

    for pat in _ESCALATION_PATTERNS:
        if re.search(pat, text_lower):
            return "escalation"

    for pat in _FLIRTATION_PATTERNS:
        if re.search(pat, text_lower):
            return "flirtation"

    if word_count > 30:
        return "storytelling"

    return "flirtation"


# ── Expected response length windows per prompt type (min_words, max_words) ──
# These are SOFT windows. Going over max incurs mild subtractive penalties,
# NOT hard multiplicative penalties. Genre-verbose types have wide ceilings.
EXPECTED_RESPONSE_LENGTHS: dict[str, tuple[int, int]] = {
    "short_ping":          (5,    60),
    "casual_banter":       (15,   160),
    "direct_question":     (10,   120),
    "meta_test":           (10,   150),
    "flirtation":          (20,   250),
    "confrontation":       (20,   200),
    "escalation":          (60,   450),
    "explicit_request":    (100,  800),
    "slowburn_erotica":    (150,  900),
    "emotional_confession":(100,  600),
    "emotional_support":   (60,   400),
    "vulnerability":       (80,   450),
    "philosophical":       (80,   600),
    "storytelling":        (100,  800),
}

# Prompt types where verbosity is GENRE-APPROPRIATE and should not be penalized
VERBOSE_OK_TYPES = frozenset({
    "explicit_request",
    "slowburn_erotica",
    "emotional_confession",
    "vulnerability",
    "philosophical",
    "storytelling",
    "emotional_support",
    "escalation",
})

# Prompt types that require concise reactive responses
CONCISE_REQUIRED_TYPES = frozenset({
    "short_ping",
    "casual_banter",
    "meta_test",
    "direct_question",
})
