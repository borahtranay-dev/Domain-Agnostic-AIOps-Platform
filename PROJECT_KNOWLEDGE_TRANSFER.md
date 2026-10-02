# AIOps Self-Healing Platform
# Project Knowledge Transfer — P0/P1

---

## 1. Executive Summary

### Short Samajh
Is project ka overall goal ek aisa domain-agnostic AIOps self-healing platform banana hai jo operational aur CI/CD failures ko automatically detect kare, AI/RAG ke through diagnose kare, remediation plan propose kare, human approval ke baad execute kare, aur verify kare. Current stage par humne actual business logic ya AI diagnosis start nahi kiya hai; humne Phase P0 (governance, ownership, repository rules) aur Phase P1 (Docker containers, PostgreSQL, Redis, FastAPI API, RQ Worker, AI-Worker foundation, Next.js Web Cockpit) ko clean slate se establish aur empirically verify kiya hai.

### Deep Technical Samajh
Current repository state mein zero business domain logic hai. Documented architecture aur current codebase mein clear distinction rakhi gayi hai: documented state intended target hai, jabki repository implementation state verified foundation hai. P0 ke under complete 4-member ownership model (Rudra, Saurav, Taranay, Vivek), strict Git/PR governance, CODEOWNERS, CI baselines, aur AI assistant rules ([`AGENTS.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/AGENTS.md)) commit ho chuke hain. P1 ke under 6 independent containers ([`docker-compose.yml`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/docker-compose.yml)) live hain aur verify ho chuke hain:
1. `postgres` (port 5432, healthy)
2. `redis` (port 6379, healthy)
3. `api` (port 8000, FastAPI HTTP service with `/health` and `/ready`)
4. `worker` (Python 3.12 + RQ connected to Redis on queue `aiops-default`)
5. `ai-worker` (port 8001, FastAPI service with LangChain v0.2.17 dependency verified)
6. `web` (port 3000, Next.js 14 Developer Cockpit foundation serving live status)

P2 next isliye hai kyunki multiple team members bina shared contracts freeze kiye agar code likhna shuru karenge toh catastrophic contract drift hoga.

---

## 2. Project Vision — Simple Explanation

### Short Samajh
AIOps Self-Healing Platform ka vision software pipelines aur deployments mein aane wale issues ko bina manual delay ke identify aur resolve karna hai. Iska future workflow ek continuous loop hoga: Event aayega -> Incident detect hoga -> Evidence gather hoga -> AI diagnose karega -> Fix suggest hoga -> Human engineer approve karega -> Fix apply hoga -> System verify karega ki issue solve hua ya nahi.

### Deep Technical Samajh
Platform ka intended self-healing remediation loop bounded autonomy principle par based hai:

```text
+-----------------------------------------------------------------------------------+
|                        FUTURE AIOPS SELF-HEALING LIFECYCLE                        |
+-----------------------------------------------------------------------------------+
  [Event]                Pipeline failure, pod crash, ya webhook trigger [FUTURE]
     |
     v
  [Incident]             Deduplicated & correlated operational failure [FUTURE]
     |
     v
  [Evidence]             Logs, stacktraces, commits, runbook extracts [FUTURE]
     |
     v
  [Diagnosis]            RAG-grounded root cause determination by AI [FUTURE]
     |
     v
  [Remediation Plan]     Suggested patch, rollback config, ya parameter change [FUTURE]
     |
     v
  [Human Approval]       MANDATORY: Engineer reviews & approves in Cockpit [FUTURE]
     |
     v
  [Adapter Execution]    Git PR creation / deployment rollback via Adapter [FUTURE]
     |
     v
  [Verification]         Re-running pipeline / health-check verification [FUTURE]
     |
     v
  [Recorded Result]      PostgreSQL audit trail & feedback update [FUTURE]
```

#### Important Distinction: Future Architecture vs Current Implementation
- **Future Architecture:** Real GitHub webhooks sunna, automatic incident correlation, LangChain RAG vector store se logs match karna, automated PR raise karna, aur health check verify karke incident auto-close karna.
- **Currently Implemented Architecture:** Sirf multi-service runtime foundation (FastAPI, Redis, PostgreSQL, RQ Worker, Next.js Web UI). Abhi koi real incident ingestion, diagnosis, ya remediation loop code mein exist nahi karta.

---

## 3. What We Are Building vs What We Have Built

| Functional Area | Long-Term Goal (Vision / PRD) | Current Reality (Repository State) |
|---|---|---|
| **Event Ingestion** | GitHub actions webhooks, CI failure webhooks, Kubernetes crash alerts ingest karna. | **Not Implemented.** Sirf HTTP foundation routes (`/health`, `/ready`) available hain. |
| **Incident Management** | Lifecycle states: `DETECTED` -> `DIAGNOSING` -> `PENDING_APPROVAL` -> `EXECUTING` -> `RESOLVED`. | **Not Implemented.** Koi Incident DB table ya state machine abhi nahi hai. |
| **Evidence Collection** | Automated log scraping, git diff fetching, stacktrace extraction. | **Not Implemented.** Reserved for Phase P4. |
| **Diagnosis Engine** | AI model evidence ko analyze karke probable root-cause identify karega. | **Not Implemented.** Reserved for Phase P5. |
| **RAG Pipeline** | Vector database (embeddings) mein past runbooks aur documentation query karna. | **Not Implemented.** Sirf `langchain` library install hui hai technical foundation verify karne ke liye. |
| **Remediation Plan** | Structured fix (diff patch, config change, restart) generate karna. | **Not Implemented.** Reserved for Phase P6. |
| **Human Approval** | Engineer Cockpit mein review karega, reject ya approve karega. | **Not Implemented.** Governance rule documented hai, execution logic P6/P7 mein aayega. |
| **GitHub Automation** | Approved fix ko automatically branch create karke PR open karna. | **Not Implemented.** Koi GitHub API integration code nahi hai. |
| **Verification Engine** | Post-execution build/health status check karke success declare karna. | **Not Implemented.** Reserved for Phase P6/P8. |
| **Developer Cockpit** | Live incident dashboard, diff viewer, evidence browser, approval button. | **Foundation Only.** Single-page Next.js dashboard jo sirf P1 container health show karta hai. |
| **Domain Adapters** | E-commerce reference adapter (orders/cart specific operational knowledge). | **Not Implemented.** Domain-agnostic boundary clean rakhi gayi hai; adapter P3/P4 mein aayega. |
| **Generic Platform Core** | Domain-agnostic contracts (`Pipeline`, `Incident`, `Evidence`, `Verification`). | **Not Implemented.** Schema directory [`packages/contracts/`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/packages/contracts) reserved hai, schemas P2 mein banenge. |

---

## 4. Phase Timeline

```text
+-----------------------------------------------------------------------------------+
|                        PROJECT SEQUENTIAL PHASE TIMELINE                          |
+-----------------------------------------------------------------------------------+
  [P0: Governance]  -->  [P1: Foundation]  -->  [P2: Contracts]  -->  [P3: Construction]
     (COMPLETE)             (COMPLETE)            (NOT STARTED)         (NOT STARTED)
         |                      |
         v                      v
  Rules, Ownership,      Docker, DB, Redis,
  CODEOWNERS, Git        API, Worker, Web
         |
         +--> [P4: Events & Incidents]  (Abhi implement nahi hua)
         +--> [P5: AI Diagnosis & RAG]  (Abhi implement nahi hua)
         +--> [P6: Remediation & Git]   (Abhi implement nahi hua)
         +--> [P7: Developer Cockpit]   (Abhi implement nahi hua)
         +--> [P8: End-to-End System]   (Abhi implement nahi hua)
         +--> [P9: Hardening & Sec]     (Abhi implement nahi hua)
         +--> [P10: Staging & Deploy]   (Abhi implement nahi hua)
         +--> [P11: Release Prep]       (Abhi implement nahi hua)
         +--> [P12: Post-MVP Evolution] (Abhi implement nahi hua)
```

### P0 — Governance & Repository Bootstrap
- **Objective:** Code likhne se pehle rules, team ownership, Git workflow aur AI collaboration boundaries set karna.
- **What was actually implemented:** Git repository initialization, `.gitignore`, `.editorconfig`, `CODEOWNERS`, `CONTRIBUTING.md`, PR & Issue templates, `AGENTS.md`, AI IDE directives.
- **Why necessary:** 4 human engineers aur multiple AI assistants bina conflict ke ek repo par kaam kar sakein.
- **Important files:** [`AGENTS.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/AGENTS.md), [`.github/CODEOWNERS`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.github/CODEOWNERS), [`CONTRIBUTING.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/CONTRIBUTING.md).
- **Verification performed:** Git repository created, clean initial commit (`6e16c30`), files formatted.
- **What it intentionally does NOT do:** Koi application code compile ya run nahi karta.

### P1 — Technical Foundation
- **Objective:** Ek working local development runtime environment establish karna jismein sabhi foundational services boot ho sakein aur aapas mein network communicate kar sakein.
- **What was actually implemented:** Docker Compose orchestration, PostgreSQL 16 container, Redis 7 container, FastAPI backend service (`apps/api`), RQ background worker (`apps/worker`), FastAPI AI worker skeleton (`apps/ai-worker`), Next.js 14 web cockpit (`apps/web`), unit tests (`tests/foundation/`), CI workflow (`.github/workflows/ci.yml`).
- **Why necessary:** Business logic likhne se pehle ensure karna ki databases, message queues, container networks aur API servers reliably start aur communicate kar rahe hain.
- **Important files:** [`docker-compose.yml`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/docker-compose.yml), [`apps/api/src/main.py`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/apps/api/src/main.py), [`apps/worker/src/worker.py`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/apps/worker/src/worker.py), [`apps/ai-worker/src/main.py`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/apps/ai-worker/src/main.py), [`apps/web/src/app/page.tsx`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/apps/web/src/app/page.tsx).
- **Verification performed:** Docker Compose build pass, 6 containers up & healthy, HTTP status 200 on all endpoints, PostgreSQL & Redis connection verified, 9/9 pytest unit tests passed.
- **What it intentionally does NOT do:** No incident models, no database tables for business entities, no RAG embeddings, no diagnosis logic, no PR generation.

### P2 to P12 (Future Phases)
- **P2 — Contract & Domain Foundation:** *Abhi implement nahi hua hai.* Shared schemas aur database tables define honge.
- **P3 — Parallel Component Construction:** *Abhi implement nahi hua hai.* Leads apne components independently build karenge.
- **P4 — Event & Incident Pipeline:** *Abhi implement nahi hua hai.* Real webhook ingestion start hogi.
- **P5 — AI Diagnosis & RAG:** *Abhi implement nahi hua hai.* Vector database aur real diagnosis connect hoga.
- **P6 — Remediation & GitHub Automation:** *Abhi implement nahi hua hai.* Automated PR creation engine banega.
- **P7 — Developer Cockpit:** *Abhi implement nahi hua hai.* Full interactive incident management UI banegi.
- **P8 — End-to-End Integration:** *Abhi implement nahi hua hai.* Golden path testing hogi.
- **P9 — Hardening:** *Abhi implement nahi hua hai.* Security, performance, retry policies.
- **P10 — Staging:** *Abhi implement nahi hua hai.* Staging environment deployment.
- **P11 — Release:** *Abhi implement nahi hua hai.* Production readiness.
- **P12 — Post-MVP:** *Abhi implement nahi hua hai.* Multi-domain scaling.

---

## 5. P0 Deep Dive — What Exactly Was Implemented

### 1. Git Repository Initialization & `main` Branch
- **What?** Empty directory mein Git repo init karke `main` branch banayi gayi.
- **Why?** Version control baseline aur audit trail maintain karne ke liye.
- **How?** `git init -b main`.
- **Why this design?** Single trunk-based collaboration model jismein feature branches PR ke through merge hoti hain.
- **Problem prevented:** Unversioned overwrites aur uncoordinated changes.

### 2. [`.gitignore`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.gitignore)
- **What?** Python (`__pycache__`, `.venv`), Node (`node_modules`, `.next`), Docker data volumes, logs, aur sensitive `.env` files ko ignore karne ki file.
- **Why?** Repositories mein binaries, temporary caches aur secrets commit hone se rokna.
- **How?** Standard unified ruleset combining Python, Node.js, Next.js, and Secrets filters.
- **Why this design?** Secrets aur multi-gigabyte build folders ko repo se bahar rakhna.
- **Problem prevented:** Git bloat aur credentials leak security breach.

### 3. [`.editorconfig`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.editorconfig)
- **What?** Indentation (Python 4 spaces, TS/JSON 2 spaces, LF line endings, utf-8) enforce karne wali configuration.
- **Why?** Windows aur Linux developers ke beech line-ending (`CRLF` vs `LF`) aur formatting wars khatam karna.
- **How?** Standard EditorConfig specification.
- **Why this design?** Cross-platform development consistency.
- **Problem prevented:** Dirty git diffs jismein sirf formatting ya newline change hoti hai.

### 4. [`.github/CODEOWNERS`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.github/CODEOWNERS)
- **What?** Subsystems ki ownership map karne wali GitHub file:
  - `/apps/ai-worker/` -> `@Rudra`
  - `/infrastructure/`, `docker-compose*.yml` -> `@Saurav`
  - `/apps/api/`, `/apps/worker/` -> `@Taranay`
  - `/apps/web/` -> `@Vivek`
  - `/packages/contracts/`, root docs -> `@Rudra @Saurav @Taranay @Vivek`
- **Why?** CODEOWNERS ka purpose sirf ownership likhna nahi hai. Iska main reason yeh hai ki sensitive area mein random approval ya accidental change na ho.
- **How?** GitHub CODEOWNERS syntax format.
- **Why this design?** Cross-boundary changes par coordination enforce karna.
- **Problem prevented:** Ek team member ka doosre ke system ko unilaterally tod dena.

### 5. [`CONTRIBUTING.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/CONTRIBUTING.md)
- **What?** Git branching strategy (`feat/<owner>-<topic>`), PR review requirements, Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`), aur phase governance document.
- **Why?** Sabhi developers aur AI assistants ek hi standard protocol follow karein.
- **How?** Markdown guide repository root par.
- **Why this design?** Clear, human-readable rules of engagement.
- **Problem prevented:** Direct push to main aur cryptic commit messages.

### 6. Pull Request & Task Templates
- **What?** [`.github/pull_request_template.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.github/pull_request_template.md) aur [`.github/ISSUE_TEMPLATE/task.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.github/ISSUE_TEMPLATE/task.md).
- **Why?** PR submit karte time explicit checkboxes fill karne honge: Phase reference, Subsystem owner, Domain-Agnosticity check, local verification proof.
- **How?** Markdown checklist templates.
- **Why this design?** PR submission ke time developer se conscious self-check karwana.
- **Problem prevented:** Unverified code aur domain leakage (`order_id` in core) merge ho jana.

### 7. [`AGENTS.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/AGENTS.md) & [`.agents/rules/ai-collaboration.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.agents/rules/ai-collaboration.md)
- **What?** Antigravity aur any AI coding assistant ke liye binding rules:
  1. Inspect before modifying
  2. Strict phase discipline (no jumping ahead)
  3. Respect ownership boundaries
  4. Shared contracts are inviolable
  5. Avoid blind rewrites
  6. Domain-agnosticity test (no e-commerce leak in core)
  7. Verification after changes
- **Why?** AI assistants code hallucinate karte hain ya aage ke phases ka code prematurely generate karke pure codebase ka architecture ruin kar dete hain.
- **How?** Workspace instruction rulesets.
- **Why this design?** AI IDE ko autonomous developer nahi, controlled implementation assistant ki tarah treat kiya gaya hai.
- **Problem prevented:** AI-driven mass rewrites aur architectural divergence.

### 8. Project Documentation Preservation
- **What?** Pre-existing specification documents ([`architecture.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/architecture.md), [`design.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/design.md), [`Memory.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/Memory.md), [`Rules.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/Rules.md), [`PRD.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/PRD.md), [`Phases.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/Phases.md)) ko inspect karke preserve kiya gaya.
- **Why?** In documents mein system ki authoritative architectural requirements hain.
- **How?** Exact byte-for-byte preservation without modification.
- **Why this design?** Baseline ground-truth ko distort hone se bachana.
- **Problem prevented:** Accidental loss of project specifications.

---

## 6. P0 Git and Collaboration Workflow

### Branches
- `main`: Protected production/integration trunk. Direct commit prohibited once team collaboration starts.
- `feat/<owner>-<feature>`: Feature work (e.g., `feat/taranay-api-foundation`).
- `fix/<owner>-<fix>`: Bug fixes (e.g., `fix/saurav-docker-network`).

### Commits
- Conventional Commits: `type(scope): description`.
- Scopes: `api`, `worker`, `ai-worker`, `web`, `infra`, `contracts`, `docs`, `ci`.
- Focused commits: Frontend, backend, AI changes ko ek hi mix commit mein bundle nahi karna hai.

### PR Expectations
1. PR template fill karna mandatory hai.
2. CI checks green hone chahiye.
3. Affected subsystem CODEOWNER ka approval mandatory hai.
4. Shared contract (`packages/contracts`) change hone par chaaron leads ka agreement chahiye.

### AI IDE Collaboration Rules
AI IDE ko autonomous developer nahi, controlled implementation assistant ki tarah treat kiya gaya hai:
- AI assistant kisi file ko edit karne se pehle disk se inspect karega.
- AI assistant sirf assigned subsystem ke andar kaam karega.
- AI assistant bina permission ke whole file replace nahi karega.
- AI assistant execution ke baad empirical testing chala kar proof dega.

---

## 7. P1 Deep Dive — Technical Foundation

### 1. PostgreSQL (`postgres`)
- **Short Samajh:** PostgreSQL system ka permanent database hai, jahan future mein incidents, evidence logs aur audit trail store honge.
- **Technical Samajh:** Containerized PostgreSQL 16 (Alpine image) running on port 5432 with dedicated named volume `main_postgres_data`. Built-in Docker healthcheck uses `pg_isready -U aiops_user -d aiops_db` every 5 seconds.
- **Responsibility:** Persistent system of record for operational state.
- **What it currently does:** Starts reliably, accepts incoming TCP socket connections, responds to `SELECT 1` queries from the API container.
- **What it currently does NOT do:** Has no incident tables, no foreign keys, no schema migrations (Alembic), and stores no business data yet.
- **Dependencies:** None (root infrastructure component).
- **Communication:** Reached over `aiops-network` on `postgres:5432` by `aiops-api`.
- **Why it exists separately:** Relational data integrity, ACID compliance, aur persistent audit history ensure karna.
- **Verification performed:** Container status `Up (healthy)`, `pg_isready` output `/var/run/postgresql:5432 - accepting connections`.

### 2. Redis (`redis`)
- **Short Samajh:** Redis ek fast in-memory store hai jo background tasks ke queue aur temporary cache ke liye use hota hai.
- **Technical Samajh:** Containerized Redis 7 (Alpine) running on port 6379 with named volume `main_redis_data`. Healthcheck executes `redis-cli ping` every 5s with 3s timeout.
- **Responsibility:** Task broker for Python RQ (Redis Queue) background execution.
- **What it currently does:** Accepts connection pools, executes PING/PONG, and hosts the `aiops-default` RQ queue registry.
- **What it currently does NOT do:** Does not store persistent operational incidents, does not run pub/sub event ingestion streams yet.
- **Dependencies:** None.
- **Communication:** Reached over `aiops-network` on `redis:6379` by `aiops-worker` and `aiops-api`.
- **Why it exists separately:** PostgreSQL ko transient queue polling se overload hone se bachata hai aur ultra-fast task dispatch deta hai.
- **Verification performed:** Container status `Up (healthy)`, `redis-cli ping` returned `PONG`.

### 3. API (`apps/api`)
- **Short Samajh:** API frontend aur external systems ke liye central HTTP entry point hai.
- **Technical Samajh:** Python 3.12 + FastAPI + Uvicorn server running on container port 8000. Uses Pydantic Settings for typed configuration (`src/config.py`), psycopg2 for PostgreSQL ping checks (`src/database.py`), and exposes structured CORS middleware.
- **Responsibility:** HTTP request handling, readiness orchestration, inter-service coordination.
- **What it currently does:**
  - `GET /` -> Returns service metadata, title, and version `0.1.0`.
  - `GET /health` -> Liveness probe returning `{"status": "ok", "service": "api"}`.
  - `GET /ready` -> Readiness probe testing real PostgreSQL connection via `SELECT 1;`.
  - `GET /api/v1/system-status` -> Aggregates real-time health of both PostgreSQL and Redis.
- **What it currently does NOT do:** Does not receive real GitHub webhooks, has no incident creation logic, no auth/JWT, no business CRUD.
- **Dependencies:** Depends on `postgres` (healthy) and `redis` (healthy).
- **Communication:** Listens on port 8000; calls PostgreSQL (5432) and Redis (6379); callable by Web (Next.js).
- **Why it exists separately:** Decouples external HTTP contracts from heavy background processing.
- **Verification performed:** `GET /health` -> 200 OK; `GET /ready` -> 200 OK (`database.connected: true`); `GET /api/v1/system-status` -> 200 OK (`postgresql.connected: true, redis.connected: true`).

### 4. Background Worker (`apps/worker`)
- **Short Samajh:** Worker background tasks ko bina API ko block kiye run karne ke liye banaya gaya hai.
- **Technical Samajh:** Python 3.12 worker process using `rq` (Redis Queue). Connects to Redis with retry support (`src/worker.py`), registers worker process with PID, and listens on queue `aiops-default` with an integrated scheduler process.
- **Responsibility:** Asynchronous execution of heavy jobs (future log fetching, diagnosis execution, PR dispatch, verification).
- **What it currently does:** Successfully connects to Redis on startup, cleans registries, and actively polls `aiops-default` queue ready to process jobs.
- **What it currently does NOT do:** Does not process real incidents, does not call LLMs, does not interact with Git.
- **Dependencies:** Depends on `redis` (healthy).
- **Communication:** Communicates exclusively with Redis via TCP socket (`redis://redis:6379/0`).
- **Why it exists separately:** Heavy or long-running tasks (e.g. 30-second LLM calls or CI builds) API thread pool ko block na karein.
- **Verification performed:** Process logs: `Successfully connected to Redis at redis://redis:6379/0`, `Worker listening on queues: ['aiops-default']`, `Scheduler for aiops-default started`.

### 5. AI Worker (`apps/ai-worker`)
- **Short Samajh:** AI Worker AI aur RAG diagnosis ke liye dedicated boundary service hai.
- **Technical Samajh:** Python 3.12 + FastAPI HTTP service running on port 8001. Formally imports `langchain` and `langchain_core` to prove container build and dependency resolution readiness.
- **Responsibility:** Future RAG retrieval, prompt assembly, LLM inference, and remediation proposal formatting.
- **What it currently does:**
  - `GET /` -> Returns service status, phase info, and confirms `langchain_status: {available: true, version: "0.2.17"}`.
  - `GET /health` -> Returns `{"status": "ok", "service": "ai-worker", "langchain_available": true}`.
- **What it currently does NOT do:** Does NOT perform RAG, does NOT connect to vector stores (Chroma/FAISS), does NOT call OpenAI/Gemini, does NOT diagnose root causes.
- **Dependencies:** Standalone HTTP service on `aiops-network`.
- **Communication:** Listens on port 8001. Callable by API or Developer Cockpit.
- **Why it exists separately:** AI libraries (LangChain, PyTorch, transformers) bohot heavy hoti hain aur fast-evolving dependencies rakhti hain. Core API ko AI library version conflicts se isolate rakhna zaroori hai.
- **Verification performed:** `GET /health` -> 200 OK (`langchain_available: true`), root endpoint shows LangChain v0.2.17 loaded.

### 6. Developer Cockpit Web (`apps/web`)
- **Short Samajh:** Web Developer Cockpit engineers ke liye operational dashboard hai jahan se system status inspect kiya ja sakta hai.
- **Technical Samajh:** Next.js 14 application using TypeScript, React 18, and App Router (`src/app/page.tsx`). Compiled with `output: "standalone"` in a multi-stage Docker build. Styled with a custom dark glassmorphic Vanilla CSS design system ([`src/app/globals.css`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/apps/web/src/app/globals.css)).
- **Responsibility:** Frontend application shell, real-time subsystem connectivity probe, operational inspection interface.
- **What it currently does:** Boots on port 3000, renders a live Subsystem Health grid that dynamically polls `http://localhost:8000/api/v1/system-status` and `http://localhost:8001/health`, displaying live status badges and architecture mental models.
- **What it currently does NOT do:** Has no incident triage table, no diff review viewer, no approval action buttons (because no real incidents exist).
- **Dependencies:** Depends on `api` (service started).
- **Communication:** Serves HTTP traffic to browser on port 3000; browser-side client fetches API on port 8000 and AI-Worker on port 8001.
- **Why it exists separately:** Complete frontend/backend decoupling; allows frontend team to develop UI against stable API contracts.
- **Verification performed:** Next.js build compiled successfully in Docker, container boots in 137ms, HTTP GET `http://localhost:3000/` returns status code 200 and compiled HTML.

---

## 8. Docker Architecture

### Container Orchestration
Platform ko local reproduction ke liye Docker Compose ke through package kiya gaya hai. Sabhi containers ek isolated bridge network `main_aiops-network` ke andar run hote hain.

```text
+-----------------------------------------------------------------------------------+
|                        CURRENT DOCKER RUNTIME ARCHITECTURE                        |
+-----------------------------------------------------------------------------------+

     [Developer / Browser]
         |          |
         | :3000    | :8000, :8001
         v          v
   +------------+   |
   | aiops-web  |---+
   +------------+
         |
         | (aiops-network)
         v
   +------------+                      +------------------+
   | aiops-api  |                      | aiops-ai-worker  |
   +------------+                      +------------------+
     |        |                          (LangChain 0.2.17)
     |        +--------------+
     | :5432                 | :6379
     v                       v
+----------------+      +----------------+
| aiops-postgres |      |  aiops-redis   |
+----------------+      +----------------+
  (Data Volume)           (Data Volume)
                             ^
                             | :6379
                        +----------------+
                        |  aiops-worker  |
                        +----------------+
                          (RQ Worker on
                          aiops-default)
```

### Network & Environment Configuration
- **Network:** `main_aiops-network` (bridge driver).
- **Volumes:** `main_postgres_data` (`/var/lib/postgresql/data`), `main_redis_data` (`/data`).
- **Health Checks:**
  - Postgres: `pg_isready -U aiops_user -d aiops_db` (interval: 5s, timeout: 5s, retries: 5).
  - Redis: `redis-cli ping` (interval: 5s, timeout: 3s, retries: 5).
- **Startup Ordering (`depends_on`):**
  - `api` waits until `postgres` and `redis` are **healthy**.
  - `worker` waits until `redis` is **healthy**.
  - `web` starts after `api` is started.

---

## 9. Why PostgreSQL?

### "Why This Way?" Explanation
1. **Decision Made:** PostgreSQL 16 ko persistent system of record banaya gaya.
2. **Alternative Considered:** MongoDB, SQLite, ya Redis-only storage.
3. **Why Chosen:** AIOps incidents, remediation actions, aur verification audit trails highly relational hote hain (e.g. 1 Incident has N Evidence items, 1 Diagnosis, 1 RemediationPlan, 1 Approval, 1 ExecutionResult, 1 Verification). Relational schema ACID guarantee aur strong consistency deti hai.
4. **Problem Solved:** Audit log corruption, race conditions in status transitions, aur loose schema inconsistencies.
5. **Tradeoff:** Schema migrations (Alembic) aur strict foreign key management ki zarurat padti hai.
6. **Implemented vs Intent:** Currently only foundation container and connection check implemented (`SELECT 1`). **Abhi domain model/tables P2 ka part hain; isliye PostgreSQL foundation level par available hai, lekin full Incident/Evidence/Remediation model abhi implement nahi hua.**

---

## 10. Why Redis?

### "Why This Way?" Explanation
1. **Decision Made:** Redis 7 ko message broker aur queue engine banaya gaya.
2. **Alternative Considered:** RabbitMQ, Kafka, AWS SQS, ya PostgreSQL table-based queuing (Celery with DB).
3. **Why Chosen:** Lightweight, ultra-fast in-memory operations, zero-fuss local development footprint, and native compatibility with Python RQ.
4. **Problem Solved:** Fast task enqueueing without taxing the relational database with polling queries.
5. **Tradeoff:** Default persistence memory-based hoti hai; long-term durable events ke liye persistent database zaroori hota hai.
6. **Implemented vs Intent:** Currently Redis starts healthy, worker connects, and queue registers. **Redis connectivity exists, lekin incident processing exist nahi karti — dono alag cheezein hain.**

---

## 11. Worker Architecture

### Short Samajh
Worker ek alag Python process hai jo Redis queue se background jobs utha kar run karta hai, taaki main API par koi slow ya blocking kaam na ho.

### Deep Technical Samajh
Worker `apps/worker/src/worker.py` mein defined hai:
- Standard Python `rq.Worker` architecture.
- Connection logic mein built-in retry mechanism hai jo Docker startup race conditions ko handle karta hai (agar Redis startup mein 2 second delay le, worker crash nahi hota, retry karta hai).
- Yeh `aiops-default` queue ko subscribe karta hai.
- Future phases mein worker ka role:
  - P4: Webhook payloads ko normalize karna aur background incident correlation run karna.
  - P5: AI worker ko call karke heavy LLM diagnosis request execute karna.
  - P6: Approved remediation ke liye GitHub API call karke branch aur PR banana.
  - P8: Post-fix verification probes trigger karna.

---

## 12. AI Worker Architecture

### Short Samajh
AI Worker ek alag microservice hai jiska kaam future mein incident logs analyze karna aur fixes suggest karna hoga. Abhi sirf iska server aur LangChain library readiness verify hui hai.

### Deep Technical Samajh
- **Isolation Rationale:** AI frameworks (LangChain, LangSmith, vector database SDKs) bohot fast change hote hain aur heavy binary dependencies (NumPy, PyTorch, tokenizers) le aate hain. Agar inko main API mein daal diya jaye, toh API ka build time, memory footprint aur dependency conflicts escalate ho jate hain.
- **Current Runtime State:** FastAPI application on port 8001 exposing `/` and `/health`. It verifies `import langchain` and reports its version (`0.2.17`).
- **CRITICAL DISTINCTIONS:**
  - **LangChain installed hona ≠ RAG implemented hona.** (Abhi koi vector database, embeddings, ya documents index nahi hue hain).
  - **AI worker running hona ≠ AI diagnosis implemented hona.** (Abhi koi LLM call ya root cause prompt execute nahi hota).

---

## 13. Frontend/Web Foundation

### Short Samajh
Frontend Next.js par bana ek modern web dashboard hai jo abhi sabhi backend services ki real-time health aur architecture status dikhata hai.

### Deep Technical Samajh
- **Tech Stack:** Next.js 14, React 18, TypeScript, custom Vanilla CSS design system.
- **Current State:** Single-page dashboard ([`apps/web/src/app/page.tsx`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/apps/web/src/app/page.tsx)) jo browser-side se `http://localhost:8000/api/v1/system-status` aur `http://localhost:8001/health` ko probe karta hai aur real-time green/red badge show karta hai.
- **CRITICAL BOUNDARY:** **Developer Cockpit ka full incident-management/approval workflow abhi implement nahi hua hai.** Abhi yeh sirf technical foundation aur connectivity proof hai. Real incident triage, diff review, aur approval buttons Phase P7 mein implement honge jab P2/P4 ke contracts aur data available honge.

---

## 14. API / Worker / AI Worker / Web Separation

| Component | Responsibility (What it Owns) | Should NOT Own (Strict Isolation) |
|---|---|---|
| **API (`apps/api`)** | HTTP routing, request validation, authentication, orchestration, readiness checks. | Heavy background processing, direct LLM execution, frontend rendering. |
| **Worker (`apps/worker`)** | Asynchronous task execution, retry loops, long-running jobs, background I/O. | Serving public HTTP requests, managing UI state, defining primary database schemas. |
| **AI Worker (`apps/ai-worker`)** | RAG retrieval, vector search, prompt assembly, LLM inference, remediation proposal generation. | Direct database state mutation, direct GitHub PR execution, human approval decisions. |
| **Web (`apps/web`)** | Operational visualization, Developer Cockpit UI, user interaction, human approval capture. | Direct database access, business logic orchestration, autonomous remediation decisions. |

### Why This Separation?
1. **Modular:** Har subsystem independent technology stack par evolve ho sakta hai.
2. **Maintainable:** Subsystem leads (Taranay, Vivek, Rudra, Saurav) ek doosre ke code ko modify kiye bina kaam kar sakte hain.
3. **Debuggable:** Agar worker fail ho toh API alive rehti hai; agar AI slow ho toh backend down nahi hota.
4. **Scalable:** Heavy LLM load ke time sirf `ai-worker` scale kiya ja sakta hai bina pure system ko duplicate kiye.
5. **Safer for AI Integration:** AI subsystem ko direct database write ya code commit permissions nahi di gayi hain; yeh sirf suggestions return karta hai jo API aur human gatekeeper ke through pass hoti hain.

---

## 15. Current Request / Runtime Flow

### 30-Second Explanation
Jab system start hota hai, Docker Compose sabse pehle PostgreSQL aur Redis containers boot karta hai. Jab unke healthchecks green ho jate hain, API aur Worker start hote hain. API database aur Redis se connect hoti hai, Worker Redis queue ko listen karta hai, AI-Worker LangChain load karke start hota hai, aur Web cockpit live status fetch karke screen par healthy badges dikha deta hai.

### Deep Technical Explanation
1. `docker compose up -d` execute hota hai.
2. Bridge network `main_aiops-network` aur volumes `main_postgres_data`, `main_redis_data` initialize hote hain.
3. `aiops-postgres` container start hota hai; internal daemon `pg_isready` check karta hai. 5 seconds mein healthy mark hota hai.
4. `aiops-redis` container start hota hai; `redis-cli ping` run hota hai aur container healthy mark hota hai.
5. `aiops-worker` start hota hai (depends on redis: healthy); `src/worker.py` Redis connection retry loop execute karta hai, PING success verify karta hai, aur queue `aiops-default` par listen karna start karta hai.
6. `aiops-api` start hota hai (depends on postgres: healthy, redis: healthy); Uvicorn port 8000 par listen karta hai.
7. `aiops-ai-worker` start hota hai; LangChain modules verify karke port 8001 par Uvicorn bind karta hai.
8. `aiops-web` start hota hai; compiled standalone Next.js server port 3000 par bind hota hai.
9. Browser `http://localhost:3000` load karta hai; React `useEffect` hook `http://localhost:8000/api/v1/system-status` par HTTP request bhejta hai. API instantly internal PostgreSQL aur Redis ko ping karke aggregated JSON return karti hai, jo Cockpit screen par visual status update kar deti hai.

---

## 16. Verification and Testing

### Executed Verification Commands & Empirical Results

| Command Executed | What Was This Test Proving? | Result | Proof |
|---|---|---|---|
| `docker compose config` | Compose file syntax, volume mapping, network configuration valid hai ya nahi. | **PASS** | Exit code 0, complete resolved YAML output generated. |
| `docker compose ps` | Sabhi 6 containers continuously running aur healthy hain ya nahi. | **PASS** | 6 containers `Up 5 minutes`, postgres & redis `(healthy)`. |
| `docker exec aiops-postgres pg_isready` | PostgreSQL daemon actually connections accept kar raha hai ya nahi. | **PASS** | `/var/run/postgresql:5432 - accepting connections`. |
| `docker exec aiops-redis redis-cli ping` | Redis server ready hai aur PING par respond kar raha hai ya nahi. | **PASS** | Output `PONG`. |
| `Invoke-RestMethod http://localhost:8000/health` | API web server running hai aur liveness probe succeed ho rahi hai. | **PASS** | HTTP 200: `{"status": "ok", "service": "api", "version": "0.1.0"}`. |
| `Invoke-RestMethod http://localhost:8000/ready` | API successfully PostgreSQL se connection establish karke query run kar pa rahi hai. | **PASS** | HTTP 200: `{"status": "ready", "database": {"connected": true}}`. |
| `Invoke-RestMethod http://localhost:8000/api/v1/system-status` | API both Postgres and Redis dependencies ko concurrently verify kar sakti hai. | **PASS** | HTTP 200: `postgresql.connected: true, redis.connected: true`. |
| `Invoke-RestMethod http://localhost:8001/health` | AI-Worker independently alive hai aur LangChain load ho raha hai. | **PASS** | HTTP 200: `{"status": "ok", "service": "ai-worker", "langchain_available": true}`. |
| `docker compose logs worker` | Background worker process Redis se connect hokar queue par subscribe hua ya nahi. | **PASS** | Log: `Successfully connected to Redis... Listening on aiops-default...`. |
| `Invoke-WebRequest http://localhost:3000/` | Next.js Developer Cockpit production bundle compile hokar HTTP 200 de raha hai. | **PASS** | HTTP 200, HTML body served with Next.js compiled chunks. |
| `pytest test_api_health.py` | API root, health, ready-healthy, ready-unhealthy mock unit test behavior. | **PASS** | 4 passed in 0.66s. |
| `pytest test_ai_worker_health.py` | AI-Worker root and health contract unit tests. | **PASS** | 2 passed in 0.46s. |
| `pytest test_worker_connectivity.py` | Worker Redis connection success and failure exception handling. | **PASS** | 2 passed in 0.39s. |
| `pytest test_domain_agnostic_rules.py` | Core services mein koi e-commerce leak (`order_id`, `cart_id`) toh nahi hua. | **PASS** | 1 passed in 0.01s. |

### Known Limitations / Verification Caveats
1. **Manual Container Test Installation:** Runtime containers (`aiops-api`, `aiops-ai-worker`, `aiops-worker`) lean production images hain jinmein `pytest` pre-installed nahi tha. In-container verification run karne ke liye container ke andar `pip install pytest` execute kiya gaya aur `tests/` directory copy karke run ki gayi. Future CI image builds mein test stage multi-stage Dockerfile mein integrate kiya jana chahiye.
2. **Mocked Database in API Unit Tests:** Unit test file `test_api_health.py` database connection ko mock karti hai; live database connectivity verification live container integration test (`/ready` endpoint probe) ke through prove hui hai.
3. **No Migration Engine Yet:** PostgreSQL mein abhi Alembic ya Flyway configured nahi hai kyunki domain schema P2 mein define hoga.
4. **Placeholder UI:** Developer Cockpit UI abhi sirf container connectivity check karta hai; real incident feeds display nahi karta.

---

## 17. Git State and Commit History

### Commit History
```text
* 6e16c30 (HEAD -> main) chore(governance): establish P0 repository structure, ownership, and collaboration rules
```

### Current Status
- **Committed in P0:** 14 files ([`.editorconfig`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.editorconfig), [`.gitignore`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.gitignore), [`AGENTS.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/AGENTS.md), [`CONTRIBUTING.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/CONTRIBUTING.md), [`.github/CODEOWNERS`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.github/CODEOWNERS), templates, specification markdown files).
- **Currently Untracked (P1 Implementation):**
  - `.env.example`
  - `.github/workflows/`
  - `apps/`
  - `docker-compose.yml`
  - `packages/`
  - `tests/`
  - `PROJECT_KNOWLEDGE_TRANSFER.md`
- **Rule Followed:** User ne specifically instruct kiya hai ki jab tak explicit permission na mile, P1 files ko commit na kiya jaye. Isliye P1 files currently untracked aur verified state mein chhod di gayi hain.

---

## 18. Security and Secrets

### Secrets Policy
- **Gitignore Protection:** Local file [`.env`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.env) strictly `.gitignore` mein included hai. `git check-ignore .env` command run karke verify kiya gaya hai ki Git isko ignore kar raha hai.
- **No Hardcoded Credentials:** Codebase mein koi API keys (OpenAI keys, GitHub personal access tokens, AWS keys) ya production passwords hardcoded nahi hain.
- **[`.env.example`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.env.example):** Template file mein sirf generic local development credentials (`aiops_user`, `aiops_password`, `aiops_db`) hain.
- **Important Distinction:** Local development configuration standard dev environment ke liye safe hai, lekin yeh production-grade secret management (e.g. HashiCorp Vault, AWS Secrets Manager, GitHub Encrypted Secrets) nahi hai. Production secrets management Phase P9/P10 mein aayega.

---

## 19. Domain-Agnostic Architecture

### The Core Principle
Platform ka naam hai:
```text
Domain-Agnostic AIOps Self-Healing Platform: E-Commerce Reference Implementation
```
Iska matlab e-commerce platform ka universal definition **nahi** hai. E-commerce sirf pehla evaluation environment aur reference adapter hai.

```text
+-----------------------------------------------------------------------------------+
|                        CORE VS ADAPTER BOUNDARY MODEL                             |
+-----------------------------------------------------------------------------------+

     +---------------------------------------------------------------+
     |                  DOMAIN-AGNOSTIC AIOPS CORE                   |
     |                                                               |
     |  • Pipeline                 • PipelineRun                     |
     |  • Service                  • Deployment                      |
     |  • Environment              • Event                           |
     |  • Incident                 • Evidence                        |
     |  • Diagnosis / RootCause    • RemediationPlan                 |
     |  • RemediationAction        • Approval                        |
     |  • Change / ExecutionResult • Verification                    |
     +---------------------------------------------------------------+
                                    |
                                    v
                     [ PLUGGABLE ADAPTER BOUNDARY ]
                                    |
          +-------------------------+-------------------------+
          |                                                   |
          v                                                   v
+-------------------------------+           +-------------------------------+
|     E-COMMERCE ADAPTER        |           |        FUTURE ADAPTERS        |
|  (First Reference MVP)        |           |    (FinTech, Healthcare, etc.)|
|                               |           |                               |
| • E-com telemetry mapping     |           | • Banking txn failure mapping |
| • Orders/Cart knowledge base  |           | • HIPAA audit logging         |
| • Store checkout test suite   |           | • Custom legacy orchestrator  |
| • GitHub PR patch executor    |           | • Ansible / Terraform executor|
+-------------------------------+           +-------------------------------+
```

### Architectural Non-Negotiables
- `order_id`, `payment_status`, `cart_id`, `inventory_count` jaise concepts generic core models (`Incident`, `Evidence`, `Diagnosis`, `RemediationAction`) mein bilkul nahi ghusne chahiye.
- Generic core sirf generic operational entities samajhta hai: e.g. "Service `payment-gateway` in Environment `production` failed during Deployment `v2.1.0` with Evidence `HTTP 500 in logs`."
- E-commerce specific details hamesha adapter payload ya generic metadata dictionary ke andar isolate rahenge.

---

## 20. RAG Boundary — Future Architecture

### What RAG Will Eventually Do (Phase P5)
1. Operational event aane par AI system raw stacktrace aur service logs gather karega.
2. RAG pipeline past resolved incidents, architecture docs, codebase repositories, aur operational runbooks ko vector database se retrieve karegi.
3. LLM retrieved context aur current evidence ko combine karke probable root cause diagnose karega (e.g., "Missing environment variable `DATABASE_SSL` after deployment commit `abc1234`").
4. AI remediation plan propose karega.

### Critical Safety Rules
- **Evidence-Grounded:** AI output hawa mein hallucinated nahi hona chahiye; har diagnosis ke sath supporting evidence reference linked hoga.
- **RAG Does NOT Execute:** AI RAG subsystem kabhi bhi directly production database par query nahi chalayega aur na hi direct code commit karega. AI sirf propose karta hai.
- **CURRENT STATUS:** **RAG abhi implemented nahi hai.** AI worker foundation exists, but diagnosis and RAG belong strictly to Phase P5.

---

## 21. Human Approval Boundary

### Bounded Autonomy Principle
Platform literature review aur SRE safety best practices par based hai: **Autonomous interventions must be governed.**

```text
AI Proposes Fix  -->  Human Reviews in Cockpit  -->  Human Approves  -->  System Executes  -->  System Verifies
```

### Non-Negotiables
- AI kitna bhi confident ho (e.g. 99% confidence score), consequential production changes (code patch, git commit, database migration, traffic rerouting) bina explicit human approval ke execute nahi honge.
- Approval implicit nahi hogi (engineer ke incident dekh lene se approval nahi maani jayegi; explicit `APPROVE` action record hoga).
- **Execution != Resolution:** PR merge hona ya script run hona resolution nahi hai. System explicitly target service ko re-verify karega (Phase P6/P8).

---

## 22. What We Deliberately DID NOT Build Yet

Taki koi future AI assistant ya developer confuse na ho, yeh list explicitly confirm karti hai ki kya deliberately chhod diya gaya hai:

| Component / Capability | Status | Target Phase | Reason for Exclusion |
|---|---|---|---|
| **Incident Domain Models** | NOT IMPLEMENTED | **P2** | Shared contracts freeze hone se pehle model banana contract drift create karega. |
| **Evidence Schema** | NOT IMPLEMENTED | **P2** | Schema agreement across all 4 leads is required first. |
| **Database Migrations / Tables** | NOT IMPLEMENTED | **P2** | Persistent models P2 contracts ke baad hi table structure lenge. |
| **Event Webhook Ingestion** | NOT IMPLEMENTED | **P4** | Pipeline events ingest karne se pehle data models freeze hone chahiye. |
| **Vector Database (Chroma / FAISS)** | NOT IMPLEMENTED | **P5** | Foundation phase mein vector DB add karna premature complexity thi. |
| **RAG Embeddings & Retrieval** | NOT IMPLEMENTED | **P5** | Incident data aur evidence collection ke bina RAG useless hai. |
| **Root Cause Diagnosis Engine** | NOT IMPLEMENTED | **P5** | Business logic boundary; strictly belongs to Rudra in P5. |
| **Remediation Plan Generator** | NOT IMPLEMENTED | **P6** | Diagnosis verification ke bina remediation plan nahi ban sakta. |
| **GitHub Automation (PyGithub)** | NOT IMPLEMENTED | **P6** | Automatic PR creation P6 ka core scope hai. |
| **Automated Patch Execution** | NOT IMPLEMENTED | **P6** | Requires human approval workflow to be ready first. |
| **Full Developer Cockpit Triage** | NOT IMPLEMENTED | **P7** | Cockpit ko display karne ke liye real incident stream chahiye jo P4/P5 mein banegi. |
| **End-to-End Self-Healing Loop** | NOT IMPLEMENTED | **P8** | Sabhi independent components P3–P7 mein banne ke baad hi integrate honge. |

---

## 23. Why We Stopped Before P2

### "Why This Way?" Explanation
1. **Decision Made:** P1 foundation verify hote hi implementation ko freeze karke knowledge-transfer checkpoint banaya gaya.
2. **Alternative Considered:** Seedhe P2 ke Pydantic schemas aur SQL models likhna shuru kar dena.
3. **Why Chosen:** **P2 mein actual domain and shared contracts freeze honge, isliye bina P0/P1 ko samjhe P2 start karna future integration conflicts create kar sakta hai.**
4. **Problem Solved:** 4 leads (AI, DevOps, Backend, Frontend) ke beech incompatible entity definitions banana.
5. **Tradeoff:** Short pause in coding velocity.
6. **Implemented vs Intent:** Freeze implemented; P2 starts only upon formal human approval.

---

## 24. P2 Preview — What Will Happen Next

> **NEXT PHASE — NOT IMPLEMENTED YET**

Phase P2 (**Contract & Domain Foundation**) mein project-wide shared contracts freeze honge:
1. **Generic Domain Schemas (`packages/contracts`):**
   - `Pipeline`, `PipelineRun`
   - `Service`, `Deployment`, `Environment`
   - `Event`
   - `Incident`
   - `Evidence`
   - `Diagnosis`, `RootCause`
   - `RemediationPlan`, `RemediationAction`
   - `Approval`
   - `Change`, `ExecutionResult`
   - `Verification`
2. **Database Schema:**
   - PostgreSQL table definitions and foreign keys.
   - Alembic migration setup in `apps/api`.
3. **API & Event Contracts:**
   - OpenAPI specifications and shared Pydantic v2 schemas.
4. **Adapter Boundary Definition:**
   - E-commerce reference adapter mapping interfaces.

---

## 25. Team Ownership

| Lead | Subsystem Scope | Primary Deliverable | Shared Contract Role |
|---|---|---|---|
| **Rudra** | AI / RAG Lead (`apps/ai-worker`) | RAG pipeline, LLM integration, diagnosis generation, remediation proposals. | Diagnosis & Evidence schemas review. |
| **Saurav** | DevOps Lead (`infrastructure/`, `.github/`) | Containerization, Docker Compose, CI/CD pipelines, staging & deployment. | Deployment, PipelineRun & Environment schemas review. |
| **Taranay** | Backend Lead (`apps/api`, `apps/worker`) | API endpoints, RQ worker, PostgreSQL schema, shared contracts. | Primary author/custodian of shared database and event schemas. |
| **Vivek** | Frontend Lead (`apps/web`) | Developer Cockpit, incident visualization, approval UX flow. | Incident, Approval, and Cockpit API contract consumer. |

---

## 26. How AI IDE / Antigravity Is Being Used

Platform development mein AI IDE (Antigravity) ko strict engineering discipline ke sath operate karne ke liye configure kiya gaya hai:
- **Inspect Before Modifying:** Har action se pehle actual filesystem check kiya jata hai.
- **Phase Boundary Enforcement:** AI autonomous hoke aage ke phases (P5 RAG, P6 GitHub PRs) ko prematurely generate nahi kar sakta.
- **Shared Contracts Inviolable:** AI independently schemas rewrite nahi kar sakta.
- **Empirical Proof Mandatory:** AI tab tak task complete nahi bol sakta jab tak tests, logs, aur container healthchecks run karke empirical output na dikha de.
- **No Hallucinated Claims:** Documentation mein likhe target ko implementation state nahi mana jata.

---

## 27. Current Architecture — One-Page Mental Model

```text
+-----------------------------------------------------------------------------------+
|                     ONE-PAGE MENTAL MODEL (THE HOUSE ANALOGY)                     |
+-----------------------------------------------------------------------------------+

  Abhi system ko ek naye ban rahe ghar ki foundation samjho:

  [P0: House Rules & Blueprint]  Plot ke boundaries define ho gaye, owners assign ho gaye,
                                 aur building code (rules) sign ho gaye.
                                 (STATUS: COMPLETE)

  [P1: Foundation & Utilities]   Zameen khud gayi, concrete foundation dal gayi, water pipe
                                 (PostgreSQL), electricity grid (Redis), main doors (API),
                                 utility room (Worker), workshop (AI Worker), aur front
                                 porch (Web) lag chuke hain aur light/paani chalu hai.
                                 (STATUS: COMPLETE)

  [P2: Architectural Contract]   Next step: Har kamre ka exact measurement aur interior
                                 standard (Shared Domain Schemas) freeze karna.
                                 (STATUS: NEXT)

  [P3 to P12: Furnishing & Living] Deewarein khadi karna, AI furniture lagana, automation
                                   doors lagana, aur rehna shuru karna.
                                   (STATUS: FUTURE)
```

---

## 28. Technical Mental Model

Backend engineer ke point of view se architecture:
```text
  [Repository]               Git on `main` + .gitignore + CODEOWNERS + CONTRIBUTING
       |
  [Orchestration]            docker-compose.yml defines 6 containers on bridge network
       |
  [Web Shell]                Next.js 14 (:3000) standalone container serving cockpit foundation
       |
  [API Gateway]              FastAPI (:8000) checking DB connectivity and exposing health probes
       |
  +----+----+
  |         |
  v         v
[PostgreSQL] [Redis Broker] (:6379)
(:5432)            ^
                   |
             [RQ Worker] listening on queue `aiops-default`
                   ^
                   | (Future internal RPC/HTTP)
             [AI Worker] (:8001) FastAPI service isolating LangChain dependencies
```

---

## 29. Glossary

1. **AIOps**
   - *Simple Meaning:* IT aur software operations ko Artificial Intelligence aur automation ke through manage karna.
   - *Technical Meaning:* Applying machine learning, natural language processing, and automated event correlation to telemetry and log data to enhance SRE operations.
2. **Self-Healing**
   - *Simple Meaning:* System mein kharabi aane par bina human ke manual code likhe system ka khud ko fix kar lena.
   - *Technical Meaning:* Automated detection, diagnosis, remediation proposal, governed execution, and verification cycle that restores an unhealthy service to healthy state.
3. **Adapter**
   - *Simple Meaning:* Ek translator jo kisi specific domain ki language ko platform ki common language mein convert karta hai.
   - *Technical Meaning:* A design pattern boundary isolating domain-specific telemetry normalization, knowledge sources, and execution tooling from the generic platform core.
4. **Domain-Agnostic**
   - *Simple Meaning:* Aisa software jise farq nahi padta ki woh e-commerce ke liye chal raha hai, banking ke liye, ya healthcare ke liye.
   - *Technical Meaning:* Architectural decoupling where core entities reason exclusively over operational primitives (`Incident`, `Evidence`, `Verification`) without hardcoding business attributes.
5. **Event**
   - *Simple Meaning:* System mein hone wali koi bhi activity (jaise build fail hona ya pod restart hona).
   - *Technical Meaning:* A point-in-time immutable record emitted by an external system representing operational state change.
6. **Incident**
   - *Simple Meaning:* Ek aisi serious problem jisko fix karna zaroori hai.
   - *Technical Meaning:* An aggregated, correlated, and deduplicated operational degradation requiring active diagnostic and remediation lifecycle management.
7. **Evidence**
   - *Simple Meaning:* Saboot (jaise error logs ya stacktrace) jo problem ko prove karta hai.
   - *Technical Meaning:* Collected contextual artifacts (log extracts, diffs, configuration dumps, metrics) linked to an incident to ground AI diagnosis.
8. **Diagnosis**
   - *Simple Meaning:* Doctor ki report ki tarah issue ka actual root cause batana.
   - *Technical Meaning:* The probable root cause explanation and confidence score produced by reasoning over collected evidence and retrieved runbook knowledge.
9. **RAG (Retrieval-Augmented Generation)**
   - *Simple Meaning:* AI ko generic jawab dene ke bajaye repo ke actual documents aur logs padha kar jawab nikalwana.
   - *Technical Meaning:* A technique combining information retrieval from a vector database (runbooks, codebase) with LLM generation to produce grounded, non-hallucinated explanations.
10. **Remediation**
    - *Simple Meaning:* Problem ko theek karne ke liye uthaya gaya step ya code fix.
    - *Technical Meaning:* An actionable plan (patch, configuration rollback, restart) formulated to restore system health.
11. **Verification**
    - *Simple Meaning:* Fix lagane ke baad double check karna ki issue sach mein theek hua ya nahi.
    - *Technical Meaning:* Post-execution automated testing and metric observation confirming that system metrics have returned to healthy thresholds before incident resolution.
12. **Human Approval**
    - *Simple Meaning:* AI ke banaye plan par engineer ka 'Yes' bolna.
    - *Technical Meaning:* A mandatory governance checkpoint where a human operator reviews and explicitly signs off on a proposed change before consequential execution.
13. **Worker**
    - *Simple Meaning:* Background mein chupchap mehnat karne wala process.
    - *Technical Meaning:* An asynchronous execution daemon that polls queues for distributed job execution outside the HTTP request/response cycle.
14. **Queue**
    - *Simple Meaning:* Line jismein tasks khade rehte hain jab tak unki baari na aaye.
    - *Technical Meaning:* A FIFO data structure managed by a message broker holding serialized tasks for asynchronous worker consumption.
15. **Redis**
    - *Simple Meaning:* Super-fast memory store jo queue manage karne ke kaam aata hai.
    - *Technical Meaning:* An open-source, in-memory key-value data structure store used as a message broker and cache.
16. **PostgreSQL**
    - *Simple Meaning:* Bharosemand database jahan important data permanently save hota hai.
    - *Technical Meaning:* An enterprise-grade, ACID-compliant relational database management system serving as the persistent system of record.
17. **FastAPI**
    - *Simple Meaning:* Modern aur super-fast Python framework jisse APIs banayi jaati hain.
    - *Technical Meaning:* A high-performance, asynchronous web framework for building APIs with Python 3.8+ based on standard Python type hints and Pydantic.
18. **Next.js**
    - *Simple Meaning:* React ka powerful framework jisse modern websites aur dashboards banaye jaate hain.
    - *Technical Meaning:* A production React framework providing server-side rendering, static site generation, standalone deployment, and optimized routing.
19. **LangChain**
    - *Simple Meaning:* AI models aur documents ko aapas mein connect karne wali toolkit.
    - *Technical Meaning:* An open-source orchestration framework for building applications powered by large language models via composable chains and agents.
20. **Docker**
    - *Simple Meaning:* Software ko ek dabbe (container) mein pack karna taaki har computer par ek jaisa chale.
    - *Technical Meaning:* An OS-level virtualization platform that packages an application and its dependencies into standardized containers.
21. **Docker Compose**
    - *Simple Meaning:* Ek sath 5-6 containers ko ek file se chalane ka remote control.
    - *Technical Meaning:* A tool for defining and running multi-container Docker applications via declarative YAML configurations.
22. **Contract**
    - *Simple Meaning:* Services ke beech ka pakka agreement ki data kis format mein aayega aur jayega.
    - *Technical Meaning:* A formalized, machine-readable schema definition (OpenAPI, Pydantic, JSON Schema) defining interaction rules between producers and consumers.
23. **API Schema**
    - *Simple Meaning:* Request aur response ka structure ya format.
    - *Technical Meaning:* A strict data validation model specifying field names, data types, constraints, and validation rules for HTTP payloads.
24. **Health Check / Readiness Check**
    - *Simple Meaning:* Doctor ka checkup ki container zinda hai ya nahi aur kaam karne ke liye ready hai ya nahi.
    - *Technical Meaning:* Container runtime probes (`/health` for liveness, `/ready` for upstream/downstream dependency verification).

---

## 30. Final Current-State Summary

### CURRENTLY COMPLETE
- **Phase P0 (Governance & Repository Bootstrap):** **PASS / VERIFIED.**
  - Git repository on `main` initialized and committed.
  - Ownership ([`.github/CODEOWNERS`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/.github/CODEOWNERS)) mapped across Rudra, Saurav, Taranay, Vivek.
  - Contribution guidelines ([`CONTRIBUTING.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/CONTRIBUTING.md)), PR templates, and Issue templates active.
  - AI Assistant directives ([`AGENTS.md`](file:///c:/Users/DELL/Desktop/Minors/DomainAgnostic/main/AGENTS.md)) binding and active.
  - All 6 root specification docs preserved without contradiction.
- **Phase P1 (Technical Foundation):** **PASS / VERIFIED.**
  - Docker Compose orchestrates 6 containers: `postgres`, `redis`, `api`, `worker`, `ai-worker`, `web`.
  - All 6 containers live, healthy, and communicating over `main_aiops-network`.
  - Database connectivity verified via `/ready`.
  - RQ background worker connected to Redis on queue `aiops-default`.
  - AI Worker running independently with LangChain v0.2.17 verified.
  - Developer Cockpit frontend running on Next.js 14 serving live status.
  - 9/9 foundation unit tests pass.

### CURRENTLY NOT IMPLEMENTED
- No Incident/Evidence/Diagnosis/Remediation domain models.
- No database tables or migrations.
- No real event ingestion or webhook handlers.
- No RAG pipelines, vector databases, or embeddings.
- No AI diagnosis prompts or LLM integrations.
- No GitHub automation or PR creation code.
- No automated patch execution.
- No interactive incident management triage in Cockpit.

### NEXT PHASE
- **Phase P2 (Contract & Domain Foundation):** Defining shared schemas in `packages/contracts` and database models before any component logic is built.

### IMPORTANT RULE
> **"Documentation mein jo likha hai usko implementation ka proof mat samjho; actual repository state ko source of truth samjho."**
