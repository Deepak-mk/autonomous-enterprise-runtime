from typing import Dict, List

class PermissionManager:
    def __init__(self):
        # Role mapping
        self.roles = {
            "SupportAgent": ["read_customer", "write_support_ticket", "propose_refund"],
            "BillingAgent": ["read_customer", "propose_refund", "approve_refund", "execute_wire_transfer"],
            "AdminAgent": ["read_customer", "propose_refund", "approve_refund", "execute_wire_transfer", "deploy_code", "write_raw_sql"]
        }

    def register_agent_role(self, agent_name: str, role: str):
        """Maps an agent instance to an RBAC role."""
        pass  # Map roles dynamically if needed

    def verify_permission(self, agent_role: str, action: str) -> bool:
        """Verifies if a specific role possesses permission for an action."""
        allowed_scopes = self.roles.get(agent_role, [])
        return action in allowed_scopes
