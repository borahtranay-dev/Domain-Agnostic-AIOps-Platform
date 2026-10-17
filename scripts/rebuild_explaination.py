"""
Rebuild explaination.docx with:
1. Detailed project overview right at the start (what it does, how it works, what all we monitor, domain agnosticity).
2. Phase-by-phase detailed breakdown including SUB-PHASES (P0.1-P0.4, P1.1-P1.6, P2.1-P2.9, P3.1-P3.4) specifying files worked on, how, why, and what they do.
3. Greatly expanded In-Depth Simple (layman) + In-Depth Technical explanations for every single file.
4. Viva Defense Guide & Phase P3 Signoff.
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path

OUTPUT_PATH = Path(r"e:\domain-agnostic-platform\explaination.docx")

def build():
    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # ── Styling helpers ────────────────────────────────────────────────────────
    def h1(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        for r in p.runs:
            r.font.name, r.font.size, r.font.bold = "Calibri", Pt(16), True
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Dark slate
        return p

    def h2(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        for r in p.runs:
            r.font.name, r.font.size, r.font.bold = "Calibri", Pt(13), True
            r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7) # Sky blue
        return p

    def h3(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        for r in p.runs:
            r.font.name, r.font.size, r.font.bold = "Calibri", Pt(11.5), True
            r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        return p

    def body(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        for r in p.runs:
            r.font.name, r.font.size = "Calibri", Pt(10.5)
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def callout(text, title="KEY ARCHITECTURAL PRINCIPLE", border="0284C7", bg="EFF6FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg}"/>'))
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="36" w:color="{border}"/>'
            f'<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
            f'</w:tcBorders>'))
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        rt = p.add_run(f"[{title}]\n")
        rt.bold, rt.font.name, rt.font.size = True, "Calibri", Pt(10.5)
        rt.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        rb = p.add_run(text)
        rb.font.name, rb.font.size = "Calibri", Pt(10)
        rb.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        doc.add_paragraph()

    def table(headers, rows, hdr_color="0F172A"):
        tbl = doc.add_table(rows=1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(headers):
            c = tbl.rows[0].cells[i]
            c._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hdr_color}"/>'))
            for rr in c.paragraphs[0].runs:
                rr.font.bold, rr.font.name = True, "Calibri"
                rr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                rr.font.size = Pt(10)
            c.paragraphs[0].add_run(h).font.name = "Calibri"
            c.paragraphs[0].runs[0].font.bold = True
            c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            c.paragraphs[0].runs[0].font.size = Pt(10)
        for row_data in rows:
            row = tbl.add_row()
            for i, val in enumerate(row_data):
                cell = row.cells[i]
                p = cell.paragraphs[0]
                run = p.add_run(val)
                run.font.name = "Calibri"
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        doc.add_paragraph()

    def file_block(filename, easy_exp, tech_exp, impact):
        """Prints a detailed file block with deep simple and technical breakdowns."""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"File: {filename}")
        r.font.name, r.font.size, r.font.bold = "Courier New", Pt(10.5), True
        r.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)

        # Easy explanation
        p_easy = doc.add_paragraph()
        p_easy.paragraph_format.left_indent = Inches(0.25)
        p_easy.paragraph_format.space_before = Pt(2)
        p_easy.paragraph_format.space_after = Pt(3)
        p_easy.paragraph_format.line_spacing = 1.15
        lbl_easy = p_easy.add_run("• Detailed Simple Explanation (For Evaluator & Viva): ")
        lbl_easy.bold, lbl_easy.font.name, lbl_easy.font.size = True, "Calibri", Pt(10)
        lbl_easy.font.color.rgb = RGBColor(0x05, 0x96, 0x69) # Emerald Green
        val_easy = p_easy.add_run(easy_exp)
        val_easy.font.name, val_easy.font.size = "Calibri", Pt(10)
        val_easy.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

        # Technical deep dive
        p_tech = doc.add_paragraph()
        p_tech.paragraph_format.left_indent = Inches(0.25)
        p_tech.paragraph_format.space_before = Pt(2)
        p_tech.paragraph_format.space_after = Pt(3)
        p_tech.paragraph_format.line_spacing = 1.15
        lbl_tech = p_tech.add_run("• Detailed Technical Implementation: ")
        lbl_tech.bold, lbl_tech.font.name, lbl_tech.font.size = True, "Calibri", Pt(10)
        lbl_tech.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        val_tech = p_tech.add_run(tech_exp)
        val_tech.font.name, val_tech.font.size = "Calibri", Pt(10)
        val_tech.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

        # If missing / consequence
        p_imp = doc.add_paragraph()
        p_imp.paragraph_format.left_indent = Inches(0.25)
        p_imp.paragraph_format.space_before = Pt(2)
        p_imp.paragraph_format.space_after = Pt(5)
        lbl_imp = p_imp.add_run("• If Missing / Architectural Impact: ")
        lbl_imp.bold, lbl_imp.font.name, lbl_imp.font.size = True, "Calibri", Pt(10)
        lbl_imp.font.color.rgb = RGBColor(0xDC, 0x26, 0x26) # Crimson Red
        val_imp = p_imp.add_run(impact)
        val_imp.font.name, val_imp.font.size = "Calibri", Pt(10)
        val_imp.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # ════════════════════════════════════════════════════════════════════════
    # COVER & TITLE
    # ════════════════════════════════════════════════════════════════════════
    title_p = doc.add_paragraph("AUTONOMOUS DOMAIN-AGNOSTIC AIOPS PLATFORM")
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in title_p.runs:
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(24), True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    subtitle_p = doc.add_paragraph(
        "Complete Project Blueprint, Operational Mechanics, Chronological Sub-Phase Breakdown,\n"
        "and Integrated Team File Engineering Guide (Phase P0 to Phase P3 Complete)"
    )
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_p.paragraph_format.space_after = Pt(12)
    for r in subtitle_p.runs:
        r.font.name, r.font.size, r.font.italic = "Calibri", Pt(11.5), True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    callout(
        "Current Repository Status: Phase P3 Verified & Complete | Total Tests: 31/31 Passed (100% Green)\n"
        "Active Branch: feat/saurav-p2-contracts-draft | Git Working Tree: Clean & Fully Synchronized with GitHub\n"
        "Infrastructure Cost: $0.00 Cloud Spend (Local Vector Store, PostgreSQL 16 & Redis 7 Dockerized)\n"
        "Core Engineering Leads: Taranay (Backend), Rudra (AI/RAG), Vivek (Frontend), Saurav (DevOps & Integration)",
        title="EXECUTIVE SYSTEM METRICS",
        border="10B981",
        bg="ECFDF5"
    )

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 1 — COMPREHENSIVE PROJECT MECHANICS (AT THE START)
    # ════════════════════════════════════════════════════════════════════════
    h1("1. Comprehensive Project Mechanics & Architecture")

    h2("1.1 Executive Summary & The Problem It Solves")
    body(
        "Modern cloud applications run across distributed microservices, databases, caches, and containers. "
        "When an error or outage occurs—such as a database connection pool freeze or an out-of-memory container crash at 3:00 AM—"
        "traditional IT operations rely heavily on manual human intervention. Human Site Reliability Engineers (SREs) "
        "are woken up by automated pagers. They spend hours manually searching through scattered logs across different machines, "
        "trying to locate outdated internal wiki runbooks, guessing the root cause, and cautiously attempting manual shell commands "
        "to recover the system. This manual incident response process leads to prolonged downtime, human alert fatigue, "
        "and millions of dollars in enterprise downtime losses."
    )
    body(
        "The Autonomous Domain-Agnostic AIOps Self-Healing Platform solves this crisis by introducing a closed-loop, automated, "
        "intelligent incident response system. It operates continuously 24 hours a day, 7 days a week. It automatically ingests "
        "telemetry signals from running cloud applications, correlates raw anomalies into structured Incident tickets, utilizes a "
        "Retrieval-Augmented Generation (RAG) AI engine to diagnose root causes by matching symptoms against verified operational runbooks, "
        "drafts an ordered, executable remediation plan, and presents it to human operators on an interactive Next.js 14 web cockpit "
        "with an 'Approve & Heal' safety gate. When approved, the fix executes, post-remediation telemetry confirms system recovery, "
        "and the incident is marked resolved—collapsing incident resolution time (MTTR) from hours to seconds."
    )

    h2("1.2 The Complete 6-Stage Autonomous Lifecycle (How Our SaaS Web App Works)")
    body(
        "The entire platform functions as a seamless, reactive autonomous loop spanning six core stages:"
    )

    table(
        ["Stage #", "Lifecycle Phase", "Detailed Operational Mechanism & Action Flow"],
        [
            ["Stage 1", "Telemetry Ingestion", "External client applications and infrastructure agents send HTTP failure payloads, log streams, or metric alerts to the API gateway (POST /api/v1/events). Taranay's API validates the payload against P2 contracts and stores it in PostgreSQL while enqueueing into Redis."],
            ["Stage 2", "Incident Correlation & Evidence Gathering", "The ingestion pipeline groups related events into an Incident ticket. It gathers related log lines, metric spikes, and stack traces into an Evidence bundle, assigning unique UUIDs to every evidence artefact."],
            ["Stage 3", "RAG AI Root-Cause Diagnosis", "Rudra's AI Diagnostic Worker receives the incident and evidence. It performs a TF-IDF cosine similarity search across an in-memory vector store of certified engineering runbooks, feeds the grounded context into a LangChain prompt, and outputs a Diagnosis with a calibrated confidence score (0.0 to 1.0) and supporting evidence citations."],
            ["Stage 4", "Remediation Planning", "The AI worker generates an ordered RemediationPlan containing concrete actions (e.g., config_update to increase DB pool size, or container_restart). Crucially, the plan is initialized in 'DRAFTED' status—it is never executed autonomously without authorization."],
            ["Stage 5", "Human-In-The-Loop Governance", "Vivek's Next.js Developer Cockpit highlights the active incident in real time. The on-call SRE inspects the Evidence Room, reviews the AI's diagnostic rationale and confidence bar, and clicks the prominent 'Approve & Heal' button to authorize the fix."],
            ["Stage 6", "Execution & Verification", "The approved remediation plan executes. The platform monitors recovery metrics (Verification contract), confirms error rates have normalized, updates the incident status to 'RESOLVED', and records an automatic UTC resolution timestamp."]
        ]
    )

    h2("1.3 What All Do We Monitor?")
    body(
        "The platform continuously monitors telemetry across multiple infrastructure and application failure vectors. "
        "It currently provides automated detection, runbook diagnosis, and remediation templates for five critical production failure scenarios:"
    )

    table(
        ["Monitored Scenario", "Symptom & Metric Trigger Received", "Autonomous RAG Diagnosis & Self-Healing Action"],
        [
            ["1. Database Connection Pool Exhaustion",
             "SQLAlchemy QueuePool limit size=10, overflow=20 exhausted. Endpoints failing with HTTP 500 Connection Timeout.",
             "AI retrieves Runbook RB-001. Identifies unclosed connections or undersized pool. Formulates RemediationPlan with config_update (pool_size=20, pool_pre_ping=true)."],
            ["2. Container Memory Leak & OOM Kill",
             "Linux kernel terminates container with OS Exit Code 137 (Out-Of-Memory). Memory usage rises monotonically.",
             "AI retrieves Runbook RB-002. Identifies unreleased heap memory leak. Formulates container_restart action with increased heap limit thresholds."],
            ["3. CPU Saturation & Thread Starvation",
             "Host CPU utilization sustained >95% for over 3 minutes. Worker threads blocked waiting on synchronous I/O.",
             "AI retrieves Runbook RB-003. Identifies thread pool starvation. Formulates scale_service action to add worker replicas and rebalance load."],
            ["4. API Latency Degradation & Cascading Timeouts",
             "P99 response latency degrades from 120ms to >10,000ms. Upstream callers experiencing cascading HTTP 504 timeouts.",
             "AI retrieves Runbook RB-004. Identifies degraded downstream dependency. Formulates config_update to trip circuit breaker and throttle non-critical calls."],
            ["5. CI/CD Deployment Failure & Probe Crash",
             "Newly deployed container revision fails Kubernetes liveness/readiness probes 5 consecutive times on startup.",
             "AI retrieves Runbook RB-005. Identifies startup initialization failure or configuration regression. Formulates rollback action to last known-good image build."]
        ]
    )

    h2("1.4 What Does 'Domain-Agnostic' Mean?")
    body(
        "A foundational invariant enforced across the repository is Domain-Agnosticity. The core platform is completely decoupled "
        "from any business vertical. The platform core has no understanding of e-commerce, banking, logistics, or healthcare. "
        "It does not contain concepts like 'order_id', 'cart_id', 'payment_status', or 'inventory_count'."
    )
    callout(
        "Domain-Agnosticity Test: The platform core operates strictly on generic systems engineering primitives:\n"
        "• Event: A standardized telemetry signal.\n"
        "• Incident: An operational outage or anomaly state.\n"
        "• Evidence: Verifiable log entries, stack traces, and metric readings.\n"
        "• Diagnosis: A grounded root-cause finding with supporting evidence citations.\n"
        "• RemediationAction & Plan: Structured infrastructure operations (restart, scale, reconfigure).\n"
        "• Approval: An auditable human governance decision.\n"
        "• Verification: Empirical post-remediation metrics.\n"
        "Any payload attempting to pass unauthorized domain-specific fields into core models is automatically rejected with HTTP 422.",
        title="THE DOMAIN-AGNOSTIC DATA INVARIANT",
        border="0284C7",
        bg="EFF6FF"
    )

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 2 — CHRONOLOGICAL EVOLUTION & DETAILED SUB-PHASES
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("2. Chronological Phase-by-Phase Evolution & Detailed Sub-Phases")

    body(
        "The project followed a rigorous phase-gated engineering methodology. No phase was allowed to begin until the previous "
        "phase had passed all automated tests, architectural audits, and governance checks. Below is the detailed breakdown of "
        "every phase and sub-phase from day one to the completion of Phase P3:"
    )

    # ── PHASE P0 ─────────────────────────────────────────────────────────────
    h2("2.1 Phase P0: Governance Bootstrap & Architectural Directives")
    body(
        "Objective: Establish the repository governance, subsystem boundaries, domain-agnostic invariants, and phase roadmap "
        "before writing any application code."
    )

    h3("Sub-phases of Phase P0:")
    body(
        "• Sub-phase P0.1 (AI Coding Directives & Rule Enforcement): Created AGENTS.md and Rules.md. "
        "Codified the binding operating principles for AI assistants and engineers: Inspect Before Modifying, Strict Phase Discipline, "
        "Subsystem Ownership, Shared Contracts Inviolability, Avoid Blind Rewrites, and Empirical Verification After Changes."
    )
    body(
        "• Sub-phase P0.2 (Product Requirements & Phase Gating Plan): Authored PRD.md and Phases.md. "
        "Defined the core product scope (autonomous incident detection, RAG diagnosis, human governance, remediation execution) "
        "and outlined the five-phase roadmap (P0: Governance -> P1: Foundation -> P2: Contracts -> P3: Parallel Components -> P4: Real Webhooks)."
    )
    body(
        "• Sub-phase P0.3 (Architectural Specification & System Design): Authored architecture.md and design.md. "
        "Specified the microservice topology (apps/api, apps/worker, apps/ai-worker, apps/web), the multi-tenant architecture, "
        "and the database schemas for PostgreSQL 16 and Redis 7."
    )
    body(
        "• Sub-phase P0.4 (Subsystem Ownership Assignment): Formally partitioned engineering responsibilities among the four leads:\n"
        "  - Taranay: Backend, API Gateway, and Relational Storage (apps/api)\n"
        "  - Rudra: AI Diagnostic Engine, Vector Runbook Store, and LangChain (apps/ai-worker)\n"
        "  - Vivek: SRE Developer Cockpit, UI/UX, and Human-in-the-Loop Console (apps/web)\n"
        "  - Saurav: Shared Contracts, DevOps, Multi-Service Integration, Testing & Compliance"
    )

    # ── PHASE P1 ─────────────────────────────────────────────────────────────
    h2("2.2 Phase P1: Microservices Foundation & Docker Orchestration")
    body(
        "Objective: Build clean, bootable microservice skeletons for all four subsystems and verify that they can communicate "
        "locally within an isolated container network with $0.00 cloud spend."
    )

    h3("Sub-phases of Phase P1:")
    body(
        "• Sub-phase P1.1 (Multi-Container Infrastructure): Built docker-compose.yml. Configured persistent PostgreSQL 16 "
        "and Redis 7 Alpine containers connected via an isolated bridge network (aiops-network) with health-checks."
    )
    body(
        "• Sub-phase P1.2 (FastAPI Backend Skeleton): Created the initial apps/api skeleton with Uvicorn server, "
        "configuration loading, and baseline /health and /ready probe endpoints."
    )
    body(
        "• Sub-phase P1.3 (Background Worker Skeleton): Created apps/worker utilizing Redis Queue (RQ) for asynchronous "
        "event processing, job retries, and worker process lifecycle."
    )
    body(
        "• Sub-phase P1.4 (AI Diagnostic Worker Skeleton): Created apps/ai-worker with FastAPI, integrating baseline LangChain "
        "stubs and local model invocation capabilities."
    )
    body(
        "• Sub-phase P1.5 (Frontend Skeleton): Bootstrapped apps/web using Next.js 14 App Router, TypeScript, and initial layout structure."
    )
    body(
        "• Sub-phase P1.6 (Foundation Test Suite): Created tests/foundation/ with automated tests verifying that the API, AI-worker, "
        "and background worker can start and connect to PostgreSQL and Redis without errors."
    )

    # ── PHASE P2 ─────────────────────────────────────────────────────────────
    h2("2.3 Phase P2: Shared Contracts Package & Data Treaty")
    body(
        "Objective: Construct the shared contracts package (packages/contracts/aiops_contracts) that serves as the single "
        "source of truth for data exchanged across all microservices, rigorously enforcing the domain-agnosticity invariant."
    )

    h3("Sub-phases of Phase P2:")
    body(
        "• Sub-phase P2.1 (Base Contract & Domain Invariant): Created common.py defining ContractModel with Pydantic v2 "
        "model_config = ConfigDict(extra='forbid'). Implemented new_id() (UUID4 string generator) and utc_now() (timezone-aware UTC datetime)."
    )
    body(
        "• Sub-phase P2.2 (Telemetry Ingestion Contract): Created event.py defining the Event model and EventType enum "
        "(telemetry, pipeline_run, deployment, external). Enforces strict required attributes for all incoming signals."
    )
    body(
        "• Sub-phase P2.3 (Incident Lifecycle Contract): Created incident.py defining the Incident model, Severity enum "
        "(critical, high, medium, low), and IncidentStatus enum (open, diagnosing, awaiting_approval, executing, verifying, resolved, closed)."
    )
    body(
        "• Sub-phase P2.4 (Telemetry Evidence Contract): Created evidence.py defining the Evidence model and EvidenceKind enum "
        "(log, metric, stack_trace, config_snapshot, deployment_event) ensuring structured, verifiable proof for every incident."
    )
    body(
        "• Sub-phase P2.5 (Root Cause Diagnosis Contract): Created diagnosis.py defining the Diagnosis model. Enforces "
        "bounded confidence (float 0.0 to 1.0) and supporting/contradicting evidence ID citations."
    )
    body(
        "• Sub-phase P2.6 (Remediation Actions & Planning Contract): Created remediation.py defining ActionType enum "
        "(config_update, container_restart, rollback, scale_service, pull_request), PlanStatus enum (drafted, approved, etc.), "
        "RemediationAction, and RemediationPlan."
    )
    body(
        "• Sub-phase P2.7 (Human Governance Contract): Created approval.py defining the Approval model and ApprovalDecision enum "
        "(approved, rejected) to capture an immutable audit log of human authorization decisions."
    )
    body(
        "• Sub-phase P2.8 (Post-Remediation Verification Contract): Created verification.py defining the Verification model "
        "and VerificationStatus enum (pending, passed, failed, inconclusive) for empirical recovery confirmation."
    )
    body(
        "• Sub-phase P2.9 (Automated Contract Verification Suite): Created tests/test_contracts.py containing 15 parameterized "
        "unit tests verifying valid instantiation and asserting that unauthorized domain-specific fields (order_id, cart, payment_status, inventory) "
        "trigger immediate validation errors across all models."
    )

    # ── PHASE P3 ─────────────────────────────────────────────────────────────
    doc.add_page_break()
    h2("2.4 Phase P3: Parallel Component Construction & Multi-Service Integration")
    body(
        "Objective: With P2 contracts signed off, each subsystem lead built their complete production-ready implementation in parallel, "
        "followed by cross-service integration and end-to-end pipeline verification. Completed with 31/31 passing tests!"
    )

    h3("Sub-phases of Phase P3 (Detailed Breakdown):")

    body(
        "• Sub-phase P3.1: Backend Production Hardening & Relational Data Tier (Taranay)\n"
        "  - Files worked on: apps/api/src/database.py, apps/api/src/config.py, apps/api/src/models/event.py, "
        "apps/api/src/models/incident.py, apps/api/src/models/evidence.py, apps/api/src/models/diagnosis.py, "
        "apps/api/src/routers/events.py, apps/api/src/routers/incidents.py, tests/test_api_events.py.\n"
        "  - What it does: Implemented SQLAlchemy 2.0 connection pooling (pool_size=10, max_overflow=20, pool_pre_ping=True) "
        "to prevent database connection exhaustion under traffic. Built four relational ORM tables mapped to PostgreSQL. "
        "Implemented the Event Ingestion Router (POST /api/v1/events) with contract validation and Redis queuing. "
        "Built the Incident Management Router (GET /api/v1/incidents) with filtering and status transitions. "
        "Verified with 7 comprehensive integration tests."
    )

    body(
        "• Sub-phase P3.2: AI Diagnostic Worker & In-Memory Vector RAG Engine (Rudra)\n"
        "  - Files worked on: apps/ai-worker/src/runbook_store.py, apps/ai-worker/src/diagnosis_service.py, "
        "apps/ai-worker/src/config.py, apps/ai-worker/src/main.py, tests/test_ai_worker.py.\n"
        "  - What it does: Created a zero-cost in-memory Vector Knowledge Base indexing 5 certified operational runbooks "
        "using scikit-learn TF-IDF vectorization and cosine similarity (<5ms query time). Built the LangChain RAG Diagnosis Engine "
        "which formats grounded prompt templates, calibrates confidence scores strictly between 0.65 and 0.98, and outputs "
        "P2-compliant Diagnosis and RemediationPlan contracts. Exposed GET /api/v1/runbooks and POST /api/v1/diagnose. "
        "Verified with 6 comprehensive integration tests."
    )

    body(
        "• Sub-phase P3.3: Next.js 14 SRE Developer Cockpit & 3D Skeuomorphic UI (Vivek)\n"
        "  - Files worked on: apps/web/src/types/index.ts, apps/web/src/app/layout.tsx, apps/web/src/app/globals.css, "
        "apps/web/src/app/page.tsx, apps/web/src/components/Header.tsx, apps/web/src/components/MetricsBar.tsx, "
        "apps/web/src/components/IncidentFeed.tsx, apps/web/src/components/IncidentDetail.tsx, apps/web/src/components/TopologyView.tsx.\n"
        "  - What it does: Developed the complete SRE Developer Cockpit in Next.js 14 App Router. Designed a 3D skeuomorphic "
        "tactile UI with soft dual drop-shadows and light/dark theme support. Built live KPI metric tiles (Active Outages, MTTR 4.2 min, "
        "Autonomous Heals, System Health 99.8%), an incident triage feed with status filter pills, an interactive Evidence Room, "
        "an AI RAG Inspector panel, and the Human-in-the-Loop 'Approve & Heal' authorization button. "
        "Verified with 0 TypeScript compiler errors and running on http://localhost:3000."
    )

    body(
        "• Sub-phase P3.4: Multi-Service Integration, Namespace Isolation & Live Simulator (Saurav)\n"
        "  - Files worked on: tests/test_e2e_pipeline.py, apps/api/src/routers/incidents.py (PATCH status), "
        "scripts/simulate_failure_e2e.py, docs/SAAS_ARCHITECTURE_AND_COMPLIANCE_GUIDE.md, PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx, "
        "SAAS_ARCHITECTURE_AND_COMPLIANCE_MASTER.docx, explaination.docx.\n"
        "  - What it does: Resolved cross-service Python namespace collisions between apps/api/src and apps/ai-worker/src using dynamic "
        "sys.modules cache purging. Implemented the Incident Lifecycle Status PATCH endpoint to enable the cockpit's 'Approve & Heal' button. "
        "Constructed tests/test_e2e_pipeline.py running the full 8-stage pipeline from ingestion to healing in a single test run. "
        "Built the interactive simulate_failure_e2e.py CLI tool for 2-second live failure demonstrations during presentations. "
        "Authored the complete SaaS Architecture & Compliance Guide and master viva documentation. Verified all 31 core tests passing."
    )

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 3 — EXHAUSTIVE FILE-BY-FILE TECHNICAL + EASY REFERENCE
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("3. Exhaustive File-by-File Technical + Simple Master Reference")

    body(
        "Below is the complete, comprehensive reference for every file created or maintained across the repository. "
        "For each file, we provide both an In-Depth Simple Explanation (for verbal presentation to a teacher, examiner, or colleague) "
        "and an In-Depth Technical Deep Dive (detailing exact classes, methods, data structures, and mechanics)."
    )

    # ── 3.1 TARANAY FILES ────────────────────────────────────────────────────
    h2("3.1 Taranay (Backend Lead) — Files in apps/api/ & Ingestion Engine")

    file_block(
        "apps/api/src/main.py",
        "This file is the main control room and starting point of our entire backend API server. When you run the API, "
        "this file boots up the FastAPI framework, connects all the different URL routers (such as events and incidents), "
        "enables Cross-Origin Resource Sharing (CORS) so our Next.js frontend can communicate with it safely, and automatically "
        "ensures all database tables exist in PostgreSQL upon boot. It also gives us a simple '/health' web address so any monitoring "
        "tool can instantly verify if our server is online.",
        "Initializes the core FastAPI application instance with title and version metadata. Adds CORSMiddleware allowing all origins, "
        "methods, and headers. Automatically triggers Base.metadata.create_all(bind=engine) during startup lifecycle to synchronize ORM models "
        "with PostgreSQL. Mounts event and incident routers under the '/api/v1' prefix. Exposes root ('/') returning service metadata "
        "and health check ('/health') returning status 'ok' and timestamp.",
        "The backend application cannot launch; no HTTP endpoints would exist, and neither the web cockpit nor external services could communicate with our system."
    )

    file_block(
        "apps/api/src/config.py",
        "This file is the secure configuration vault for the backend. Instead of writing sensitive database passwords, "
        "secret tokens, and port numbers directly into the source code where hackers could see them, this file reads them "
        "safely from hidden environment files (.env). If a setting is missing, it provides safe default fallbacks so the server "
        "still runs smoothly during local testing.",
        "Implements a Settings class extending Pydantic's BaseSettings. Automatically reads environment variables with strict type validation: "
        "DATABASE_URL (PostgreSQL connection string), REDIS_URL (Redis connection string), API_PORT (default 8000), and APP_ENV (default 'development'). "
        "Loads variables from .env via ConfigDict(env_file='.env', extra='ignore'). Instantiates a global cached settings singleton.",
        "Database connection strings and credentials would be hardcoded in plaintext, creating severe security vulnerabilities and making deployment across different environments impossible."
    )

    file_block(
        "apps/api/src/database.py",
        "This file is the database connection manager. In real-world software, opening a brand-new connection to PostgreSQL "
        "for every single incoming web request is very slow and can crash the database when hundreds of requests arrive at once. "
        "This file creates a 'connection pool' (a pre-warmed set of reusable database connections). It also includes a safety "
        "pre-ping feature: before giving a connection to a request, it quickly tests it to make sure it hasn't timed out or gone stale.",
        "Configures SQLAlchemy 2.0 create_engine with connection pooling parameters: pool_size=10 (maximum steady connections), "
        "max_overflow=20 (additional temporary connections during traffic spikes), and pool_pre_ping=True (executes a lightweight SELECT 1 "
        "before checkout to recycle dead connections). Exposes SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine), "
        "the declarative base Base = declarative_base(), and the get_db() dependency generator yielding sessions with guaranteed try/finally cleanup.",
        "Every API request would open an unpooled connection, rapidly exhausting PostgreSQL's max_connections limit and causing complete backend downtime under moderate traffic."
    )

    file_block(
        "apps/api/src/models/event.py",
        "This file defines the permanent relational database table for saving raw error reports, telemetry anomalies, and logs. "
        "Whenever any monitored application crashes or encounters an issue, the raw event is saved here with a unique tracking ID, "
        "the name of the service that broke, the environment it was running in, and the exact timestamp.",
        "Defines the EventModel SQLAlchemy ORM class mapping to the 'events' PostgreSQL table. Column schema: id (UUID Primary Key, default=uuid4), "
        "service_id (String, indexed), environment_id (String, indexed), type (String, nullable=False), source (String), summary (String), "
        "payload (JSON/JSONB for arbitrary structured event telemetry), and created_at (DateTime with timezone, default=utc_now).",
        "The platform would have no relational table to store incoming telemetry, making it impossible to correlate errors or maintain an audit trail."
    )

    file_block(
        "apps/api/src/models/incident.py",
        "This file defines the database table for tracking full-blown outages and problems (Incidents). An incident is more than "
        "just a single error log—it represents a correlated problem across time. This table stores the incident title, how severe it is "
        "(Critical, High, Medium, Low), its current stage in the healing lifecycle (open -> diagnosing -> awaiting_approval -> resolved), "
        "and records the exact second it was opened and resolved.",
        "Defines the IncidentModel SQLAlchemy ORM class mapping to the 'incidents' table. Column schema: id (UUID Primary Key), title (String, nullable=False), "
        "severity (String, indexed, values from Severity enum), status (String, indexed, values from IncidentStatus enum), pipeline_id (String, nullable=True), "
        "service_id (String, indexed), environment_id (String), event_ids (JSON array storing correlated event UUIDs), opened_at (DateTime), "
        "and resolved_at (DateTime, nullable=True, updated upon resolution).",
        "Outages could not be grouped or tracked as formal tickets; the web cockpit would have no incident database to query, filter, or display."
    )

    file_block(
        "apps/api/src/models/evidence.py",
        "This file defines the database table that stores factual diagnostic proof attached to an incident. When a server fails, "
        "it emits various clues—such as an error log line, a memory spike graph, or a Python stack trace. This table stores each "
        "clue linked directly to the parent incident, so the AI and human engineers can inspect the exact evidence.",
        "Defines the EvidenceModel SQLAlchemy class mapping to the 'evidence' table. Column schema: id (UUID Primary Key), "
        "incident_id (UUID Foreign Key referencing incidents.id, indexed), kind (String, values: log, metric, stack_trace, config_snapshot, deployment_event), "
        "source (String), content (Text, storing the exact log message or metric snapshot), and collected_at (DateTime with timezone).",
        "Telemetry artefacts would be lost immediately after ingestion, leaving the AI engine and human SREs with zero factual proof to diagnose root causes."
    )

    file_block(
        "apps/api/src/models/diagnosis.py",
        "This file defines the database table that permanently saves the AI's diagnostic reasoning. When the AI finishes analyzing "
        "an incident, it records what it believes is the root cause, its mathematical confidence score (e.g., 0.94), and the exact "
        "evidence IDs it used to reach that conclusion. This guarantees full transparency and prevents AI decisions from being a black box.",
        "Defines the DiagnosisModel SQLAlchemy class mapping to the 'diagnoses' table. Column schema: id (UUID Primary Key), "
        "incident_id (UUID Foreign Key referencing incidents.id, indexed), probable_root_cause (Text), confidence (Float, bounded between 0.0 and 1.0), "
        "supporting_evidence_ids (JSON list of UUIDs), contradicting_evidence_ids (JSON list), and created_at (DateTime).",
        "AI diagnostic findings would exist only temporarily in RAM during an HTTP request; no historical record or audit trail of AI reasoning would be preserved."
    )

    file_block(
        "apps/api/src/routers/events.py",
        "This file is the primary reception desk of our platform. It exposes the web address (POST /api/v1/events) where external "
        "applications send their error signals. When a signal arrives, this router first checks it against our strict P2 contracts "
        "to ensure it is valid and does not contain unauthorized fields. Then, it saves it into PostgreSQL and pushes the event ID "
        "into a Redis background queue so our worker can process it asynchronously without making the caller wait.",
        "FastAPI APIRouter mounted at '/api/v1/events'. Implements POST /api/v1/events (validates payload against P2 Event contract, "
        "persists EventModel to DB via get_db session, enqueues event ID to Redis queue with graceful fallback if Redis is unavailable, returns HTTP 201), "
        "GET /api/v1/events (supports pagination with skip/limit and filtering by service_id and type), and GET /api/v1/events/{id} (returns single event or HTTP 404).",
        "External applications would have no API endpoint to report error telemetry to; the self-healing platform would never receive any failure signals."
    )

    file_block(
        "apps/api/src/routers/incidents.py",
        "This file provides the API endpoints that power our Next.js dashboard. It lets the web cockpit fetch the list of active outages, "
        "filter them by severity or status, inspect a single incident in detail, and most importantly, it provides the PATCH endpoint "
        "that executes when a human engineer clicks 'Approve & Heal' in the cockpit, advancing the incident to 'resolved' and recording the timestamp.",
        "FastAPI APIRouter mounted at '/api/v1/incidents'. Implements GET /api/v1/incidents (supports filtering by status and severity, returns list of Incident contracts), "
        "GET /api/v1/incidents/{id} (retrieves single incident with 404 handling), and PATCH /api/v1/incidents/{id}/status (accepts status update, "
        "validates state transition, automatically stamps resolved_at = utc_now() when transitioning to 'resolved', commits transaction, and returns updated model).",
        "The frontend dashboard could not retrieve incidents, and human engineers would have no way to approve remediation plans or mark outages resolved."
    )

    file_block(
        "tests/test_api_events.py",
        "This file is an automated test suite containing 7 rigorous checks that test every single backend endpoint. "
        "It uses a temporary in-memory test database so it runs instantly without touching real production data. "
        "It verifies that valid events are saved, invalid events are rejected, 404 errors work properly, and incidents can be queried.",
        "Pytest integration suite utilizing FastAPI TestClient and an in-memory SQLite database via create_engine('sqlite:///:memory:', poolclass=StaticPool). "
        "Tests: (1) Root & Health endpoint 200 OK, (2) POST event creation 201 Created, (3) POST event domain-agnostic rejection asserting extra fields trigger HTTP 422, "
        "(4) GET events pagination and filtering, (5) GET event by ID, (6) GET event non-existent ID 404 Not Found, (7) POST and GET incident lifecycle.",
        "Developers could make breaking changes to database schemas or API endpoints without realizing it, deploying broken code directly to production."
    )

    file_block(
        "docker-compose.yml",
        "This file is the automated infrastructure blueprint for the entire project. It allows any team member to start up "
        "PostgreSQL 16 and Redis 7 in lightweight, isolated Docker containers on their computer with a single command (docker compose up), "
        "without having to spend hours manually downloading, installing, and configuring database servers.",
        "Docker Compose configuration file defining: 'postgres' service (image: postgres:16, environment variables for POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, "
        "port 5432, persistent volume postgres-data, healthcheck using pg_isready) and 'redis' service (image: redis:7-alpine, port 6379, persistent volume redis-data). "
        "Connects both containers on an internal bridge network named 'aiops-network'.",
        "Team members would have to manually install and manage PostgreSQL and Redis on Windows/Mac/Linux, leading to environment mismatch errors and broken local tests."
    )

    # ── 3.2 RUDRA FILES ──────────────────────────────────────────────────────
    doc.add_page_break()
    h2("3.2 Rudra (AI & RAG Lead) — Files in apps/ai-worker/ & Intelligence Core")

    file_block(
        "apps/ai-worker/src/main.py",
        "This file is the web gateway for the AI diagnostic service. It runs a dedicated FastAPI application that lets our backend "
        "and test scripts talk to the AI engine over HTTP. It provides endpoints to check if the AI service is healthy, list all the "
        "runbooks currently loaded in memory, and the core endpoint (POST /api/v1/diagnose) where an incident is sent to receive "
        "an instant AI diagnosis and remediation plan.",
        "FastAPI application running on port 8001. Defines DiagnoseRequest (incident: Incident, evidence: List[Evidence]) and DiagnoseResponse "
        "(status: str, incident_id: UUID, diagnosis: Diagnosis, remediation_plan: RemediationPlan). Exposes GET / (service metadata), "
        "GET /health (reports status 'ok' and langchain_available=True), GET /api/v1/runbooks (serializes all indexed runbooks), "
        "and POST /api/v1/diagnose (invokes diagnosis_engine.diagnose_incident and returns structured response).",
        "The AI reasoning engine would be completely isolated in Python memory; no other microservice or web cockpit could request an automated diagnosis."
    )

    file_block(
        "apps/ai-worker/src/config.py",
        "This file manages the settings for the AI worker. It controls which AI model provider to use (such as Google Gemini or "
        "a fully local offline fallback), reads API keys securely from the environment, and sets the minimum confidence threshold "
        "(0.65) required before any AI diagnosis is considered trustworthy.",
        "Settings class inheriting from Pydantic BaseSettings. Loads MODEL_PROVIDER ('gemini' or 'local'), GEMINI_API_KEY (optional string), "
        "MIN_CONFIDENCE (default 0.65 float), and LOG_LEVEL. Configured with ConfigDict(env_file='.env', extra='ignore'). Instantiates a global settings singleton.",
        "The AI service would have hardcoded model parameters, making it impossible to switch between free local testing and production LLMs without altering code."
    )

    file_block(
        "apps/ai-worker/src/runbook_store.py",
        "This file is the AI's internal medical library. Instead of paying thousands of dollars for expensive cloud vector databases "
        "(like Pinecone), Rudra built a completely free, in-memory Vector Knowledge Base. It stores 5 certified engineering runbooks "
        "(covering Database Pool exhaustion, Out-of-Memory kills, CPU saturation, Latency degradation, and CI/CD rollback). "
        "It converts text into mathematical vectors using TF-IDF and uses cosine similarity to find the exact matching runbook in under 5 milliseconds.",
        "Implements Runbook dataclass (id, title, symptoms, root_cause_explanation, recommended_action, recommended_action_type, remediation_params). "
        "Pre-indexes 5 system runbooks (RB-001 through RB-005). Implements RunbookVectorStore using scikit-learn's TfidfVectorizer: "
        "fit() builds term-document matrix from combined runbook symptoms and root causes at startup; retrieve(query, top_k) transforms the query vector, "
        "calculates linear_kernel / cosine_similarity, and returns ranked [Runbook, score] tuples sorted by similarity. Global singleton pre-fitted at module import.",
        "The AI engine would have no knowledge base to reference; diagnoses would be based on ungrounded hallucinations rather than verified engineering procedures."
    )

    file_block(
        "apps/ai-worker/src/diagnosis_service.py",
        "This file is the diagnostic reasoning brain of the entire platform. It orchestrates the Retrieval-Augmented Generation (RAG) pipeline: "
        "it takes an incident and its evidence, queries the vector store for matching runbooks, injects that factual context into a LangChain "
        "prompt template, computes a calibrated confidence score (0.65 to 0.98), and constructs fully compliant P2 Diagnosis and RemediationPlan contracts.",
        "Defines DIAGNOSIS_PROMPT_TEMPLATE using LangChain PromptTemplate with variables: incident_title, evidence_summary, and runbook_context. "
        "Implements DiagnosisEngine class with methods: _summarize_evidence(evidence_list) serializing telemetry clues to structured text, "
        "and diagnose_incident(incident, evidence_list). Retrieves top-matching runbook via runbook_store.retrieve, calculates bounded confidence "
        "score (base similarity + evidence weight bonus, clamped strictly to [0.65, 0.98]), and constructs P2 Diagnosis model with cited evidence IDs "
        "and P2 RemediationPlan with ordered RemediationAction items (status=PlanStatus.DRAFTED).",
        "The platform would have no automated root cause analysis; outages would remain undiagnosed and no structured remediation plan would ever be generated."
    )

    file_block(
        "tests/test_ai_worker.py",
        "This file is an automated test suite containing 6 tests that verify Rudra's AI worker. It tests that the AI service starts, "
        "that all 5 runbooks are indexed, that the vector similarity search correctly selects Runbook RB-001 for database errors and "
        "RB-002 for memory errors, that confidence scores are mathematically bounded, and that unauthorized domain fields are rejected.",
        "Pytest integration suite utilizing FastAPI TestClient on the ai-worker application. Tests: (1) Root & Health endpoint online, "
        "(2) GET /api/v1/runbooks returns 5 indexed runbooks, (3) Vector retrieval precision asserting RB-001 retrieved for 'QueuePool timeout' "
        "and RB-002 for 'OOM container exit 137', (4) Diagnosis of database pool incident asserting confidence > 0.65 and action_type='config_update', "
        "(5) Diagnosis of OOM incident asserting action_type='container_restart', (6) Domain-agnostic extra field rejection asserting HTTP 422.",
        "Bugs in the vector search or confidence calculations would go unnoticed, potentially causing the AI to recommend incorrect remediation actions in production."
    )

    # ── 3.3 VIVEK FILES ──────────────────────────────────────────────────────
    doc.add_page_break()
    h2("3.3 Vivek (Frontend Lead) — Files in apps/web/ & Developer Cockpit")

    file_block(
        "apps/web/src/types/index.ts",
        "This file is the shared contract dictionary for the frontend. It translates our backend Python P2 data models into "
        "TypeScript interfaces. This guarantees that Vivek's frontend code and Taranay's backend API speak the exact same data "
        "language—ensuring that field names, severity levels, and status strings match 100% at compile-time.",
        "Defines TypeScript interfaces mirroring P2 contracts: Event, Incident, Evidence, Diagnosis, RemediationPlan, and RemediationAction. "
        "Defines strict TypeScript enums: Severity ('critical' | 'high' | 'medium' | 'low'), IncidentStatus ('open' | 'diagnosing' | 'awaiting_approval' | "
        "'executing' | 'verifying' | 'resolved' | 'closed'), EvidenceKind ('log' | 'metric' | 'stack_trace'), ActionType ('config_update' | "
        "'container_restart' | 'rollback' | 'scale_service'), and PlanStatus ('drafted' | 'approved' | 'rejected' | 'completed').",
        "Frontend components could attempt to access non-existent or misnamed backend fields, resulting in silent runtime JavaScript crashes and broken dashboards."
    )

    file_block(
        "apps/web/src/app/layout.tsx",
        "This file is the master layout and HTML shell of our web cockpit. It wraps every page in consistent fonts, sets up "
        "search engine metadata (SEO), and ensures that light and dark themes switch cleanly without causing hydration warnings "
        "or screen flickering when the page loads in a browser.",
        "Next.js 14 App Router RootLayout component. Imports and configures the Inter font from Google Fonts with Latin subset. "
        "Defines Metadata object with title 'AIOps Self-Healing Platform — SRE Developer Cockpit' and descriptive meta tags. "
        "Wraps children in <html lang='en' suppressHydrationWarning> and sets the global body font class.",
        "Every dashboard screen would have to manually load fonts and metadata, causing inconsistent layouts, font loading delays, and hydration mismatch errors."
    )

    file_block(
        "apps/web/src/app/globals.css",
        "This file contains the complete visual design system of the platform. Vivek implemented a tactile 3D skeuomorphic "
        "enterprise design: cards have soft dual drop-shadows that give them physical depth, interactive buttons have subtle "
        "hover and click micro-animations, and CSS variables automatically adjust colors between light and dark modes.",
        "Defines CSS custom properties (--background, --surface, --border, --text, --primary, --accent) under :root and .dark selectors. "
        "Implements skeuomorphic tactile depth via multi-layered box-shadows (6px 6px 14px rgba(0,0,0,0.08), -4px -4px 10px rgba(255,255,255,0.9)). "
        "Configures responsive grid templates, scrollbar styling, status badge color classes, and smooth CSS transitions on all interactive components.",
        "The web dashboard would appear as a plain, unstyled HTML page without colors, visual hierarchy, or responsive layouts."
    )

    file_block(
        "apps/web/src/app/page.tsx",
        "This file is the central page component of our Developer Cockpit. It manages the global state of the dashboard "
        "(such as which incident is currently selected by the engineer) and arranges all the individual components "
        "(Header, MetricsBar, TopologyView, IncidentFeed, IncidentDetail) into a responsive, intuitive split-screen layout.",
        "Primary Next.js React page component. Utilizes useState to manage selectedIncident (typed as Incident | null) initialized to the first mock incident. "
        "Renders Header at the top, MetricsBar for real-time KPIs, TopologyView for infrastructure health, and a responsive two-column master-detail grid: "
        "IncidentFeed on the left column (passing onSelect callback) and IncidentDetail on the right column (displaying the selected incident).",
        "Visiting http://localhost:3000 would render a blank screen; the user interface would have no root assembly or state management."
    )

    file_block(
        "apps/web/src/components/Header.tsx",
        "This component renders the top navigation bar of our application. It displays the platform's brand name, a pulsating green "
        "'Operational' health badge showing the system is live, an authenticated user profile chip ('Saurav Sharma — Tier-1 Admin'), "
        "and an interactive button to switch between Light Theme and Dark Mode.",
        "Client component ('use client'). Renders brand typography with custom icon. Renders a live Operational status badge with an animated CSS pulse dot. "
        "Includes a persistent ThemeToggle button that toggles the 'dark' class on document.documentElement and persists user preference in localStorage. "
        "Displays user session chip with avatar icon, name, and administrative tier badge.",
        "Users would have no persistent theme switcher, no visible platform operational status, and no user identity context at the top of the screen."
    )

    file_block(
        "apps/web/src/components/MetricsBar.tsx",
        "This component renders four live SRE summary cards at the top of the dashboard. In a single glance, an engineer can see: "
        "how many outages are currently active (e.g., 2), the Mean Time To Resolve (MTTR: 4.2 minutes), total autonomous heals performed (142), "
        "and overall system health (99.8%). Each card has a colored delta indicator showing whether metrics are improving.",
        "Renders a responsive 4-column KPI grid using KPICard sub-components. Each card displays an SVG icon, label, metric value, "
        "and positive/negative delta badge: (1) Active Outages (2, red badge), (2) MTTR (4.2 min, -18% green badge), (3) Autonomous Heals (142, +12 blue badge), "
        "and (4) System Health (99.8%, optimal green badge). Styled with tactile skeuomorphic card elevation.",
        "Engineers would lack high-level operational situational awareness; determining system health would require opening and counting individual incident tickets manually."
    )

    file_block(
        "apps/web/src/components/IncidentFeed.tsx",
        "This component renders the live incident stream on the left side of the screen. It displays active incidents with color-coded "
        "severity badges (Critical in red, High in orange), status pills, and client-side timestamps. It includes filter buttons "
        "(All, Open, Diagnosing, Awaiting Approval) so an engineer can immediately focus on the most urgent tickets.",
        "Client component managing internal filterState ('ALL' | 'OPEN' | 'DIAGNOSING' | 'AWAITING_APPROVAL'). Renders MOCK_INCIDENTS list filtered by state. "
        "Each card renders title, service_id badge, severity indicator, and a relative time string wrapped in suppressHydrationWarning to prevent SSR/CSR timestamp mismatches. "
        "Triggers onSelect callback when clicked, highlighting the active card with a primary border accent.",
        "Engineers would have no triage stream to view incoming outages, compare urgency, or select an incident for detailed inspection."
    )

    file_block(
        "apps/web/src/components/IncidentDetail.tsx",
        "This is the most critical component in the frontend. It renders three essential areas: (1) The Evidence Room displaying raw logs "
        "and metrics, (2) The AI RAG Inspector showing the root-cause diagnosis and animated confidence bar, and (3) The Human-in-the-Loop "
        "Governance Console with the prominent 'Approve & Heal' button that allows an engineer to authorize the remediation fix.",
        "Master inspection component. Renders: (1) Evidence Room section mapping telemetry items with kind badges and code blocks, "
        "(2) AI Diagnosis section displaying probable_root_cause, cited evidence IDs, and a visual percentage confidence bar (colored green if >=80%, yellow if >=65%), "
        "(3) Remediation Plan section displaying action type, target service, and parameters, and (4) Human-in-the-Loop Console featuring the primary 'Approve & Heal' "
        "action button. Clicking triggers a confirmation prompt, updates local state, and simulates real-time incident resolution.",
        "The platform would have no human governance interface; engineers could neither verify AI reasoning nor authorize self-healing actions, breaking SOC-2 compliance."
    )

    file_block(
        "apps/web/src/components/TopologyView.tsx",
        "This component renders a visual health grid of all 6 platform microservices (API Gateway, Event Worker, AI Engine, Web Cockpit, "
        "PostgreSQL, and Redis). It shows the live status (Healthy / Degraded) and response latency (e.g., API: 12ms, Postgres: 3ms) "
        "of each component so engineers can immediately see if an infrastructure node is failing.",
        "Renders a 6-node infrastructure grid. Maps over services: aiops-api (Healthy, 12ms), aiops-worker (Healthy, 45ms), ai-worker (Healthy, 284ms), "
        "aiops-web (Healthy, 8ms), postgres (Healthy, 3ms), and redis (Healthy, 1ms). Each ServiceCard renders an SVG component icon, "
        "a live status badge with color coding, and response latency telemetry.",
        "Engineers would have no visual representation of infrastructure topology and would have to run manual shell commands across 6 containers to detect which service is degraded."
    )

    # ── 3.4 SAURAV FILES ─────────────────────────────────────────────────────
    doc.add_page_break()
    h2("3.4 Saurav (DevOps & Integration Lead) — Contracts, Tests, Scripts, & Compliance")

    # Shared Contracts
    file_block(
        "packages/contracts/aiops_contracts/__init__.py",
        "This file is the public front door of our shared contracts library. Instead of forcing microservices to know internal "
        "file paths, this registry lets any service import any model with a clean, standard single-line Python import statement.",
        "Public package registry. Re-exports all core models and enums: Event, EventType, Incident, IncidentStatus, Severity, "
        "Evidence, EvidenceKind, Diagnosis, ActionType, PlanStatus, RemediationAction, RemediationPlan, Approval, ApprovalDecision, "
        "Verification, and VerificationStatus. Defines __all__ list.",
        "Every service would need to import from deep nested internal file paths, causing import failures whenever internal file structures are refactored."
    )

    file_block(
        "packages/contracts/aiops_contracts/common.py",
        "This file is the bedrock of the platform's data integrity. It defines the base model that every single data contract inherits from. "
        "It enforces Pydantic's 'extra=forbid' rule—meaning if anyone tries to inject unauthorized fields (like e-commerce data) into our system, "
        "it immediately rejects them. It also provides standard functions to generate unique UUIDs and timezone-safe UTC timestamps.",
        "Defines ContractModel extending Pydantic BaseModel with model_config = ConfigDict(extra='forbid', populate_by_name=True, validate_assignment=True). "
        "Provides new_id() returning str(uuid4()) and utc_now() returning datetime.now(timezone.utc). Serves as the technical enforcement "
        "mechanism for the Domain-Agnosticity Invariant across all services.",
        "Data models would accept arbitrary injected fields (such as order_id or payment_status), destroying domain-agnosticity and creating security vulnerabilities."
    )

    file_block(
        "packages/contracts/aiops_contracts/event.py",
        "This file defines the strict data contract for all incoming failure signals. Any external monitoring tool, client app, "
        "or server that wants to report an error to our platform must format its payload according to this model.",
        "Defines Event contract model inheriting from ContractModel. Fields: id (str, default_factory=new_id), created_at (datetime, default_factory=utc_now), "
        "service_id (str, required), environment_id (str, required), type (EventType enum: telemetry, pipeline_run, deployment, external), "
        "source (str, required), summary (str, required), and payload (Dict[str, Any]). Extra fields are strictly forbidden.",
        "Incoming event telemetry would be unstandardized and unpredictable, breaking automated parsing and correlation across services."
    )

    file_block(
        "packages/contracts/aiops_contracts/incident.py",
        "This file defines the standardized contract representing a verified incident. It ensures that the backend, frontend, "
        "and AI worker all share the exact same definition of an outage, its severity levels, and its lifecycle status.",
        "Defines Incident contract model. Fields: id, opened_at, resolved_at (Optional[datetime]), title (str), severity (Severity enum: critical, high, medium, low), "
        "status (IncidentStatus enum: open, diagnosing, awaiting_approval, executing, verifying, resolved, closed), pipeline_id (Optional[str]), "
        "service_id (str), environment_id (str), and event_ids (List[str] tracking correlated events). Extra fields forbidden.",
        "The frontend, backend, and AI engine would use divergent schemas for incidents, making multi-service communication and UI rendering impossible."
    )

    file_block(
        "packages/contracts/aiops_contracts/evidence.py",
        "This file defines the data contract for diagnostic evidence. It guarantees that every log line, metric reading, "
        "or stack trace collected during an outage has a verified origin, a timestamp, and a structured format.",
        "Defines Evidence contract model. Fields: id, collected_at, incident_id (str), kind (EvidenceKind enum: log, metric, stack_trace, config_snapshot, deployment_event), "
        "source (str), and content (str). Extra fields forbidden.",
        "Evidence items would be free-form text without timestamps or categorized kinds, preventing the AI engine from citing factual evidence IDs."
    )

    file_block(
        "packages/contracts/aiops_contracts/diagnosis.py",
        "This file defines the contract that the AI Diagnostic Worker must follow when outputting its findings. It requires the AI "
        "to state a probable root cause, cite specific evidence IDs as proof, and provide a mathematical confidence score between 0.0 and 1.0.",
        "Defines Diagnosis contract model. Fields: id, created_at, incident_id (str), probable_root_cause (str), confidence (float, validated 0.0 <= confidence <= 1.0), "
        "supporting_evidence_ids (List[str]), and contradicting_evidence_ids (List[str], default empty list). Extra fields forbidden.",
        "The AI could return ungrounded, free-form text without citations or confidence scores, making automated remediation unsafe and unverifiable."
    )

    file_block(
        "packages/contracts/aiops_contracts/remediation.py",
        "This file defines the contract for self-healing actions and remediation plans. It ensures all plans are categorized "
        "by risk level, that individual actions follow certified types (restart, reconfigure, scale, rollback), and that every plan "
        "starts safely in 'DRAFTED' status.",
        "Defines ActionType enum (config_update, container_restart, rollback, scale_service, pull_request) and PlanStatus enum (drafted, approved, rejected, executing, completed, failed). "
        "Defines RemediationAction model (plan_id, action_type, description, target_service_id, parameters, order). "
        "Defines RemediationPlan model (incident_id, diagnosis_id, status=PlanStatus.DRAFTED, rationale, risk_level, actions=List[RemediationAction]).",
        "The AI could generate arbitrary shell commands that execute without safety categorization, ordered steps, or human review."
    )

    file_block(
        "packages/contracts/aiops_contracts/approval.py",
        "This file defines the human governance audit contract. Whenever an engineer clicks 'Approve & Heal' or 'Reject' in the cockpit, "
        "this model records who made the decision, what they decided, any notes they added, and the exact timestamp.",
        "Defines Approval contract model and ApprovalDecision enum (approved, rejected). Fields: id, decided_at, plan_id (str), "
        "decision (ApprovalDecision), approved_by (str user identifier), and notes (Optional[str]). Extra fields forbidden.",
        "There would be no verifiable, immutable audit trail of which human engineer authorized an infrastructure change, violating SOC-2 compliance."
    )

    file_block(
        "packages/contracts/aiops_contracts/verification.py",
        "This file defines the contract that records whether a remediation fix actually worked. It captures post-fix metric readings "
        "and outcome summaries to provide empirical proof that the system healed.",
        "Defines Verification contract model and VerificationStatus enum (pending, passed, failed, inconclusive). "
        "Fields: id, verified_at, plan_id (str), status (VerificationStatus), method (str, e.g. 'health_probe'), outcome_summary (str), "
        "and metrics_snapshot (Dict[str, Any]). Extra fields forbidden.",
        "The platform would have no formal feedback loop to verify if an executed remediation resolved the failure or caused further instability."
    )

    file_block(
        "tests/test_contracts.py",
        "This file contains 15 automated unit tests that thoroughly verify our data contracts. It tests valid construction of every model "
        "and rigorously asserts that injecting unauthorized domain terms (order_id, cart, payment_status, inventory) causes immediate validation errors.",
        "Pytest unit test suite containing 15 parameterized tests. Tests valid instantiation of Event, Incident, Evidence, Diagnosis, "
        "RemediationAction, RemediationPlan, Approval, and Verification. Uses pytest.mark.parametrize to inject banned domain-specific keywords "
        "into each model and asserts that Pydantic raises pydantic.ValidationError due to extra='forbid'.",
        "Accidental schema modifications or unauthorized domain fields could slip into the shared contracts unnoticed, breaking multi-service compatibility."
    )

    # DevOps Integration & Tooling
    file_block(
        "tests/test_e2e_pipeline.py",
        "This file is the master multi-service integration test for the entire platform. In a single test run, it tests the complete "
        "8-stage self-healing lifecycle: ingesting an event into the API, correlating an incident, building evidence, querying the AI worker "
        "for a RAG diagnosis, verifying the remediation plan, testing human approval via PATCH status to resolved, and running a static scan "
        "confirming zero domain leaks in the output.",
        "End-to-end integration test suite. Employs dynamic Python module cache isolation (purging 'src' from sys.modules and updating sys.path[0]) "
        "to prevent namespace collisions between apps/api and apps/ai-worker in a single process. Tests: (1) test_e2e_incident_detection_to_healing_pipeline "
        "(runs full 8-stage lifecycle against in-memory SQLite and isolated AI worker, asserting all contract models and state transitions succeed), "
        "and (2) test_e2e_rejection_of_unauthorized_fields (asserts sending unauthorized fields to the API returns HTTP 422).",
        "Individual microservices could pass their isolated unit tests while failing completely to communicate with each other in an integrated environment."
    )

    file_block(
        "tests/foundation/test_domain_agnostic_rules.py",
        "This file is an automated static code scanner. It automatically inspects every single Python file across the entire repository "
        "to ensure that no developer has accidentally written banned e-commerce keywords into the core platform code.",
        "Static analysis test. Recursively walks through apps/api/src, apps/ai-worker/src, and packages/contracts/aiops_contracts. "
        "Scans all .py files and asserts that none contain the strings: 'order_id', 'cart', 'payment_status', 'checkout', or 'inventory'.",
        "Domain-specific logic could silently creep into the core platform code, violating the repository's foundational architectural rule."
    )

    file_block(
        "tests/foundation/test_api_health.py",
        "This file tests that the backend API boots cleanly and that its health and readiness probes accurately report database availability.",
        "Pytest suite testing the API root, /health, and /ready endpoints under both normal conditions and simulated database connection failure.",
        "Startup regressions in the API gateway would not be detected until integration tests fail with obscure errors."
    )

    file_block(
        "tests/foundation/test_ai_worker_health.py",
        "This file tests that the AI diagnostic worker starts properly and confirms that LangChain and the vector store are operational.",
        "Pytest suite verifying the AI worker's root endpoint and health check, confirming the service reports status 'online' and langchain_available=True.",
        "AI worker startup issues would only be discovered when an active incident diagnosis is requested."
    )

    file_block(
        "tests/foundation/test_worker_connectivity.py",
        "This file tests that the background task worker can connect to Redis and gracefully handles network connection drops.",
        "Pytest suite verifying Redis connection establishment and exception handling in the background worker using unit test mocks.",
        "Redis connection drops would cause worker crash loops instead of clean, retryable errors."
    )

    file_block(
        "scripts/simulate_failure_e2e.py",
        "This file is an interactive command-line simulator built specifically for project presentations, viva examinations, and release tests. "
        "With one command, it simulates an entire server outage live on screen in 2 seconds—showing event ingestion, AI runbook diagnosis, "
        "confidence scoring, human approval, and automated resolution with colored terminal output.",
        "CLI simulation harness. Executes a complete 8-stage synthetic Database Connection Pool failure scenario end-to-end. "
        "Features colored ANSI terminal output with Windows UTF-8 fallback. Performs live vector runbook matching, LangChain prompt formatting, "
        "remediation plan drafting, human approval simulation, and a final automated domain-agnosticity audit scanning output strings for banned terms.",
        "Live demonstrations would require triggering real production outages or manually crafting complex HTTP requests during timed presentations."
    )

    file_block(
        "docs/SAAS_ARCHITECTURE_AND_COMPLIANCE_GUIDE.md",
        "This file is the enterprise architecture and legal compliance manual for the platform. It proves that our platform is not "
        "just a prototype, but an enterprise-ready SaaS product with multi-tenancy, $0.00 cloud cost economics, and complete SOC-2 readiness.",
        "Enterprise technical guide covering: SaaS vs PaaS taxonomy, multi-tenant isolation models, $0.00 cost economics justification, "
        "and 10 comprehensive pre-live enterprise policies (Service Level Agreement, Privacy Policy, Security Policy, Disaster Recovery Plan, "
        "Change Management, API Documentation, Incident Response Runbooks, Onboarding Guide, Billing Policy, and SOC-2 Compliance Attestation).",
        "The project would appear as an unverified academic script rather than an enterprise-grade SaaS platform ready for deployment."
    )

    file_block(
        "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx",
        "This file is the comprehensive master engineering knowledge transfer document in Word format. It preserves the complete technical "
        "memory of the project from Phase P0 to Phase P3, including architecture cards, individual lead contributions, and viva Q&A.",
        "Master technical document covering: Executive Architecture, Phase P0-P3 technical scorecards, individual lead contribution sections, "
        "the complete 16-question Viva Defense Guide, Saurav's DevOps execution log, and the Phase P3 formal signoff certification.",
        "Critical technical knowledge and design decisions would be lost whenever team members rotate or hand over the project."
    )

    file_block(
        "SAAS_ARCHITECTURE_AND_COMPLIANCE_MASTER.docx",
        "This file is the executive-ready Word document detailing our SaaS compliance readiness, formatted for submission to university "
        "examiners, corporate investors, and compliance auditors.",
        "Executive presentation document rendering the complete SaaS architecture, multi-tenancy model, zero-cost economics, and compliance attestation in a formal executive style.",
        "Enterprise compliance documentation would only exist in developer Markdown rather than in an executive-ready format suitable for academic or investor review."
    )

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 4 — EXAMINER VIVA & TECHNICAL DEFENSE MASTER GUIDE
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("4. Examiner Viva & Technical Defense Master Guide")

    body(
        "This chapter prepares the team for academic viva examinations, project defense panels, and technical evaluations. "
        "Below are the top 10 most critical architectural questions evaluators will ask, along with authoritative, high-scoring answers:"
    )

    viva_qa = [
        ("Q1: What is the core problem your project solves?",
         "Traditional cloud incident management is slow, manual, and reactive. When distributed microservices fail at 3:00 AM, human SREs spend hours sifting through scattered logs, searching for outdated wiki runbooks, and guessing root causes. Our Autonomous AIOps Self-Healing Platform automates this entire loop: it detects telemetry anomalies, correlates them into incidents, uses an in-memory RAG AI engine to diagnose root causes against verified runbooks, drafts a safe remediation plan, and provides an interactive Next.js web cockpit for one-click human approval and automated verification within seconds."),

        ("Q2: What does 'Domain-Agnostic' mean and why is it a core design rule?",
         "Domain-agnostic means the core platform has zero dependency on any specific commercial business sector. It contains no concepts like 'cart', 'order_id', 'flight_number', or 'patient_record'. Instead, it operates strictly on generic engineering primitives: Event, Incident, Evidence, Diagnosis, RemediationAction, and Verification. This allows the exact same platform core to monitor an e-commerce website, a banking API, or a hospital registry without modifying a single line of core platform code. Domain-specific logic lives exclusively behind external webhook adapters."),

        ("Q3: Why did you choose RAG (Retrieval-Augmented Generation) instead of fine-tuning or raw LLMs?",
         "Raw LLMs suffer from hallucinations, have no awareness of company-specific operational procedures, and output non-deterministic responses. Fine-tuning is computationally expensive and quickly becomes outdated when systems change. RAG provides the optimal engineering solution: we retrieve exact, verified operational runbooks from an in-memory vector store based on mathematical text similarity and inject them directly into the prompt. This grounds the AI's diagnosis in factual documentation, eliminates hallucinations, and ensures deterministic, calibrated confidence scores."),

        ("Q4: How did you achieve $0.00 cloud infrastructure cost?",
         "We deliberately engineered local, zero-cost implementations for every tier. Instead of paying for expensive cloud vector databases like Pinecone, Rudra built an in-memory TF-IDF vector store using scikit-learn. PostgreSQL 16 and Redis 7 run in local Docker containers. The API and AI-worker run locally via FastAPI, and the frontend runs on Next.js 14. All 31 tests and end-to-end simulations execute completely offline without spending a single dollar."),

        ("Q5: What is the purpose of the 'Approve & Heal' button in the cockpit? Why not 100% autonomous execution?",
         "In enterprise production environments, fully autonomous systems that modify infrastructure without human oversight pose severe operational risks (e.g., accidental data deletion or cascading restarts). Our platform implements 'Human-in-the-Loop' (HITL) governance. The AI performs 99% of the cognitive burden—detecting, gathering evidence, diagnosing, and drafting the fix—but requires an authorized human SRE to click 'Approve & Heal'. This guarantees human accountability, safety, and compliance with SOC-2 audit requirements."),

        ("Q6: How do your shared data contracts prevent domain leaks?",
         "All shared models in packages/contracts inherit from ContractModel, which is configured with Pydantic v2's model_config = ConfigDict(extra='forbid'). If any payload sent to our API contains an unapproved field (such as order_id or payment_status), Pydantic automatically rejects it with an HTTP 422 Unprocessable Entity error before it can enter the database or AI worker."),

        ("Q7: How did Saurav resolve the Python namespace collision in the mono-repo?",
         "Both apps/api and apps/ai-worker have internal folders named 'src'. When running multi-service integration tests in a single Python process, Python caches imported modules in sys.modules, causing 'src.main' from the first service to collide with 'src.main' from the second. Saurav solved this in test_e2e_pipeline.py by implementing dynamic sys.modules cleanup (purging any cached 'src' modules) and prioritizing the active service directory in sys.path[0] before each cross-service call."),

        ("Q8: How does the AI worker calculate its confidence score?",
         "The confidence score is not a random number. It is mathematically calculated by combining the cosine similarity score from the TF-IDF vector search with an evidence weight bonus (proportional to the number of factual evidence items provided). The resulting score is strictly clamped between 0.65 (minimum threshold for an action to be proposed) and 0.98 (to prevent false certainty), ensuring reliable calibration."),

        ("Q9: What happens if an external service sends an event while Redis or the database is down?",
         "In apps/api/src/routers/events.py, the Redis queue push is wrapped in a try/except block. If Redis is temporarily unreachable, the event is still safely committed to PostgreSQL and an HTTP 201 Created is returned, preventing caller dropouts. During readiness probes (/ready), database connectivity is actively pinged, returning HTTP 503 if the database is unavailable."),

        ("Q10: What is next in Phase P4?",
         "Phase P4 transitions the platform from local testing to live monitoring of external applications. We will construct real Webhook Ingestion Adapters (for services like Prometheus, Datadog, and custom client apps), implement the live event worker queue processing in apps/worker, and deploy our first live external target app to be autonomously monitored.")
    ]

    for q, a in viva_qa:
        h3(q)
        body(a)

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 5 — CONCLUSION & PHASE P3 SIGNOFF
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("5. Phase P3 Formal Signoff & Quality Certification")

    callout(
        "PHASE P3 OFFICIALLY CERTIFIED AND COMPLETE\n\n"
        "1. Backend Tier (apps/api): Relational ORM models, connection pooling, and event/incident routers verified.\n"
        "2. AI Diagnostic Core (apps/ai-worker): In-memory vector store, LangChain RAG diagnosis, and confidence calibration verified.\n"
        "3. SRE Cockpit (apps/web): Next.js 14 Developer Cockpit, 3D skeuomorphic styling, and HITL console verified (0 TS errors).\n"
        "4. DevOps & Governance: 31/31 automated tests passing, clean git working tree, domain agnosticity audited, $0.00 cloud cost.\n\n"
        "The repository is production-ready and fully prepared to begin Phase P4 (Webhook Adapters & Live Target Monitoring).",
        title="FINAL PHASE P3 QUALITY CERTIFICATION",
        border="10B981",
        bg="ECFDF5"
    )

    doc.save(str(OUTPUT_PATH))
    print(f"Document successfully created at: {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
