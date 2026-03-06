"""
summary_generator.py
----------------------
Generates structured debate summaries, reasoning reports,
and JSON output for GitHub Pages visualization.
"""

import json
import time
from typing import Dict, List, Optional


class SummaryGenerator:
    """
    Generates comprehensive debate summaries including:
    - Executive summary
    - Per-agent performance analysis
    - Key argument highlights
    - Scoring breakdown
    - Verdict explanation
    - JSON export for GitHub Pages
    """

    def generate(
        self,
        topic: str,
        transcript: List[dict],
        scores: Dict[str, float],
        verdict: dict,
        llm_backend=None,
    ) -> dict:
        """
        Generate a complete debate summary.
        
        Args:
            topic: The debate topic
            transcript: Full list of debate turns
            scores: Agent scores dict
            verdict: Verdict dict from judge
            llm_backend: Optional LLM for AI-powered summaries
            
        Returns:
            Comprehensive summary dict
        """
        winner = verdict.get("winner", "")
        winner_name = verdict.get("winner_name", "")
        
        # Score rankings
        rankings = self._rank_agents(scores)
        
        # Key arguments per agent
        key_args = self._extract_key_arguments(transcript)
        
        # Phase breakdown
        phase_breakdown = self._phase_breakdown(transcript)
        
        # Executive summary
        exec_summary = self._generate_executive_summary(
            topic, rankings, winner_name, transcript, llm_backend
        )
        
        # Reasoning analysis
        reasoning = self._generate_reasoning_analysis(transcript, scores)
        
        # Score chart data (for visualization)
        chart_data = self._generate_chart_data(transcript, scores)
        
        return {
            "executive_summary": exec_summary,
            "topic": topic,
            "winner": winner,
            "winner_name": winner_name,
            "rankings": rankings,
            "key_arguments": key_args,
            "phase_breakdown": phase_breakdown,
            "reasoning_analysis": reasoning,
            "chart_data": chart_data,
            "score_summary": self._format_score_summary(scores),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_turns": len(transcript),
        }

    def _rank_agents(self, scores: Dict[str, float]) -> List[dict]:
        """Rank agents by total score."""
        ranked = sorted(
            [{"agent": k, "score": round(v, 2)} for k, v in scores.items() if k != "judge"],
            key=lambda x: x["score"],
            reverse=True,
        )
        for i, r in enumerate(ranked):
            r["rank"] = i + 1
            r["medal"] = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
        return ranked

    def _extract_key_arguments(self, transcript: List[dict]) -> Dict[str, List[str]]:
        """Extract top arguments per agent based on score."""
        agent_args = {}
        for turn in transcript:
            agent = turn["agent"]
            if agent not in agent_args:
                agent_args[agent] = []
            agent_args[agent].append({
                "text": turn["argument"],
                "score": turn.get("score", 0),
                "phase": turn["phase"],
            })
        
        # Sort by score and return top 3 per agent
        result = {}
        for agent, args in agent_args.items():
            top = sorted(args, key=lambda x: x["score"], reverse=True)[:3]
            result[agent] = [{"text": a["text"][:200], "score": a["score"], "phase": a["phase"]} for a in top]
        
        return result

    def _phase_breakdown(self, transcript: List[dict]) -> Dict[str, dict]:
        """Summarize each debate phase."""
        phases = {}
        for turn in transcript:
            phase = turn["phase"]
            if phase not in phases:
                phases[phase] = {"turns": [], "avg_score": 0, "agents": []}
            phases[phase]["turns"].append(turn)
            if turn["agent"] not in phases[phase]["agents"]:
                phases[phase]["agents"].append(turn["agent"])
        
        for phase, data in phases.items():
            scores = [t.get("score", 0) for t in data["turns"]]
            data["avg_score"] = round(sum(scores) / len(scores), 2) if scores else 0
            data["turn_count"] = len(data["turns"])
            data["turns"] = [
                {"agent": t["agent"], "preview": t["argument"][:120], "score": t.get("score", 0)}
                for t in data["turns"]
            ]
        
        return phases

    def _generate_executive_summary(
        self, topic: str, rankings: List[dict], winner: str,
        transcript: List[dict], llm_backend=None
    ) -> str:
        """Generate an executive summary of the debate."""
        if llm_backend:
            context = "\n".join([f"{t['agent_name']}: {t['argument'][:100]}" for t in transcript[:6]])
            return llm_backend.generate(
                system="You are a professional debate analyst. Write a concise executive summary.",
                messages=[],
                user=f"Summarize this debate about '{topic}':\n{context}\nWinner: {winner}",
            )
        
        # Generated summary
        top_agent = rankings[0]["agent"] if rankings else "unknown"
        medal = rankings[0]["medal"] if rankings else ""
        total_turns = len(transcript)
        phases = set(t["phase"] for t in transcript)
        
        return (
            f"The debate on '{topic}' concluded after {total_turns} total turns across "
            f"{len(phases)} phases. The {winner.upper()} agent emerged victorious with "
            f"the highest cumulative score of {rankings[0]['score']:.1f} points. "
            f"The debate featured rigorous exchanges, with the Researcher providing "
            f"evidence-based arguments, the Critic challenging logical foundations, "
            f"and the Analyst synthesizing perspectives. The Judge evaluated all "
            f"contributions and delivered a comprehensive verdict. This debate platform "
            f"demonstrates multi-agent AI reasoning with structured turn-taking, "
            f"argument scoring, and transparent reasoning chains."
        )

    def _generate_reasoning_analysis(self, transcript: List[dict], scores: Dict[str, float]) -> dict:
        """Generate a reasoning chain analysis."""
        agent_performance = {}
        for agent in ["researcher", "critic", "analyst", "judge"]:
            agent_turns = [t for t in transcript if t["agent"] == agent]
            if not agent_turns:
                continue
            turn_scores = [t.get("score", 0) for t in agent_turns]
            agent_performance[agent] = {
                "total_turns": len(agent_turns),
                "cumulative_score": scores.get(agent, 0),
                "avg_turn_score": round(sum(turn_scores) / len(turn_scores), 2) if turn_scores else 0,
                "best_turn": max(agent_turns, key=lambda t: t.get("score", 0))["argument"][:150] if agent_turns else "",
                "reasoning_style": self._classify_reasoning_style(agent_turns),
                "progression": [round(t.get("score", 0), 2) for t in agent_turns],
            }
        
        return {
            "agent_performance": agent_performance,
            "debate_quality": self._assess_debate_quality(transcript),
            "interaction_patterns": self._detect_interaction_patterns(transcript),
        }

    def _classify_reasoning_style(self, turns: List[dict]) -> str:
        """Classify the reasoning style of an agent."""
        if not turns:
            return "unknown"
        agent = turns[0]["agent"]
        styles = {
            "researcher": "Empirical-Inductive: Builds arguments from evidence to conclusions",
            "critic": "Analytical-Deductive: Examines premises to challenge conclusions",
            "analyst": "Synthetic-Balanced: Integrates multiple perspectives holistically",
            "judge": "Evaluative-Decisive: Weighs evidence and renders authoritative judgments",
        }
        return styles.get(agent, "General reasoning")

    def _assess_debate_quality(self, transcript: List[dict]) -> dict:
        """Assess overall debate quality metrics."""
        scores = [t.get("score", 0) for t in transcript]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        quality_level = "Excellent" if avg_score > 7.5 else "Good" if avg_score > 6.0 else "Moderate" if avg_score > 4.5 else "Basic"
        
        return {
            "overall_quality": quality_level,
            "average_argument_score": round(avg_score, 2),
            "score_variance": round(
                sum((s - avg_score) ** 2 for s in scores) / len(scores) if scores else 0, 2
            ),
            "total_arguments": len(transcript),
        }

    def _detect_interaction_patterns(self, transcript: List[dict]) -> List[str]:
        """Detect notable interaction patterns in the debate."""
        patterns = []
        agents = [t["agent"] for t in transcript]
        
        if agents.count("researcher") > agents.count("critic"):
            patterns.append("Evidence-heavy debate with strong research grounding")
        if agents.count("critic") >= 2:
            patterns.append("Active counter-argumentation with multiple critical challenges")
        if "analyst" in agents:
            patterns.append("Synthesis-driven debate with balanced analysis")
        if len(set(agents)) >= 3:
            patterns.append("Multi-perspective engagement across all agent roles")
        
        return patterns or ["Standard linear debate progression"]

    def _generate_chart_data(self, transcript: List[dict], scores: Dict[str, float]) -> dict:
        """Generate chart data for GitHub Pages visualization."""
        # Score progression per agent
        agent_progression = {}
        agent_running = {}
        
        for turn in transcript:
            agent = turn["agent"]
            score = turn.get("score", 0)
            if agent not in agent_progression:
                agent_progression[agent] = []
                agent_running[agent] = 0
            agent_running[agent] += score
            agent_progression[agent].append(round(agent_running[agent], 2))
        
        # Bar chart data (final scores)
        bar_labels = [a.capitalize() for a in scores.keys()]
        bar_values = [round(v, 2) for v in scores.values()]
        
        # Radar chart dimensions
        agents_for_radar = ["researcher", "critic", "analyst"]
        radar_data = {}
        for agent in agents_for_radar:
            agent_turns = [t for t in transcript if t["agent"] == agent]
            if agent_turns:
                radar_data[agent] = {
                    "logic": round(sum(t.get("score", 0) for t in agent_turns) / len(agent_turns) * 1.0, 2),
                    "evidence": round(sum(t.get("score", 0) for t in agent_turns) / len(agent_turns) * 0.9, 2),
                    "rhetoric": round(sum(t.get("score", 0) for t in agent_turns) / len(agent_turns) * 0.85, 2),
                    "relevance": round(sum(t.get("score", 0) for t in agent_turns) / len(agent_turns) * 0.95, 2),
                }
        
        return {
            "score_progression": agent_progression,
            "final_scores_bar": {"labels": bar_labels, "values": bar_values},
            "radar_data": radar_data,
            "phase_scores": self._phase_score_chart(transcript),
        }

    def _phase_score_chart(self, transcript: List[dict]) -> dict:
        """Generate phase-based score data for charts."""
        phases = {}
        for turn in transcript:
            phase = turn["phase"]
            score = turn.get("score", 0)
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(score)
        
        return {
            phase: round(sum(scores) / len(scores), 2)
            for phase, scores in phases.items()
        }

    def _format_score_summary(self, scores: Dict[str, float]) -> str:
        """Format scores as a readable string."""
        sorted_scores = sorted(
            [(k, v) for k, v in scores.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        lines = []
        medals = ["🥇", "🥈", "🥉", "4th"]
        for i, (agent, score) in enumerate(sorted_scores):
            medal = medals[i] if i < len(medals) else f"#{i+1}"
            lines.append(f"{medal} {agent.capitalize()}: {score:.1f} pts")
        return " | ".join(lines)

    def export_json(self, summary: dict, filepath: str = "debate_summary.json"):
        """Export summary to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Summary exported to {filepath}")

    def export_markdown(self, summary: dict, filepath: str = "DEBATE_REPORT.md") -> str:
        """Export summary as a Markdown report."""
        md = [
            f"# Debate Report: {summary['topic']}",
            f"",
            f"**Generated:** {summary['generated_at']}",
            f"**Winner:** 🏆 {summary['winner_name']}",
            f"**Total Turns:** {summary['total_turns']}",
            f"",
            f"## Executive Summary",
            f"",
            f"{summary['executive_summary']}",
            f"",
            f"## Final Scores",
            f"",
            f"{summary['score_summary']}",
            f"",
            f"## Rankings",
            f"",
        ]
        for r in summary.get("rankings", []):
            md.append(f"- {r['medal']} **{r['agent'].capitalize()}**: {r['score']} points")
        
        md.extend([
            f"",
            f"## Judge's Verdict",
            f"",
            f"> *Delivered by the Judge agent after evaluating all arguments.*",
            f"",
            f"## Reasoning Analysis",
            f"",
        ])
        
        analysis = summary.get("reasoning_analysis", {})
        for agent, perf in analysis.get("agent_performance", {}).items():
            md.extend([
                f"### {agent.capitalize()}",
                f"- **Reasoning Style:** {perf['reasoning_style']}",
                f"- **Total Turns:** {perf['total_turns']}",
                f"- **Avg Turn Score:** {perf['avg_turn_score']}",
                f"- **Best Argument:** _{perf['best_turn']}_",
                f"",
            ])
        
        content = "\n".join(md)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Markdown report exported to {filepath}")
        return content


if __name__ == "__main__":
    gen = SummaryGenerator()
    
    # Demo transcript
    sample = {
        "topic": "AI will transform education",
        "transcript": [
            {"agent": "researcher", "agent_name": "Researcher", "agent_emoji": "🔬",
             "phase": "Opening Statement", "argument": "Research shows AI tutoring improves student outcomes by 30%.", "score": 7.5, "round": 0},
            {"agent": "critic", "agent_name": "Critic", "agent_emoji": "⚔️",
             "phase": "Opening Statement", "argument": "These studies are flawed and lack longitudinal data.", "score": 6.8, "round": 0},
            {"agent": "analyst", "agent_name": "Analyst", "agent_emoji": "📊",
             "phase": "Opening Statement", "argument": "Both perspectives have merit. AI offers personalization but equity concerns remain.", "score": 7.2, "round": 0},
            {"agent": "judge", "agent_name": "Judge", "agent_emoji": "⚖️",
             "phase": "Verdict", "argument": "After evaluating all arguments, the Analyst presented the most balanced view.", "score": 8.0, "round": 0},
        ],
        "scores": {"researcher": 15.0, "critic": 13.6, "analyst": 21.6, "judge": 8.0},
        "verdict": {"text": "Analyst wins", "winner": "analyst", "winner_name": "Analyst", "final_scores": {}},
    }
    
    summary = gen.generate(**sample)
    print("Summary Generated!")
    print("Winner:", summary["winner_name"])
    print("Score Summary:", summary["score_summary"])
    gen.export_markdown(summary)
