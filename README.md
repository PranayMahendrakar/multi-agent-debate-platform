# 🤖 Multi-Agent AI Debate Platform

> A sophisticated multi-agent AI debate environment featuring four specialized agents—Researcher, Critic, Analyst, and Judge—with multi-turn reasoning, argument scoring, and GitHub Pages visualization.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://PranayMahendrakar.github.io/multi-agent-debate-platform/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🌐 Live Demo

**[View Debate Results on GitHub Pages →](https://PranayMahendrakar.github.io/multi-agent-debate-platform/)**

---

## 🏗️ Architecture

```
Topic Input
    ↓
┌─────────────────────────────────────────────────┐
│              Agent Controller                    │
│  ┌──────────┐  ┌────────┐  ┌──────────┐  ┌──────┐ │
│  │Researcher│  │ Critic │  │ Analyst  │  │Judge │ │
│  │   🔬     │  │  ⚔️    │  │   📊     │  │  ⚖️  │ │
│  └──────────┘  └────────┘  └──────────┘  └──────┘ │
└─────────────────────────────────────────────────┘
    ↓               ↓               ↓
┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
│Conversation │ │  Argument    │ │ Summary          │
│  Manager   │ │  Evaluator   │ │ Generator        │
└─────────────┘ └──────────────┘ └──────────────────┘
    ↓
JSON Results → GitHub Pages → Visual Dashboard
```

---

## 🤖 Agents

| Agent | Role | Reasoning Style |
|-------|------|----------------|
| 🔬 **Researcher** | Presents evidence-based arguments with data, studies, and empirical findings | Empirical-Inductive |
| ⚔️ **Critic** | Challenges arguments, exposes logical fallacies, presents counter-evidence | Analytical-Deductive |
| 📊 **Analyst** | Provides balanced synthesis, weighs pros and cons objectively | Synthetic-Balanced |
| ⚖️ **Judge** | Evaluates all arguments, scores performance, delivers final verdict | Evaluative-Decisive |

---

## 🔄 Debate Workflow

```
1. OPENING STATEMENTS  →  Researcher, Critic, Analyst present positions
2. DEBATE ROUNDS (x3)  →  Rotating order, contextual rebuttals
3. ANALYSIS PHASE      →  Analyst synthesizes all arguments
4. VERDICT             →  Judge scores and declares winner
5. SUMMARY             →  Full report + GitHub Pages data
```

---

## 📁 Project Structure

```
multi-agent-debate-platform/
├── agent_controller.py       # Orchestrates debate workflow & turn-taking
├── conversation_manager.py   # Manages history, context windows
├── argument_evaluator.py     # Multi-dimensional argument scoring
├── summary_generator.py      # Report & JSON generation
├── main.py                   # CLI entry point
├── requirements.txt          # Dependencies
├── docs/
│   ├── index.html            # GitHub Pages dashboard
│   └── debate_results.json   # Debate data (Chart.js visualized)
└── README.md
```

---

## 🚀 Quick Start

### Run with simulation mode (no API key needed)
```bash
git clone https://github.com/PranayMahendrakar/multi-agent-debate-platform.git
cd multi-agent-debate-platform
python main.py --demo
```

### Run with custom topic
```bash
python main.py --topic "Remote work is more productive than office work" --rounds 3
```

### Run with OpenAI (real LLM responses)
```bash
export OPENAI_API_KEY=your_key_here
python main.py --openai --topic "AI will transform education" --rounds 3
```

### View help
```bash
python main.py --help
```

---

## 📊 Features

### Multi-Turn Reasoning
- Agents build on previous arguments with full conversation context
- Sliding context window (last N turns) for efficient LLM prompting
- Turn rotation across rounds for fair argumentation

### Argument Scoring (0-10 scale)
Each argument is evaluated on 4 dimensions with phase-specific weights:

| Dimension | Opening | Debate | Analysis | Verdict |
|-----------|---------|--------|----------|---------|
| Logic | 30% | 30% | 35% | 40% |
| Evidence | 35% | 30% | 30% | 30% |
| Rhetoric | 20% | 20% | 15% | 15% |
| Relevance | 15% | 20% | 20% | 15% |

Logical fallacy detection applies penalties for: strawman arguments, ad hominem attacks, circular reasoning, false dichotomies.

### GitHub Pages Dashboard
- 📊 Bar chart: Final score comparison
- 📈 Line chart: Score progression across rounds
- 🔄 Phase chart: Average scores per debate phase
- 🕸️ Radar chart: Multi-dimensional performance (logic, evidence, rhetoric, relevance)
- 💬 Filterable transcript: View by agent or all at once
- 🧠 Reasoning analysis: Agent style, progression dots, best argument
- 🏆 Winner announcement with verdict text

---

## 🔌 LLM Backend Integration

The platform supports any LLM through the pluggable backend interface:

```python
class MyLLMBackend:
    def generate(self, system: str, messages: list, user: str) -> str:
        # Your LLM call here
        return response_text

controller = AgentController(
    topic="Your debate topic",
    num_rounds=3,
    llm_backend=MyLLMBackend()
)
results = controller.run_debate()
```

**Supported backends:**
- 🤖 OpenAI (GPT-4o, GPT-4o-mini) — built-in via `--openai` flag
- 🧠 Anthropic Claude — plug in via custom backend
- 🔮 Google Gemini — plug in via custom backend
- 🦙 Ollama (local LLMs) — plug in via custom backend

---

## 📤 Output

Running a debate produces:
1. **`docs/debate_results.json`** — Full structured results for GitHub Pages
2. **Console output** — Real-time debate progress with scores
3. **DEBATE_REPORT.md** — Markdown report (via `SummaryGenerator.export_markdown()`)

---

## 🛠️ Module Reference

### `AgentController`
```python
AgentController(topic, num_rounds=3, llm_backend=None)
controller.run_debate() → dict  # Full results
```

### `ConversationManager`
```python
ConversationManager(topic, max_history=50)
cm.add_turn(role, content)
cm.get_context(last_n=None, roles=None) → list
cm.get_formatted_transcript() → str
```

### `ArgumentEvaluator`
```python
ArgumentEvaluator(max_score=10.0)
evaluator.score_argument(text, phase, topic) → float
evaluator.compare_arguments(args, phase) → list
evaluator.get_statistics() → dict
```

### `SummaryGenerator`
```python
SummaryGenerator()
generator.generate(topic, transcript, scores, verdict) → dict
generator.export_json(summary, filepath)
generator.export_markdown(summary, filepath)
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with Python · Chart.js · GitHub Pages*
