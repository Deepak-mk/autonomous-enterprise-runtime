import argparse
from runtime_scheduler.trace_logger import TraceLogger
from runtime_scheduler.policy_engine import PolicyEngine
from runtime_scheduler.recovery_handler import RecoveryHandler
from runtime_scheduler.agent_executor import AgentExecutor, Task
from runtime_scheduler.scheduler import RuntimeScheduler

def generate_simulation_tasks() -> list:
    tasks = []
    
    # 1. Simple Sentiment Analysis Task (Priority: Low - 1)
    # Succeeds immediately without issues.
    tasks.append(Task(
        task_id="TSK-001",
        name="Analyze Customer Support Sentiment",
        agent_type="AnalysisAgent",
        priority=1,
        steps=[
            {
                "tool": "query_database",
                "args": {"query": "SELECT comment FROM support_tickets WHERE id = 104"},
                "expected_cost": 0.05,
                "failure_modes": []
            },
            {
                "tool": "sentiment_analysis",
                "args": {"text": "I really love the product but the shipping was slightly delayed."},
                "expected_cost": 0.02,
                "failure_modes": []
            }
        ]
    ))
    
    # 2. Database Sync Task (Priority: Medium - 2)
    # Triggers a Network Timeout, which recovers via exponential backoff.
    tasks.append(Task(
        task_id="TSK-002",
        name="Sync CRM Customer Records",
        agent_type="SupportAgent",
        priority=2,
        steps=[
            {
                "tool": "query_database",
                "args": {"query": "SELECT * FROM users WHERE last_sync < '2026-05-01'"},
                "expected_cost": 0.08,
                "failure_modes": ["network_timeout"]  # Will fail on first attempt
            },
            {
                "tool": "write_to_crm",
                "args": {"updates": [{"user_id": 402, "sync_status": "synced"}]},
                "expected_cost": 0.12,
                "failure_modes": []
            }
        ]
    ))

    # 3. Invoice Parsing Task (Priority: Medium - 3)
    # Triggers a Parsing Error (hallucination simulation), which recovers via LLM-model escalation.
    tasks.append(Task(
        task_id="TSK-003",
        name="Extract Invoice Metadata",
        agent_type="AnalysisAgent",
        priority=3,
        steps=[
            {
                "tool": "parse_document",
                "args": {"doc_path": "/invoices/inv_2026_988.pdf"},
                "expected_cost": 0.15,
                "model": "gpt-3.5-turbo",
                "failure_modes": ["parsing_error"]  # Will fail parsing validation
            },
            {
                "tool": "record_invoice",
                "args": {"invoice_id": "INV-988", "amount": 1250.00},
                "expected_cost": 0.10,
                "failure_modes": []
            }
        ]
    ))

    # 4. Customer Refund (Priority: High - 4)
    # Triggers a Policy Violation ($250 > $100 limit) requiring HITL approval.
    tasks.append(Task(
        task_id="TSK-004",
        name="Process Customer Refund Request",
        agent_type="SupportAgent",
        priority=4,
        steps=[
            {
                "tool": "query_database",
                "args": {"query": "SELECT status, balance FROM accounts WHERE user_id = 99"},
                "expected_cost": 0.05,
                "failure_modes": []
            },
            {
                "tool": "send_refund",
                "args": {"recipient": "user_99@domain.com", "amount": 250.00},
                "expected_cost": 0.20,
                "failure_modes": []
            }
        ]
    ))

    # 5. Production Application Deployment (Priority: Critical - 5)
    # Triggers restricted tool policy block & Human-in-the-loop approval.
    tasks.append(Task(
        task_id="TSK-005",
        name="Deploy Hotfix patch to Production Cluster",
        agent_type="AnalysisAgent",  # Prohibited agent from deploying
        priority=5,
        steps=[
            {
                "tool": "deploy_to_production",
                "args": {"image": "frontend:v1.4.2-hotfix"},
                "expected_cost": 0.50,
                "failure_modes": []
            }
        ]
    ))

    return tasks

def main():
    parser = argparse.ArgumentParser(description="Autonomous Enterprise Runtime Simulator")
    parser.add_argument(
        "--interactive", 
        action="store_true", 
        help="Run simulation with interactive console inputs for human-in-the-loop decisions."
    )
    args = parser.parse_args()

    # Initialize subsystems
    logger = TraceLogger()
    policy_engine = PolicyEngine(max_cost_limit=5.0, transaction_limit=100.0)
    recovery_handler = RecoveryHandler(logger=logger)
    agent_executor = AgentExecutor(
        policy_engine=policy_engine, 
        recovery_handler=recovery_handler, 
        logger=logger
    )
    scheduler = RuntimeScheduler(agent_executor=agent_executor, logger=logger)

    # Queue up standard tasks
    tasks = generate_simulation_tasks()
    for task in tasks:
        scheduler.add_task(task)

    # Run the cycle
    scheduler.run_all(interactive=args.interactive)

if __name__ == "__main__":
    main()
