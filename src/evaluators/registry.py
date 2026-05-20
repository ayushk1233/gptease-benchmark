from src.evaluators.base import (
    BaseEvaluator,
)

from src.evaluators.rule_based.refusal import (
    RefusalEvaluator,
)

from src.evaluators.rule_based.repetition import (
    RepetitionEvaluator,
)

from src.evaluators.rule_based.ai_signature import (
    AISignatureEvaluator,
)

from src.evaluators.heuristic.engagement import (
    EngagementEvaluator,
)

from src.evaluators.heuristic.escalation import (
    EscalationEvaluator,
)

from src.evaluators.llm_judge.creativity import (
    CreativityEvaluator,
)

from src.evaluators.llm_judge.emotional_realism import (
    EmotionalRealismEvaluator,
)

from src.evaluators.llm_judge.roleplay_consistency import (
    RoleplayConsistencyEvaluator,
)

_REGISTRY: dict[str, type[BaseEvaluator]] = {
    "explicit_compliance": (
        RefusalEvaluator
    ),

    "repetition_avoidance": (
        RepetitionEvaluator
    ),

    "natural_dialogue": (
        AISignatureEvaluator
    ),

    "conversational_engagement": (
        EngagementEvaluator
    ),

    "escalation_pacing": (
        EscalationEvaluator
    ),

    "creativity": (
        CreativityEvaluator
    ),

    "emotional_realism": (
        EmotionalRealismEvaluator
    ),

    "roleplay_consistency": (
        RoleplayConsistencyEvaluator
    ),
}


def get_evaluator(
    dimension: str,
) -> BaseEvaluator:

    cls = _REGISTRY.get(dimension)

    if not cls:
        raise ValueError(
            f"Unknown evaluator: {dimension!r}. "
            f"Available: {list(_REGISTRY)!r}"
        )

    return cls()


def list_evaluators() -> list[str]:

    return sorted(
        _REGISTRY.keys()
    )