class ReasoningBudget:
    def __init__(self, max_budget: float = 0.50):
        self.max_budget = max_budget
        self.accumulated_cost = 0.0

    def has_budget(self, estimated_cost: float) -> bool:
        """Checks if the next step's estimated cost falls within the remaining budget."""
        return (self.accumulated_cost + estimated_cost) <= self.max_budget

    def spend(self, amount: float):
        """Records spending of compute resources."""
        self.accumulated_cost += amount

    def get_remaining(self) -> float:
        """Returns remaining available budget."""
        return max(0.0, self.max_budget - self.accumulated_cost)

    def is_exhausted(self) -> bool:
        """Returns True if the budget has been exceeded or fully spent."""
        return self.accumulated_cost >= self.max_budget
