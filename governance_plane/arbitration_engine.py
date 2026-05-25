from typing import Dict, Any, List

class GovernanceArbitrationEngine:
    def __init__(self):
        # Security/Control priority rankings (higher numbers = higher authority)
        self.priority_ranks = {
            "SupportAgent": 3,
            "BillingAgent": 6,
            "FraudAgent": 8,
            "SecurityAgent": 9,
            "AdminAgent": 10
        }

    def arbitrate(self, task_id: str, conflicts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Arbitrates conflicts by evaluating the authority ranking of participating agent roles."""
        print(f"\n[ARBITRATION ENGINE] Resolving conflict for task '{task_id}'...")
        
        # Sort conflicts based on authority rankings
        sorted_claims = []
        for agent_role, decision in conflicts.items():
            rank = self.priority_ranks.get(agent_role, 1)
            sorted_claims.append({
                "role": agent_role,
                "rank": rank,
                "action": decision.get("action"),
                "payload": decision.get("payload")
            })
            print(f"  - Claim: {agent_role} (Rank: {rank}) proposes '{decision.get('action')}'")

        # Sort claims descending by authority rank
        sorted_claims.sort(key=lambda c: c["rank"], reverse=True)
        winner = sorted_claims[0]
        
        reason = f"Agent '{winner['role']}' holds higher authority ranking ({winner['rank']}) than other claimants."
        
        print(f"  - Resolution: Winner '{winner['role']}' -> Action '{winner['action']}'")
        
        return {
            "task_id": task_id,
            "winner": winner["role"],
            "winning_action": winner["action"],
            "winner_rank": winner["rank"],
            "reason": reason
        }
