import time
from typing import Tuple, Any, Dict
from runtime_scheduler.trace_logger import TraceLogger
from runtime_scheduler.policy_engine import PolicyDecision

# Define custom exceptions for simulated errors
class PolicyViolationError(Exception):
    def __init__(self, message: str, requires_approval: bool = False):
        super().__init__(message)
        self.requires_approval = requires_approval

class NetworkTimeoutError(Exception):
    pass

class ToolExecutionError(Exception):
    pass

class AgentHallucinationError(Exception):
    pass

class RecoveryHandler:
    def __init__(self, logger: TraceLogger):
        self.logger = logger
        self.max_retries = 3

    def handle_error(
        self, 
        task_id: str, 
        agent_name: str, 
        error: Exception, 
        attempt: int, 
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Determines recovery action based on exception type and retry attempts."""
        
        error_name = error.__class__.__name__
        
        self.logger.log(
            task_id=task_id,
            agent_name=agent_name,
            event_type="RECOVERY",
            message=f"Analyzing error '{error_name}' (Attempt {attempt}/{self.max_retries})",
            details={"error_msg": str(error), "context_keys": list(context.keys())}
        )

        # 1. Network Error -> Retry with backoff
        if isinstance(error, NetworkTimeoutError):
            if attempt < self.max_retries:
                backoff_time = 2 ** attempt
                self.logger.log(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type="RECOVERY",
                    message=f"Applying Exponential Backoff. Sleeping for {backoff_time}s before retry...",
                    details={"backoff_seconds": backoff_time}
                )
                time.sleep(backoff_time)
                return "RETRY", {"attempt": attempt + 1}
            else:
                return "FAIL", {"reason": "Max network retries exceeded"}

        # 2. Agent Hallucination/Output Parse Error -> Fallback to stronger model
        elif isinstance(error, AgentHallucinationError):
            current_model = context.get("model", "gpt-3.5-turbo")
            fallback_model = "gpt-4o" if current_model != "gpt-4o" else "claude-3-5-sonnet"
            self.logger.log(
                task_id=task_id,
                agent_name=agent_name,
                event_type="RECOVERY",
                message=f"Output parsing/hallucination detected. Escalating model from '{current_model}' to '{fallback_model}'",
                details={"original_model": current_model, "escalated_model": fallback_model}
            )
            return "RETRY_WITH_MODEL_FALLBACK", {"model": fallback_model, "attempt": attempt + 1}

        # 3. Tool Execution failure -> Reflection and argument correction
        elif isinstance(error, ToolExecutionError):
            if attempt < self.max_retries:
                self.logger.log(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type="RECOVERY",
                    message="Tool call failed. Engaging reflection loop to correct parameters...",
                    details={"original_error": str(error)}
                )
                # Simulating a reflection modification to arguments
                corrected_args = context.get("tool_args", {}).copy()
                if "amount" in corrected_args:
                    # e.g., trying to fix negative amount or format issue
                    if isinstance(corrected_args["amount"], str):
                        try:
                            corrected_args["amount"] = float(corrected_args["amount"].replace("$", ""))
                        except ValueError:
                            pass
                return "RETRY_WITH_CORRECTED_ARGS", {"tool_args": corrected_args, "attempt": attempt + 1}
            else:
                return "FAIL", {"reason": "Max tool retries exceeded"}

        # Default fallback
        return "FAIL", {"reason": f"Unhandled exception: {error_name}"}

    def handle_policy_block(
        self, 
        task_id: str, 
        agent_name: str, 
        decision: PolicyDecision, 
        interactive: bool = False
    ) -> Tuple[str, Dict[str, Any]]:
        """Handles a policy violation decision. Decides whether to escalate to human or fail."""
        
        self.logger.log(
            task_id=task_id,
            agent_name=agent_name,
            event_type="POLICY",
            message=f"Policy Block: {decision.reason}",
            details={"requires_human_approval": decision.requires_human_approval}
        )

        if decision.requires_human_approval:
            self.logger.log(
                task_id=task_id,
                agent_name=agent_name,
                event_type="RECOVERY",
                message="Initiating Human-in-the-Loop (HITL) approval sequence...",
                details={}
            )
            
            # Interactive Terminal prompt or Simulated prompt
            if interactive:
                try:
                    response = input(f"\n[HITL Verification Required] Approve action '{decision.reason}'? (y/n): ").strip().lower()
                    approved = response == 'y'
                except Exception:
                    # If input is closed or non-interactive
                    approved = True
            else:
                # Simulated approval
                print(f"[Simulated HITL] Reviewing request... -> APPROVED by administrator")
                approved = True
                
            if approved:
                self.logger.log(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type="SUCCESS",
                    message="Action manually overridden and approved by Human Administrator",
                    details={}
                )
                return "BYPASS_POLICY", {}
            else:
                self.logger.log(
                    task_id=task_id,
                    agent_name=agent_name,
                    event_type="ERROR",
                    message="Action rejected by Human Administrator. Aborting step.",
                    details={}
                )
                return "FAIL", {"reason": "Human administrator denied the request"}
        else:
            # Policy violations that can't be bypassed by simple human authorization (e.g. hard cost boundaries exceeded)
            return "FAIL", {"reason": f"Hard policy block: {decision.reason}"}
