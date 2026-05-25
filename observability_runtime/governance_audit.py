import time
from typing import List, Dict, Any

class GovernanceAudit:
    def __init__(self):
        self.audits: List[Dict[str, Any]] = []

    def record_policy_check(self, policy_name: str, passed: bool, reason: str, context: Dict[str, Any]):
        """Records a policy evaluation check by a governance module."""
        self.audits.append({
            "timestamp": time.time(),
            "type": "POLICY_CHECK",
            "policy": policy_name,
            "result": "PASS" if passed else "DENY",
            "reason": reason,
            "context": context
        })

    def record_approval(self, approver: str, transaction_id: str, outcome: str):
        """Records a Human-in-the-loop (HITL) or supervisor override approval."""
        self.audits.append({
            "timestamp": time.time(),
            "type": "HITL_APPROVAL",
            "approver": approver,
            "transaction_id": transaction_id,
            "result": outcome
        })

    def record_arbitration(self, topic: str, agents: List[str], winner: str, reason: str):
        """Records the outcome of a coordination conflict arbitration."""
        self.audits.append({
            "timestamp": time.time(),
            "type": "ARBITRATION",
            "topic": topic,
            "agents_involved": agents,
            "winner": winner,
            "reason": reason
        })
