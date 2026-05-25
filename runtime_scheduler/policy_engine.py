from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    requires_human_approval: bool = False
    alternative_action: Optional[str] = None

class PolicyEngine:
    def __init__(self, max_cost_limit: float = 10.0, transaction_limit: float = 100.0):
        self.max_cost_limit = max_cost_limit
        self.transaction_limit = transaction_limit
        
        # Predefined list of sensitive tools/actions
        self.sensitive_tools = {
            "delete_database", 
            "deploy_to_production", 
            "send_refund", 
            "execute_wire_transfer"
        }
        
        # Tools prohibited for specific lower-tier agents
        self.agent_restrictions = {
            "SupportAgent": ["deploy_to_production", "execute_wire_transfer"],
            "AnalysisAgent": ["send_refund", "delete_database", "deploy_to_production", "execute_wire_transfer"]
        }

    def check_action(
        self, 
        task_id: str, 
        agent_name: str, 
        tool_name: str, 
        args: Dict[str, Any], 
        accumulated_cost: float
    ) -> PolicyDecision:
        """Evaluates whether an agent's proposed tool action complies with system policies."""
        
        # 1. Budget check
        if accumulated_cost > self.max_cost_limit:
            return PolicyDecision(
                allowed=False,
                reason=f"Accumulated task cost (${accumulated_cost:.2f}) exceeds max policy limit (${self.max_cost_limit:.2f})",
                requires_human_approval=False
            )
            
        # 2. Agent restrictions check
        restricted_tools = self.agent_restrictions.get(agent_name, [])
        if tool_name in restricted_tools:
            return PolicyDecision(
                allowed=False,
                reason=f"Agent '{agent_name}' is restricted from executing the tool '{tool_name}'",
                requires_human_approval=False
            )
            
        # 3. Transaction limits check
        if tool_name == "send_refund" or tool_name == "execute_wire_transfer":
            amount = args.get("amount", 0.0)
            if amount > self.transaction_limit:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Transaction amount (${amount:.2f}) exceeds automated limit (${self.transaction_limit:.2f})",
                    requires_human_approval=True  # Escalation potential
                )
                
        # 4. Critical actions requiring confirmation
        if tool_name in ["delete_database", "deploy_to_production"]:
            return PolicyDecision(
                allowed=False,
                reason=f"Critical tool '{tool_name}' requires explicit human verification",
                requires_human_approval=True
            )
            
        # If all checks pass, allow the execution
        return PolicyDecision(
            allowed=True,
            reason="Action conforms to all policy boundaries",
            requires_human_approval=False
        )
