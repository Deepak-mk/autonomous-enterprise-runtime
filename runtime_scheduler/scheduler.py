import time
from typing import List, Dict, Any
from runtime_scheduler.trace_logger import TraceLogger
from runtime_scheduler.agent_executor import AgentExecutor, Task

class RuntimeScheduler:
    def __init__(self, agent_executor: AgentExecutor, logger: TraceLogger):
        self.agent_executor = agent_executor
        self.logger = logger
        self.queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        
    def add_task(self, task: Task):
        """Adds a task to the scheduler queue and re-sorts by priority."""
        self.queue.append(task)
        # Sort queue by priority (descending order, higher number = higher priority)
        self.queue.sort(key=lambda t: t.priority, reverse=True)
        
        self.logger.log(
            task_id=task.task_id,
            agent_name=task.agent_type,
            event_type="INFO",
            message=f"Task queued: '{task.name}' (Priority: {task.priority})",
            details={}
        )

    def run_all(self, interactive: bool = False) -> Dict[str, Any]:
        """Executes all pending tasks in priority order and returns runtime analytics."""
        self.agent_executor.interactive = interactive
        
        total_tasks = len(self.queue)
        successful_tasks = 0
        failed_tasks = 0
        total_cost = 0.0
        
        start_time = time.time()
        
        print("\n" + "="*80)
        print(f"  AUTONOMOUS ENTERPRISE RUNTIME SCHEDULER: STARTING EXECUTION CYCLE ({total_tasks} Tasks)")
        print("="*80 + "\n")
        
        while self.queue:
            task = self.queue.pop(0)
            success = self.agent_executor.execute(task)
            
            if success:
                successful_tasks += 1
            else:
                failed_tasks += 1
                
            total_cost += task.accumulated_cost
            self.completed_tasks.append(task)
            print("-" * 80 + "\n")
            
        duration = time.time() - start_time
        
        metrics = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0.0,
            "total_cost": total_cost,
            "duration_seconds": round(duration, 2)
        }
        
        self.print_summary_report(metrics)
        return metrics

    def print_summary_report(self, metrics: Dict[str, Any]):
        """Prints a styled execution summary report."""
        print("="*80)
        print("  CYCLE EXECUTION SUMMARY REPORT")
        print("="*80)
        print(f"  Total Scheduled Tasks : {metrics['total_tasks']}")
        print(f"  Successful Tasks      : {metrics['successful_tasks']} (Success Rate: {metrics['success_rate']:.1f}%)")
        print(f"  Failed Tasks          : {metrics['failed_tasks']}")
        print(f"  Total Compute Cost    : ${metrics['total_cost']:.2f}")
        print(f"  Total Duration        : {metrics['duration_seconds']} seconds")
        print("="*80 + "\n")
