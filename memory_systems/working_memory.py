from typing import Dict, Any, List

class WorkingMemory:
    def __init__(self, task_id: str):
        self.task_id = task_id
        # Simple storage representing RAM/Registers
        self.variables: Dict[str, Any] = {}
        # Chronological steps within the current task execution
        self.execution_trace: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any):
        """Sets a variable in short-term working memory."""
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a variable from working memory."""
        return self.variables.get(key, default)

    def add_step(self, tool_name: str, args: Dict[str, Any], output: Any):
        """Logs a step in the active task execution trace."""
        self.execution_trace.append({
            "tool": tool_name,
            "args": args,
            "output": output
        })

    def clear(self):
        """Clears short-term memory after task execution completes."""
        self.variables.clear()
        self.execution_trace.clear()

    def get_summary(self) -> Dict[str, Any]:
        """Returns a snapshot summary of working memory."""
        return {
            "variables": self.variables.copy(),
            "trace_length": len(self.execution_trace)
        }
