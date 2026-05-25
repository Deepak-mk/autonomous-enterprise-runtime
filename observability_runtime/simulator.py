import time
from observability_runtime.reasoning_trace import ReasoningTrace
from observability_runtime.execution_monitor import ExecutionMonitor
from observability_runtime.memory_telemetry import MemoryTelemetry
from observability_runtime.governance_audit import GovernanceAudit
from observability_runtime.replay_engine import ReplayEngine

def run_simulation():
    print("\n" + "="*80)
    print("  STARTING AUTONOMOUS AGENT OBSERVABILITY RUNTIME SIMULATION")
    print("="*80 + "\n")

    # Initialize observability telemetry probes
    reasoning = ReasoningTrace()
    execution = ExecutionMonitor()
    memory = MemoryTelemetry()
    governance = GovernanceAudit()
    replay_engine = ReplayEngine()

    print("[SYSTEM] Probes attached. Recording session for task 'Process Corporate Refund Audit (TX-900)'...")
    time.sleep(0.5)

    # --- STEP 1: Plan & Receive Context ---
    reasoning.add_step(
        thought="Dispute TX-900 received. Loading customer transaction history and amount data.",
        action="load_context",
        confidence=0.98
    )
    memory.log_write("WORKING", "tx_id", "TX-900")
    memory.log_write("WORKING", "dispute_amount", 250.00)
    time.sleep(0.1)

    # --- STEP 2: Policy Validation ---
    reasoning.add_step(
        thought="Evaluating dispute amount against corporate auto-refund limits in semantic memory.",
        action="check_policy",
        confidence=0.95
    )
    memory.log_read("SEMANTIC", "refund_limit", 100.00)
    governance.record_policy_check(
        policy_name="Auto-Refund Authorization Limit",
        passed=False,
        reason="Dispute amount ($250.00) exceeds automatic refund policy cap ($100.00).",
        context={"dispute_amount": 250.00, "limit": 100.00}
    )
    time.sleep(0.1)

    # --- STEP 3: Escalation and Human in the Loop ---
    reasoning.add_step(
        thought="Dispute exceeds limit. Escalating task details to Slack and waiting for manager approval.",
        action="request_approval",
        confidence=0.88
    )
    
    # Tool Execution Telemetry
    tool_start = time.time()
    # Simulate slack call latency
    time.sleep(0.05)
    execution.record_tool_call(
        tool_name="trigger_slack_approval",
        args={"channel": "#billing-alerts", "tx_id": "TX-900", "amount": 250.00},
        duration=time.time() - tool_start,
        success=True,
        output="Slack notification delivered (Thread: p1748293)"
    )
    
    # Governance records approval event
    governance.record_approval(
        approver="Admin_Sarah",
        transaction_id="TX-900",
        outcome="APPROVED"
    )
    time.sleep(0.1)

    # --- STEP 4: Execution Gateway Tool ---
    reasoning.add_step(
        thought="Manager override approval confirmed. Directing Stripe payment gateway API to release refund.",
        action="execute_payment_refund",
        confidence=0.99
    )
    
    # Tool Execution Telemetry
    tool_start = time.time()
    time.sleep(0.15)  # Simulate Stripe network latency
    execution.record_tool_call(
        tool_name="stripe_refund_gateway",
        args={"tx_id": "TX-900", "amount": 250.00},
        duration=time.time() - tool_start,
        success=True,
        output="Refund transaction resolved (Stripe ID: ch_3N2s9L)"
    )
    
    # LLM API Call Telemetry
    execution.record_api_call(
        model="gpt-4o",
        input_tokens=1500,
        output_tokens=320,
        cost=0.0123,
        duration=1.45
    )
    time.sleep(0.1)

    # --- STEP 5: Consolidate Memory ---
    reasoning.add_step(
        thought="dispute transaction resolved successfully. Running memory sync consolidations.",
        action="consolidate_memories",
        confidence=0.92
    )
    memory.log_sync("WORKING", "EPISODIC", "Saved transaction trace history as EP-1004")
    memory.log_sync("EPISODIC", "SEMANTIC", "Updated Customer 104's consolidated statistics in knowledge base.")
    time.sleep(0.1)

    print("[SYSTEM] Task execution complete. Detaching probes and generating replay trail...")
    time.sleep(0.5)

    # --- STEP 6: Compile and Playback Replay Trail ---
    timeline = replay_engine.build_timeline(
        reasoning=reasoning.get_trace(),
        execution_tools=execution.tool_calls,
        execution_apis=execution.api_metrics,
        memory_ops=memory.operations,
        governance_audits=governance.audits
    )

    replay_engine.play(timeline)

    # Observability Statistics Summary
    totals = execution.get_totals()
    print("="*80)
    print("  OBSERVABILITY METRICS SUMMARY")
    print("="*80)
    print(f"  Total API Cost Accrued : ${totals['total_cost']:.5f}")
    print(f"  Total Tokens Consumed  : {totals['total_tokens']}")
    print(f"  Tool Executions Run    : {totals['tool_call_count']}")
    print(f"  Avg Tool Execution Time: {totals['avg_tool_duration_ms']}ms")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_simulation()
