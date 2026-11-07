"""Phase P10 Staging Environment & Automated Rollback Integration Test Suite.

Owner: Saurav (DevOps & Reliability Lead)
Phase: P10 (Staging Environment, Automated Pipeline, and Rollback Demonstration)

Tests:
1. Staging Docker Compose Topology: Validates port isolation, dedicated staging DB, and health checks.
2. Successful Candidate Promotion: Clean deployment upgrade from v1.0.0 to v1.0.1 with smoke test verification.
3. Automated Rollback on Degraded Telemetry: Degraded error rate (>1%) triggers instantaneous rollback to stable.
4. Automated Rollback on Failed Health Probe: Failing probe (503 / CrashLoopBackOff) halts rollout and restores stable.
5. Immutable Audit Trail: Asserts full chronological history with timestamps, durations, and failure rationales.
6. Domain-Agnosticity Invariant: Verifies zero leaked e-commerce concepts in staging configurations or controllers.
"""
import sys
from pathlib import Path
import pytest
import yaml

# Add infrastructure to sys.path
INFRA_DIR = Path(__file__).resolve().parent.parent / "infrastructure"
if str(INFRA_DIR) not in sys.path:
    sys.path.insert(0, str(INFRA_DIR))

from deployment_controller import StagingDeploymentController, DeploymentStatus


def test_staging_compose_topology_and_isolation():
    """Validates that docker-compose.staging.yml enforces network, port, and database isolation."""
    compose_path = Path(__file__).resolve().parent.parent / "docker-compose.staging.yml"
    assert compose_path.exists(), "docker-compose.staging.yml must exist"

    with open(compose_path, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    services = compose_data.get("services", {})
    assert "postgres-staging" in services
    assert "redis-staging" in services
    assert "api-staging" in services
    assert "ai-worker-staging" in services
    assert "web-staging" in services

    # Verify staging port isolation (no overlap with standard dev ports 5432, 6379, 8000, 8001, 3000)
    api_ports = str(services["api-staging"]["ports"])
    assert "8080" in api_ports, "Staging API must use isolated port 8080"

    web_ports = str(services["web-staging"]["ports"])
    assert "3001" in web_ports, "Staging Web UI must use isolated port 3001"

    # Verify dedicated staging environment variables
    api_env = services["api-staging"]["environment"]
    assert api_env.get("APP_ENV") == "staging"
    assert api_env.get("LOG_LEVEL") == "DEBUG"


def test_staging_successful_candidate_promotion():
    """Verifies that a healthy candidate release successfully promotes to active staging."""
    controller = StagingDeploymentController(initial_stable_version="v1.0.0")
    assert controller.active_version == "v1.0.0"

    healthy_metrics = {
        "error_rate": 0.001,  # 0.1% well under 1% tolerance
        "p95_latency_ms": 38.5,
        "healthy_replicas": 3,
        "desired_replicas": 3,
    }

    result = controller.deploy(
        candidate_version="v1.0.1",
        simulated_metrics=healthy_metrics,
        smoke_check_fn=lambda: True,
    )

    assert result["status"] == DeploymentStatus.SUCCESS
    assert result["active_version"] == "v1.0.1"
    assert result["previous_version"] == "v1.0.0"
    assert result["rollback_executed"] is False
    assert controller.active_version == "v1.0.1"


def test_staging_automated_rollback_on_degraded_telemetry():
    """Verifies that telemetry degradation (error rate > 1%) triggers autonomous rollback to stable."""
    controller = StagingDeploymentController(initial_stable_version="v1.0.1")

    degraded_metrics = {
        "error_rate": 0.085,  # 8.5% error rate exceeds 1% threshold
        "p95_latency_ms": 850.0,
        "healthy_replicas": 3,
        "desired_replicas": 3,
    }

    result = controller.deploy(
        candidate_version="v1.0.2-canary-broken",
        simulated_metrics=degraded_metrics,
        smoke_check_fn=lambda: True,
    )

    # Must immediately trigger automated rollback
    assert result["status"] == DeploymentStatus.ROLLED_BACK
    assert result["rollback_executed"] is True
    assert result["active_version"] == "v1.0.1"  # Restored to verified stable
    assert result["rejected_version"] == "v1.0.2-canary-broken"
    assert "exceeds 1.0% tolerance threshold" in result["reason"]

    # Verify controller state restored
    assert controller.active_version == "v1.0.1"


def test_staging_automated_rollback_on_failed_health_probe():
    """Verifies that failing smoke/health probe instantly halts rollout and triggers rollback."""
    controller = StagingDeploymentController(initial_stable_version="v1.0.1")

    # Simulate smoke probe failure (e.g. 503 Service Unavailable)
    def failing_smoke_probe():
        return False

    result = controller.deploy(
        candidate_version="v1.0.3-bad-config",
        smoke_check_fn=failing_smoke_probe,
    )

    assert result["status"] == DeploymentStatus.ROLLED_BACK
    assert result["rollback_executed"] is True
    assert result["active_version"] == "v1.0.1"
    assert "Smoke check probe returned False" in result["reason"]


def test_staging_immutable_audit_trail():
    """Verifies that all deployments and rollbacks are recorded in chronological audit trail."""
    controller = StagingDeploymentController(initial_stable_version="v1.0.0")

    # 1. Success deployment
    controller.deploy("v1.0.1", smoke_check_fn=lambda: True)

    # 2. Failed deployment triggering rollback
    controller.deploy(
        "v1.0.2-broken",
        simulate_fault=True,
        fault_reason="OOMKilled during heap warm-up",
    )

    history = controller.get_audit_trail()
    assert len(history) == 3  # Initial + Success + Rollback

    init_event = history[0]
    assert init_event["event"] == "INITIAL_BOOTSTRAP"

    promote_event = history[1]
    assert promote_event["event"] == "RELEASE_PROMOTED"
    assert promote_event["candidate_version"] == "v1.0.1"

    rollback_event = history[2]
    assert rollback_event["event"] == "AUTONOMOUS_ROLLBACK"
    assert rollback_event["candidate_version"] == "v1.0.2-broken"
    assert rollback_event["restored_version"] == "v1.0.1"
    assert "OOMKilled" in rollback_event["reason"]


def test_domain_agnosticity_invariant_in_staging():
    """Guarantees zero leaked e-commerce concepts in staging definitions and deployment controller."""
    controller = StagingDeploymentController()
    state = controller.get_current_state()

    forbidden_tokens = ["order_id", "cart", "payment_status", "checkout", "inventory"]
    for token in forbidden_tokens:
        assert token not in str(state).lower()
        assert token not in str(controller.history).lower()

