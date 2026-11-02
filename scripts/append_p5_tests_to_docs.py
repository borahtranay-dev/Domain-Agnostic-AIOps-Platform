import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path

BASE_DIR = Path(r"e:\domain-agnostic-platform")

p5_files = [
    {
        "path": "tests/test_p5_ai_diagnosis.py",
        "owner": "Rudra (AI / RAG Lead) / Saurav (DevOps)",
        "phase": "Phase P5 (AI Diagnosis & LangChain RAG)",
        "what": "Contains 4 integration tests verifying RAG runbook matching, calibrated confidence scoring, evidence citation integrity, and domain agnosticity.",
        "why": "To guarantee that AI root-cause reasoning is mathematically verified and grounded strictly in real evidence without hallucinations.",
        "analogy": "Think of this file as the Board Certification Examination for the AI Doctor. It tests the AI on real medical cases and makes sure it cites the exact X-ray numbers and never invents symptoms.",
        "technical": "Pytest test suite using FastAPI TestClient and SQLite in-memory database. Tests: (1) Prometheus alert RAG diagnosis, (2) GitHub deployment failure matching RB-006, (3) Generic worker timeout matching RB-007, (4) Domain-agnosticity audit asserting zero e-commerce terms in AI output.",
        "missing": "The AI engine could suffer from silent prompt regressions or hallucinated root causes without automated test detection."
    },
    {
        "path": "scripts/simulate_p5_ai_diagnosis.py",
        "owner": "Saurav (DevOps Lead) / Rudra (AI / RAG Lead)",
        "phase": "Phase P5 (AI Diagnosis & LangChain RAG)",
        "what": "Provides a colored CLI simulation harness demonstrating Phase P5 RAG vector retrieval, confidence scoring, and plan drafting in 2 seconds.",
        "why": "To enable live evaluation and viva demonstrations of the AI intelligence core without relying on slow external APIs.",
        "analogy": "Think of this file as an Ultra-Fast Flight Simulator Drill for the AI copilot. It injects a simulated engine flameout and lets evaluators watch the AI pull up the emergency manual and diagnose the fault live on screen.",
        "technical": "Standalone demonstration script using ANSI colors. Demonstrates: (1) Ingestion of failure signals, (2) TF-IDF vector similarity retrieval against RB-001..RB-007, (3) Calibrated confidence calculation, (4) P2 Diagnosis model creation with cited evidence, (5) Contract invariant validation.",
        "missing": "Evaluators would have to inspect raw database tables manually rather than seeing an intuitive, live terminal demonstration."
    }
]

for doc_name in ["explaination.docx", "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx"]:
    doc_path = BASE_DIR / doc_name
    doc = docx.Document(str(doc_path))
    for item in p5_files:
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>'))
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="36" w:color="0284C7"/>'
            f'<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
            f'</w:tcBorders>'))
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        r_title = p.add_run(f"FILE: {item['path']}\n")
        r_title.bold, r_title.font.name, r_title.font.size = True, "Calibri", Pt(12)
        r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r_meta = p.add_run(f"Lead Owner: {item['owner']}  |  {item['phase']}\n\n")
        r_meta.bold, r_meta.font.name, r_meta.font.size = True, "Calibri", Pt(10)
        r_meta.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

        def add_sub(label, text, color_rgb):
            r_l = p.add_run(f"• {label}: ")
            r_l.bold, r_l.font.name, r_l.font.size = True, "Calibri", Pt(10)
            r_l.font.color.rgb = color_rgb
            r_t = p.add_run(f"{text}\n\n")
            r_t.font.name, r_t.font.size = "Calibri", Pt(10)
            r_t.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

        add_sub("What Does This File Do?", item["what"], RGBColor(0x0F, 0x17, 0x2A))
        add_sub("Why Was It Built?", item["why"], RGBColor(0x0F, 0x17, 0x2A))
        add_sub("Super-Easy Explanation (Layman & Evaluator)", item["analogy"], RGBColor(0x10, 0xB9, 0x81))
        add_sub("Detailed Technical Implementation", item["technical"], RGBColor(0x63, 0x66, 0xF1))
        add_sub("If Missing / What Would Break", item["missing"], RGBColor(0xEF, 0x44, 0x44))

    doc.save(str(doc_path))
    print(f"Updated {doc_name} with P5 test & simulation files successfully!")
