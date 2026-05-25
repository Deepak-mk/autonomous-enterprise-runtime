from typing import List, Tuple, Any, Optional

class SemanticMemory:
    def __init__(self):
        # Long-term knowledge base represented as semantic triplets (Subject, Relation, Object)
        self.triplets: List[Tuple[str, str, Any]] = []
        
        # Populate initial corporate policy facts
        self._load_default_policies()

    def _load_default_policies(self):
        # Add basic business rules and entity relationship facts
        self.add_fact("Refund Limit", "has_value", 100.0)
        self.add_fact("SupportAgent", "can_trigger", "refund_proposals")
        self.add_fact("FraudAgent", "can_trigger", "refund_blocks")
        self.add_fact("SupportManagerAgent", "has_authority_level", 10)

    def add_fact(self, subject: str, relation: str, obj: Any):
        """Adds a triplet fact to long-term semantic memory."""
        # Avoid duplicate facts
        fact = (subject, relation, obj)
        if fact not in self.triplets:
            self.triplets.append(fact)

    def query(self, subject: Optional[str] = None, relation: Optional[str] = None, obj: Optional[str] = None) -> List[Tuple[str, str, Any]]:
        """Queries the semantic database matching any combination of subject, relation, or object."""
        results = []
        for s, r, o in self.triplets:
            if subject and s != subject:
                continue
            if relation and r != relation:
                continue
            if obj and o != obj:
                continue
            results.append((s, r, o))
        return results
