from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Episode:
    episode_id: str
    timestamp: str
    task_name: str
    steps: List[Dict[str, Any]]
    success: bool
    summary: str

class EpisodicMemory:
    def __init__(self):
        # Time-ordered log of past task experiences
        self.episodes: List[Episode] = []

    def add_episode(self, task_name: str, steps: List[Dict[str, Any]], success: bool, summary: str) -> Episode:
        """Stores a new episode of task execution."""
        episode_id = f"EP-{len(self.episodes) + 1001}"
        episode = Episode(
            episode_id=episode_id,
            timestamp=datetime.now().isoformat(),
            task_name=task_name,
            steps=steps,
            success=success,
            summary=summary
        )
        self.episodes.append(episode)
        return episode

    def recall_similar(self, query: str) -> List[Episode]:
        """Recalls past experiences matching keywords in the task name or summary."""
        keywords = query.lower().split()
        matches = []
        for ep in self.episodes:
            score = 0
            for kw in keywords:
                if kw in ep.task_name.lower() or kw in ep.summary.lower():
                    score += 1
            if score > 0:
                matches.append((ep, score))
        
        # Sort by match score descending
        matches.sort(key=lambda item: item[1], reverse=True)
        return [item[0] for item in matches]
