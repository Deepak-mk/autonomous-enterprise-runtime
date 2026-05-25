import time
from economic_routing.task_classifier import TaskClassifier
from economic_routing.model_selector import ModelSelector
from economic_routing.observability_engine import ObservabilityEngine
from economic_routing.routing_engine import RoutingEngine

def run_simulation():
    classifier = TaskClassifier()
    model_selector = ModelSelector()
    observability_engine = ObservabilityEngine()
    routing_engine = RoutingEngine(
        classifier=classifier,
        model_selector=model_selector,
        observability_engine=observability_engine
    )

    print("\n" + "="*80)
    print("  STARTING ECONOMIC ROUTING & COMPUTATION SCHEDULER SIMULATION")
    print("="*80 + "\n")

    # Batch of typical tasks for an agent network
    tasks = [
        {
            "id": "T-1001",
            "desc": "Summarize client's 5-line support email regarding password reset.",
            "budget": 0.05
        },
        {
            "id": "T-1002",
            "desc": "Write a python script to parse CSV log files and extract IP addresses.",
            "budget": 0.10
        },
        {
            "id": "T-1003",
            "desc": "Reconcile corporate account statement sheet to locate a financial discrepancy of $450.",
            "budget": 0.50
        },
        {
            "id": "T-1004",
            "desc": "Analyze system server log traces to diagnose memory leak occurrences.",
            "budget": 0.30
        },
        {
            "id": "T-1005",
            "desc": "Translate French customer complaint text to English.",
            "budget": 0.02
        }
    ]

    print("--- SCENARIO 1: Dynamic Cost-Effective Routing ---")
    for t in tasks:
        routing_engine.execute_task(
            task_id=t["id"],
            description=t["desc"],
            max_budget=t["budget"]
        )
        time.sleep(0.3)

    print("\n--- SCENARIO 2: Budget Constraint Fallback Enforcement ---")
    # A critical financial task requiring high reasoning models (deepseek-r1), which normally cost ~$0.04+
    # But we set a tight budget of $0.005
    critical_discrepancy_task = {
        "id": "T-2001",
        "desc": "Perform strategic financial audit on corporate revenue and trace ledger anomalies.",
        "budget": 0.005  # extremely tight budget
    }
    
    print(f"Submitting high-reasoning task '{critical_discrepancy_task['desc'][:40]}...' with tight budget: ${critical_discrepancy_task['budget']:.4f}")
    routing_engine.execute_task(
        task_id=critical_discrepancy_task["id"],
        description=critical_discrepancy_task["desc"],
        max_budget=critical_discrepancy_task["budget"]
    )
    time.sleep(0.5)

    print("\n" + "="*80)
    print("  ECONOMIC ROUTING COMPUTATION REPORT & SAVINGS INSIGHTS")
    print("="*80)

    summary = observability_engine.get_summary()
    print(f"  Total Tasks Processed        : {summary['total_tasks']}")
    print(f"  Average Execution Latency    : {summary['avg_latency_seconds']}s")
    print(f"  Total actual routed cost     : \033[92m${summary['total_actual_cost']:.5f}\033[0m")
    print(f"  Baseline cost (GPT-4o only)  : \033[91m${summary['total_baseline_cost']:.5f}\033[0m")
    print(f"  Net computing pool savings   : \033[96m${summary['total_savings']:.5f} ({summary['savings_percentage']:.1f}% reduction)\033[0m")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_simulation()
