import time
from typing import Dict, Any

class EscalationController:
    def __init__(self):
        pass

    def trigger_escalation(
        self, 
        task_id: str, 
        agent_name: str, 
        policy_name: str, 
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Escalates a task execution block to a human supervisor for override sign-off."""
        print(f"\n[ESCALATION TRIGGERED] Task '{task_id}' blocked by policy '{policy_name}'.")
        print(f"  - Agent  : {agent_name}")
        print(f"  - Context: {details}")
        print("  - Routing approval ticket to Human Operations...")
        
        # Simulate human decision delay
        time.sleep(0.3)
        
        # Simulating automated human override approval
        override_authorizer = "Operations_Manager_Sarah"
        resolution = "APPROVED_OVERRIDE"
        reason = "Customer verified via phone. High lifetime value customer."
        
        print(f"  - Response: Approved by {override_authorizer} (Reason: {reason})")
        
        return {
            "task_id": task_id,
            "escalated_from": agent_name,
            "policy": policy_name,
            "approver": override_authorizer,
            "outcome": resolution,
            "reason": reason
        }
    
    def escalate_critical_error(self, task_id: str, error_message: str) -> str:
        """Escalates fatal errors to engineer pager alerts."""
        return "PAGER_DISPATCHED"
