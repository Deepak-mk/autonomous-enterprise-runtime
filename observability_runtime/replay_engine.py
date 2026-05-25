import time
from typing import List, Dict, Any

class ReplayEngine:
    def __init__(self):
        pass

    def build_timeline(
        self, 
        reasoning: List[Dict[str, Any]], 
        execution_tools: List[Dict[str, Any]], 
        execution_apis: List[Dict[str, Any]],
        memory_ops: List[Dict[str, Any]], 
        governance_audits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merges disparate telemetry logs into a unified, chronologically sorted timeline."""
        timeline = []

        for r in reasoning:
            timeline.append({**r, "category": "COGNITIVE"})
            
        for t in execution_tools:
            timeline.append({**t, "category": "EXECUTION_TOOL"})
            
        for a in execution_apis:
            timeline.append({**a, "category": "EXECUTION_API"})
            
        for m in memory_ops:
            timeline.append({**m, "category": "MEMORY"})
            
        for g in governance_audits:
            timeline.append({**g, "category": "GOVERNANCE"})

        # Sort chronologically by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline

    def play(self, timeline: List[Dict[str, Any]]):
        """Replays the session timeline with color-coded, structured step readouts."""
        print("="*80)
        print("  PLAYBACK SESSION REPLAY TRAIL")
        print("="*80)
        
        # Color codes
        c_cognitive = "\033[94m"     # Blue
        c_exec = "\033[92m"          # Green
        c_memory = "\033[93m"        # Yellow
        c_gov = "\033[95m"           # Magenta
        c_reset = "\033[0m"

        for idx, event in enumerate(timeline):
            t_offset = f"+{idx * 0.1:.1f}s"
            category = event["category"]
            
            if category == "COGNITIVE":
                print(f"[{t_offset}] {c_cognitive}[COGNITIVE]{c_reset} Agent Thought: '{event['thought']}'")
                print(f"         └─ Action Selected: {c_cognitive}{event['action']}{c_reset} (Confidence: {event['confidence']:.2f})")
                
            elif category == "EXECUTION_TOOL":
                print(f"[{t_offset}] {c_exec}[TOOL RUN]{c_reset} Executed tool '{event['tool']}' with args: {event['args']}")
                print(f"         └─ Duration: {event['duration_ms']}ms | Success: {event['success']} | Output: '{event['output']}'")
                
            elif category == "EXECUTION_API":
                print(f"[{t_offset}] {c_exec}[API CALL]{c_reset} Invoked model '{event['model']}' | Cost: ${event['cost']:.5f} | Latency: {event['duration_sec']}s")
                print(f"         └─ Tokens: {event['input_tokens']} in, {event['output_tokens']} out")
                
            elif category == "MEMORY":
                op = event["operation"]
                if op == "READ" or op == "WRITE":
                    print(f"[{t_offset}] {c_memory}[MEMORY {op}]{c_reset} Key: '{event['key']}' | Value: '{event['value']}'")
                elif op == "RECALL":
                    print(f"[{t_offset}] {c_memory}[MEMORY RECALL]{c_reset} Query: '{event['query']}' | Matches: {event['matches']} (Confidence: {event['confidence']:.2f})")
                elif op == "SYNC":
                    print(f"[{t_offset}] {c_memory}[MEMORY CONSOLIDATION]{c_reset} {event['summary']}")
                    
            elif category == "GOVERNANCE":
                g_type = event["type"]
                if g_type == "POLICY_CHECK":
                    res_color = "\033[92m" if event["result"] == "PASS" else "\033[91m"
                    print(f"[{t_offset}] {c_gov}[GOVERNANCE POLICY]{c_reset} Check '{event['policy']}' -> {res_color}{event['result']}{c_reset} (Reason: {event['reason']})")
                elif g_type == "HITL_APPROVAL":
                    print(f"[{t_offset}] {c_gov}[GOVERNANCE HITL]{c_reset} HITL approval review by '{event['approver']}' for TX: '{event['transaction_id']}' -> Result: {event['result']}")
                elif g_type == "ARBITRATION":
                    print(f"[{t_offset}] {c_gov}[GOVERNANCE ARBITRATE]{c_reset} Conflict in topic '{event['topic']}' | Arbitrated winner: '{event['winner']}' (Reason: {event['reason']})")
            
            print("-" * 80)
            time.sleep(0.1)  # brief pause to simulate real playback speed
            
        print("="*80)
        print("  PLAYBACK SESSION REPLAY TRAIL COMPLETE")
        print("="*80 + "\n")
