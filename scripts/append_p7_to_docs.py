"""
Script to append Phase P7 (Developer Cockpit Full Workflow & Live Remediation API Wiring)
to PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx and explaination.docx.
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from pathlib import Path

BASE_DIR = Path(r"e:\domain-agnostic-platform")
KT_MASTER_PATH = BASE_DIR / "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx"
EXPLAIN_PATH = BASE_DIR / "explaination.docx"

def append_p7_to_kt_master():
    if not KT_MASTER_PATH.exists():
        print(f"Skipping {KT_MASTER_PATH}, not found")
        return

    doc = docx.Document(str(KT_MASTER_PATH))

    # Check if already added
    for p in doc.paragraphs:
        if "PHASE P7: DEVELOPER COCKPIT FULL WORKFLOW" in p.text:
            print("P7 section already in KT Master. Skipping duplicate append.")
            return

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(16), True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(13), True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return p

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

    h1("PHASE P7: DEVELOPER COCKPIT FULL WORKFLOW & LIVE REMEDIATION WIRING (COMPLETE)")
    body(
        "Phase P7 delivers the unified frontend interface for on-call SREs and Platform Engineers. "
        "It wires the Developer Cockpit (apps/web) directly to the FastAPI backend (apps/api) and "
        "the GitHub remediation engine (apps/worker). It renders the end-to-end incident lifecycle "
        "from detection through evidence collection, diagnosis, approval, execution, and verification."
    )

    h2("Key Capabilities Implemented in Phase P7")
    bullet("Live Approval REST API Dispatch",
           "Clicking 'Approve & Execute Remediation' in the AI Console directly dispatches an authenticated HTTP POST "
           "to /api/v1/incidents/{id}/remediation/approve with the active SRE identity and audit timestamp.")

    bullet("Direct GitHub Pull Request Rendering",
           "Upon verified remediation, the cockpit dynamically extracts the generated GitHub Pull Request URL "
           "(e.g., https://github.com/acme-corp/core-infrastructure/pull/632) and renders a clickable badge directly on screen.")

    bullet("Graceful Offline Fault Tolerance",
           "The cockpit implements network failure resilience: if the backend API container is restarting or offline during "
           "a college presentation, the UI automatically falls back to deterministic local state simulation, preventing "
           "any UI freezes, blank screens, or uncaught promise rejections.")

    bullet("Verified End-to-End Progression",
           "Engineers can visually inspect the entire pipeline: Incident -> Evidence -> Diagnosis -> Remediation Proposal -> "
           "Approval -> Execution -> Verification.")

    doc.save(str(KT_MASTER_PATH))
    print(f"Updated {KT_MASTER_PATH} successfully!")


def append_p7_to_explaination():
    if not EXPLAIN_PATH.exists():
        print(f"Skipping {EXPLAIN_PATH}, not found")
        return

    doc = docx.Document(str(EXPLAIN_PATH))

    for p in doc.paragraphs:
        if "PHASE P7: DEVELOPER COCKPIT" in p.text:
            print("P7 section already in explaination.docx. Skipping duplicate append.")
            return

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(16), True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(13), True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return p

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

    h1("PHASE P7: DEVELOPER COCKPIT — ARCHITECTURAL SPECIFICATION & VIVA DEFENSE")
    body(
        "Phase P7 bridges the human operator to the automated platform. It implements the Next.js 14 Developer Cockpit "
        "allowing SREs to triage incidents in real time, review AI-synthesized root-cause evidence, and authorize automated fixes."
    )

    h2("Viva Defense Questions for Phase P7")
    bullet("Q: Who is the primary user of Phase P7?",
           "Answer: Vivek (Frontend Lead) designed the Developer Cockpit specifically for on-call SREs and DevOps leads. "
           "It provides immediate situational awareness during live cloud incidents.")

    bullet("Q: How does the Cockpit enforce Human-in-the-Loop Governance?",
           "Answer: When an incident is diagnosed, the UI transitions to 'awaiting_approval'. The automated fix cannot execute "
           "until the SRE clicks 'Approve & Execute Remediation'. The click dispatches an authenticated POST to /remediation/approve, "
           "capturing the SRE's email and audit notes.")

    bullet("Q: What happens when the remediation completes?",
           "Answer: The Cockpit receives the execution payload containing the GitHub Pull Request URL. The UI displays the verified "
           "recovery status, updates the incident to 'RESOLVED', and embeds the clickable GitHub hotfix PR link directly on the dashboard.")

    doc.save(str(EXPLAIN_PATH))
    print(f"Updated {EXPLAIN_PATH} successfully!")


if __name__ == "__main__":
    append_p7_to_kt_master()
    append_p7_to_explaination()
