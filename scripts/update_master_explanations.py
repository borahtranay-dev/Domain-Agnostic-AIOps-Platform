"""
Master File-by-File Documentation Generator.
Appends the complete, comprehensive file breakdowns with super-easy layman analogies
and exact team ownership to both explaination.docx and PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx.
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path

BASE_DIR = Path(r"e:\domain-agnostic-platform")
EXPLAIN_PATH = BASE_DIR / "explaination.docx"
KT_MASTER_PATH = BASE_DIR / "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx"

FILES_DATA = [
    # ── TARANAY (BACKEND LEAD) ──
    {
        "path": "apps/api/src/models/remediation.py",
        "owner": "Taranay (Backend Lead)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Defines the PostgreSQL database table schemas for RemediationPlanModel and RemediationActionModel.",
        "why": "To persist drafted and approved remediation actions, their risk levels, and execution timestamps in the database.",
        "analogy": "Think of this file as the Doctor's Written Prescription Sheet. When the specialist doctor decides on the cure (e.g. adjust server memory or restart the cluster), they write down the exact medicine, the dosage, and the steps to take on a carbon-copy prescription pad so nurses and pharmacists can execute it safely.",
        "technical": "SQLAlchemy models extending Base. RemediationPlanModel maps to 'remediation_plans' table with columns: id, incident_id (FK to incidents.id), diagnosis_id, status (default 'drafted'), rationale, risk_level (low/med/high), created_at, executed_at. RemediationActionModel maps to 'remediation_actions' table with columns: id, plan_id (FK), action_type, description, target_service_id, parameters (JSON), and order (int).",
        "missing": "Remediation proposals would only exist in temporary RAM during an API request; no database record of planned or executed fixes would exist."
    },
    {
        "path": "apps/api/src/models/approval.py",
        "owner": "Taranay (Backend Lead)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Defines the database table schema for the Human-in-the-Loop ApprovalModel entity.",
        "why": "To enforce Rule 15 and create an immutable audit trail of who approved or rejected a remediation action and why.",
        "analogy": "Think of this file as the Patient Surgery Consent Form with the Chief Surgeon's Signature. Before any surgical knife touches the patient, the lead doctor must sign their name, write the exact date and minute, and add a signed note saying 'I have reviewed the X-rays and authorize this procedure'.",
        "technical": "ApprovalModel maps to 'approvals' table. Columns: id (primary key), incident_id (FK to incidents.id), plan_id (FK to remediation_plans.id), decision ('approved' or 'rejected'), approver_id (string, e.g. SRE email), decided_at (DateTime with timezone), and notes (Text audit rationale).",
        "missing": "The platform would have zero audit trail of human governance; automated fixes could be triggered without accountability, violating SOC 2 compliance."
    },
    {
        "path": "apps/api/src/models/verification.py",
        "owner": "Taranay (Backend Lead)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Defines the database table schema for the Post-Remediation VerificationModel entity.",
        "why": "To enforce Rule 17 by recording post-fix telemetry metrics, confirming that error rates actually dropped to 0% before resolving an incident.",
        "analogy": "Think of this file as the Post-Surgery Recovery Room Health Monitor. After the surgery is finished, the nurse hooks the patient up to an EKG heart monitor. Only when their pulse stabilizes and body temperature returns to 98.6°F does the head doctor stamp 'Fully Recovered' on their medical chart.",
        "technical": "VerificationModel maps to 'verifications' table. Columns: id (primary key), incident_id (FK), plan_id (FK), status ('passed' or 'failed'), telemetry_summary (Text), verified_at (DateTime), and metrics (JSON payload storing error_rate, p95_latency_ms, replica count).",
        "missing": "Incidents could be marked resolved blindly after running a script, with zero empirical verification of whether the fix actually restored system stability."
    },
    {
        "path": "apps/api/src/routers/remediation.py",
        "owner": "Taranay (Backend Lead) / Saurav (DevOps)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Exposes HTTP REST endpoints for retrieving remediation plans and executing governed human approvals or rejections.",
        "why": "To provide the secure API gateway for the Developer Cockpit to approve fixes, trigger the GitHub execution adapter, and verify recovery.",
        "analogy": "Think of this file as the Hospital Treatment Authorization Desk. When the human SRE clicks 'Approve', this desk stamps the consent form, calls the surgical robot (the GitHub worker) to apply the hotfix, watches the telemetry monitor, and announces 'Patient is Cured' over the loudspeaker.",
        "technical": "FastAPI APIRouter mounted at '/api/v1/incidents'. Implements: GET /{id}/remediation (fetches plan and actions), POST /{id}/remediation/approve (validates human approval, transitions plan to 'approved', calls RemediationOrchestrator, invokes TelemetryVerificationEngine, and marks incident 'resolved'), POST /{id}/remediation/reject (records rejection audit notes), and GET /{id}/verification.",
        "missing": "SREs would have no API to inspect or approve AI-suggested fixes; the Developer Cockpit could not trigger automated remediation or receive verification status."
    },

    # ── RUDRA (AI / RAG LEAD) ──
    {
        "path": "apps/ai-worker/src/diagnosis_service.py",
        "owner": "Rudra (AI / RAG Lead)",
        "phase": "Phase P5 (AI Diagnosis & LangChain RAG)",
        "what": "Orchestrates LangChain RAG prompts, retrieves operational runbooks via vector similarity, calculates calibrated confidence scores, and synthesizes root-cause diagnoses.",
        "why": "To turn raw error logs and Prometheus alerts into evidence-grounded root causes and drafted remediation plans without hallucinations.",
        "analogy": "Think of this file as the Chief Diagnostic Specialist in a major research hospital. When a mysterious fever hits the ICU, this specialist cross-references the patient's lab results with certified medical textbooks, calculates exactly how sure they are (e.g. 94% certain), and drafts a safe treatment plan.",
        "technical": "Implements DiagnosisEngine using LangChain PromptTemplate. Performs vector search against RunbookVectorStore, computes calibrated confidence bounded strictly between 0.65 and 0.98, cites factual supporting evidence IDs, maps recommended actions to ActionType enum, and returns structured P2 Diagnosis and RemediationPlan contract objects.",
        "missing": "The platform would lack artificial intelligence; error alerts would remain raw unanalyzed logs requiring human engineers to manually debug for hours at midnight."
    },
    {
        "path": "apps/ai-worker/src/runbook_store.py",
        "owner": "Rudra (AI / RAG Lead)",
        "phase": "Phase P5 (AI Diagnosis & LangChain RAG)",
        "what": "Maintains an in-memory vector store of certified SRE runbooks (RB-001 to RB-007) and executes sub-5ms cosine similarity retrieval.",
        "why": "To provide zero-cost, instant knowledge retrieval grounded in real infrastructure playbooks without paying for third-party cloud vector databases.",
        "analogy": "Think of this file as an indexed digital encyclopedia of 7 certified engineering repair manuals memorized directly inside the AI's brain. When an error symptom is described, it instantly flips to the exact matching repair procedure in 3 milliseconds.",
        "technical": "Uses scikit-learn TfidfVectorizer with unigram and bigram tokenization. Pre-indexes 7 system runbooks (database pool saturation, pod OOM, circuit breaker trip, worker queue timeout, probe failures). fit() builds the term-document matrix in memory; retrieve(query, top_k) calculates cosine similarity scores via linear_kernel and returns ranked runbooks.",
        "missing": "The AI diagnosis would have no runbooks to ground its reasoning, leading to unreliable LLM hallucinations instead of verified engineering procedures."
    },

    # ── VIVEK (FRONTEND LEAD) ──
    {
        "path": "apps/web/src/components/LoginScreen.tsx",
        "owner": "Vivek (Frontend Lead)",
        "phase": "Phase P7 (Developer Cockpit & B2B Multi-Tenant Security)",
        "what": "Renders an enterprise B2B login screen enforcing Role-Based Access Control (RBAC) and tenant session isolation.",
        "why": "To protect the cockpit from unauthenticated access and ensure client company engineers cannot see platform admin capabilities or other tenants.",
        "analogy": "Think of this file as the Biometric Security Gate at the entrance of a high-security defense facility. Depending on whether you scan a Super Admin badge or an Acme Corp Client badge, you are guided into completely different, soundproofed rooms.",
        "technical": "Client React component with zero pre-filled hints or demo shortcuts. Validates Super Admin (admin@platform.io -> Global Platform scope) and Tenant Client SRE (sre@acme.com -> Acme Corp sandboxed view). Dispatches authenticated session callback to root page.",
        "missing": "Any anonymous visitor on the internet could enter the Developer Cockpit, view proprietary infrastructure health, and trigger remediation commands."
    },
    {
        "path": "apps/web/src/components/AiRootCauseConsole.tsx",
        "owner": "Vivek (Frontend Lead)",
        "phase": "Phase P7 (Developer Cockpit & Remediation UI)",
        "what": "Renders the AI diagnostic root-cause inspection card, confidence metrics, proposed actions, and human approval buttons.",
        "why": "To give on-call SREs complete visibility into AI reasoning and provide the one-click 'Approve & Execute' button that heals the cluster.",
        "analogy": "Think of this file as the High-Tech Surgical Console in the cockpit. It shows the live X-ray scan, points out the exact broken valve, shows the AI's 94% certainty badge, and gives the captain the physical green button to authorize the repair robot.",
        "technical": "React component styled with matte obsidian black (#09090b) and monochrome SVG icons. Displays probable_root_cause, runbook badge, ordered action checklist, and approval/rejection buttons. Dynamically renders clickable GitHub Pull Request link when incident transitions to RESOLVED.",
        "missing": "Engineers would have no visual interface to inspect AI diagnostic findings or authorize remediation plans, breaking the human-in-the-loop workflow."
    },
    {
        "path": "apps/web/src/components/TopologyView.tsx",
        "owner": "Vivek (Frontend Lead)",
        "phase": "Phase P7 (Developer Cockpit UI)",
        "what": "Renders the interactive 6-node cloud microservice topology grid with live latency, throughput, and health tier metrics.",
        "why": "To provide instant visual situational awareness showing whether degraded performance originates in the API Gateway, Auth Engine, Database, or Cache.",
        "analogy": "Think of this file as the Air Traffic Control Radar Screen. At a single glance, the controller sees all 6 airplanes (services) in the sky, their speed, altitude, and whether any engine is running hot (yellow/red alerts).",
        "technical": "Interactive component displaying 6 enterprise cloud nodes: API Gateway, Authentication Engine, Core API, PostgreSQL Primary, Redis Queue Broker, and AI Diagnostic Brain. Tracks live latency (ms), uptime (%), throughput, and degraded status badges.",
        "missing": "SREs would have to manually SSH into 6 different servers and run terminal commands to figure out which microservice is experiencing an outage."
    },

    # ── SAURAV (DEVOPS LEAD) ──
    {
        "path": "apps/worker/src/remediation_adapter.py",
        "owner": "Saurav (DevOps Lead)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Implements the decoupled GitHubRemediationAdapter and RemediationOrchestrator for automated fix execution.",
        "why": "To keep the platform domain-agnostic while providing concrete GitHub Pull Request and Actions workflow automation for approved fixes.",
        "analogy": "Think of this file as the Automated Robotic Surgeon and GitHub Courier. Once the human doctor signs the approval order, this robot creates a clean code branch, writes the configuration patch, and opens an official GitHub Pull Request ready for review.",
        "technical": "Implements BaseRemediationAdapter interface and GitHubRemediationAdapter concrete class. Dispatches actions based on ActionType: PULL_REQUEST generates hotfix branch (remediation/hotfix-...) and PR URL; CONTAINER_RESTART dispatches GitHub Actions workflow; CONFIG_UPDATE applies parameters. Enforces Rule 15: raises ValueError if plan is not in APPROVED status.",
        "missing": "Approved remediation plans would sit as dead text in the database with no bridge to external Git infrastructure or deployment pipelines."
    },
    {
        "path": "apps/worker/src/verification_engine.py",
        "owner": "Saurav (DevOps Lead)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Implements the TelemetryVerificationEngine that verifies post-remediation health metrics.",
        "why": "To enforce Rule 17: guaranteeing that error rates dropped to 0.00% and latency normalized before resolving an incident ticket.",
        "analogy": "Think of this file as the Official Building Safety Inspector. After the construction crew fixes the leaking gas pipe, this inspector uses electronic gas sniffers to verify that gas levels are literally 0.00% before allowing people back into the building.",
        "technical": "Evaluates telemetry snapshots against configurable thresholds (error_rate_threshold=0.01, target_latency_ms=200). Generates Verification contract model with VerificationStatus.PASSED or FAILED and detailed telemetry summary string.",
        "missing": "The platform would suffer from 'remediation blind optimism'—assuming every executed script worked without ever checking telemetry."
    },
    {
        "path": "tests/test_p6_remediation.py",
        "owner": "Saurav (DevOps Lead)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Contains 5 automated integration tests verifying the complete human approval, execution, and verification lifecycle.",
        "why": "To provide empirical proof that Rule 15 (Human Approval) and Rule 17 (Verification) are strictly enforced by the code.",
        "analogy": "Think of this file as the Official Government Audit Inspection. It runs 5 surprise security drills: tests what happens if someone tries to run a fix without approval (BLOCKED), tests what happens if the SRE approves (PR CREATED & VERIFIED), and tests what happens if a fix is rejected.",
        "technical": "Pytest integration suite utilizing FastAPI TestClient and SQLite in-memory database. Tests: (1) 404 for missing plans, (2) End-to-end approval, GitHub PR creation, and verification, (3) Rejection workflow, (4) 409 Conflict on double execution, (5) Static code audit asserting zero forbidden e-commerce terms.",
        "missing": "Regressions in the approval or execution engine could slip into production, risking unauthorized or unverified automated changes."
    },
    {
        "path": "scripts/simulate_p6_remediation.py",
        "owner": "Saurav (DevOps Lead)",
        "phase": "Phase P6 (Remediation & GitHub Automation)",
        "what": "Provides an interactive, colored CLI demonstration tool that showcases the complete Phase P6 golden path in 1.7 seconds.",
        "why": "To allow evaluators, teachers, and clients to see live AI diagnosis, human approval, GitHub PR creation, and verification without waiting hours for real production failures.",
        "analogy": "Think of this file as an Ultra-High-Speed Flight Simulator Demonstration. Instead of waiting for a real thunderstorm in the middle of the night, this simulator demonstrates how the autopilot and captain handle an engine failure in 2 seconds right in front of the evaluators.",
        "technical": "Self-contained demonstration harness using ANSI terminal colors and cp1252-safe ASCII formatting. Demonstrates: (1) Inspecting AI-drafted plan, (2) Rule 15 execution block, (3) Human approval recording, (4) GitHub PR generation, (5) Rule 17 verification audit, (6) Resolution lifecycle transition.",
        "missing": "Demonstrating the platform to college evaluators would require setting up live external GitHub tokens and simulated multi-hour cluster failures."
    }
]

def append_to_explaination():
    if not EXPLAIN_PATH.exists():
        print(f"Skipping {EXPLAIN_PATH}, file not found")
        return

    doc = docx.Document(str(EXPLAIN_PATH))

    # Check if section already added
    for p in doc.paragraphs:
        if "DETAILED FILE-BY-FILE COMPREHENSIVE GUIDE (PHASE P5, P6 & P7)" in p.text:
            print("File breakdown already in explaination.docx. Skipping duplicate append.")
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

    def file_block(item):
        doc.add_paragraph()
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

    doc.add_page_break()
    h1("DETAILED FILE-BY-FILE COMPREHENSIVE GUIDE (PHASE P5, P6 & P7)")
    p_intro = doc.add_paragraph(
        "Below is the complete file-by-file breakdown for every component built or enhanced during "
        "Phase P5 (AI Diagnosis), Phase P6 (Remediation & GitHub Automation), and Phase P7 (Developer Cockpit). "
        "Each file explicitly specifies who built it, why it was built, a super-easy real-world analogy, "
        "the technical implementation, and what would break if missing."
    )
    p_intro.paragraph_format.line_spacing = 1.15

    for item in FILES_DATA:
        file_block(item)

    doc.save(str(EXPLAIN_PATH))
    print(f"Updated {EXPLAIN_PATH} with comprehensive file blocks successfully!")


def append_to_kt_master():
    if not KT_MASTER_PATH.exists():
        print(f"Skipping {KT_MASTER_PATH}, file not found")
        return

    doc = docx.Document(str(KT_MASTER_PATH))

    for p in doc.paragraphs:
        if "DETAILED FILE-BY-FILE ARCHITECTURAL SPECIFICATION (PHASE P5, P6 & P7)" in p.text:
            print("File breakdown already in KT Master. Skipping duplicate append.")
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

    def file_block(item):
        doc.add_paragraph()
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
        add_sub("Detailed Technical Implementation", item["technical"], RGBColor(0x63, 0x66, 0xF1))
        add_sub("Impact / If Missing", item["missing"], RGBColor(0xEF, 0x44, 0x44))

    doc.add_page_break()
    h1("DETAILED FILE-BY-FILE ARCHITECTURAL SPECIFICATION (PHASE P5, P6 & P7)")
    p_intro = doc.add_paragraph(
        "Below is the complete engineering reference specifying the exact responsibility, owner, purpose, "
        "and technical implementation for each file built during Phase P5, P6, and P7."
    )
    p_intro.paragraph_format.line_spacing = 1.15

    for item in FILES_DATA:
        file_block(item)

    doc.save(str(KT_MASTER_PATH))
    print(f"Updated {KT_MASTER_PATH} with comprehensive file blocks successfully!")


if __name__ == "__main__":
    append_to_explaination()
    append_to_kt_master()
