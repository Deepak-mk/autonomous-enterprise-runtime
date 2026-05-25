import random
from typing import Dict, Any, List
from runtime_scheduler.trace_logger import TraceLogger
from runtime_scheduler.policy_engine import PolicyEngine, PolicyDecision
from runtime_scheduler.recovery_handler import (
    RecoveryHandler, 
    NetworkTimeoutError, 
    AgentHallucinationError, 
    ToolExecutionError
)

class Task:
    def __init__(self, task_id: str, name: str, agent_type: str, steps: List[Dict[str, Any]], priority: int = 1):
        self.task_id = task_id
        self.name = name
        self.agent_type = agent_type
        self.steps = steps  # List of steps, each containing: tool, args, expected_cost, failure_modes
        self.priority = priority
        self.status = "PENDING"
        self.accumulated_cost = 0.0

class AgentExecutor:
    def __init__(self, policy_engine: PolicyEngine, recovery_handler: RecoveryHandler, logger: TraceLogger):
        self.policy_engine = policy_engine
        self.recovery_handler = recovery_handler
        self.logger = logger
        self.interactive = False

    def execute(self, task: Task) -> bool:
        """Executes all steps in a task, checking policy rules and applying recovery handlers when needed."""
        task.status = "RUNNING"
        self.logger.log(
            task_id=task.task_id,
            agent_name=task.agent_type,
            event_type="TASK_START",
            message=f"Starting task: '{task.name}' (Priority: {task.priority})",
            details={"total_steps": len(task.steps)}
        )

        step_idx = 0
        while step_idx < len(task.steps):
            step = task.steps[step_idx]
            tool_name = step.get("tool")
            args = step.get("args", {})
            base_cost = step.get("expected_cost", 0.05)
            failure_modes = step.get("failure_modes", [])
            
            # Simulated model parameters
            model = step.get("model", "gpt-3.5-turbo")
            attempt = step.get("attempt", 1)

            self.logger.log(
                task_id=task.task_id,
                agent_name=task.agent_type,
                event_type="TOOL_CALL",
                message=f"Planning step {step_idx + 1}/{len(task.steps)}: {tool_name}",
                details={"tool": tool_name, "args": args, "model": model, "attempt": attempt}
            )

            # 1. Policy Pre-Check
            decision = self.policy_engine.check_action(
                task_id=task.task_id,
                agent_name=task.agent_type,
                tool_name=tool_name,
                args=args,
                accumulated_cost=task.accumulated_cost
            )

            if not decision.allowed:
                # Handle Policy Violations
                action, params = self.recovery_handler.handle_policy_block(
                    task_id=task.task_id,
                    agent_name=task.agent_type,
                    decision=decision,
                    interactive=self.interactive
                )

                if action == "BYPASS_POLICY":
                    self.logger.log(
                        task_id=task.task_id,
                        agent_name=task.agent_type,
                        event_type="POLICY",
                        message="Bypassing policy check per human override",
                        details={}
                    )
                else:
                    task.status = "FAILED"
                    self.logger.log(
                        task_id=task.task_id,
                        agent_name=task.agent_type,
                        event_type="ERROR",
                        message=f"Task terminated: {params.get('reason')}",
                        details={}
                    )
                    return False

            # 2. Simulate Execution with Potential Failures
            task.accumulated_cost += base_cost
            try:
                # If there are simulated failures in this step, trigger them on specified attempts
                if failure_modes and attempt == 1:
                    triggered_failure = failure_modes[0]
                    # Simulate random or targeted failures
                    if triggered_failure == "network_timeout":
                        raise NetworkTimeoutError("Gateway Connection Timeout (504)")
                    elif triggered_failure == "parsing_error":
                        raise AgentHallucinationError("Failed to parse JSON: key 'transaction_id' not found in model response")
                    elif triggered_failure == "malformed_args":
                        raise ToolExecutionError("Invalid parameter format: amount must be numeric float, received '$150.00'")

                # Tool executes successfully
                self.logger.log(
                    task_id=task.task_id,
                    agent_name=task.agent_type,
                    event_type="SUCCESS",
                    message=f"Step {step_idx + 1} completed successfully via {tool_name}",
                    details={"cost_added": f"${base_cost:.2f}", "total_cost": f"${task.accumulated_cost:.2f}"},
                    cost=base_cost
                )
                step_idx += 1  # Move to next step

            except Exception as e:
                # 3. Handle Exceptions via Recovery Handler
                action, params = self.recovery_handler.handle_error(
                    task_id=task.task_id,
                    agent_name=task.agent_type,
                    error=e,
                    attempt=attempt,
                    context={"tool_args": args, "model": model}
                )

                if action == "RETRY":
                    # Re-run same step with updated attempt counter
                    step["attempt"] = params.get("attempt", attempt + 1)
                    # Clear the simulated failure modes so it succeeds on the next try
                    step["failure_modes"] = []
                elif action == "RETRY_WITH_MODEL_FALLBACK":
                    step["attempt"] = params.get("attempt", attempt + 1)
                    step["model"] = params.get("model")
                    step["failure_modes"] = []
                elif action == "RETRY_WITH_CORRECTED_ARGS":
                    step["attempt"] = params.get("attempt", attempt + 1)
                    step["args"] = params.get("tool_args", args)
                    step["failure_modes"] = []
                else:
                    # Fail Task
                    task.status = "FAILED"
                    self.logger.log(
                        task_id=task.task_id,
                        agent_name=task.agent_type,
                        event_type="ERROR",
                        message=f"Task execution failed: {params.get('reason', 'Unknown failure')}",
                        details={}
                    )
                    return False

        task.status = "COMPLETED"
        self.logger.log(
            task_id=task.task_id,
            agent_name=task.agent_type,
            event_type="TASK_COMPLETE",
            message=f"Task completed successfully: '{task.name}'",
            details={"total_spend": f"${task.accumulated_cost:.2f}"}
        )
        return True
