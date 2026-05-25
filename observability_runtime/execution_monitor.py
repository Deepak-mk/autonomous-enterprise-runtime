import time
from typing import List, Dict, Any

class ExecutionMonitor:
    def __init__(self):
        self.tool_calls: List[Dict[str, Any]] = []
        self.api_metrics: List[Dict[str, Any]] = []

    def record_tool_call(self, tool_name: str, args: Dict[str, Any], duration: float, success: bool, output: Any):
        """Records metadata about a tool execution."""
        self.tool_calls.append({
            "timestamp": time.time(),
            "tool": tool_name,
            "args": args,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            "output": str(output)
        })

    def record_api_call(self, model: str, input_tokens: int, output_tokens: int, cost: float, duration: float):
        """Records LLM API token consumption and compute cost."""
        self.api_metrics.append({
            "timestamp": time.time(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "duration_sec": round(duration, 3)
        })

    def get_totals(self) -> Dict[str, Any]:
        """Aggregates total runtime statistics for execution audits."""
        total_cost = sum(x["cost"] for x in self.api_metrics)
        total_tokens = sum(x["input_tokens"] + x["output_tokens"] for x in self.api_metrics)
        avg_tool_duration = sum(x["duration_ms"] for x in self.tool_calls) / len(self.tool_calls) if self.tool_calls else 0.0
        
        return {
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "tool_call_count": len(self.tool_calls),
            "avg_tool_duration_ms": round(avg_tool_duration, 2)
        }
