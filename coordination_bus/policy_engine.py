from typing import Dict, List, Tuple, Any

class CoordinationPolicyEngine:
    def __init__(self):
        # Maps event topic -> list of agent roles authorized to publish
        self.topic_publishers = {
            "financial_settlement": ["BillingAgent", "SupportManagerAgent"],
            "disputes": ["SYSTEM", "SupportAgent", "FraudAgent", "SupportManagerAgent"],
            "system_deploy": ["DevopsAgent"],
            "refund_proposals": ["SupportAgent", "FraudAgent", "SupportManagerAgent"]
        }
        
        # Restricted communication paths (Direct communication restrictions)
        # Key: Sender -> list of prohibited direct receivers
        self.prohibited_interactions = {
            "SupportAgent": ["DevopsAgent"]  # SupportAgent must not coordinate directly with DevopsAgent
        }

    def validate_publication(self, sender: str, topic: str) -> Tuple[bool, str]:
        """Checks if an agent is authorized to publish to a topic."""
        # If the topic has restriction rules
        if topic in self.topic_publishers:
            allowed_publishers = self.topic_publishers[topic]
            if sender not in allowed_publishers:
                return False, f"Agent '{sender}' is not authorized to publish to topic '{topic}'. Authorized roles: {allowed_publishers}"
                
        return True, "Publication permitted under policy rules"

    def validate_interaction(self, sender: str, receiver: str, topic: str) -> Tuple[bool, str]:
        """Checks if a direct message/coordination between two agents violates structural protocols."""
        restricted_receivers = self.prohibited_interactions.get(sender, [])
        if receiver in restricted_receivers:
            return False, f"Direct communication path between '{sender}' and '{receiver}' is restricted. Messages must route through a manager."
            
        return True, "Communication path permitted under policy rules"
