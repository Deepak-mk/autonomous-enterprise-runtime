import time
from typing import Dict, Any
from coordination_bus.trace_logger import TraceLogger
from coordination_bus.event_bus import EventBus, Event
from coordination_bus.policy_engine import CoordinationPolicyEngine
from coordination_bus.arbitration_engine import ArbitrationEngine
from coordination_bus.coordinator import CoordinationBus

# Define Mock Agents with handlers
class SimulatedAgent:
    def __init__(self, name: str, event_bus: EventBus):
        self.name = name
        self.event_bus = event_bus

class SupportAgent(SimulatedAgent):
    def handle_event(self, event: Event):
        if event.sender == self.name:
            return
        # Support agent acts when a customer dispute is created
        if event.topic == "disputes" and event.payload.get("status") == "OPEN":
            tx_id = event.payload.get("transaction_id")
            amount = event.payload.get("amount", 0.0)
            
            # Support wants to satisfy the customer, so they publish a refund proposal
            refund_payload = {
                "transaction_id": tx_id,
                "amount": amount,
                "action": "REFUND",
                "reason": "Customer satisfaction guarantee"
            }
            self.event_bus.publish(
                topic="refund_proposals",
                sender=self.name,
                payload=refund_payload
            )

class FraudAgent(SimulatedAgent):
    def handle_event(self, event: Event):
        if event.sender == self.name:
            return
        # Fraud Agent intercepts refund proposals and audits them
        if event.topic == "refund_proposals":
            tx_id = event.payload.get("transaction_id")
            amount = event.payload.get("amount", 0.0)
            
            # Simple rule: block any refund for transaction IDs ending in "00" (simulated high risk)
            if tx_id.endswith("00"):
                block_payload = {
                    "transaction_id": tx_id,
                    "amount": amount,
                    "action": "BLOCK",
                    "reason": "Anti-fraud match: multiple credit cards used within 24h"
                }
                # Publish the fraud block intent to "refund_proposals" to trigger resolution
                self.event_bus.publish(
                    topic="refund_proposals",
                    sender=self.name,
                    payload=block_payload
                )

class SupportManagerAgent(SimulatedAgent):
    def handle_event(self, event: Event):
        pass  # Manager registers to inspect but is driven manually for override scenarios

class DevopsAgent(SimulatedAgent):
    def handle_event(self, event: Event):
        pass

def main():
    logger = TraceLogger()
    policy_engine = CoordinationPolicyEngine()
    arbitration_engine = ArbitrationEngine()
    event_bus = EventBus(logger=logger)
    
    coordinator = CoordinationBus(
        event_bus=event_bus,
        policy_engine=policy_engine,
        arbitration_engine=arbitration_engine,
        logger=logger
    )

    # Wire up the default interceptor in the event bus
    event_bus.interceptor = coordinator

    # Initialize and register agents
    support = SupportAgent("SupportAgent", event_bus)
    fraud = FraudAgent("FraudAgent", event_bus)
    manager = SupportManagerAgent("SupportManagerAgent", event_bus)
    devops = DevopsAgent("DevopsAgent", event_bus)

    coordinator.register_agent("SupportAgent", support)
    coordinator.register_agent("FraudAgent", fraud)
    coordinator.register_agent("SupportManagerAgent", manager)
    coordinator.register_agent("DevopsAgent", devops)

    # Wire up event subscriptions
    event_bus.subscribe("disputes", support.handle_event)
    event_bus.subscribe("refund_proposals", fraud.handle_event)

    print("\n" + "="*80)
    print("  STARTING AUTONOMOUS COORDINATION BUS SIMULATION")
    print("="*80 + "\n")

    # SCENARIO 1: Unauthorized Topic Publication Policy Violation
    print("--- SCENARIO 1: Unauthorized Topic Publication ---")
    event_bus.publish(
        topic="system_deploy",
        sender="SupportAgent",
        payload={"image": "new-ui:latest"}
    )
    time.sleep(0.5)
    print("\n")

    # SCENARIO 2: Prohibited Direct Agent-to-Agent Communication path
    print("--- SCENARIO 2: Prohibited Direct Communication Path ---")
    event_bus.publish(
        topic="disputes",
        sender="SupportAgent",
        payload={
            "transaction_id": "TX-101", 
            "target_agent": "DevopsAgent",
            "message": "Please hotfix database for this customer"
        }
    )
    time.sleep(0.5)
    print("\n")

    # SCENARIO 3: Conflict Arbitration (Fraud Agent safety block overrides refund request)
    print("--- SCENARIO 3: Conflict Arbitration (Fraud Agent overrides SupportAgent) ---")
    # Step A: Customer support dispute created
    print("[Simulator Step] Creating Customer Dispute for TX-500...")
    event_bus.publish(
        topic="disputes",
        sender="SYSTEM",
        payload={"status": "OPEN", "transaction_id": "TX-500", "amount": 150.00}
    )
    
    # Step B: SupportAgent proposes refund
    # This automatically invokes support.handle_event -> publish "refund_proposals"
    # Which in turn invokes fraud.handle_event -> publish "refund_proposals" with BLOCK.
    # The coordinator registers both intentions on TX-500 and invokes Arbitration.
    event_bus.publish(
        topic="refund_proposals",
        sender="SupportAgent",
        payload={"transaction_id": "TX-500", "amount": 150.00, "action": "REFUND"}
    )
    event_bus.publish(
        topic="refund_proposals",
        sender="FraudAgent",
        payload={"transaction_id": "TX-500", "amount": 150.00, "action": "BLOCK"}
    )
    
    time.sleep(0.5)
    print("\n")

    # SCENARIO 4: Manager Overrides Fraud Block (Support Manager override takes precedence)
    print("--- SCENARIO 4: Manager Overrides Fraud Block ---")
    print("[Simulator Step] Creating Customer Dispute for TX-600...")
    
    # Register intentions for TX-600
    event_bus.publish(
        topic="refund_proposals",
        sender="SupportAgent",
        payload={"transaction_id": "TX-600", "amount": 150.00, "action": "REFUND"}
    )
    event_bus.publish(
        topic="refund_proposals",
        sender="FraudAgent",
        payload={"transaction_id": "TX-600", "amount": 150.00, "action": "BLOCK"}
    )
    
    # Support Manager steps in and issues a manual OVERRIDE to REFUND
    print("[Simulator Step] Support Manager steps in with override decision...")
    event_bus.publish(
        topic="refund_proposals",
        sender="SupportManagerAgent",
        payload={"transaction_id": "TX-600", "amount": 150.00, "action": "REFUND"}
    )
    
    print("\n" + "="*80)
    print("  COORDINATION BUS SIMULATION COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
