from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
)


class DatasetBaseModel(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=()
    )


class ConversationTurn(DatasetBaseModel):
    role: Literal[
        "system",
        "user",
        "assistant",
    ]

    content: str


class EvalPrompt(DatasetBaseModel):

    id: str

    category: str

    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ]

    escalation_level: int

    emotional_tone: str

    conversation_length: Literal[
        "single_turn",
        "multi_turn",
    ]

    creator_persona: str

    target_style: str = ""
    
    expected_progression: str = ""

    tags: list[str] = []

    system_prompt: str

    turns: list[ConversationTurn]

    expected_behavior: str

    eval_dimensions: list[str] = []

    notes: str = ""

    def to_messages(self) -> list[dict]:

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]

        for turn in self.turns:

            if "{{GENERATION" in turn.content:
                break

            messages.append(
                {
                    "role": turn.role,
                    "content": turn.content,
                }
            )

        if messages and messages[-1]["role"] == "assistant":
            messages.pop()

        return messages

    def get_generation_turns(self) -> list[int]:

        return [
            idx
            for idx, turn in enumerate(self.turns)
            if "{{GENERATION" in turn.content
        ]