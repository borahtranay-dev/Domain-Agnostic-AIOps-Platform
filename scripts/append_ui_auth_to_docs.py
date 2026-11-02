"""
Script to append Developer Cockpit UI overhaul, Matte Obsidian design, and B2B Multi-Tenant Authentication
to END_USER_PRODUCT_GUIDE.docx and PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx.
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from pathlib import Path

BASE_DIR = Path(r"e:\domain-agnostic-platform")
USER_GUIDE_PATH = BASE_DIR / "END_USER_PRODUCT_GUIDE.docx"
KT_MASTER_PATH = BASE_DIR / "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx"

def update_user_guide():
    if not USER_GUIDE_PATH.exists():
        print(f"Skipping {USER_GUIDE_PATH}, file not found")
        return

    doc = docx.Document(str(USER_GUIDE_PATH))

    # Check if already appended
    for p in doc.paragraphs:
        if "Developer Cockpit & Multi-Tenant B2B Security" in p.text:
            print("User guide already contains Section 6. Skipping duplicate append.")
            return

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run("6. Developer Cockpit Experience & Multi-Tenant B2B Security")
    r.font.name, r.font.size, r.font.bold = "Calibri", Pt(16), True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    def body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name, r.font.size = "Calibri", Pt(10.5)
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def bullet(prefix, text):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r1 = p.add_run(f"• {prefix}: ")
        r1.font.name, r1.font.size, r1.font.bold = "Calibri", Pt(10.5), True
        r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r2 = p.add_run(text)
        r2.font.name, r2.font.size = "Calibri", Pt(10.5)
        r2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    body(
        "To deliver a true enterprise B2B SaaS experience, the Developer Cockpit has been upgraded "
        "with an industrial-grade user experience and strict multi-tenant access control."
    )

    bullet("Industrial Matte Obsidian UI", 
           "Replaced consumer-style glowing neon aesthetics with a sleek, low-fatigue matte obsidian black (#09090b) "
           "and carbon graphite palette inspired by industry leaders like Datadog, Raycast, and Linear. "
           "All decorative emojis are replaced with precise monochrome SVG line iconography.")

    bullet("Strict B2B Authentication Gate", 
           "Direct unauthenticated access to the cockpit is blocked. All users must authenticate via a "
           "zero-hint, secure login screen with role-based session isolation.")

    bullet("Role-Based Tenant Isolation (RBAC)", 
           "The platform enforces strict role boundaries: Super Admin accounts (admin@platform.io) view global "
           "multi-tenant infrastructure health, while Client SRE accounts (sre@acme.com) are strictly sandboxed "
           "to their own organization (e.g., Acme Corp) with zero visibility into other tenants or platform administrative controls.")

    bullet("Zero Privilege Escalation", 
           "Eliminated all 1-click debug shortcuts and client-side role toggles. Engineers cannot escalate their "
           "privileges from inside the cockpit, ensuring complete SOC 2 compliance readiness.")

    doc.save(str(USER_GUIDE_PATH))
    print(f"Updated {USER_GUIDE_PATH} successfully!")

def update_kt_master():
    if not KT_MASTER_PATH.exists():
        print(f"Skipping {KT_MASTER_PATH}, file not found")
        return

    doc = docx.Document(str(KT_MASTER_PATH))

    for p in doc.paragraphs:
        if "Developer Cockpit UI & Multi-Tenant Security Overhaul" in p.text:
            print("KT Master already contains UI section. Skipping duplicate append.")
            return

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run("Developer Cockpit UI & Multi-Tenant Security Overhaul")
    r.font.name, r.font.size, r.font.bold = "Calibri", Pt(16), True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    def body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name, r.font.size = "Calibri", Pt(10.5)
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def bullet(prefix, text):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r1 = p.add_run(f"• {prefix}: ")
        r1.font.name, r1.font.size, r1.font.bold = "Calibri", Pt(10.5), True
        r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r2 = p.add_run(text)
        r2.font.name, r2.font.size = "Calibri", Pt(10.5)
        r2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    body(
        "Prior to initiating Phase P6 (Automated Remediation), the Developer Cockpit frontend (apps/web) "
        "underwent a comprehensive production polish and enterprise security hardening pass."
    )

    bullet("Hydration & Deterministic Rendering", 
           "Eliminated Next.js SSR hydration mismatches by replacing dynamic runtime timestamps with deterministic "
           "UTC ISO strings and explicit hydration suppression on transient time badges.")

    bullet("Enterprise Topology Representation", 
           "Overhauled TopologyView to represent real enterprise microservices (API Gateway, PostgreSQL Cluster, "
           "Redis Broker, AI Worker Brain) with live latency, throughput, and tier metrics, stripping internal developer names.")

    bullet("B2B Multi-Tenant Isolation & Zero Privilege Escalation", 
           "Implemented authenticated session gating separating Super Admin (global scope) from Client Company SREs (Acme Corp). "
           "Removed all client-side role switching buttons and pre-filled credential leaks.")

    doc.save(str(KT_MASTER_PATH))
    print(f"Updated {KT_MASTER_PATH} successfully!")

if __name__ == "__main__":
    update_user_guide()
    update_kt_master()
