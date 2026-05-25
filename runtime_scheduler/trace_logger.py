import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

# ANSI color codes for pretty printing
COLORS = {
    "INFO": "\033[94m",       # Blue
    "SUCCESS": "\033[92m",    # Green
    "WARNING": "\033[93m",    # Yellow
    "ERROR": "\033[91m",      # Red
    "CRITICAL": "\033[95m",   # Magenta
    "POLICY": "\033[36m",     # Cyan (for policy decisions)
    "RECOVERY": "\033[96m",   # Light Cyan (for recovery attempts)
    "RESET": "\033[0m"
}

@dataclass
class TraceEvent:
    timestamp: str
    task_id: str
    agent_name: str
    event_type: str  # e.g., "TASK_START", "POLICY_CHECK", "TOOL_CALL", "RECOVERY", "TASK_COMPLETE"
    message: str
    details: Dict[str, Any]
    cost: float = 0.0

class TraceLogger:
    def __init__(self, log_dir: str = "traces"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure standard logging
        self.logger = logging.getLogger("RuntimeScheduler")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers if already initialized
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            
        self.current_trace_file = os.path.join(
            log_dir, f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

    def log(self, task_id: str, agent_name: str, event_type: str, message: str, details: Optional[Dict[str, Any]] = None, cost: float = 0.0, level: str = "INFO"):
        """Logs a structured event to file and prints a colored summary to the console."""
        timestamp = datetime.now().isoformat()
        details_dict = details or {}
        
        event = TraceEvent(
            timestamp=timestamp,
            task_id=task_id,
            agent_name=agent_name,
            event_type=event_type,
            message=message,
            details=details_dict,
            cost=cost
        )
        
        # Write to JSONL trace file
        try:
            with open(self.current_trace_file, "a") as f:
                f.write(json.dumps(asdict(event)) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write to trace file: {e}")

        # Format and print to console
        color = COLORS.get(event_type, COLORS.get(level, COLORS["RESET"]))
        reset = COLORS["RESET"]
        
        prefix = f"[{timestamp.split('T')[1][:8]}] [{task_id}] [{agent_name}]"
        console_message = f"{color}{prefix} {event_type} - {message}{reset}"
        
        if details_dict:
            # Print a concise representation of details if they exist
            details_str = json.dumps(details_dict, default=str)
            if len(details_str) > 80:
                details_str = details_str[:77] + "..."
            console_message += f"\n    {COLORS['INFO']}Details: {details_str}{reset}"
            
        print(console_message)

    def get_task_traces(self, task_id: str) -> list:
        """Retrieves all trace events associated with a specific task."""
        events = []
        if not os.path.exists(self.current_trace_file):
            return events
            
        with open(self.current_trace_file, "r") as f:
            for line in f:
                try:
                    event_data = json.loads(line.strip())
                    if event_data["task_id"] == task_id:
                        events.append(event_data)
                except json.JSONDecodeError:
                    continue
        return events
