import time
from typing import List, Dict, Any

class MemoryTelemetry:
    def __init__(self):
        self.operations: List[Dict[str, Any]] = []

    def log_read(self, memory_type: str, key: str, value: Any):
        """Logs read access to a specific memory layer."""
        self.operations.append({
            "timestamp": time.time(),
            "operation": "READ",
            "memory_type": memory_type,  # WORKING, EPISODIC, SEMANTIC, COORDINATION
            "key": key,
            "value": str(value)
        })

    def log_write(self, memory_type: str, key: str, value: Any):
        """Logs write access/update to a specific memory layer."""
        self.operations.append({
            "timestamp": time.time(),
            "operation": "WRITE",
            "memory_type": memory_type,
            "key": key,
            "value": str(value)
        })

    def log_recall(self, query: str, matched_episodes: List[str], confidence: float):
        """Logs recall query execution against episodic memory."""
        self.operations.append({
            "timestamp": time.time(),
            "operation": "RECALL",
            "memory_type": "EPISODIC",
            "query": query,
            "matches": matched_episodes,
            "confidence": confidence
        })

    def log_sync(self, source: str, target: str, summary: str):
        """Logs consolidation sync processes between memory layers."""
        self.operations.append({
            "timestamp": time.time(),
            "operation": "SYNC",
            "memory_type": f"{source}->{target}",
            "summary": summary
        })
