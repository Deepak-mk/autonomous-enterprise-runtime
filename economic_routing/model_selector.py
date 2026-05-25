from typing import Dict, Any, List

class ModelSelector:
    def __init__(self):
        # Pricing structured as cost per 1,000,000 tokens
        self.models = {
            "gpt-4o-mini": {
                "name": "gpt-4o-mini",
                "input_cost_1m": 0.15,
                "output_cost_1m": 0.60,
                "latency_sec": 0.4,
                "capability": 4.0  # arbitrary rank
            },
            "gpt-3.5-turbo": {
                "name": "gpt-3.5-turbo",
                "input_cost_1m": 0.50,
                "output_cost_1m": 1.50,
                "latency_sec": 0.6,
                "capability": 5.0
            },
            "claude-3-5-sonnet": {
                "name": "claude-3-5-sonnet",
                "input_cost_1m": 3.00,
                "output_cost_1m": 15.00,
                "latency_sec": 1.2,
                "capability": 9.0
            },
            "gpt-4o": {
                "name": "gpt-4o",
                "input_cost_1m": 5.00,
                "output_cost_1m": 15.00,
                "latency_sec": 1.0,
                "capability": 9.0
            },
            "o1-mini": {
                "name": "o1-mini",
                "input_cost_1m": 3.00,
                "output_cost_1m": 12.00,
                "latency_sec": 3.5,  # high latency due to reasoning time
                "capability": 9.5
            },
            "deepseek-r1": {
                "name": "deepseek-r1",
                "input_cost_1m": 2.50,
                "output_cost_1m": 8.00,
                "latency_sec": 5.0,
                "capability": 9.8
            }
        }

    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimates cost based on token sizes and model specs."""
        model = self.models.get(model_name)
        if not model:
            return 0.05
            
        in_cost = (input_tokens / 1_000_000) * model["input_cost_1m"]
        out_cost = (output_tokens / 1_000_000) * model["output_cost_1m"]
        return in_cost + out_cost

    def select_model(
        self, 
        complexity: str, 
        needs_reasoning: bool, 
        remaining_budget: float,
        estimated_input: int,
        estimated_output: int
    ) -> Dict[str, Any]:
        """Selects the best available model, downgrading if remaining budget is too tight."""
        
        # 1. Map target model based on complexity and reasoning needs
        if complexity == "CRITICAL" or needs_reasoning:
            target = "deepseek-r1" if complexity == "CRITICAL" else "o1-mini"
        elif complexity == "HIGH":
            target = "gpt-4o"
        elif complexity == "MEDIUM":
            target = "gpt-3.5-turbo"
        else:
            target = "gpt-4o-mini"
            
        # 2. Budget constraint check
        estimated_cost = self.estimate_cost(target, estimated_input, estimated_output)
        
        if estimated_cost <= remaining_budget:
            return self.models[target]
            
        # 3. Budget fallback loop (find cheapest model that fits the budget)
        fallback_candidates = sorted(
            self.models.values(), 
            key=lambda m: self.estimate_cost(m["name"], estimated_input, estimated_output)
        )
        
        for model in fallback_candidates:
            cost = self.estimate_cost(model["name"], estimated_input, estimated_output)
            if cost <= remaining_budget:
                # Return the best option that fits budget constraints
                return model
                
        # If even the cheapest model exceeds budget, return cheapest model as absolute fallback
        return fallback_candidates[0]
