from typing import Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class ArbitrationResult:
    resolved: bool
    winner: str
    decision: str
    action_required: str  # e.g., "EXECUTE_REFUND", "BLOCK_TRANSACTION", "ESCALATE_TO_MANAGER"
    reason: str

class ArbitrationEngine:
    def __init__(self):
        # Authority ranks (higher = stronger authority on dispute resolution)
        self.authority_ranks = {
            "SupportAgent": 5,
            "FraudAgent": 8,
            "SupportManagerAgent": 10
        }

    def arbitrate(
        self, 
        transaction_id: str, 
        agent_actions: Dict[str, Dict[str, Any]]
    ) -> ArbitrationResult:
        """Resolves conflicting decisions made by multiple agents on the same transaction."""
        
        agents_involved = list(agent_actions.keys())
        
        # If there's only one assertion, no arbitration is needed
        if len(agents_involved) <= 1:
            agent = agents_involved[0] if agents_involved else "System"
            action = agent_actions[agent].get("action", "ALLOW")
            return ArbitrationResult(
                resolved=True,
                winner=agent,
                decision=action,
                action_required="EXECUTE",
                reason="No conflict detected"
            )

        # Let's inspect conflicting actions
        decisions = {agent: info.get("action") for agent, info in agent_actions.items()}
        
        # If all agents agree, then no conflict resolution rules are needed
        if len(set(decisions.values())) == 1:
            agent = agents_involved[0]
            return ArbitrationResult(
                resolved=True,
                winner=agent,
                decision=decisions[agent],
                action_required="EXECUTE",
                reason="All participating agents agreed on the decision"
            )

        # Conflict detected! SupportAgent wants "REFUND", FraudAgent wants "BLOCK"
        print(f"\n[Arbitration Log] Conflict detected on transaction '{transaction_id}':")
        for agent, decision in decisions.items():
            print(f"  - {agent} proposes: {decision}")

        # Rule 1: Fraud blocks take precedence over support requests unless overridden by a Manager
        if "FraudAgent" in agent_actions and agent_actions["FraudAgent"].get("action") == "BLOCK":
            # Check if there is a Manager override
            if "SupportManagerAgent" in agent_actions:
                manager_decision = agent_actions["SupportManagerAgent"].get("action")
                return ArbitrationResult(
                    resolved=True,
                    winner="SupportManagerAgent",
                    decision=manager_decision,
                    action_required=f"EXECUTE_{manager_decision}",
                    reason=f"Conflict resolved: SupportManagerAgent override takes precedence over FraudAgent block."
                )
            
            # Otherwise, FraudAgent wins (safety first)
            return ArbitrationResult(
                resolved=True,
                winner="FraudAgent",
                decision="BLOCK",
                action_required="BLOCK_TRANSACTION",
                reason=f"Conflict resolved: FraudAgent safety block holds higher priority (Rank {self.authority_ranks['FraudAgent']}) than SupportAgent request (Rank {self.authority_ranks['SupportAgent']})."
            )

        # General authority rank fallback
        highest_rank = -1
        winner = None
        for agent in agents_involved:
            rank = self.authority_ranks.get(agent, 1)
            if rank > highest_rank:
                highest_rank = rank
                winner = agent

        return ArbitrationResult(
            resolved=True,
            winner=winner,
            decision=decisions[winner],
            action_required=f"EXECUTE_{decisions[winner]}",
            reason=f"Conflict resolved by authority ranking. '{winner}' wins with authority rank {highest_rank}."
        )
