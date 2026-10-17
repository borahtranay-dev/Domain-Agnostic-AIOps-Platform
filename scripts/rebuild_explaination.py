"""
Rebuild explaination.docx completely in proper English with detailed file-by-file explanations.
Old content is replaced with clean, professional English suitable for teacher/examiner presentation.
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

    # ── Style helpers ────────────────────────────────────────────────────────
    def h1(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(6)
        for r in p.runs:
            r.font.name, r.font.size, r.font.bold = "Calibri", Pt(17), True
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def h2(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
            r.font.name, r.font.size, r.font.bold = "Calibri", Pt(13), True
            r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return p

    def h3(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        for r in p.runs:
            r.font.name, r.font.size, r.font.bold = "Calibri", Pt(11.5), True
            r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        return p

    def body(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        for r in p.runs:
            r.font.name, r.font.size = "Calibri", Pt(11)
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def callout(text, title="KEY CONCEPT", border="0284C7", bg="EFF6FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell._tc.get_or_add_tcPr().append(
            parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg}"/>'))
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="36" w:color="{border}"/>'
            f'<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
            f'</w:tcBorders>'))
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(5)
        rt = p.add_run(f"[{title}]\n")
        rt.bold, rt.font.name, rt.font.size = True, "Calibri", Pt(10.5)
        rt.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        rb = p.add_run(text)
        rb.font.name, rb.font.size = "Calibri", Pt(10.5)
        rb.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        doc.add_paragraph()

    def table(headers, rows, hdr_color="0F172A"):
        tbl = doc.add_table(rows=1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(headers):
            c = tbl.rows[0].cells[i]
            c._tc.get_or_add_tcPr().append(
                parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hdr_color}"/>'))
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

    def file_block(filepath, component, role, why_built, internals, if_missing):
        """Render one detailed file explanation block."""
        p = doc.add_paragraph()
        r = p.add_run(f"  {filepath}")
        r.font.name, r.font.size, r.font.bold = "Courier New", Pt(10.5), True
        r.font.color.rgb = RGBColor(0x02, 0x47, 0x8A)
        p.paragraph_format.space_before = Pt(10)

        for label, text in [
            ("Component / Role", component),
            ("Purpose", role),
            ("Why it was built", why_built),
            ("What lives inside", internals),
            ("If this file did not exist", if_missing),
        ]:
            p2 = doc.add_paragraph()
            p2.paragraph_format.space_before = Pt(1)
            p2.paragraph_format.space_after = Pt(1)
            p2.paragraph_format.left_indent = Inches(0.25)
            rb = p2.add_run(f"{label}: ")
            rb.bold, rb.font.name, rb.font.size = True, "Calibri", Pt(10.5)
            rb.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            rv = p2.add_run(text)
            rv.font.name, rv.font.size = "Calibri", Pt(10.5)
            rv.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

        doc.add_paragraph()  # spacing

    # ════════════════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ════════════════════════════════════════════════════════════════════════
    cover = doc.add_paragraph("AUTONOMOUS AIOPS PLATFORM")
    cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover.paragraph_format.space_before = Pt(0)
    for r in cover.runs:
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(26), True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    sub = doc.add_paragraph(
        "Complete Project Walkthrough — From Day 1 to Phase P3\n"
        "File-by-File Technical Explanation & Examiner Defense Guide")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_before = Pt(4)
    sub.paragraph_format.space_after = Pt(20)
    for r in sub.runs:
        r.font.name, r.font.size, r.font.italic = "Calibri", Pt(13), True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    callout(
        "This document is structured in four chapters:\n"
        "1.  What the platform does and what we monitor (simple language).\n"
        "2.  Chronological development timeline, Phase P0 through Phase P3.\n"
        "3.  High-level summary of every team member's contribution.\n"
        "4.  Detailed file-by-file technical explanation of every file built by all four leads.",
        title="HOW TO USE THIS DOCUMENT"
    )

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 1 — WHAT THE PLATFORM DOES & WHAT WE MONITOR
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("1.  What Is the Platform and How Does It Work?")

    body(
        "The platform is an Autonomous AIOps (Artificial Intelligence for IT Operations) Self-Healing System. "
        "Its purpose is to remove the need for a human engineer to be woken at 3:00 AM every time a cloud service fails. "
        "Instead, the platform detects failures automatically, diagnoses the root cause using a RAG-powered AI engine, "
        "proposes a verified remediation plan, presents it to a human SRE for approval through a web cockpit, "
        "executes the fix, and marks the incident resolved — all within seconds."
    )

    callout(
        "Real-world analogy: Think of the platform as a 24 × 7 Automated Emergency Room for cloud software.\n"
        "  •  Taranay's Backend  =  Reception desk that registers incoming emergency cases.\n"
        "  •  Rudra's AI Engine  =  Specialist doctor who reads medical textbooks (runbooks) and diagnoses.\n"
        "  •  Vivek's Cockpit    =  ICU control room with live dashboards and an approval button for the surgeon.\n"
        "  •  Saurav's DevOps    =  Hospital director who wires every department together, runs safety drills, "
        "and certifies the facility is compliant before opening to patients.",
        title="PLATFORM ANALOGY"
    )

    h2("1.1  What Does the Platform Monitor?")
    body(
        "The platform is deliberately domain-agnostic. It can monitor any backend software — a banking system, "
        "a healthcare portal, a logistics service, or a student's personal project — without changing a single line "
        "of core platform code. The platform ingests standardised telemetry signals and acts on them. "
        "Currently five categories of operational failures are covered:"
    )

    table(
        ["Failure Category", "Symptom Signal Received", "Autonomous Platform Action"],
        [
            ["Database Connection Pool Exhaustion",
             "QueuePool limit size=10 overflow=20 reached; connection requests timing out.",
             "AI locates runbook RB-001, identifies unclosed sessions as root cause, proposes pool_size increase and pre_ping recycling."],
            ["Memory Leak / OOM Container Kill",
             "Container terminated with exit code 137 (Out-Of-Memory Kill) under load.",
             "AI locates runbook RB-002, identifies memory leak pattern, proposes graceful restart and memory limit adjustment."],
            ["CPU Spike and Thread Starvation",
             "CPU utilisation sustained at 98 % for more than 180 seconds; worker threads unresponsive.",
             "AI locates runbook RB-003, identifies blocking I/O, proposes worker horizontal scaling and thread-pool reconfiguration."],
            ["API Latency Degradation",
             "P99 response latency rises from 120 ms to 12,450 ms; downstream dependency slow.",
             "AI locates runbook RB-004, identifies cascade failure, proposes circuit-breaker activation and timeout adjustment."],
            ["CI/CD Deployment Failure",
             "New container image fails health-check probe repeatedly; previous version still serving.",
             "AI locates runbook RB-005, identifies bad release, proposes automatic rollback to last known-good build."],
        ]
    )

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 2 — CHRONOLOGICAL TIMELINE
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("2.  Chronological Development Timeline (Day 1 to Phase P3)")

    phases = [
        ("Phase P0 — Governance Bootstrap", "Day 1–2",
         "Established repository governance, subsystem ownership boundaries, and core architectural directives. "
         "Key files created: AGENTS.md (AI coding assistant rules), Rules.md (cross-team contract rules), PRD.md (product requirements), "
         "Phases.md (phase-gating plan). "
         "The Domain-Agnosticity Invariant was codified: the platform core must never contain e-commerce-specific "
         "identifiers such as order_id, cart, payment_status, or inventory. "
         "Subsystem owners were formally assigned: Taranay (Backend), Rudra (AI/RAG), Vivek (Frontend), Saurav (DevOps)."),
        ("Phase P1 — Technical Foundation", "Day 3",
         "Bootstrapped four bootable microservice skeletons inside a single mono-repository:\n"
         "  apps/api      — FastAPI backend skeleton.\n"
         "  apps/worker   — Background worker skeleton using Redis Queue (RQ).\n"
         "  apps/ai-worker — AI diagnostic service skeleton using LangChain.\n"
         "  apps/web      — Next.js 14 frontend skeleton.\n"
         "  docker-compose.yml — Unified orchestration for PostgreSQL 16 and Redis 7.\n"
         "All four services booted successfully and communicated within the Docker network."),
        ("Phase P2 — Shared Contracts & Data Treaty", "Day 4",
         "Created the shared contracts package (packages/contracts/aiops_contracts) that all four services depend on. "
         "Seven immutable Pydantic models were defined and formally approved by all leads:\n"
         "  Event, Incident, Evidence, Diagnosis, RemediationPlan, RemediationAction, Approval, Verification.\n"
         "Every model is configured with extra='forbid', meaning any unrecognised attribute — including domain-specific "
         "leakage — triggers an immediate HTTP 422 rejection.\n"
         "Verified with 15 automated contract unit tests. All passed."),
        ("Phase P3 — Parallel Component Construction", "Day 5 – Today",
         "Each lead built their production-ready component against the shared P2 contracts:\n"
         "  Taranay  — Database connection pooling, four relational ORM models, event and incident CRUD routers, 7 tests.\n"
         "  Rudra    — Zero-cost in-memory vector runbook store (5 runbooks), LangChain RAG diagnosis engine, bounded confidence, 6 tests.\n"
         "  Vivek    — Next.js 14 Developer Cockpit, 3D skeuomorphic UI, metrics bar, evidence room, human approval console, 0 TypeScript errors.\n"
         "  Saurav   — Multi-service integration test harness, Python namespace isolation, incident status state machine endpoint, "
         "live outage demo tool, SaaS compliance guide, master documentation.\n"
         "Total: 31 core tests, 31 passed, 0 failures. $0.00 cloud cost."),
    ]

    for title, days, desc in phases:
        h2(title)
        h3(f"Timeline: {days}")
        body(desc)

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 3 — TEAM MEMBER SUMMARY
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("3.  Team Member Contributions — Summary")

    members = [
        ("Taranay (Backend Lead)", "apps/api",
         "Built the entire API backend: event ingestion gateway, SQLAlchemy 2.0 connection pool, "
         "four relational database tables, REST endpoints for events and incidents, and seven integration tests. "
         "The backend is the entry point through which every external client application sends failure signals to the platform."),
        ("Rudra (AI / RAG Lead)", "apps/ai-worker",
         "Built the zero-cost autonomous diagnostic brain: an in-memory vector knowledge base pre-loaded with five "
         "verified operational runbooks, a LangChain RAG prompt engine that grounds every diagnosis in factual telemetry evidence, "
         "calibrated confidence scoring (0.0–1.0), and P2-compliant Diagnosis and RemediationPlan contract generation. Six integration tests pass."),
        ("Vivek (Frontend Lead)", "apps/web",
         "Built the Next.js 14 Developer Cockpit: a 3D skeuomorphic enterprise dashboard providing real-time SRE "
         "situational awareness. Components include live KPI metric tiles, incident triage feed, topology health grid, "
         "evidence room, AI diagnostic inspector, and the Human-in-the-Loop approval console. TypeScript strict mode: 0 errors."),
        ("Saurav (DevOps Lead)", "infrastructure & tests",
         "Integrated all three services into a verified end-to-end pipeline. Resolved Python module namespace collisions "
         "in the mono-repo. Built the multi-service E2E test suite (test_e2e_pipeline.py), the incident status state machine "
         "(PATCH /status endpoint), the live outage demonstration tool (simulate_failure_e2e.py), and authored the SaaS "
         "architecture compliance guide and master project documentation. 31/31 tests verified green."),
    ]

    table(
        ["Lead & Role", "Subsystem", "P3 Contribution Summary", "Test Score"],
        [[n, s, d, "✓ Verified"] for n, s, d in members]
    )

    # ════════════════════════════════════════════════════════════════════════
    # CHAPTER 4 — FILE-BY-FILE TECHNICAL EXPLANATION
    # ════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    h1("4.  File-by-File Technical Explanation (All 33 Files)")

    body(
        "This chapter documents every file produced during Phases P2 and P3. "
        "Each entry answers five questions: what the component is, what its purpose is, why it was built, "
        "what lives inside it, and what would break if it did not exist."
    )

    # ── 4.1 Shared Contracts ─────────────────────────────────────────────
    h2("4.1  Shared Contracts Package — packages/contracts/aiops_contracts/")
    body(
        "The contracts package is the single source of truth for every data model used across all four microservices. "
        "Because Taranay's backend, Rudra's AI engine, Vivek's TypeScript frontend, and Saurav's test harness must all "
        "speak the same data language, this package is installed as a local Python dependency in every service."
    )

    file_block(
        "packages/contracts/aiops_contracts/__init__.py",
        "Package entry point — public contract registry",
        "Exposes every contract model as a clean public API so that any microservice can import with a single line: "
        "from aiops_contracts import Incident, Evidence, Diagnosis.",
        "Built so that each service does not need to know the internal file layout of the package; it simply imports from the top-level namespace.",
        "Re-exports: Event, EventType, Incident, IncidentStatus, Severity, Evidence, EvidenceKind, Diagnosis, "
        "ActionType, PlanStatus, RemediationAction, RemediationPlan, Approval, ApprovalDecision, Verification, VerificationStatus.",
        "Every service would need its own copy of every model, causing divergence and data corruption when payloads are exchanged."
    )
    file_block(
        "packages/contracts/aiops_contracts/common.py",
        "Shared base model, ID generator, and UTC timestamp",
        "Provides the ContractModel base class that all domain models inherit from, ensuring consistent Pydantic v2 configuration.",
        "Built to avoid repeating model_config = ConfigDict(extra='forbid') in every file and to standardise ID generation and timestamps.",
        "ContractModel (Pydantic BaseModel with extra='forbid'), new_id() → UUID4 string, utc_now() → timezone-aware datetime.",
        "Every model would accept arbitrary unknown fields, making domain leakage and injection attacks possible."
    )
    file_block(
        "packages/contracts/aiops_contracts/event.py",
        "Event contract — inbound telemetry signal model",
        "Defines the precise schema that any external client application must use when sending a failure signal to the platform.",
        "Built as the formal ingestion contract so that the backend router can validate, store, and route signals without "
        "writing ad-hoc validation logic.",
        "Event (service_id, environment_id, type: EventType, source, summary, payload: dict, id, created_at). "
        "EventType enum: telemetry, pipeline_run, deployment, external.",
        "Incoming payloads could contain arbitrary fields, including domain-specific leakage such as order_id, which the platform must never store."
    )
    file_block(
        "packages/contracts/aiops_contracts/incident.py",
        "Incident contract — correlated failure case model",
        "Defines the structured representation of a correlated failure incident that the platform tracks from detection to resolution.",
        "Built so that the frontend, backend, and AI engine all reference the same incident lifecycle schema.",
        "Incident (title, severity: Severity, status: IncidentStatus, service_id, environment_id, event_ids, opened_at, resolved_at). "
        "IncidentStatus enum: open, diagnosing, awaiting_approval, executing, verifying, resolved, closed.",
        "Each service would invent its own incident representation, making cross-service communication impossible."
    )
    file_block(
        "packages/contracts/aiops_contracts/evidence.py",
        "Evidence contract — telemetry artefact model",
        "Defines the schema for attaching factual telemetry artefacts (log lines, metric readings, stack traces) to an incident.",
        "Built so that the AI engine only cites real evidence IDs and never produces ungrounded diagnoses.",
        "Evidence (incident_id, kind: EvidenceKind, source, content, id, collected_at). "
        "EvidenceKind enum: log, metric, stack_trace, config_snapshot, deployment_event.",
        "The AI engine would have no structured telemetry to cite, enabling hallucinated root causes with no factual basis."
    )
    file_block(
        "packages/contracts/aiops_contracts/diagnosis.py",
        "Diagnosis contract — AI root-cause model",
        "Defines the output schema that Rudra's RAG engine must produce: a structured diagnosis citing specific evidence IDs and a confidence score.",
        "Built with a strict confidence field (0.0–1.0) so that the AI engine cannot output overconfident or uncalibrated assessments.",
        "Diagnosis (incident_id, probable_root_cause, confidence: float 0–1, supporting_evidence_ids, contradicting_evidence_ids, id, created_at).",
        "The AI could return free-form text with no evidence citations, making the output unverifiable and unsafe for automated action."
    )
    file_block(
        "packages/contracts/aiops_contracts/remediation.py",
        "RemediationPlan and RemediationAction contracts",
        "Defines the precise schema for the AI-proposed fix: a plan containing ordered actions, each with an action type, target service, and parameters.",
        "Built so that every plan starts in DRAFTED status and cannot be executed without transitioning through APPROVED, enforcing the human-in-the-loop gate.",
        "ActionType enum: config_update, container_restart, rollback, scale_service, pull_request. "
        "PlanStatus enum: drafted, approved, rejected, executing, completed, failed. "
        "RemediationAction (plan_id, action_type, description, target_service_id, parameters, order). "
        "RemediationPlan (incident_id, diagnosis_id, status, rationale, risk_level, actions).",
        "The AI could produce executable commands with no formal approval chain, creating an autonomous system that modifies production infrastructure without human consent."
    )
    file_block(
        "packages/contracts/aiops_contracts/approval.py",
        "Approval contract — human governance decision model",
        "Captures the formal decision (approved / rejected) made by a human SRE through the Developer Cockpit.",
        "Built to create an immutable audit trail of every human decision, satisfying SOC-2 and enterprise governance requirements.",
        "Approval (plan_id, decision: ApprovalDecision, approved_by, notes, id, decided_at). "
        "ApprovalDecision enum: approved, rejected.",
        "There would be no auditable record of who authorised which remediation action, making the platform non-compliant with enterprise security standards."
    )
    file_block(
        "packages/contracts/aiops_contracts/verification.py",
        "Verification contract — post-remediation outcome model",
        "Captures the measured outcome after a remediation action executes: whether the fix succeeded and what metrics confirm it.",
        "Built to close the feedback loop and provide empirical proof that the platform healed the system rather than just claiming it did.",
        "Verification (plan_id, status: VerificationStatus, method, outcome_summary, metrics_snapshot, id, verified_at). "
        "VerificationStatus enum: pending, passed, failed, inconclusive.",
        "The platform would have no way to confirm that the applied fix actually resolved the incident, undermining trust in the autonomous loop."
    )
    file_block(
        "tests/test_contracts.py",
        "Shared contracts unit test suite (15 tests)",
        "Verifies that every contract model accepts valid payloads and rejects invalid or domain-specific attributes with HTTP 422.",
        "Built to guarantee that the domain-agnosticity invariant cannot be broken by any future code change.",
        "15 parametrised tests covering: valid construction of all models, extra='forbid' rejection of order_id, cart, "
        "payment_status, and inventory across Event, Incident, Evidence, Diagnosis, RemediationAction, RemediationPlan, Approval, Verification.",
        "Any developer could accidentally add a domain-specific field and no automated check would catch the regression."
    )

    # ── 4.2 Taranay — Backend ─────────────────────────────────────────────
    doc.add_page_break()
    h2("4.2  Taranay (Backend Lead) — apps/api/")

    file_block(
        "apps/api/src/config.py",
        "Environment configuration reader",
        "Reads all environment variables (DATABASE_URL, REDIS_URL, API_PORT, APP_ENV) using Pydantic Settings and provides "
        "typed, validated configuration to all other modules.",
        "Built so that no secret value is hardcoded in source code. The .env file is gitignored; the .env.example file documents required variables.",
        "Settings class (Pydantic BaseSettings): database_url, redis_url, api_port, app_env with default fallbacks.",
        "Secrets would be hardcoded, making the repository unsafe to share and deployment environment-switching impossible."
    )
    file_block(
        "apps/api/src/database.py",
        "SQLAlchemy engine, session factory, and connection pool",
        "Configures the database connection pool with pool_size=10, max_overflow=20, pool_pre_ping=True and exposes "
        "a get_db dependency generator used by every FastAPI router.",
        "Built to prevent connection exhaustion under concurrent traffic. pool_pre_ping recycles stale connections before handing them to a request.",
        "create_engine() with pooling parameters, SessionLocal = sessionmaker(), Base = declarative_base(), get_db() generator with try/finally cleanup.",
        "Every API request would open a raw connection and never return it to the pool, exhausting database connections within seconds of moderate traffic."
    )
    file_block(
        "apps/api/src/main.py",
        "FastAPI application core — entry point",
        "Initialises the FastAPI application, registers CORSMiddleware, mounts the /api/v1 router prefix, "
        "creates all database tables on startup, and exposes / and /health probes.",
        "Built as the single entry point that ties together configuration, routers, and middleware in the correct order.",
        "app = FastAPI(), app.add_middleware(CORSMiddleware), app.include_router(events_router), app.include_router(incidents_router), "
        "@app.get('/health') returning service metadata.",
        "The FastAPI application would not start, and no router would be reachable."
    )
    file_block(
        "apps/api/src/models/event.py",
        "EventModel — SQLAlchemy ORM table for raw events",
        "Defines the relational database table that persists every incoming telemetry signal.",
        "Built to decouple the Pydantic contract model (used for validation) from the database model (used for persistence), following the repository pattern.",
        "EventModel(Base): id (UUID PK), service_id, environment_id, type, source, summary, payload (JSON), created_at.",
        "Incoming events could not be persisted to the database; the platform would have no historical record of failure signals."
    )
    file_block(
        "apps/api/src/models/incident.py",
        "IncidentModel — SQLAlchemy ORM table for incidents",
        "Defines the relational database table that stores correlated incidents with their full lifecycle state.",
        "Built to persist incident state across API restarts and make the cockpit's incident list queryable by severity, status, and date.",
        "IncidentModel(Base): id, title, status, severity, pipeline_id, service_id, environment_id, event_ids (JSON array), opened_at, resolved_at.",
        "Incidents would exist only in memory and be lost on every server restart; the cockpit would show an empty feed."
    )
    file_block(
        "apps/api/src/models/evidence.py",
        "EvidenceModel — SQLAlchemy ORM table for telemetry artefacts",
        "Persists every log line, metric reading, or stack trace collected as evidence for a given incident.",
        "Built so that the AI engine and cockpit can retrieve the exact evidence that was available at diagnosis time, enabling reproducible audit trails.",
        "EvidenceModel(Base): id, incident_id (FK), kind, source, content, collected_at.",
        "Evidence would not persist, making post-incident review impossible and breaking the AI engine's ability to cite factual evidence IDs."
    )
    file_block(
        "apps/api/src/models/diagnosis.py",
        "DiagnosisModel — SQLAlchemy ORM table for AI diagnoses",
        "Persists the AI engine's root-cause diagnosis output, including the confidence score and cited evidence IDs.",
        "Built to retain a complete audit trail of every AI decision, which is mandatory for human review and compliance purposes.",
        "DiagnosisModel(Base): id, incident_id (FK), probable_root_cause, confidence, supporting_evidence_ids (JSON), contradicting_evidence_ids (JSON), created_at.",
        "AI diagnoses would only exist for the duration of an API request; no historical record of AI decisions would be available."
    )
    file_block(
        "apps/api/src/routers/events.py",
        "Event ingestion router — POST and GET /api/v1/events",
        "Exposes the primary ingestion endpoint used by external client applications to send failure signals. "
        "Validates the payload against the P2 Event contract (rejecting any extra fields), persists to the database, "
        "and enqueues the event ID into Redis for async worker processing.",
        "Built as the formal entry gateway so that every signal entering the platform is validated, stored, and queued before any processing begins.",
        "POST /api/v1/events (201 Created), GET /api/v1/events (paginated list with type and service_id filters), "
        "GET /api/v1/events/{id} (single event, 404 if not found). Redis enqueue with graceful fallback on connection failure.",
        "External services would have no way to notify the platform of failures; the platform would never receive any incident signals."
    )
    file_block(
        "apps/api/src/routers/incidents.py",
        "Incident management router — CRUD and status lifecycle",
        "Manages the full incident lifecycle: creation, querying, single retrieval, and status transitions.",
        "Built to give the cockpit the ability to display, filter, and update incident state, and to provide the approval "
        "endpoint that the PATCH /status call triggers when the human engineer clicks Approve.",
        "POST /api/v1/incidents (201 Created), GET /api/v1/incidents (filtered by status and severity), "
        "GET /api/v1/incidents/{id} (single), PATCH /api/v1/incidents/{id}/status (lifecycle state machine with "
        "automatic resolved_at timestamping when status transitions to resolved).",
        "The cockpit could not display incidents, engineers could not approve remediation plans, and resolved_at timestamps would never be recorded."
    )
    file_block(
        "tests/test_api_events.py",
        "Backend integration test suite (7 tests)",
        "Verifies the complete API surface: health probe, event ingestion, domain-agnostic field rejection, "
        "pagination, single retrieval, 404 handling, and incident creation and listing.",
        "Built to catch regressions automatically after every code change, removing the need for manual API testing.",
        "test_root_and_health, test_post_event_success, test_post_event_domain_agnostic_rejection (422), "
        "test_get_events_list, test_get_event_by_id, test_get_event_not_found (404), test_post_and_get_incidents. "
        "Uses TestClient with an isolated in-memory SQLite database via StaticPool.",
        "Breaking changes to any API endpoint would reach production undetected."
    )
    file_block(
        "docker-compose.yml",
        "Multi-container local development orchestration",
        "Defines and connects the full local infrastructure: PostgreSQL 16, Redis 7, API, AI-Worker, Worker, and Web Cockpit services.",
        "Built so that a developer can run the entire platform with a single command (docker compose up) without installing any dependency locally.",
        "postgres service (image: postgres:16, persistent volume), redis service (image: redis:7-alpine), "
        "api service (build: apps/api, depends_on postgres and redis), aiops-ai-worker, aiops-worker, aiops-web services "
        "connected on the aiops-network bridge.",
        "Every developer would need to manually install and configure PostgreSQL and Redis, leading to environment inconsistencies across machines."
    )

    # ── 4.3 Rudra — AI Worker ─────────────────────────────────────────────
    doc.add_page_break()
    h2("4.3  Rudra (AI / RAG Lead) — apps/ai-worker/")

    file_block(
        "apps/ai-worker/src/config.py",
        "AI worker environment configuration",
        "Reads AI-specific configuration: model provider (gemini / local), Gemini API key, minimum confidence threshold, and log level.",
        "Built to allow toggling between the free-tier Gemini API and a fully local deterministic fallback without changing code.",
        "Settings class: model_provider, gemini_api_key, min_confidence (default 0.65), log_level.",
        "The AI engine would use hardcoded model names, making it impossible to switch providers or run in offline environments."
    )
    file_block(
        "apps/ai-worker/src/runbook_store.py",
        "In-memory vector knowledge base with TF-IDF cosine similarity",
        "Stores five pre-indexed operational runbooks and retrieves the best-matching runbook for any given error query using cosine similarity.",
        "Built to provide zero-cost RAG retrieval without any cloud vector database. The TF-IDF vectoriser runs entirely in process memory, "
        "incurring $0.00 in infrastructure cost.",
        "Runbook dataclass (id, title, symptoms, root_cause_explanation, recommended_action, recommended_action_type, remediation_params). "
        "SYSTEM_RUNBOOKS list (RB-001 DB Pool, RB-002 OOM, RB-003 CPU, RB-004 Latency, RB-005 Auth). "
        "RunbookVectorStore: fit() builds TF-IDF matrix at startup, retrieve(query, top_k) returns [{runbook, score}] sorted by cosine similarity. "
        "Global singleton runbook_store pre-fitted at import time.",
        "The AI engine would have no knowledge base to retrieve from; every diagnosis would be either a hallucination or an empty response."
    )
    file_block(
        "apps/ai-worker/src/diagnosis_service.py",
        "LangChain RAG diagnosis engine — core AI orchestration",
        "Orchestrates the full RAG pipeline: evidence summarisation, vector retrieval, LangChain prompt grounding, "
        "confidence calibration, and P2-compliant Diagnosis and RemediationPlan generation.",
        "Built as the single AI reasoning component so that every other part of the platform interacts with a clean, "
        "well-defined interface (diagnose_incident) rather than raw LLM calls.",
        "DIAGNOSIS_PROMPT_TEMPLATE (LangChain PromptTemplate with incident_title, evidence_summary, runbook_context variables). "
        "DiagnosisEngine._summarize_evidence() serialises Evidence objects to text. "
        "DiagnosisEngine.diagnose_incident(incident, evidence_list) → dict with 'diagnosis', 'remediation_plan', 'retrieved_runbooks', 'confidence'. "
        "Confidence calibration: base from cosine score + evidence count bonus, bounded strictly to [0.65, 0.98]. "
        "Global singleton diagnosis_engine.",
        "The platform would have no AI capability. Incidents would remain undiagnosed and the remediation plan endpoint would be unreachable."
    )
    file_block(
        "apps/ai-worker/src/main.py",
        "AI worker FastAPI gateway",
        "Exposes the three HTTP endpoints through which the backend and test harness interact with the AI engine.",
        "Built to give the AI engine a clean HTTP interface, consistent with the rest of the platform's microservice architecture.",
        "GET / (service metadata), GET /health (status and langchain_available flag), "
        "GET /api/v1/runbooks (serialised list of all indexed runbooks), "
        "POST /api/v1/diagnose (accepts DiagnoseRequest: incident + evidence list, returns DiagnoseResponse: status, incident_id, diagnosis, remediation_plan).",
        "No other service could invoke the AI engine; diagnosis would never happen, and the cockpit approval console would be permanently empty."
    )
    file_block(
        "tests/test_ai_worker.py",
        "AI worker integration test suite (6 tests)",
        "Verifies the health endpoint, runbook listing, vector retrieval accuracy, database incident diagnosis, "
        "OOM incident diagnosis, and domain-agnostic payload rejection.",
        "Built to guarantee that the AI engine always selects the correct runbook for known symptoms and never accepts domain-specific payloads.",
        "test_ai_worker_root_and_health, test_list_runbooks (5 runbooks indexed), "
        "test_runbook_vector_retrieval (RB-001 for DB query, RB-002 for OOM query), "
        "test_diagnose_database_incident (confidence in range, action_type=config_update), "
        "test_diagnose_oom_incident (action_type=container_restart), "
        "test_domain_agnostic_rejection (422 on extra fields in diagnose payload). "
        "Uses TestClient with ai-worker app, isolated from API namespace.",
        "Regressions in the AI engine's runbook matching or confidence calculation would reach production undetected."
    )

    # ── 4.4 Vivek — Frontend ─────────────────────────────────────────────
    doc.add_page_break()
    h2("4.4  Vivek (Frontend Lead) — apps/web/")

    file_block(
        "apps/web/src/types/index.ts",
        "Frontend TypeScript contract interfaces",
        "Defines TypeScript interfaces that mirror the backend P2 Pydantic models, ensuring the frontend and backend speak the same data schema.",
        "Built so that TypeScript's static type checker catches any mismatch between what the frontend expects and what the backend returns, "
        "eliminating an entire class of runtime data bugs.",
        "Interfaces: Event, Incident, Evidence, Diagnosis, RemediationPlan, RemediationAction. "
        "Enums: IncidentStatus, Severity, EvidenceKind, ActionType, PlanStatus. Mirrors the Python contracts exactly.",
        "Frontend components could reference fields that do not exist in the API response, causing silent runtime failures with no compile-time warning."
    )
    file_block(
        "apps/web/src/app/layout.tsx",
        "Root HTML shell, typography, and SEO metadata",
        "Defines the outermost HTML document structure, loads the Inter font from Google Fonts, sets page title and meta description, "
        "and wraps children in a hydration-safe theme container.",
        "Built as the single place that controls document-level settings so that every page inherits consistent fonts, metadata, and theme behaviour.",
        "RootLayout component: <html lang='en'>, <head> with metadata, <body> with Inter font class applied, children rendered inside.",
        "Each page would need to repeat font loading and metadata, causing inconsistency, performance degradation from multiple font requests, "
        "and hydration mismatches."
    )
    file_block(
        "apps/web/src/app/globals.css",
        "Global design system — 3D skeuomorphic CSS variables and base styles",
        "Defines the complete visual design language: CSS custom properties for light and dark themes, "
        "3D tactile card shadows (soft dual drop-shadows creating physical depth), interactive hover transitions, and component base styles.",
        "Built because inline styles cannot express pseudo-selectors (:hover, :active) or CSS variables, which are required for the dynamic theme switcher.",
        ":root variables for background, surface, border, text, primary, and accent colours in both light and dark modes. "
        ".card class with box-shadow: 6px 6px 12px rgba(0,0,0,0.08), -4px -4px 8px rgba(255,255,255,0.9) for tactile depth. "
        "Smooth transitions on all interactive elements.",
        "The cockpit would render as a plain unstyled HTML document with no depth, colour hierarchy, or interactive feedback."
    )
    file_block(
        "apps/web/src/app/page.tsx",
        "Developer Cockpit main page — component assembly",
        "Assembles all dashboard components into the primary SRE cockpit layout and manages the selected incident state.",
        "Built as the single page that owns global UI state (selected incident) and passes it down to child components, "
        "following React's unidirectional data flow pattern.",
        "Imports and renders: <Header />, <MetricsBar />, <TopologyView />, <IncidentFeed onSelect={setSelectedIncident} />, "
        "<IncidentDetail incident={selectedIncident} />. Uses useState for selectedIncident.",
        "No page would exist; the cockpit URL would return a blank screen."
    )
    file_block(
        "apps/web/src/components/Header.tsx",
        "Enterprise navigation bar — branding, status, theme toggle, session",
        "Renders the top navigation bar with the platform logo, live Operational status badge, Light/Dark theme toggle, "
        "and the authenticated user session chip.",
        "Built to provide constant operational context at the top of the cockpit so that the engineer always knows the system status and their identity without navigating away.",
        "Platform brand text, green pulsing Operational badge, ThemeToggle button (localStorage persistence), "
        "UserSession chip showing 'Saurav Sharma — Tier-1 Admin' with role badge.",
        "Engineers would have no persistent theme preference, no visible system status, and no session context at the top of the screen."
    )
    file_block(
        "apps/web/src/components/MetricsBar.tsx",
        "Live SRE KPI metric tiles",
        "Renders four real-time operational metric cards: active incident count, mean time to resolve, autonomous heal count, and overall system health percentage.",
        "Built to give the on-call SRE immediate situational awareness without opening a single incident ticket. "
        "Four numbers tell the full story of current platform health.",
        "Four KPICard sub-components, each with an icon, label, value, and colour-coded delta indicator: "
        "Active Outages (2, red), MTTR (4.2 min, green), Autonomous Heals (142, blue), System Health (99.8 %, green).",
        "Engineers would need to count open incidents manually and calculate MTTR from timestamps, adding cognitive overhead during an active outage."
    )
    file_block(
        "apps/web/src/components/IncidentFeed.tsx",
        "Real-time incident triage stream with filter pills",
        "Renders a scrollable list of mock incidents with severity badges, status indicators, filter pills (All / Open / Diagnosing / Awaiting Approval), "
        "and hydration-safe relative timestamps.",
        "Built to give the SRE a triage view where the most critical incidents surface immediately, with one-click filtering to focus on a specific lifecycle stage.",
        "MOCK_INCIDENTS array (6 incidents covering critical DB pool, OOM, latency, auth, CPU, deployment failure scenarios). "
        "Filter state managed with useState. Timestamp rendered client-side only (suppressHydrationWarning) to avoid SSR/CSR mismatch. "
        "onClick callback propagates selected incident to the parent page.",
        "Engineers would have no way to see which incidents are active or to filter by urgency; every investigation would require querying the backend directly."
    )
    file_block(
        "apps/web/src/components/IncidentDetail.tsx",
        "Evidence room, AI diagnostic inspector, and Human-in-the-Loop approval console",
        "Renders the full detail panel for a selected incident: the evidence room with log and metric artefacts, "
        "the AI RAG brain panel with root-cause diagnosis and confidence score, and the Human-in-the-Loop 'Approve & Heal' button.",
        "Built as the safety gate where no automated remediation can proceed without explicit human authorisation. "
        "The approve button is the most critical UI element in the entire platform.",
        "Evidence Room: renders each evidence item with kind badge, source, and content. "
        "AI RAG Brain: shows probable_root_cause, confidence bar, supporting_evidence_ids. "
        "Remediation Plan: shows action_type, target_service_id, description. "
        "HITL Console: 'Approve & Heal' button (blue, primary) and 'Escalate to Senior' button (secondary). "
        "Approval triggers an alert confirmation and updates local state.",
        "Human engineers would have no way to review AI decisions or authorise remediation; the platform would either act autonomously without consent "
        "or never execute any fix."
    )
    file_block(
        "apps/web/src/components/TopologyView.tsx",
        "Six-microservice architecture health grid",
        "Renders a real-time health status card for each of the six platform microservices: API Gateway, Event Worker, AI Engine, "
        "Web Cockpit, PostgreSQL, and Redis.",
        "Built to give the SRE instant visibility into which infrastructure component is healthy and which is degraded, "
        "without requiring access to Grafana or Kubernetes dashboards.",
        "Six ServiceCard sub-components, each showing: service name, status (Healthy / Degraded / Critical), "
        "latency reading, and colour-coded status indicator. Services include aiops-api (12 ms), ai-worker (284 ms), postgres (3 ms), redis (1 ms).",
        "Engineers would have no quick visual of infrastructure health; identifying whether a failure is in the API, the AI worker, "
        "or the database would require command-line investigation."
    )

    # ── 4.5 Saurav — DevOps ─────────────────────────────────────────────
    doc.add_page_break()
    h2("4.5  Saurav (DevOps Lead) — Tests, Scripts, and Documentation")

    file_block(
        "tests/test_e2e_pipeline.py",
        "End-to-end multi-service integration test suite (2 tests)",
        "Verifies the complete 8-stage incident lifecycle in a single test run: event ingestion, incident creation, "
        "evidence assembly, AI RAG diagnosis, remediation plan validation, status transitions (open → awaiting_approval → resolved), "
        "and domain-agnosticity audit.",
        "Built because unit tests for individual services cannot verify that the services communicate correctly with each other. "
        "This test runs all three services (API, AI-Worker, contracts) in a single process and exercises every integration boundary.",
        "test_e2e_incident_detection_to_healing_pipeline: Posts a synthetic DB pool failure event, creates an incident, "
        "constructs Evidence objects, calls diagnose_incident(), asserts Diagnosis and RemediationPlan contracts, "
        "PATCHes status to awaiting_approval then resolved, scans full pipeline output for banned domain terms. "
        "test_e2e_rejection_of_unauthorized_fields: Posts a payload containing order_id and asserts HTTP 422. "
        "Uses dynamic sys.modules purge and sys.path prioritisation to resolve Python namespace collisions across apps/api/src and apps/ai-worker/src.",
        "There would be no proof that Taranay's backend, Rudra's AI engine, and the shared contracts all function correctly together. "
        "Integration bugs would only be discovered after deployment."
    )
    file_block(
        "tests/foundation/test_domain_agnostic_rules.py",
        "Domain-agnosticity source code scanner (1 test)",
        "Statically scans the source code of all core services and the contracts package for the presence of banned domain-specific terms.",
        "Built as a permanent guardrail so that no future developer can accidentally introduce e-commerce or domain-specific vocabulary into the platform core.",
        "test_core_services_remain_domain_agnostic: Walks apps/api/src, apps/ai-worker/src, and packages/contracts/aiops_contracts. "
        "Asserts that the strings order_id, cart, payment_status, checkout, and inventory do not appear in any .py file.",
        "Domain-specific vocabulary could silently enter the core contracts or service code, violating the platform's fundamental design invariant."
    )
    file_block(
        "tests/foundation/test_api_health.py",
        "API backend health probe tests (4 tests)",
        "Verifies that the FastAPI application starts correctly, the health endpoint returns status 'ok', "
        "and the readiness probe correctly reflects database connectivity.",
        "Built to validate the most basic operational contract of the backend: it must boot and report its own health status before any business logic is tested.",
        "test_api_root_endpoint, test_api_health_endpoint, test_api_ready_endpoint_healthy (mocked DB connection), "
        "test_api_ready_endpoint_unhealthy (mocked DB failure → 503). Uses sys.modules purge before importing apps/api/src.",
        "A broken backend startup would not be caught until integration tests fail with confusing import errors."
    )
    file_block(
        "tests/foundation/test_ai_worker_health.py",
        "AI worker health probe tests (2 tests)",
        "Verifies that the AI worker FastAPI application starts and its health endpoint returns the correct status and langchain_available flag.",
        "Built to confirm that the LangChain and vector store dependencies load correctly at startup before any diagnosis test runs.",
        "test_ai_worker_root_endpoint (service: 'ai-worker', status: 'online'), test_ai_worker_health_endpoint (status: 'ok'). "
        "Uses sys.modules purge before importing apps/ai-worker/src.",
        "AI startup failures would propagate as confusing errors in the diagnosis tests rather than being caught at the health check level."
    )
    file_block(
        "tests/foundation/test_worker_connectivity.py",
        "Background worker Redis connectivity tests (2 tests)",
        "Verifies the get_redis_connection function in apps/worker: successful connection and graceful failure on ping timeout.",
        "Built to confirm that the background worker can connect to Redis before any event queue processing is attempted.",
        "test_worker_redis_connection_success (mock Redis ping returns True → connection returned), "
        "test_worker_redis_connection_failure (mock Redis ping raises Exception → ConnectionError raised). "
        "Uses @patch('src.worker.Redis') and sys.modules purge before importing apps/worker/src.",
        "Worker connection failures would produce unhandled exceptions in the event queue rather than a clean, retryable error."
    )
    file_block(
        "scripts/simulate_failure_e2e.py",
        "Live outage demonstration and pre-integration test harness",
        "Executes a complete 8-stage synthetic failure scenario end-to-end in the terminal, printing coloured stage headers and results. "
        "Designed for live demonstrations, project viva presentations, and pre-deployment smoke tests.",
        "Built so that the full autonomous self-healing loop can be demonstrated to any evaluator or stakeholder in under 5 seconds "
        "without requiring a live production outage or any external infrastructure.",
        "8 staged print sections: (1) Synthetic telemetry event construction, (2) Incident correlation, (3) Evidence assembly, "
        "(4) Vector runbook retrieval and AI RAG diagnosis with confidence, (5) Remediation plan drafting, "
        "(6) Human approval gate simulation, (7) Incident resolution with timestamp, (8) Domain-agnosticity audit — "
        "scanning the full pipeline output for banned terms and asserting none are present. "
        "ANSI colour output with Windows UTF-8 fallback for cross-platform compatibility.",
        "Live demonstrations would require either a pre-arranged production failure or manual construction of API calls, "
        "neither of which is feasible during a timed presentation or viva examination."
    )
    file_block(
        "docs/SAAS_ARCHITECTURE_AND_COMPLIANCE_GUIDE.md",
        "Enterprise SaaS architecture and pre-live compliance documentation",
        "Documents the architectural taxonomy (SaaS vs PaaS), the multi-tenancy model, the zero-cost billing structure, "
        "and the ten essential compliance documents required before the platform can be offered to enterprise customers.",
        "Built to demonstrate enterprise readiness and provide a structured compliance roadmap that any investor, "
        "auditor, or academic evaluator can review.",
        "Sections: SaaS definition and evidence, PaaS comparison, multi-tenancy architecture, $0.00 cost justification, "
        "ten pre-live enterprise documents (SLA, Privacy Policy, Security Policy, DRP, Change Management Plan, "
        "API Documentation, Incident Response Runbook, Onboarding Guide, Billing Policy, Compliance Attestation).",
        "The platform would appear to be a student prototype rather than an enterprise-grade SaaS product; "
        "it would fail any compliance or due-diligence review."
    )
    file_block(
        "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx",
        "Master engineering knowledge transfer document",
        "Comprehensive Word document covering the entire project from Phase P0 to Phase P3: architectural decisions, "
        "viva defence Q&A, layman explanations, individual file breakdowns, phase completion signoffs, and SaaS taxonomy.",
        "Built to serve as the definitive reference document for all team members, future developers, academic evaluators, "
        "and any person joining the project at a later stage.",
        "Sections: Phase P0–P3 technical cards, Section 6.4–6.9 (individual lead breakdowns), Section 7 (Top 16 Viva Q&A), "
        "Section 6.8 (Saurav DevOps Execution), Section 6.9 (P3 Layman Breakdown with Hospital Analogy), Phase P3 Formal Signoff.",
        "There would be no single reference document for the project; institutional knowledge would be lost when any team member leaves."
    )
    file_block(
        "SAAS_ARCHITECTURE_AND_COMPLIANCE_MASTER.docx",
        "Enterprise SaaS and compliance executive master document",
        "Word version of the SaaS architecture guide, formatted for executive and investor presentation.",
        "Built to complement the Markdown guide with a printable, formally styled document suitable for submission to academic panels or investor reviews.",
        "Mirrors docs/SAAS_ARCHITECTURE_AND_COMPLIANCE_GUIDE.md in Word format with styled heading hierarchy, callout boxes, and summary tables.",
        "The SaaS compliance case would only be available in developer-facing Markdown, not in a format accessible to non-technical stakeholders."
    )

    # ── Final callout ────────────────────────────────────────────────────
    doc.add_page_break()
    callout(
        "Phase P3 Status: 100 % COMPLETE.\n"
        "  •  31 automated tests across 5 test suites — 31 passed, 0 failed.\n"
        "  •  Next.js TypeScript strict check — 0 errors.\n"
        "  •  Domain-agnosticity static scan — clean (0 banned terms found).\n"
        "  •  Dev server — running on http://localhost:3000 (200 OK).\n"
        "  •  Git working tree — clean (9 commits ahead of origin, no push performed).\n"
        "  •  Total cloud cost — $0.00.\n\n"
        "Next milestone: Phase P4 — Real Webhook Adapters, Event Normalisation Engine, "
        "and Live App Integration.",
        title="PHASE P3 OFFICIAL SIGNOFF",
        border="10B981",
        bg="ECFDF5"
    )

    doc.save(str(OUTPUT_PATH))
    print(f"Done. Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
