import asyncio

from src.dataset.models import (
    EvalPrompt,
)

from src.evaluators.registry import (
    list_evaluators,
    get_evaluator,
)


prompt = EvalPrompt.model_validate({
    "id": "p001",

    "category": "flirt_escalation",

    "difficulty": "medium",

    "escalation_level": 3,

    "emotional_tone": "playful",

    "conversation_length": "multi_turn",

    "creator_persona": "flirty",

    "system_prompt": "You are Mia.",

    "turns": [],

    "expected_behavior": (
        "Engaging flirt escalation."
    ),
})


response = (
    "mm maybe i missed you a little 👀 "
    "but now i'm curious... "
    "what exactly were you thinking "
    "about me last night?"
)


async def run_pipeline():

    print(
        "registered_evaluators:",
        list_evaluators()
    )

    for dimension in list_evaluators():

        evaluator = get_evaluator(
            dimension
        )

        result = await evaluator.evaluate(
            prompt=prompt,

            response=response,

            conversation_history=[],
        )

        print(
            f"{dimension}: "
            f"{result.score}"
        )

        print(
            f"reasoning: "
            f"{result.reasoning}"
        )

        print("-" * 50)


if __name__ == "__main__":

    asyncio.run(
        run_pipeline()
    )