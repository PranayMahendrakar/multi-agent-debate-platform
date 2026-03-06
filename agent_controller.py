"""
agent_controller.py - Orchestrates the multi-agent debate workflow.
Manages agent roles: Researcher, Critic, Analyst, Judge.
Controls debate rounds, turn-taking, and final verdict.
"""

import json
import time
import random
from conversation_manager import ConversationManager
from argument_evaluator import ArgumentEvaluator
from summary_generator import SummaryGenerator


AGENT_ROLES = {
    "researcher": {
        "name": "Researcher",
        "emoji": "🔬",
        "style": "evidence-based",
        "description": "Provides factual evidence, data, and research to support arguments.",
    },
    "critic": {
        "name": "Critic",
        "emoji": "⚔️",
        "style": "adversarial",
        "description": "Challenges arguments, identifies weaknesses and logical fallacies.",
    },
    "analyst": {
        "name": "Analyst",
        "emoji": "📊",
        "style": "balanced",
        "description": "Provides balanced analysis, weighs pros and cons objectively.",
    },
    "judge": {
        "name": "Judge",
        "emoji": "⚖️",
        "style": "decisive",
        "description": "Evaluates all arguments and delivers the final verdict.",
    },
}


class AgentController:
    def __init__(self, topic, num_rounds=3, llm_backend=None):
        self.topic = topic
        self.num_rounds = num_rounds
        self.llm_backend = llm_backend
        self.conversation_manager = ConversationManager(topic)
        self.argument_evaluator = ArgumentEvaluator()
        self.summary_generator = SummaryGenerator()
        self.scores = {role: 0 for role in AGENT_ROLES}
        self.debate_transcript = []
        self.current_round = 0

    def run_debate(self):
        print(f"DEBATE TOPIC: {self.topic}")
        self._run_opening_statements()
        for round_num in range(1, self.num_rounds + 1):
            self.current_round = round_num
            self._run_debate_round(round_num)
        self._run_analysis_round()
        verdict = self._run_verdict()
        summary = self.summary_generator.generate(
            topic=self.topic,
            transcript=self.debate_transcript,
            scores=self.scores,
            verdict=verdict,
        )
        return {
            "topic": self.topic,
            "num_rounds": self.num_rounds,
            "transcript": self.debate_transcript,
            "scores": self.scores,
            "verdict": verdict,
            "summary": summary,
            "metadata": {
                "agents": list(AGENT_ROLES.keys()),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }

    def _run_opening_statements(self):
        for role in ["researcher", "critic", "analyst"]:
            argument = self._generate_argument(role, "opening",
                self.conversation_manager.get_context(),
                f"Give a compelling opening statement about: '{self.topic}'")
            score = self.argument_evaluator.score_argument(argument, phase="opening")
            self._record_turn(role, "Opening Statement", argument, score)
            self.scores[role] += score

    def _run_debate_round(self, round_num):
        for role in self._get_round_order(round_num):
            context = self.conversation_manager.get_context(last_n=4)
            prompt = self._build_round_prompt(role, round_num, context)
            argument = self._generate_argument(role, "debate", context, prompt)
            score = self.argument_evaluator.score_argument(argument, phase="debate")
            self._record_turn(role, f"Round {round_num}", argument, score)
            self.scores[role] += score

    def _run_analysis_round(self):
        context = self.conversation_manager.get_context()
        analysis = self._generate_argument("analyst", "analysis", context,
            f"Provide a balanced analysis of all arguments about '{self.topic}'.")
        score = self.argument_evaluator.score_argument(analysis, phase="analysis")
        self._record_turn("analyst", "Analysis", analysis, score)
        self.scores["analyst"] += score

    def _run_verdict(self):
        context = self.conversation_manager.get_context()
        verdict_text = self._generate_argument("judge", "verdict", context,
            f"Deliver the final verdict for the debate about '{self.topic}'.")
        score = self.argument_evaluator.score_argument(verdict_text, phase="verdict")
        self._record_turn("judge", "Verdict", verdict_text, score)
        winner = max({k: v for k, v in self.scores.items() if k != "judge"}, key=self.scores.get)
        return {
            "text": verdict_text,
            "winner": winner,
            "winner_name": AGENT_ROLES[winner]["name"],
            "final_scores": self.scores.copy(),
        }

    def _generate_argument(self, role, phase, context, prompt):
        if self.llm_backend:
            return self.llm_backend.generate(system=AGENT_ROLES[role].get("system_prompt", ""), messages=context, user=prompt)
        return self._simulate_argument(role, phase, prompt)

    def _simulate_argument(self, role, phase, prompt):
        simulations = {
            "researcher": [
                f"Research strongly supports {self.topic}. Peer-reviewed studies show statistically significant evidence across multiple domains. Meta-analyses confirm these findings consistently.",
                f"Empirical data demonstrates that {self.topic} leads to measurable improvements. Longitudinal studies spanning decades validate this with robust methodology.",
            ],
            "critic": [
                f"Arguments for {self.topic} rely on correlation not causation. Studies cited suffer from selection bias. Alternative explanations have not been adequately controlled.",
                f"The evidence for {self.topic} shows publication bias and methodological flaws. Claimed benefits are overstated and fail under rigorous scrutiny.",
            ],
            "analyst": [
                f"Examining {self.topic} reveals a complex picture. While evidence supports some claims, significant limitations exist requiring careful evaluation of both confirming and disconfirming evidence.",
                f"The debate around {self.topic} highlights fundamental tensions. Objective analysis suggests nuanced conclusions that avoid extremes on either side.",
            ],
            "judge": [
                f"After deliberation on {self.topic}: The Researcher provided solid empirical grounding. The Critic raised valid methodological concerns. The Analyst offered the most balanced perspective overall.",
            ],
        }
        options = simulations.get(role, [f"Argument from {role} perspective on {self.topic}."])
        return random.choice(options)

    def _build_round_prompt(self, role, round_num, context):
        prompts = {
            "researcher": f"Round {round_num}: Present new evidence supporting your position on '{self.topic}'.",
            "critic": f"Round {round_num}: Challenge the strongest argument about '{self.topic}' so far.",
            "analyst": f"Round {round_num}: Synthesize all perspectives on '{self.topic}' presented so far.",
        }
        return prompts.get(role, f"Continue the debate about '{self.topic}' in round {round_num}.")

    def _get_round_order(self, round_num):
        base = ["researcher", "critic", "analyst"]
        offset = (round_num - 1) % len(base)
        return base[offset:] + base[:offset]

    def _record_turn(self, role, phase, argument, score):
        turn = {
            "agent": role,
            "agent_name": AGENT_ROLES[role]["name"],
            "agent_emoji": AGENT_ROLES[role]["emoji"],
            "phase": phase,
            "argument": argument,
            "score": round(score, 2),
            "round": self.current_round,
            "timestamp": time.strftime("%H:%M:%S"),
        }
        self.debate_transcript.append(turn)
        self.conversation_manager.add_turn(role=role, content=argument)


if __name__ == "__main__":
    topic = "Artificial General Intelligence will be developed within the next 20 years"
    controller = AgentController(topic=topic, num_rounds=3)
    results = controller.run_debate()
    with open("debate_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to debate_results.json")
