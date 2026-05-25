import time
from typing import List, Dict, Any

class ReasoningStep:
    def __init__(self, thought: str, action: str, confidence: float):
        self.timestamp = time.time()
        self.thought = thought
        self.action = action
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "thought": self.thought,
            "action": self.action,
            "confidence": self.confidence
        }

class ReasoningTrace:
    def __init__(self):
        self.steps: List[ReasoningStep] = []

    def add_step(self, thought: str, action: str, confidence: float):
        """Logs a cognitive step in the agent's reasoning trace."""
        self.steps.append(ReasoningStep(thought, action, confidence))

    def get_trace(self) -> List[Dict[str, Any]]:
        """Returns the chronological list of reasoning steps."""
        return [step.to_dict() for step in self.steps]
