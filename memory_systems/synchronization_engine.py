import json
from typing import Dict, Any
from memory_systems.working_memory import WorkingMemory
from memory_systems.episodic_memory import EpisodicMemory, Episode
from memory_systems.semantic_memory import SemanticMemory

class SynchronizationEngine:
    def __init__(self, console_logger: Any = None):
        self.logger = console_logger

    def consolidate_session(
        self, 
        working_mem: WorkingMemory, 
        episodic_mem: EpisodicMemory, 
        semantic_mem: SemanticMemory,
        task_name: str,
        success: bool,
        summary: str
    ) -> Episode:
        """Promotes short-term working memory to long-term episodic memory, then extracts semantic facts."""
        
        # 1. Promote to Episodic Memory
        steps_trace = working_mem.execution_trace.copy()
        episode = episodic_mem.add_episode(
            task_name=task_name,
            steps=steps_trace,
            success=success,
            summary=summary
        )
        
        if self.logger:
            self.logger.log_sync(
                "SYNCHRONIZER",
                f"Promoted active working memory to episodic log '{episode.episode_id}'."
            )

        # 2. Consolidate into Semantic Memory
        # Extract metadata and update general facts/beliefs database
        customer_id = working_mem.get("customer_id")
        if customer_id:
            # Check if this customer already has semantic facts
            existing_disputes = semantic_mem.query(subject=f"Customer_{customer_id}", relation="dispute_count")
            if existing_disputes:
                count = existing_disputes[0][2] + 1
                # Remove old fact and write new one
                semantic_mem.triplets.remove(existing_disputes[0])
                semantic_mem.add_fact(f"Customer_{customer_id}", "dispute_count", count)
            else:
                semantic_mem.add_fact(f"Customer_{customer_id}", "dispute_count", 1)
                
            # If dispute was successfully resolved, record resolution pattern
            if success:
                semantic_mem.add_fact(f"Customer_{customer_id}", "last_resolution", "approved_refund")
                
            if self.logger:
                self.logger.log_sync(
                    "CONSOLIDATOR",
                    f"Consolidation cycle completed. Extracted semantic rules for 'Customer_{customer_id}'."
                )

        # Clear working memory
        working_mem.clear()
        return episode
