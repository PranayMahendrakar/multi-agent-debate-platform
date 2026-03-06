"""
conversation_manager.py
------------------------
Manages the conversation history and context for the multi-agent debate.
Tracks all turns, builds context windows, and maintains debate state.
"""

from typing import List, Dict, Optional
from collections import deque
import time


class ConversationManager:
    """
    Manages debate conversation history and context building.
    Supports sliding context windows and turn filtering by agent.
    """

    def __init__(self, topic: str, max_history: int = 50):
        self.topic = topic
        self.max_history = max_history
        self.history: deque = deque(maxlen=max_history)
        self.turn_count = 0
        self.session_start = time.time()

    def add_turn(self, role: str, content: str, metadata: Optional[dict] = None):
        """Add a new turn to the conversation history."""
        turn = {
            "role": role,
            "content": content,
            "turn_number": self.turn_count,
            "timestamp": time.strftime("%H:%M:%S"),
            "metadata": metadata or {},
        }
        self.history.append(turn)
        self.turn_count += 1

    def get_context(self, last_n: Optional[int] = None, roles: Optional[List[str]] = None) -> List[dict]:
        """
        Retrieve conversation context.
        
        Args:
            last_n: Return only the last N turns
            roles: Filter to specific agent roles only
            
        Returns:
            List of conversation turns as context messages
        """
        history = list(self.history)

        # Filter by roles if specified
        if roles:
            history = [t for t in history if t["role"] in roles]

        # Limit to last N turns
        if last_n:
            history = history[-last_n:]

        # Format as context messages for LLM
        return [
            {
                "role": "assistant" if t["role"] != "user" else "user",
                "name": t["role"],
                "content": f"[{t['role'].upper()}]: {t['content']}",
            }
            for t in history
        ]

    def get_formatted_transcript(self, include_scores: bool = False) -> str:
        """Return a human-readable transcript of the debate."""
        lines = [
            f"DEBATE TOPIC: {self.topic}",
            f"{'='*60}",
            "",
        ]
        for turn in self.history:
            lines.append(f"Turn {turn['turn_number']+1} | {turn['timestamp']} | {turn['role'].upper()}")
            lines.append(f"{turn['content']}")
            if include_scores and turn.get("metadata", {}).get("score"):
                lines.append(f"Score: {turn['metadata']['score']}")
            lines.append("")
        return "\n".join(lines)

    def get_turn_count_by_agent(self) -> Dict[str, int]:
        """Return count of turns per agent."""
        counts = {}
        for turn in self.history:
            counts[turn["role"]] = counts.get(turn["role"], 0) + 1
        return counts

    def get_agent_arguments(self, role: str) -> List[str]:
        """Get all arguments made by a specific agent."""
        return [t["content"] for t in self.history if t["role"] == role]

    def get_last_turn(self) -> Optional[dict]:
        """Get the most recent turn."""
        return self.history[-1] if self.history else None

    def get_session_duration(self) -> float:
        """Return debate session duration in seconds."""
        return time.time() - self.session_start

    def clear(self):
        """Clear all conversation history."""
        self.history.clear()
        self.turn_count = 0

    def to_dict(self) -> dict:
        """Serialize conversation manager state."""
        return {
            "topic": self.topic,
            "total_turns": self.turn_count,
            "history": list(self.history),
            "session_duration_seconds": round(self.get_session_duration(), 2),
            "turns_by_agent": self.get_turn_count_by_agent(),
        }


class ContextWindow:
    """
    Manages a sliding context window for LLM prompting.
    Ensures context doesn't exceed token limits.
    """

    def __init__(self, max_tokens: int = 4000, chars_per_token: int = 4):
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token
        self.max_chars = max_tokens * chars_per_token

    def truncate_context(self, context: List[dict], system_prompt: str = "") -> List[dict]:
        """Truncate context to fit within token budget."""
        available_chars = self.max_chars - len(system_prompt)
        result = []
        total_chars = 0

        # Process from most recent to oldest (LIFO)
        for turn in reversed(context):
            turn_chars = len(turn.get("content", ""))
            if total_chars + turn_chars <= available_chars:
                result.insert(0, turn)
                total_chars += turn_chars
            else:
                break

        return result

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from character count."""
        return len(text) // self.chars_per_token


if __name__ == "__main__":
    # Demo
    cm = ConversationManager("Should AI be regulated?")
    cm.add_turn("researcher", "Research shows AI regulation reduces harm by 40%.")
    cm.add_turn("critic", "That statistic lacks peer review and proper controls.")
    cm.add_turn("analyst", "Both points have merit. Regulation can help but needs careful design.")
    cm.add_turn("judge", "The debate highlights a need for evidence-based regulatory frameworks.")

    print(cm.get_formatted_transcript())
    print("Turns by agent:", cm.get_turn_count_by_agent())
    print("Context length:", len(cm.get_context()))
    print("Last 2 turns:", len(cm.get_context(last_n=2)))
