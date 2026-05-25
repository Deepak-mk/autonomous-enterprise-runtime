import time
from governance_plane.policy_engine import GovernancePolicyEngine
from governance_plane.permission_manager import PermissionManager
from governance_plane.escalation_controller import EscalationController
from governance_plane.arbitration_engine import GovernanceArbitrationEngine
from governance_plane.governance_telemetry import GovernanceTelemetry
from governance_plane.replay_engine import GovernanceReplayEngine

def run_simulation():
    # Initialize components
    policy_engine = GovernancePolicyEngine()
    permission_manager = PermissionManager()
    escalation_controller = EscalationController()
    arbitration_engine = GovernanceArbitrationEngine()
    telemetry = GovernanceTelemetry()
    replay_engine = GovernanceReplayEngine()

    print("\n" + "="*80)
    print("  STARTING SOVEREIGN GOVERNANCE PLANE SIMULATION")
    print("="*80 + "\n")

    # SCENARIO 1: Role-Based Access Control Checks
    print("--- SCENARIO 1: Role-Based Access Control Verification ---")
    
    # Check 1: Support agent reads customer details
    action_1 = "read_customer"
    verified_1 = permission_manager.verify_permission("SupportAgent", action_1)
    telemetry.record_permission("SupportAgent", action_1, verified_1)
    print(f"[RBAC Check] SupportAgent attempting '{action_1}' -> Authorized: {verified_1}")
    
    # Check 2: Support agent attempts database purge
    action_2 = "purge_database"
    verified_2 = permission_manager.verify_permission("SupportAgent", action_2)
    telemetry.record_permission("SupportAgent", action_2, verified_2)
    print(f"[RBAC Check] SupportAgent attempting '{action_2}' -> Authorized: {verified_2}")
    time.sleep(0.5)


    # SCENARIO 2: Policy Compliance & Escalation Controller
    print("\n--- SCENARIO 2: Policy Limit Violation & Human Escalation ---")
    refund_details = {"transaction_id": "TX-4001", "amount": 500.00}
    print(f"BillingAgent submitting refund of ${refund_details['amount']} for TX-4001...")
    
    # Evaluate policy boundaries
    policy_check = policy_engine.evaluate(
        agent_name="BillingAgent",
        action="approve_refund",
        details=refund_details
    )
    telemetry.record_policy("BillingAgent", "approve_refund", policy_check.allowed, policy_check.reason)
    
    if not policy_check.allowed:
        print(f"[Policy Blocked] Reason: {policy_check.reason}")
        
        # Trigger manager sign-off escalation
        escalation_result = escalation_controller.trigger_escalation(
            task_id="TX-4001",
            agent_name="BillingAgent",
            policy_name="Spend Limit Policy",
            details=refund_details
        )
        telemetry.record_escalation(escalation_result)
    time.sleep(0.5)


    # SCENARIO 3: Conflict Arbitration
    print("\n--- SCENARIO 3: Priority Authority Rank Arbitration ---")
    # Simulation: Conflicting agent commands on task TX-4002
    conflicts = {
        "BillingAgent": {
            "action": "execute_wire_transfer",
            "payload": {"amount": 10000.00}
        },
        "SecurityAgent": {
            "action": "lock_account",
            "payload": {"reason": "Abnormal activity flag"}
        }
    }
    
    arbitration_result = arbitration_engine.arbitrate(
        task_id="TX-4002",
        conflicts=conflicts
    )
    telemetry.record_arbitration(arbitration_result)
    time.sleep(0.5)


    # Run Audit trail playback
    print("\n")
    replay_engine.play(telemetry.audit_log)

if __name__ == "__main__":
    run_simulation()
