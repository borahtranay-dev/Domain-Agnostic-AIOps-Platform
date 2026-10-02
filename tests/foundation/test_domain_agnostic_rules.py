"""Continuous Domain-Agnosticity Test.

Verifies that no e-commerce-specific terms (orders, payments, carts, inventory)
contaminate the domain-agnostic core services.
"""
from pathlib import Path

FORBIDDEN_TERMS = ["order_id", "payment_status", "cart_id", "product_catalog", "inventory_count"]


def test_core_services_remain_domain_agnostic():
    repo_root = Path(__file__).resolve().parents[2]
    core_dirs = [
        repo_root / "apps" / "api" / "src",
        repo_root / "apps" / "worker" / "src",
        repo_root / "apps" / "ai-worker" / "src",
    ]

    for core_dir in core_dirs:
        for py_file in core_dir.glob("**/*.py"):
            content = py_file.read_text(encoding="utf-8").lower()
            for term in FORBIDDEN_TERMS:
                assert term not in content, f"Forbidden domain term '{term}' leaked into {py_file}!"
