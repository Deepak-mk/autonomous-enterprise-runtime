import time
from typing import Any
from memory_systems.working_memory import WorkingMemory
from memory_systems.episodic_memory import EpisodicMemory, Episode
from memory_systems.semantic_memory import SemanticMemory
from memory_systems.coordination_memory import CoordinationMemory
from memory_systems.synchronization_engine import SynchronizationEngine

# Visual logging helper
class ColorLogger:
    COLORS = {
        "WORKING": "\033[94m",       # Blue
        "EPISODIC": "\033[93m",      # Yellow
        "SEMANTIC": "\033[36m",      # Cyan
        "COORDINATION": "\033[95m",  # Magenta
        "SYNCHRONIZER": "\033[92m",  # Green
        "CONSOLIDATOR": "\033[96m",  # Light Cyan
        "RESET": "\033[0m"
    }

    def log(self, section: str, message: str):
        color = self.COLORS.get(section, self.COLORS["RESET"])
        print(f"{color}[{section} MEMORY]{self.COLORS['RESET']} {message}")

    def log_sync(self, engine_name: str, message: str):
        color = self.COLORS.get(engine_name, self.COLORS["RESET"])
        print(f"{color}[{engine_name} ENGINE]{self.COLORS['RESET']} {message}")

def run_simulation():
    cl = ColorLogger()
    
    # Initialize subsystems
    working_mem = WorkingMemory(task_id="TSK-M404")
    episodic_mem = EpisodicMemory()
    semantic_mem = SemanticMemory()
    coordination_mem = CoordinationMemory()
    sync_engine = SynchronizationEngine(console_logger=cl)

    print("\n" + "="*80)
    print("  STARTING COGNITIVE MEMORY SYSTEM SIMULATION (BEYOND RAG)")
    print("="*80 + "\n")

    # PRE-LOAD HISTORICAL EPISODE (Prior Experience)
    cl.log("EPISODIC", "Pre-seeding historical database with experience...")
    episodic_mem.add_episode(
        task_name="Resolve dispute for Customer 104",
        steps=[{"tool": "escalate", "args": {"manager": "authorized_refund"}, "output": "APPROVED"}],
        success=True,
        summary="Customer 104 billing dispute resolved last week by manager approval after limit exceeded."
    )
    time.sleep(0.5)

    # 1. Short-Term Working Memory Context Initiation
    print("\n--- STEP 1: Initiating Task Context in Working Memory ---")
    cl.log("WORKING", "Loading active task variables...")
    working_mem.set("customer_id", 104)
    working_mem.set("dispute_amount", 120.00)
    working_mem.set("status", "INVESTIGATING")
    
    cl.log("WORKING", f"Active variables in working memory: {working_mem.get_summary()['variables']}")
    time.sleep(0.5)

    # 2. Querying Long-Term Semantic Policy Rules
    print("\n--- STEP 2: Querying Semantic Rules (Business Policies) ---")
    cl.log("SEMANTIC", "Querying refund limits and agent authorization boundaries...")
    
    refund_limit_query = semantic_mem.query(subject="Refund Limit", relation="has_value")
    if refund_limit_query:
        limit = refund_limit_query[0][2]
        cl.log("SEMANTIC", f"Retrieved policy: Subject: 'Refund Limit' | Relation: 'has_value' | Value: ${limit}")
    
    dispute_val = working_mem.get("dispute_amount")
    if dispute_val > limit:
        cl.log("WORKING", f"Validation: Dispute amount (${dispute_val}) exceeds policy limit (${limit}). Direct auto-refund restricted.")
    time.sleep(0.5)

    # 3. Querying Time-Ordered Episodic Experiences (Recall)
    print("\n--- STEP 3: Querying Episodic Memory (Recalling Past Decisions) ---")
    cl.log("EPISODIC", "Searching past episodes for keyword matches: 'billing dispute'...")
    
    similar_episodes = episodic_mem.recall_similar("billing dispute")
    if similar_episodes:
        past_ep = similar_episodes[0]
        cl.log("EPISODIC", f"Recalled similar case found: Episode '{past_ep.episode_id}'")
        cl.log("EPISODIC", f"  - Previous experience summary: '{past_ep.summary}'")
        cl.log("WORKING", "Action strategy adapted: Escalate refund request for manager signature based on EP-1001 precedent.")
    time.sleep(0.5)

    # 4. Shared State Sync & Mutual Exclusion (Coordination Memory)
    print("\n--- STEP 4: Shared State Reservation & Concurrent Locking ---")
    cl.log("COORDINATION", "Attempting to reserve funds from shared billing pool...")
    
    resource_key = "lock_available_billing_pool"
    agent_id = "SupportAgent_Alpha"
    
    # Try to acquire lock
    if coordination_mem.acquire_lock(resource_key, agent_id):
        cl.log("COORDINATION", f"Acquired lock on '{resource_key}' successfully.")
        
        current_pool = coordination_mem.get_shared("available_billing_pool")
        new_pool = current_pool - dispute_val
        
        # Write updated shared pool
        coordination_mem.set_shared("available_billing_pool", new_pool, agent_id)
        cl.log("COORDINATION", f"Updated shared 'available_billing_pool': ${current_pool} -> ${new_pool}.")
        
        # Release lock
        coordination_mem.release_lock(resource_key, agent_id)
        cl.log("COORDINATION", f"Released lock on '{resource_key}'.")
    else:
        cl.log("COORDINATION", "Failed to acquire lock. Pool is busy. Task queued.")
    time.sleep(0.5)

    # Logging step execution to Working Memory Trace
    working_mem.add_step("query_policy", {"subject": "Refund Limit"}, f"Limit is ${limit}")
    working_mem.add_step("recall_history", {"keyword": "dispute"}, "EP-1001 matched")
    working_mem.add_step("reserve_funds", {"amount": dispute_val}, "Success")

    # 5. Consolidation and Sleep Sync Loop (Consolidating Working -> Episodic -> Semantic)
    print("\n--- STEP 5: Synchronization & Memory Consolidation Cycle ---")
    cl.log("WORKING", "Task complete. Initiating cleanup and consolidation sync...")
    
    consolidated_episode = sync_engine.consolidate_session(
        working_mem=working_mem,
        episodic_mem=episodic_mem,
        semantic_mem=semantic_mem,
        task_name="Resolve dispute for Customer 104",
        success=True,
        summary="Dispute of $120 resolved by SupportAgent_Alpha after lock reservation and escalation."
    )
    time.sleep(0.5)

    # 6. Verification of Long-Term Updates
    print("\n--- STEP 6: Verifying Consolidated Semantic Rules ---")
    cl.log("SEMANTIC", "Querying long-term database for Customer 104's aggregated profile...")
    
    customer_profile = semantic_mem.query(subject="Customer_104")
    for s, r, o in customer_profile:
        cl.log("SEMANTIC", f"Retrieved Fact: ({s}) --[{r}]--> ({o})")
    
    print("\n" + "="*80)
    print("  MEMORY SYSTEM SIMULATION COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_simulation()
