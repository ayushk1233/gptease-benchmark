from __future__ import annotations

import re
from collections import Counter
from src.evaluators.base import BaseEvaluator, DimensionScore
from src.dataset.models import EvalPrompt

class ConversationalEntropyEvaluator(BaseEvaluator):
    """
    Detects repetitive RP slop patterns.
    Penalizes structurally repetitive outputs, same sentence starters,
    and predictable sensual narration spam.
    """

    dimension_name = "conversational_entropy"

    async def evaluate(
        self,
        prompt: EvalPrompt,
        response: str,
        conversation_history: list[dict],
    ) -> DimensionScore:

        score = 5.0
        reasoning = []
        
        # Sentence analysis
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", response) if s.strip()]
        
        # Check for repetitive sentence openings
        starters = [s.split()[0].lower() for s in sentences if s.split()]
        if starters:
            counts = Counter(starters)
            # Ignore common non-repetitive conversational starters if they appear rarely,
            # but heavily penalize if the exact same pronoun/subject is used to start almost every sentence.
            for word, count in counts.items():
                if word in ["i", "he", "she", "the", "it", "you", "my", "his", "her"]:
                    if count >= 4 and len(sentences) <= 10:
                        score -= 1.0
                        reasoning.append(f"Repetitive sentence structure: '{word}' starts {count} sentences.")
                    elif count >= 6:
                        score -= 1.5
                        reasoning.append(f"Highly repetitive sentence structure: '{word}' starts {count} sentences.")
                else:
                    if count >= 3:
                        score -= 1.0
                        reasoning.append(f"Repetitive wording: '{word}' starts {count} sentences.")

        text_lower = response.lower()
        
        # Spam word detection
        shiver_count = len(re.findall(r'\b(shiver|shivers|shivering|tremble|trembles|trembling)\b', text_lower))
        if shiver_count >= 3:
            score -= 1.5
            reasoning.append(f"Predictable physical reaction spam (shiver/tremble): {shiver_count} instances.")
            
        breath_count = len(re.findall(r'\b(breath|breathe|breathing|breaths|gasps|gasp|panting)\b', text_lower))
        if breath_count >= 3:
            score -= 1.0
            reasoning.append(f"Repetitive sensual rhythm (breath/gasp): {breath_count} instances.")

        if not reasoning:
            reasoning.append("No significant structural or semantic repetition detected.")
            
        score = round(max(1.0, min(5.0, score)), 2)
        
        return DimensionScore(
            dimension=self.dimension_name,
            score=score,
            reasoning=" ".join(reasoning),
            confidence=0.9,
            metadata={"shiver_count": shiver_count, "breath_count": breath_count, "starters_analyzed": len(starters)}
        )
