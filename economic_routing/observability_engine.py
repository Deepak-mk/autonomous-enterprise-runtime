from typing import List, Dict, Any

class ObservabilityEngine:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def record(
        self, 
        task_id: str, 
        description: str, 
        complexity: str, 
        model_name: str, 
        latency: float, 
        actual_cost: float, 
        baseline_cost: float
    ):
        """Records a routing event decision trace."""
        self.history.append({
            "task_id": task_id,
            "description": description,
            "complexity": complexity,
            "model": model_name,
            "latency": latency,
            "cost": actual_cost,
            "baseline": baseline_cost,
            "savings": max(0.0, baseline_cost - actual_cost)
        })

    def get_summary(self) -> Dict[str, Any]:
        """Calculates total statistics and savings comparison against a premium-only baseline."""
        total_tasks = len(self.history)
        total_cost = sum(x["cost"] for x in self.history)
        total_baseline = sum(x["baseline"] for x in self.history)
        total_savings = total_baseline - total_cost
        savings_percentage = (total_savings / total_baseline * 100) if total_baseline > 0 else 0.0
        avg_latency = sum(x["latency"] for x in self.history) / total_tasks if total_tasks > 0 else 0.0

        return {
            "total_tasks": total_tasks,
            "total_actual_cost": total_cost,
            "total_baseline_cost": total_baseline,
            "total_savings": total_savings,
            "savings_percentage": savings_percentage,
            "avg_latency_seconds": round(avg_latency, 2)
        }
