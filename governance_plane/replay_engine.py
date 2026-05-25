import time
from typing import List, Dict, Any

class GovernanceReplayEngine:
    def __init__(self):
        pass

    def play(self, audit_log: List[Dict[str, Any]]):
        """Sequential playback of governance logs."""
        print("="*80)
        print("  SOVEREIGN GOVERNANCE PLANE AUDIT REPLAY")
        print("="*80)

        c_policy = "\033[94m"       # Blue
        c_perm = "\033[36m"         # Cyan
        c_esc = "\033[95m"          # Magenta
        c_arbitrate = "\033[93m"    # Yellow
        c_reset = "\033[0m"

        for idx, event in enumerate(audit_log):
            t_offset = f"+{idx * 0.2:.1f}s"
            scope = event["scope"]
            
            if scope == "POLICY":
                res_color = "\033[92m" if event["result"] == "ALLOW" else "\033[91m"
                print(f"[{t_offset}] {c_policy}[POLICY EVAL]{c_reset} Agent: '{event['agent']}' | Action: '{event['action']}' -> {res_color}{event['result']}{c_reset}")
                print(f"         └─ Details: {event['details']}")
                
            elif scope == "PERMISSION":
                res_color = "\033[92m" if event["result"] == "AUTHORIZED" else "\033[91m"
                print(f"[{t_offset}] {c_perm}[RBAC CHECK]{c_reset} Agent: '{event['agent']}' | Action: '{event['action']}' -> {res_color}{event['result']}{c_reset}")
                print(f"         └─ Details: {event['details']}")
                
            elif scope == "ESCALATION":
                print(f"[{t_offset}] {c_esc}[ESCALATION OVERRIDE]{c_reset} Agent: '{event['agent']}' | Resolution: {event['result']}")
                print(f"         └─ Action Signoff details: {event['details']}")
                
            elif scope == "ARBITRATION":
                print(f"[{t_offset}] {c_arbitrate}[CONFLICT ARBITRATED]{c_reset} Resolved in favor of: '{event['agent']}' -> Executed Action: '{event['action']}'")
                print(f"         └─ Reason: {event['details']}")
            
            print("-" * 80)
            time.sleep(0.1)

        print("="*80)
        print("  GOVERNANCE PLANE AUDIT REPLAY COMPLETE")
        print("="*80 + "\n")
