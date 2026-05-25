from typing import Dict, Any, List

class TaskCharacteristics:
    def __init__(self, complexity: str, domain: str, estimated_tokens: int, needs_reasoning: bool):
        self.complexity = complexity  # LOW, MEDIUM, HIGH, CRITICAL
        self.domain = domain          # e.g., "nlp", "coding", "math", "reasoning"
        self.estimated_tokens = estimated_tokens
        self.needs_reasoning = needs_reasoning

class TaskClassifier:
    def __init__(self):
        # Keyword mappings for heuristic classification
        self.keywords = {
            "math": ["calculate", "reconcile", "compute", "sum", "financial discrepancy", "invoice calculation"],
            "coding": ["code", "script", "deploy", "regex", "refactor", "hotfix", "bug", "patch"],
            "reasoning": ["analyze logs", "audit", "arbitrate", "conflict", "strategic decision", "diagnose"]
        }

    def classify(self, task_description: str) -> TaskCharacteristics:
        """Determines task complexity and technical requirements from the description."""
        desc_lower = task_description.lower()
        words = desc_lower.split()
        
        # 1. Determine domain
        domain = "nlp"  # Default domain
        for dom, kws in self.keywords.items():
            # Match whole words for short terms to avoid false positives (e.g. 'sum' in 'summarize')
            if any((kw in desc_lower if len(kw) > 3 else kw in words) for kw in kws):
                domain = dom
                break
                
        # 2. Determine complexity & reasoning needs
        needs_reasoning = False
        complexity = "LOW"
        estimated_tokens = 500
        
        # Heuristics
        if domain == "math" or domain == "reasoning":
            needs_reasoning = True
            complexity = "HIGH"
            estimated_tokens = 2000
        elif domain == "coding":
            complexity = "MEDIUM"
            estimated_tokens = 1200
            
        # Hard keywords pushing complexity to CRITICAL
        critical_keywords = ["production", "financial audit", "severe", "dispute", "arbitration", "security vulnerability"]
        if any(kw in desc_lower for kw in critical_keywords):
            complexity = "CRITICAL"
            needs_reasoning = True
            estimated_tokens = 3000
            
        # Simple texts are LOW complexity
        if len(task_description.split()) < 15 and complexity != "CRITICAL":
            complexity = "LOW"
            estimated_tokens = 300

        return TaskCharacteristics(
            complexity=complexity,
            domain=domain,
            estimated_tokens=estimated_tokens,
            needs_reasoning=needs_reasoning
        )
