import random
import time
from typing import Dict, Any
from economic_routing.task_classifier import TaskClassifier, TaskCharacteristics
from economic_routing.model_selector import ModelSelector
from economic_routing.reasoning_budget import ReasoningBudget
from economic_routing.observability_engine import ObservabilityEngine

class RoutingEngine:
    def __init__(
        self, 
        classifier: TaskClassifier, 
        model_selector: ModelSelector, 
        observability_engine: ObservabilityEngine
    ):
        self.classifier = classifier
        self.model_selector = model_selector
        self.observability_engine = observability_engine
        
        # Define baseline model for comparison (typically the premium generalist)
        self.baseline_model = "gpt-4o"

    def execute_task(
        self, 
        task_id: str, 
        description: str, 
        max_budget: float = 0.50
    ) -> Dict[str, Any]:
        """Classifies task requirements, matches a model within the budget, and simulates execution."""
        
        budget = ReasoningBudget(max_budget=max_budget)
        
        # 1. Classify Task
        chars = self.classifier.classify(description)
        
        # 2. Select Model within remaining budget
        model_spec = self.model_selector.select_model(
            complexity=chars.complexity,
            needs_reasoning=chars.needs_reasoning,
            remaining_budget=budget.get_remaining(),
            estimated_input=chars.estimated_tokens,
            estimated_output=500  # Default estimate for output
        )
        
        selected_model = model_spec["name"]
        
        # 3. Simulate execution token consumption
        # Introduce slight variability in output tokens
        actual_input_tokens = chars.estimated_tokens
        actual_output_tokens = int(500 * random.uniform(0.8, 1.2))
        
        actual_cost = self.model_selector.estimate_cost(
            selected_model, 
            actual_input_tokens, 
            actual_output_tokens
        )
        
        # 4. Record spend
        budget.spend(actual_cost)
        
        # 5. Compute baseline comparison (What would it cost on gpt-4o premium generalist?)
        baseline_cost = self.model_selector.estimate_cost(
            self.baseline_model, 
            actual_input_tokens, 
            actual_output_tokens
        )
        
        # Simulate latency delay
        latency = model_spec["latency_sec"]
        
        # Record trace details
        self.observability_engine.record(
            task_id=task_id,
            description=description,
            complexity=chars.complexity,
            model_name=selected_model,
            latency=latency,
            actual_cost=actual_cost,
            baseline_cost=baseline_cost
        )
        
        # Formatted trace logs to console
        print(f"[{task_id}] Routing Task: '{description[:40]}...'")
        print(f"  - Complexity : {chars.complexity} | Domain: {chars.domain}")
        if selected_model != chars.complexity:  # if budget constraint kicked in
            print(f"  - Model      : \033[93m{selected_model}\033[0m (Estimated Latency: {latency}s)")
        else:
            print(f"  - Model      : \033[94m{selected_model}\033[0m (Estimated Latency: {latency}s)")
        print(f"  - Cost       : \033[92m${actual_cost:.4f}\033[0m (Baseline GPT-4o: ${baseline_cost:.4f})")
        print(f"  - Status     : COMPLETED | Budget Remaining: ${budget.get_remaining():.4f}")
        print("-" * 60)
        
        return {
            "task_id": task_id,
            "model": selected_model,
            "cost": actual_cost,
            "baseline": baseline_cost,
            "latency": latency
        }
