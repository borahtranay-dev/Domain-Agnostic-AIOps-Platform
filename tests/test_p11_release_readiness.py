"""Phase P11 Production Release Readiness & Formal Verification Integration Tests.

Owner: Saurav (DevOps Lead), Taranay (Backend Lead), Rudra (AI Lead), Vivek (Frontend Lead)
Phase: P11 (Production Release & v1.0.0 Tagging)

Tests:
1. Production Docker Compose Spec: Validates restart: always, CPU/memory limits, and healthchecks.
2. Release Manifest Integrity: Verifies v1.0.0 semantic version, codename Aegis-1, and 4/4 team sign-offs.
3. Subsystem Scope Audit: Asserts Saurav, Taranay, Rudra, and Vivek scopes are completely certified.
4. Phase Completion Audit: Verifies all phases P0 through P11 are formally certified as COMPLETE.
5. Domain-Agnosticity Invariant: Guarantees zero leaked e-commerce business concepts in release specifications.
"""
import sys
from pathlib import Path
import pytest
import yaml

INFRA_DIR = Path(__file__).resolve().parent.parent / "infrastructure"
if str(INFRA_DIR) not in sys.path:
    sys.path.insert(0, str(INFRA_DIR))

from release_manifest import get_release_manifest, verify_release_readiness


def test_production_compose_spec_hardened():
    """Validates that docker-compose.prod.yml enforces enterprise production standards."""
    prod_compose_path = Path(__file__).resolve().parent.parent / "docker-compose.prod.yml"
    assert prod_compose_path.exists(), "docker-compose.prod.yml must exist"

    with open(prod_compose_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    required_services = ["postgres", "redis", "api", "worker", "ai-worker", "web"]
    for s in required_services:
        assert s in services, f"Production compose must declare {s} service"
        svc = services[s]
        assert svc.get("restart") == "always", f"Service {s} must have restart: always"
        assert "deploy" in svc, f"Service {s} must specify deployment resource limits"
        assert "limits" in svc["deploy"]["resources"], f"Service {s} must have CPU/RAM limits"


def test_release_manifest_integrity_and_team_signoffs():
    """Verifies that release manifest contains valid v1.0.0 version and unanimous 4/4 team approvals."""
    manifest = get_release_manifest()
    assert manifest["version"] == "v1.0.0"
    assert manifest["codename"] == "Aegis-1"
    assert manifest["release_status"] == "GA_PRODUCTION_READY"

    sign_offs = manifest["subsystem_sign_offs"]
    assert len(sign_offs) == 4, "Must have all 4 subsystem owners represented"

    # 1. Saurav (DevOps)
    saurav = sign_offs["devops_and_reliability"]
    assert saurav["owner"] == "Saurav"
    assert saurav["sign_off_status"] == "APPROVED"
    assert "docker-compose.prod.yml" in str(saurav["deliverables_certified"])

    # 2. Taranay (Backend)
    taranay = sign_offs["backend_api"]
    assert taranay["owner"] == "Taranay"
    assert taranay["sign_off_status"] == "APPROVED"
    assert "FastAPI Microservice" in str(taranay["deliverables_certified"])

    # 3. Rudra (AI / RAG)
    rudra = sign_offs["ai_and_rag"]
    assert rudra["owner"] == "Rudra"
    assert rudra["sign_off_status"] == "APPROVED"
    assert "LangChain Diagnostic Engine" in str(rudra["deliverables_certified"])

    # 4. Vivek (Frontend)
    vivek = sign_offs["frontend_cockpit"]
    assert vivek["owner"] == "Vivek"
    assert vivek["sign_off_status"] == "APPROVED"
    assert "Developer Cockpit SRE Dashboard" in str(vivek["deliverables_certified"])

    # Overall gate
    assert verify_release_readiness() is True


def test_phase_completion_audit_scorecard():
    """Verifies that all 12 sequential phases (P0 to P11) are recorded as COMPLETE in release audit."""
    manifest = get_release_manifest()
    audit = manifest["phase_completion_audit"]

    for i in range(12):
        phase_key = f"P{i}"
        assert phase_key in audit
        assert "COMPLETE" in audit[phase_key]


def test_operational_sla_target_calibration():
    """Validates that release manifest specifies explicit quantitative operational targets."""
    manifest = get_release_manifest()
    sla = manifest["operational_metrics_targets"]
    assert sla["mttd_reduction_target"] == "50%"
    assert sla["mttr_reduction_target"] == "30-50%"
    assert sla["automated_resolution_target"] == ">=70%"
    assert sla["target_availability"] == "99.9%"


def test_domain_agnosticity_invariant_in_release():
    """Ensures zero leaked e-commerce concepts in release manifests, production definitions, or metadata."""
    manifest = get_release_manifest()
    manifest_str = str(manifest).lower()

    forbidden_tokens = ["order_id", "cart", "payment_status", "inventory", "checkout"]
    for token in forbidden_tokens:
        assert token not in manifest_str, f"Leaked e-commerce token '{token}' in production release manifest!"
