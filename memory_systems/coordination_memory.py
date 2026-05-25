from typing import Dict, Any, Optional

class CoordinationMemory:
    def __init__(self):
        # Shared blackboards for variables accessible across all agent instances
        self.shared_state: Dict[str, Any] = {
            "available_billing_pool": 5000.0,
            "system_status": "HEALTHY"
        }
        # Resource lock dictionary to simulate distributed state sync locking
        self.locks: Dict[str, str] = {}  # resource_name -> agent_name holding lock

    def acquire_lock(self, resource: str, agent_name: str) -> bool:
        """Acquires a concurrency lock on a shared resource."""
        if resource not in self.locks:
            self.locks[resource] = agent_name
            return True
        elif self.locks[resource] == agent_name:
            return True
        return False  # Locked by another agent

    def release_lock(self, resource: str, agent_name: str) -> bool:
        """Releases a lock held on a shared resource."""
        if self.locks.get(resource) == agent_name:
            del self.locks[resource]
            return True
        return False

    def get_shared(self, key: str, default: Any = None) -> Any:
        """Retrieves a variable from shared coordination memory."""
        return self.shared_state.get(key, default)

    def set_shared(self, key: str, value: Any, agent_name: str) -> bool:
        """Sets a variable in shared memory. Requires acquiring a lock first if resource starts with lock_."""
        # For critical state keys requiring locks
        lock_key = f"lock_{key}"
        if lock_key in self.locks and self.locks[lock_key] != agent_name:
            return False  # Denied: Lock held by someone else
            
        self.shared_state[key] = value
        return True
