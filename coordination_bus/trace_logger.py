import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

# Color definitions for different agents and system actions
COLORS = {
    "EVENT_BUS": "\033[95m",      # Magenta
    "POLICY": "\033[36m",         # Cyan
    "ARBITRATOR": "\033[93m",     # Yellow
    "SupportAgent": "\033[94m",   # Blue
    "FraudAgent": "\033[91m",     # Red
    "SupportManagerAgent": "\033[92m", # Green
    "DevopsAgent": "\033[90m",    # Dark Grey
    "SYSTEM": "\033[97m",         # White
    "RESET": "\033[0m"
}

@dataclass
class CoordinationEvent:
    timestamp: str
    sender: str
    event_type: str  # e.g., "PUBLISH", "SUBSCRIBE", "POLICY_DENIED", "ARBITRATION_REQUIRED", "RESOLVED"
    topic: str
    message: str
    payload: Dict[str, Any]

class TraceLogger:
    def __init__(self, log_dir: str = "traces"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.current_trace_file = os.path.join(
            log_dir, f"coordination_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

    def log(self, sender: str, event_type: str, topic: str, message: str, payload: Optional[Dict[str, Any]] = None):
        """Logs a coordination event to JSONL and prints it in color to the console."""
        timestamp = datetime.now().isoformat()
        payload_dict = payload or {}
        
        event = CoordinationEvent(
            timestamp=timestamp,
            sender=sender,
            event_type=event_type,
            topic=topic,
            message=message,
            payload=payload_dict
        )

        # Write to JSONL
        try:
            with open(self.current_trace_file, "a") as f:
                f.write(json.dumps(asdict(event)) + "\n")
        except Exception:
            pass

        # Colored console output
        sender_color = COLORS.get(sender, COLORS["SYSTEM"])
        type_color = COLORS.get(event_type, COLORS["RESET"])
        reset = COLORS["RESET"]
        
        time_str = timestamp.split("T")[1][:8]
        prefix = f"[{time_str}] [{sender_color}{sender}{reset}]"
        
        console_message = f"{prefix} {event_type} ({topic}) - {message}"
        if payload_dict:
            payload_str = json.dumps(payload_dict, default=str)
            if len(payload_str) > 90:
                payload_str = payload_str[:87] + "..."
            console_message += f"\n    Payload: {payload_str}"
            
        print(console_message)
