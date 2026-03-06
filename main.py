"""
main.py
--------
Entry point for the Multi-Agent AI Debate Platform.

Usage:
  python main.py --topic "Your debate topic here" [--rounds N] [--output path]

Examples:
  python main.py --topic "AI will surpass human intelligence" --rounds 3
  python main.py --topic "Remote work is better than office work" --rounds 2 --output results.json
  python main.py --demo  (runs with built-in sample topic)
"""

import argparse
import json
import os
import sys
import time
from agent_controller import AgentController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-Agent AI Debate Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agents:
  🔬 Researcher  - Presents evidence-based arguments
  ⚔️  Critic      - Challenges and counters arguments
  📊 Analyst     - Provides balanced synthesis
  ⚖️  Judge       - Evaluates and delivers verdict

Workflow:
  Topic → Opening Statements → Debate Rounds → Analysis → Verdict → Summary
        """
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        help="The debate topic (required unless --demo is used)",
    )
    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=3,
        help="Number of debate rounds (default: 3)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="docs/debate_results.json",
        help="Output file path for results (default: docs/debate_results.json)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with a built-in demo topic",
    )
    parser.add_argument(
        "--openai",
        action="store_true",
        help="Use OpenAI API (requires OPENAI_API_KEY env variable)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)",
    )
    return parser.parse_args()


DEMO_TOPICS = [
    "Artificial General Intelligence will be developed within the next 20 years",
    "Remote work is more productive than office work",
    "Social media has done more harm than good to society",
    "Universal Basic Income should be implemented globally",
    "Nuclear energy is the best solution to climate change",
]


def get_openai_backend(model: str):
    """Initialize OpenAI backend if available."""
    try:
        from openai import OpenAI
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Running in simulation mode.")
            return None
        
        client = OpenAI(api_key=api_key)
        
        class OpenAIBackend:
            def __init__(self, client, model):
                self.client = client
                self.model = model
            
            def generate(self, system: str, messages: list, user: str) -> str:
                msgs = [{"role": "system", "content": system}]
                msgs.extend(messages[-6:])  # Keep last 6 turns for context
                msgs.append({"role": "user", "content": user})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=msgs,
                    max_tokens=400,
                    temperature=0.7,
                )
                return response.choices[0].message.content
        
        print(f"OpenAI backend initialized with model: {model}")
        return OpenAIBackend(client, model)
    
    except ImportError:
        print("OpenAI package not installed. Install with: pip install openai")
        return None


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║           🤖 MULTI-AGENT AI DEBATE PLATFORM                 ║
║                                                              ║
║  Agents: 🔬 Researcher | ⚔️  Critic | 📊 Analyst | ⚖️  Judge  ║
║  Features: Multi-turn Reasoning | Argument Scoring          ║
║           Debate Transcripts | GitHub Pages Output          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def save_results(results: dict, output_path: str):
    """Save debate results to JSON file."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Results saved to: {output_path}")


def print_summary(results: dict):
    """Print a formatted summary to console."""
    summary = results.get("summary", {})
    scores = results.get("scores", {})
    verdict = results.get("verdict", {})
    
    print("\n" + "="*62)
    print("  📋 DEBATE SUMMARY")
    print("="*62)
    print(f"  Topic: {results['topic']}")
    print(f"  Turns: {summary.get('total_turns', len(results.get('transcript', [])))}")
    print(f"  Quality: {summary.get('reasoning_analysis', {}).get('debate_quality', {}).get('overall_quality', 'Good')}")
    print()
    print("  📊 FINAL SCORES:")
    for agent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(score / 2)
        print(f"    {agent.capitalize():<12} {score:>6.1f} pts  {bar}")
    print()
    print(f"  🏆 WINNER: {verdict.get('winner_name', 'Unknown').upper()}")
    print()
    print("  📝 Executive Summary:")
    exec_summary = summary.get("executive_summary", "No summary available.")
    # Word-wrap at 60 chars
    words = exec_summary.split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 62:
            print(line)
            line = "    " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)
    print("="*62)


def main():
    print_banner()
    args = parse_args()
    
    # Determine topic
    if args.demo:
        import random
        topic = random.choice(DEMO_TOPICS)
        print(f"🎲 Demo mode - using topic: '{topic}'\n")
    elif args.topic:
        topic = args.topic
    else:
        print("Error: Please provide a --topic or use --demo mode")
        print("Example: python main.py --topic 'AI will change education'")
        sys.exit(1)
    
    # Set up LLM backend
    llm_backend = None
    if args.openai:
        llm_backend = get_openai_backend(args.model)
    
    if llm_backend is None:
        print("ℹ️  Running in simulation mode (no LLM backend configured)")
        print("   To use OpenAI: python main.py --openai --topic 'your topic'\n")
    
    # Run debate
    start_time = time.time()
    controller = AgentController(
        topic=topic,
        num_rounds=args.rounds,
        llm_backend=llm_backend,
    )
    
    results = controller.run_debate()
    elapsed = time.time() - start_time
    
    print(f"\n⏱️  Debate completed in {elapsed:.1f} seconds")
    
    # Save results
    save_results(results, args.output)
    
    # Print summary
    print_summary(results)
    
    print(f"\n🌐 View results on GitHub Pages: https://PranayMahendrakar.github.io/multi-agent-debate-platform/")
    print("   (Upload debate_results.json to docs/ folder and push to GitHub)")


if __name__ == "__main__":
    main()
