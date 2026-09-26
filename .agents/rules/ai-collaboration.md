# AI Collaboration Rules

All AI assistants must adhere to the rules defined in `AGENTS.md` and `Rules.md`:
1. Inspect actual file state before proposing or writing code.
2. Respect the four-member ownership model:
   - Rudra: AI/RAG Lead (`apps/ai-worker`)
   - Saurav: DevOps Lead (`infrastructure/`, `.github/workflows/`)
   - Taranay: Backend Lead (`apps/api/`, `apps/worker/`, `infrastructure/db/`)
   - Vivek: Frontend Lead (`apps/web/`)
3. Adhere to phase boundaries (P0 -> P1 -> P2 ...).
4. Enforce domain-agnostic core separation from e-commerce reference adapters.
5. Verify changes with automated tests and health checks before marking done.
