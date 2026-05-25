import time
from typing import List, Dict, Any

class GovernanceTelemetry:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def record_policy(self, agent: str, action: str, allowed: bool, reason: str):
        """Records policy evaluation outcome."""
        self.audit_log.append({
            "timestamp": time.time(),
            "scope": "POLICY",
            "agent": agent,
            "action": action,
            "result": "ALLOW" if allowed else "BLOCK",
            "details": reason
        })

    def record_permission(self, agent: str, action: str, verified: bool):
        """Records role permission check logs."""
        self.audit_log.append({
            "timestamp": time.time(),
            "scope": "PERMISSION",
            "agent": agent,
            "action": action,
            "result": "AUTHORIZED" if verified else "DENIED",
            "details": f"Role checked against scope permissions for action '{action}'."
        })

    def record_escalation(self, details: Dict[str, Any]):
        """Records escalation controller events."""
        self.audit_log.append({
            "timestamp": time.time(),
            "scope": "ESCALATION",
            "agent": details["escalated_from"],
            "action": "HUMAN_OVERRIDE",
            "result": details["outcome"],
            "details": f"Approved by {details['approver']}. Reason: {details['reason']}"
        })

    def record_arbitration(self, details: Dict[str, Any]):
        """Records arbitration results."""
        self.audit_log.append({
            "timestamp": time.time(),
            "scope": "ARBITRATION",
            "agent": details["winner"],
            "action": details["winning_action"],
            "result": "RESOLVED",
            "details": details["reason"]
        })
