from typing import Dict, Any, List
from coordination_bus.trace_logger import TraceLogger
from coordination_bus.event_bus import EventBus, Event
from coordination_bus.policy_engine import CoordinationPolicyEngine
from coordination_bus.arbitration_engine import ArbitrationEngine, ArbitrationResult

class AgentInstance:
    """Base representation of a registered agent in the system."""
    def __init__(self, name: str):
        self.name = name

class CoordinationBus:
    def __init__(
        self, 
        event_bus: EventBus, 
        policy_engine: CoordinationPolicyEngine, 
        arbitration_engine: ArbitrationEngine, 
        logger: TraceLogger
    ):
        self.event_bus = event_bus
        self.policy_engine = policy_engine
        self.arbitration_engine = arbitration_engine
        self.logger = logger
        
        # Track agent instances
        self.agents: Dict[str, Any] = {}
        
        # Track decisions for active transaction IDs: transaction_id -> { agent_name: { action: str, details: dict } }
        self.active_transactions: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def register_agent(self, agent_name: str, agent_instance: Any):
        """Registers an agent with the coordination bus."""
        self.agents[agent_name] = agent_instance
        self.logger.log(
            sender="SYSTEM",
            event_type="INFO",
            topic="agent_registry",
            message=f"Agent '{agent_name}' successfully registered to the coordination bus."
        )

    def verify_and_route(self, event: Event) -> bool:
        """Validates publication policies and manages transaction states, checking for conflicts."""
        
        # 1. Validate Publication Policy
        allowed, reason = self.policy_engine.validate_publication(event.sender, event.topic)
        if not allowed:
            self.logger.log(
                sender="POLICY",
                event_type="POLICY_DENIED",
                topic=event.topic,
                message=f"Blocked publication from '{event.sender}': {reason}",
                payload={"event_payload": event.payload}
            )
            return False

        # 2. Check path restrictions (Direct communication check to potential target subscribers)
        # If the event payload contains a specific target agent, we check if the path is allowed.
        target_agent = event.payload.get("target_agent")
        if target_agent:
            allowed_path, path_reason = self.policy_engine.validate_interaction(event.sender, target_agent, event.topic)
            if not allowed_path:
                self.logger.log(
                    sender="POLICY",
                    event_type="POLICY_DENIED",
                    topic=event.topic,
                    message=f"Blocked interaction: {path_reason}",
                    payload={"sender": event.sender, "target": target_agent}
                )
                return False

        # 3. Conflict tracking and state accumulation
        transaction_id = event.payload.get("transaction_id")
        if transaction_id:
            if transaction_id not in self.active_transactions:
                self.active_transactions[transaction_id] = {}
                
            # Store the agent's intent
            action = event.payload.get("action")
            if action:
                self.active_transactions[transaction_id][event.sender] = {
                    "action": action,
                    "payload": event.payload
                }
                
            # If we detect conflicting intentions (e.g., both SupportAgent and FraudAgent have posted actions)
            actions_recorded = self.active_transactions[transaction_id]
            if len(actions_recorded) >= 2:
                # Trigger Arbitration
                self.logger.log(
                    sender="SYSTEM",
                    event_type="ARBITRATION_REQUIRED",
                    topic=event.topic,
                    message=f"Conflicting decisions detected for transaction '{transaction_id}'. Initiating Arbitration Engine.",
                    payload=actions_recorded
                )
                
                result: ArbitrationResult = self.arbitration_engine.arbitrate(transaction_id, actions_recorded)
                
                self.logger.log(
                    sender="ARBITRATOR",
                    event_type="RESOLVED",
                    topic=event.topic,
                    message=f"Arbitration Complete. Winner: '{result.winner}' -> Action: {result.action_required}",
                    payload={
                        "resolution_reason": result.reason,
                        "winner": result.winner,
                        "action_required": result.action_required,
                        "final_decision": result.decision
                    }
                )
                
                # Clear the transaction record after resolution
                del self.active_transactions[transaction_id]
                return False  # Discontinue normal routing, arbitrator overrides normal flow

        return True
