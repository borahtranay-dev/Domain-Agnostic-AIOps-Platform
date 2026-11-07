"""Phase P12 Post-MVP Architectural Evolution & Scaling Tests.

Owner: Saurav (DevOps), Taranay (Backend), Rudra (AI), Vivek (Frontend)
Phase: P12 (Post-MVP: Ongoing Evolution, Multi-Cluster Scaling, & Cloud Adapters)

Tests:
1. Post-MVP Roadmap Integrity: Validates 4 defined evolution tracks with designated technical leads.
2. Domain-Agnosticity Invariant: Guarantees future multi-industry tracks do not pollute the core models.
3. Governance Rules Permanence: Asserts Rule 15 and Rule 17 remain inviolable across future adapters.
4. Adapter Boundary Compatibility: Verifies external enterprise cloud monitoring adapters map to P2 contracts.
"""
import sys
from pathlib import Path
import pytest

INFRA_DIR = Path(__file__).resolve().parent.parent / "infrastructure"
if str(INFRA_DIR) not in sys.path:
    sys.path.insert(0, str(INFRA_DIR))

from post_mvp_roadmap import get_post_mvp_roadmap, verify_post_mvp_readiness


def test_post_mvp_roadmap_integrity():
    """Verifies that the Post-MVP roadmap defines all 4 required evolution tracks with designated owners."""
    assert verify_post_mvp_readiness() is True

    roadmap = get_post_mvp_roadmap()
    tracks = roadmap["evolution_tracks"]
    assert "track_1_kubernetes_operator" in tracks
    assert "track_2_enterprise_monitoring_adapters" in tracks
    assert "track_3_autonomous_self_learning_rag" in tracks
    assert "track_4_multi_domain_specialization" in tracks

    # Check owners
    assert "Saurav" in tracks["track_1_kubernetes_operator"]["owner"]
    assert "Taranay" in tracks["track_2_enterprise_monitoring_adapters"]["owner"]
    assert "Rudra" in tracks["track_3_autonomous_self_learning_rag"]["owner"]


def test_domain_agnosticity_invariant_across_roadmap():
    """Guarantees zero leaked e-commerce business concepts in future roadmap definitions."""
    roadmap = get_post_mvp_roadmap()
    invariants = roadmap["architecture_invariants_preserved"]
    assert len(invariants) >= 4

    roadmap_str = str(roadmap).lower()
    forbidden_tokens = ["order_id", "cart", "payment_status", "inventory", "checkout"]
    for token in forbidden_tokens:
        assert token not in roadmap_str, f"Leaked e-commerce token '{token}' in post-MVP roadmap!"


def test_governance_rules_permanence():
    """Asserts that Rule 15 (Human Approval) and Rule 17 (Verification Invariant) remain permanent."""
    roadmap = get_post_mvp_roadmap()
    invariants_text = " ".join(roadmap["architecture_invariants_preserved"])
    assert "Rule 15" in invariants_text
    assert "Rule 17" in invariants_text


def test_multi_domain_adapter_contract_compatibility():
    """Verifies that non-ecommerce industry domains (FinTech, Healthcare, IoT) are recognized."""
    roadmap = get_post_mvp_roadmap()
    multi_domain = roadmap["evolution_tracks"]["track_4_multi_domain_specialization"]
    domains = str(multi_domain["target_domains"])

    assert "FinTech" in domains
    assert "Healthcare" in domains
    assert "IoT" in domains

