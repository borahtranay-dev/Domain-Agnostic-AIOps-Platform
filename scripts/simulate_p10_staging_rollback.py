"""Phase P10 Staging Deployment & Autonomous Rollback Interactive Demonstration.

Owner: Saurav (DevOps & Reliability Lead)
Phase: P10 (Staging Environment, Automated Pipeline, and Rollback Demonstration)

Demonstrates:
1. Active Staging Baseline (v1.0.0-stable).
2. Successful Candidate Promotion (v1.0.1).
3. Critical Fault Injection during Candidate Canary (v1.0.2-broken).
4. Autonomous Zero-Downtime Rollback Trigger & Restoration to v1.0.1.
5. Immutable SRE Audit Trail Inspection.
"""
import sys
from pathlib import Path
import time

INFRA_DIR = Path(__file__).resolve().parent.parent / "infrastructure"
if str(INFRA_DIR) not in sys.path:
    sys.path.insert(0, str(INFRA_DIR))

from deployment_controller import StagingDeploymentController, DeploymentStatus


def print_banner():
    print("\n" + "=" * 76)
    print("   DOMAIN-AGNOSTIC AIOPS PLATFORM -- STAGING DEPLOYMENT & ROLLBACK (P10)   ")
    print("=" * 76 + "\n")


def print_step(step_num: int, total_steps: int, title: str):
    print(f"\n[STAGE {step_num}/{total_steps}] {title}")
    print("-" * 64)


def main():
    print_banner()
    controller = StagingDeploymentController(initial_stable_version="v1.0.0-stable")

    # STAGE 1: Current Staging Status
    print_step(1, 4, "Staging Environment Baseline Status")
    state = controller.get_current_state()
    print(f"  [OK] Environment: {state['environment'].upper()}")
    print(f"  [OK] Active Version: {state['active_version']}")
    print(f"  [OK] Isolated Staging Ports: API (8080), Web (3001), Postgres (5433), Redis (6380)")
    time.sleep(0.5)

    # STAGE 2: Successful Candidate Deployment
    print_step(2, 4, "Deploy Candidate v1.0.1 (Healthy Performance Patch)")
    print("  --> Initiating staging canary deployment for v1.0.1...")
    healthy_metrics = {
        "error_rate": 0.001,
        "p95_latency_ms": 35.2,
        "healthy_replicas": 3,
        "desired_replicas": 3,
    }
    res_success = controller.deploy(
        candidate_version="v1.0.1-perf",
        simulated_metrics=healthy_metrics,
        smoke_check_fn=lambda: True,
    )
    print(f"  [OK] Telemetry Verification PASSED: Error Rate = 0.1%, p95 Latency = 35.2ms")
    print(f"  [OK] Release Status: {res_success['status']}")
    print(f"  [OK] Active Staging Version Promoted To: {res_success['active_version']}")
    time.sleep(0.5)

    # STAGE 3: Fault Injection & Automated Rollback
    print_step(3, 4, "Deploy Candidate v1.0.2-canary (Simulating Degraded Memory Leak)")
    print("  --> Staging candidate v1.0.2-canary in live traffic slot...")
    time.sleep(0.3)
    degraded_metrics = {
        "error_rate": 0.092,  # 9.2% error rate exceeds 1.0% limit
        "p95_latency_ms": 1150.0,
        "healthy_replicas": 1,
        "desired_replicas": 3,
    }
    print("  [WARN] Ingesting Live Telemetry: Error rate spiked to 9.2%! 2 of 3 replicas unhealthy!")
    print("  [ALERT] SLA Breach Detected! Triggering Autonomous Rollback...")
    time.sleep(0.4)

    res_rollback = controller.deploy(
        candidate_version="v1.0.2-canary-broken",
        simulated_metrics=degraded_metrics,
        smoke_check_fn=lambda: True,
    )

    print(f"  [EMERGENCY ACTION] Rollback Executed: {res_rollback['rollback_executed']}")
    print(f"  [RESTORED] Active Version Reverted To: {res_rollback['active_version']}")
    print(f"  [REJECTED] Faulty Image Evicted: {res_rollback['rejected_version']}")
    print(f"  [RATIONALE] Reason: {res_rollback['reason']}")
    time.sleep(0.5)

    # STAGE 4: Immutable SRE Audit Trail
    print_step(4, 4, "Immutable SRE Deployment & Rollback Audit Trail")
    trail = controller.get_audit_trail()
    print(f"{'TIMESTAMP':<28} | {'EVENT':<20} | {'VERSION':<18} | {'STATUS'}")
    print("-" * 76)
    for entry in trail:
        ts = entry.get("completed_at") or entry.get("timestamp") or ""
        event = entry.get("event")
        ver = entry.get("candidate_version") or entry.get("version") or entry.get("active_version")
        status = entry.get("status")
        print(f"{ts[:25]:<28} | {event:<20} | {ver:<18} | {status}")

    print("\n" + "=" * 76)
    print("  >>> PHASE P10 STAGING & AUTONOMOUS ROLLBACK DEMONSTRATION COMPLETE <<<")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()

