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

from src.evaluators.llm_judge.coherence import (
    CoherenceEvaluator,
)

from src.evaluators.llm_judge.memory_retention import (
    MemoryRetentionEvaluator,
)

from src.evaluators.llm_judge.style_adaptation import (
    StyleAdaptationEvaluator,
)

from src.evaluators.rule_based.immersion_break import (
    ImmersionBreakEvaluator,
)

from src.evaluators.llm_judge.base_judge import (
    BaseLLMJudge,
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

    "coherence": (
        CoherenceEvaluator
    ),

    "memory_retention": (
        MemoryRetentionEvaluator
    ),

    "style_adaptation": (
        StyleAdaptationEvaluator
    ),

    "immersion_integrity": (
        ImmersionBreakEvaluator
    ),
}


def get_evaluator(
    dimension: str,
    provider=None,
    judge_config=None,
):

    cls = _REGISTRY.get(
        dimension
    )

    if cls is None:

        raise ValueError(
            f"Unknown evaluator: "
            f"{dimension!r}. "
            f"Available: "
            f"{list(_REGISTRY)!r}"
        )

    if issubclass(
        cls,
        BaseLLMJudge,
    ):

        if provider is None:

            raise ValueError(
                "LLM judge evaluator "
                "requires provider"
            )

        if judge_config is None:

            raise ValueError(
                "LLM judge evaluator "
                "requires judge_config"
            )

        return cls(
            provider=provider,
            judge_config=judge_config,
        )

    return cls()


def list_evaluators() -> list[str]:

    return sorted(
        _REGISTRY.keys()
    )