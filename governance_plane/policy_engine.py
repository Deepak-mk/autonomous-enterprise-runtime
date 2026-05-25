from typing import Dict, Any, List

class PolicyResult:
    def __init__(self, allowed: bool, reason: str):
        self.allowed = allowed
        self.reason = reason

class GovernancePolicyEngine:
    def __init__(self):
        # Configure policies
        self.policies = {
            "spend_cap": 100.00,
            "prohibited_actions": ["purge_database", "delete_user_record"],
            "restricted_tools": ["deploy_code", "write_raw_sql"]
        }

    def evaluate(self, agent_name: str, action: str, details: Dict[str, Any]) -> PolicyResult:
        """Evaluates whether an action complies with corporate boundaries and limits."""
        # 1. Prohibited Actions Check
        if action in self.policies["prohibited_actions"]:
            return PolicyResult(
                allowed=False,
                reason=f"Action '{action}' is strictly prohibited for all agents."
            )

        # 2. Spend Limit Policy Check
        if action == "approve_refund":
            amount = details.get("amount", 0.0)
            spend_limit = self.policies["spend_cap"]
            if amount > spend_limit:
                return PolicyResult(
                    allowed=False,
                    reason=f"Refund request of ${amount} exceeds the automated auto-approval cap of ${spend_limit}."
                )

        # 3. Restricted Tools Check
        if action in self.policies["restricted_tools"]:
            if agent_name != "AdminAgent":
                return PolicyResult(
                    allowed=False,
                    reason=f"Tool '{action}' is restricted. Access requires AdminAgent privileges."
                )

        return PolicyResult(allowed=True, reason="Compliant with all governance boundaries.")
