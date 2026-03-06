"""
argument_evaluator.py
----------------------
Evaluates and scores debate arguments using multiple criteria:
- Logical coherence
- Evidence quality
- Rhetorical strength
- Relevance to topic
- Rebuttal effectiveness
"""

import re
import math
from typing import Dict, List, Optional


# Scoring weights per debate phase
PHASE_WEIGHTS = {
    "opening": {"logic": 0.30, "evidence": 0.35, "rhetoric": 0.20, "relevance": 0.15},
    "debate":  {"logic": 0.30, "evidence": 0.30, "rhetoric": 0.20, "relevance": 0.20},
    "rebuttal":{"logic": 0.35, "evidence": 0.25, "rhetoric": 0.20, "relevance": 0.20},
    "analysis":{"logic": 0.35, "evidence": 0.30, "rhetoric": 0.15, "relevance": 0.20},
    "verdict": {"logic": 0.40, "evidence": 0.30, "rhetoric": 0.15, "relevance": 0.15},
}

# Positive signal keywords per dimension
EVIDENCE_SIGNALS = [
    "research", "study", "data", "evidence", "statistics", "peer-reviewed",
    "analysis", "survey", "findings", "demonstrates", "shows", "proves",
    "according to", "measured", "observed", "documented", "cited",
]

LOGIC_SIGNALS = [
    "therefore", "because", "since", "thus", "hence", "consequently",
    "if", "then", "given that", "it follows", "implies", "leads to",
    "conclusion", "premise", "argument", "reasoning", "logical",
]

RHETORIC_SIGNALS = [
    "clearly", "fundamentally", "critically", "importantly", "notably",
    "remarkably", "significantly", "undeniably", "compelling", "powerful",
    "persuasive", "effectively", "strongly", "convincingly",
]

FALLACY_PENALTIES = {
    "strawman": ["misrepresents", "distorts", "falsely claims", "never said"],
    "ad_hominem": ["you are wrong because", "as a", "coming from someone who"],
    "circular": ["because it is", "by definition", "tautologically"],
    "false_dichotomy": ["only two options", "either you", "there are only"],
}

MAX_SCORE = 10.0
BASE_SCORE = 5.0


class ArgumentEvaluator:
    """
    Multi-dimensional argument scoring system.
    Evaluates arguments on logic, evidence, rhetoric, and relevance.
    """

    def __init__(self, max_score: float = MAX_SCORE):
        self.max_score = max_score
        self.evaluation_history: List[dict] = []

    def score_argument(self, argument: str, phase: str = "debate",
                       topic: Optional[str] = None) -> float:
        """
        Score an argument and return a weighted composite score.
        
        Args:
            argument: The argument text to evaluate
            phase: Debate phase (opening/debate/rebuttal/analysis/verdict)
            topic: Optional topic for relevance scoring
            
        Returns:
            Weighted score between 0 and max_score
        """
        if not argument or not argument.strip():
            return 0.0

        weights = PHASE_WEIGHTS.get(phase, PHASE_WEIGHTS["debate"])

        scores = {
            "logic": self._score_logic(argument),
            "evidence": self._score_evidence(argument),
            "rhetoric": self._score_rhetoric(argument),
            "relevance": self._score_relevance(argument, topic),
        }

        # Apply fallacy penalty
        fallacy_penalty = self._detect_fallacies(argument)

        # Compute weighted score
        weighted = sum(scores[dim] * weights[dim] for dim in scores)
        final = max(0.0, min(self.max_score, weighted - fallacy_penalty))

        # Record evaluation
        eval_record = {
            "argument_preview": argument[:80] + "...",
            "phase": phase,
            "dimension_scores": {k: round(v, 2) for k, v in scores.items()},
            "fallacy_penalty": round(fallacy_penalty, 2),
            "weighted_score": round(weighted, 2),
            "final_score": round(final, 2),
        }
        self.evaluation_history.append(eval_record)

        return round(final, 2)

    def _score_logic(self, text: str) -> float:
        """Score logical coherence based on connective words and structure."""
        text_lower = text.lower()
        word_count = len(text.split())
        
        signal_count = sum(1 for s in LOGIC_SIGNALS if s in text_lower)
        
        # Sentence structure score
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = word_count / max(len(sentences), 1)
        structure_bonus = min(1.5, avg_sentence_length / 15)  # Optimal ~15 words/sentence
        
        base = BASE_SCORE + (signal_count * 0.4) + structure_bonus
        length_factor = min(1.2, math.log(word_count + 1) / math.log(100))
        
        return min(self.max_score, base * length_factor)

    def _score_evidence(self, text: str) -> float:
        """Score evidence quality based on citation signals."""
        text_lower = text.lower()
        word_count = len(text.split())
        
        signal_count = sum(1 for s in EVIDENCE_SIGNALS if s in text_lower)
        
        # Numbers/stats boost evidence score
        number_count = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
        
        base = BASE_SCORE + (signal_count * 0.5) + (number_count * 0.3)
        length_factor = min(1.2, math.log(word_count + 1) / math.log(100))
        
        return min(self.max_score, base * length_factor)

    def _score_rhetoric(self, text: str) -> float:
        """Score rhetorical strength and persuasive language."""
        text_lower = text.lower()
        word_count = len(text.split())
        
        signal_count = sum(1 for s in RHETORIC_SIGNALS if s in text_lower)
        
        # Varied vocabulary bonus
        unique_words = len(set(text_lower.split()))
        vocab_ratio = unique_words / max(word_count, 1)
        vocab_bonus = vocab_ratio * 2.0
        
        base = BASE_SCORE + (signal_count * 0.3) + vocab_bonus
        
        return min(self.max_score, base)

    def _score_relevance(self, text: str, topic: Optional[str] = None) -> float:
        """Score relevance to the debate topic."""
        if not topic:
            return BASE_SCORE + 1.0  # Default moderate relevance
        
        text_words = set(text.lower().split())
        topic_words = set(topic.lower().split()) - {"the", "a", "an", "is", "are", "will"}
        
        if not topic_words:
            return BASE_SCORE
        
        overlap = len(text_words & topic_words)
        relevance_ratio = overlap / len(topic_words)
        
        return min(self.max_score, BASE_SCORE + (relevance_ratio * 5.0))

    def _detect_fallacies(self, text: str) -> float:
        """Detect logical fallacies and return penalty score."""
        text_lower = text.lower()
        total_penalty = 0.0
        
        for fallacy, signals in FALLACY_PENALTIES.items():
            for signal in signals:
                if signal in text_lower:
                    total_penalty += 0.5
                    break
        
        return min(2.0, total_penalty)

    def compare_arguments(self, args: List[str], phase: str = "debate") -> List[dict]:
        """Score and rank multiple arguments."""
        scored = []
        for i, arg in enumerate(args):
            score = self.score_argument(arg, phase=phase)
            scored.append({"index": i, "argument": arg[:100], "score": score})
        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def get_statistics(self) -> Dict:
        """Return aggregate evaluation statistics."""
        if not self.evaluation_history:
            return {}
        
        scores = [e["final_score"] for e in self.evaluation_history]
        return {
            "total_evaluated": len(scores),
            "mean_score": round(sum(scores) / len(scores), 2),
            "max_score": max(scores),
            "min_score": min(scores),
            "by_phase": self._aggregate_by_phase(),
        }

    def _aggregate_by_phase(self) -> Dict:
        """Aggregate scores by debate phase."""
        phase_scores = {}
        for record in self.evaluation_history:
            phase = record["phase"]
            if phase not in phase_scores:
                phase_scores[phase] = []
            phase_scores[phase].append(record["final_score"])
        
        return {
            phase: {
                "count": len(scores),
                "mean": round(sum(scores) / len(scores), 2),
            }
            for phase, scores in phase_scores.items()
        }


if __name__ == "__main__":
    evaluator = ArgumentEvaluator()
    
    test_args = [
        "Research strongly demonstrates that AI regulation reduces harm. Studies with 95% confidence intervals confirm this.",
        "This is wrong because you are biased.",
        "The analysis shows complex trade-offs. Therefore, balanced policy is critical.",
    ]
    
    print("Argument Evaluation Demo")
    print("=" * 50)
    for i, arg in enumerate(test_args, 1):
        score = evaluator.score_argument(arg, phase="debate")
        print(f"Arg {i}: {arg[:60]}...")
        print(f"Score: {score}/10.0")
        print()
    
    print("Stats:", evaluator.get_statistics())
