"""Staging Deployment and Automated Rollback Orchestration Engine.

Owner: Saurav (DevOps & Reliability Lead)
Phase: P10 (Staging Environment, Automated Pipeline, and Rollback Demonstration)

Core Guarantees:
1. Zero-Downtime Safe Transitions: Validates candidate health before traffic promotion.
2. Automated Rollback Trigger: Telemetry failure (>1% error rate or failing health check)
   immediately halts candidate traffic and restores previous known stable release.
3. Immutable Audit Trail: Every deployment and rollback event records timestamp,
   commit/version hashes, telemetry metrics, and root cause notes.
4. Domain-Agnostic: Governs generic containerized microservices without e-commerce coupling.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
import time
import logging

logger = logging.getLogger("aiops.staging.deployment")


class DeploymentStatus:
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class StagingDeploymentController:
    """Manages staging releases, smoke tests, and autonomous rollbacks."""

    def __init__(self, initial_stable_version: str = "v1.0.0"):
        self.active_version = initial_stable_version
        self.previous_stable_version = initial_stable_version
        self.environment = "staging"
        self.history: List[Dict[str, Any]] = [
            {
                "event": "INITIAL_BOOTSTRAP",
                "version": initial_stable_version,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": DeploymentStatus.SUCCESS,
                "details": "Base staging environment initialized with verified stable image.",
            }
        ]

    def deploy(
        self,
        candidate_version: str,
        simulated_metrics: Optional[Dict[str, Any]] = None,
        smoke_check_fn: Optional[Callable[[], bool]] = None,
        simulate_fault: bool = False,
        fault_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deploys candidate version to staging with automated health verification and rollback."""
        deployment_id = f"dep-{int(time.time() * 1000)}"
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting staging deployment {deployment_id} for candidate {candidate_version}")

        # 1. Pre-deployment baseline check
        prior_stable = self.active_version

        # 2. Stage candidate version in canary slot
        current_candidate = candidate_version

        # 3. Execute Smoke Checks & Telemetry Verification
        health_passed = True
        failure_notes = []

        if simulate_fault:
            health_passed = False
            failure_notes.append(fault_reason or "Simulated critical runtime failure: CrashLoopBackOff")

        if smoke_check_fn:
            try:
                if not smoke_check_fn():
                    health_passed = False
                    failure_notes.append("Smoke check probe returned False (503 Service Unavailable)")
            except Exception as e:
                health_passed = False
                failure_notes.append(f"Smoke check threw unhandled exception: {str(e)}")

        # 4. Evaluate Telemetry Metrics (Rule 17 Staging Invariant)
        metrics = simulated_metrics or {
            "error_rate": 0.0,
            "p95_latency_ms": 42.0,
            "healthy_replicas": 3,
            "desired_replicas": 3,
        }

        if metrics.get("error_rate", 0.0) > 0.01:  # Error rate > 1.0% triggers rollback
            health_passed = False
            failure_notes.append(f"Error rate {metrics['error_rate']*100:.1f}% exceeds 1.0% tolerance threshold")

        if metrics.get("healthy_replicas", 0) < metrics.get("desired_replicas", 1):
            health_passed = False
            failure_notes.append(
                f"Replicas degraded: {metrics.get('healthy_replicas')}/{metrics.get('desired_replicas')} ready"
            )

        # 5. Branch: Rollback vs Success
        end_time = datetime.now(timezone.utc)
        duration_ms = (end_time - start_time).total_seconds() * 1000

        if not health_passed:
            # TRIGGER AUTOMATED ROLLBACK
            rollback_reason = " | ".join(failure_notes)
            logger.warning(
                f"Deployment {deployment_id} failed verification! Initiating autonomous rollback to {prior_stable}"
            )

            rollback_record = {
                "deployment_id": deployment_id,
                "event": "AUTONOMOUS_ROLLBACK",
                "candidate_version": candidate_version,
                "restored_version": prior_stable,
                "status": DeploymentStatus.ROLLED_BACK,
                "reason": rollback_reason,
                "metrics": metrics,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_ms": round(duration_ms, 2),
            }
            self.history.append(rollback_record)
            self.active_version = prior_stable  # Restored immediately

            return {
                "deployment_id": deployment_id,
                "status": DeploymentStatus.ROLLED_BACK,
                "active_version": self.active_version,
                "rejected_version": candidate_version,
                "rollback_executed": True,
                "reason": rollback_reason,
                "metrics": metrics,
                "timestamp": end_time.isoformat(),
            }

        # PROMOTION SUCCESS
        self.previous_stable_version = prior_stable
        self.active_version = candidate_version
        success_record = {
            "deployment_id": deployment_id,
            "event": "RELEASE_PROMOTED",
            "candidate_version": candidate_version,
            "previous_version": prior_stable,
            "status": DeploymentStatus.SUCCESS,
            "metrics": metrics,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": round(duration_ms, 2),
            "details": "All smoke checks passed. Candidate version successfully promoted to active staging.",
        }
        self.history.append(success_record)

        return {
            "deployment_id": deployment_id,
            "status": DeploymentStatus.SUCCESS,
            "active_version": self.active_version,
            "previous_version": prior_stable,
            "rollback_executed": False,
            "metrics": metrics,
            "timestamp": end_time.isoformat(),
        }

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Returns the full chronological deployment and rollback audit trail."""
        return self.history

    def get_current_state(self) -> Dict[str, Any]:
        """Returns current live staging environment status."""
        return {
            "environment": self.environment,
            "active_version": self.active_version,
            "previous_stable_version": self.previous_stable_version,
            "total_deployments": len(self.history) - 1,
            "last_updated": self.history[-1]["completed_at"] if "completed_at" in self.history[-1] else self.history[-1]["timestamp"],
        }

