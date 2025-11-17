# AGENTS

Guidance for any human or AI collaborators contributing to the multimodal transcription+clipboard project.

## Mission
Deliver low-latency audio capture and transcription with mode-aware filtering (terminal, code, creative writing) and instant clipboard delivery across Android, iPad/iOS, macOS, Windows, and Steam Deck.

## Repository Conventions
- **Monorepo structure**: This repo is a monorepo with multiple project folders (backend, clients, docs, automation, etc.). Always identify which project area you’re touching and keep changes scoped to a small, coherent slice.
- **Shared tmux usage**: When checking what work is currently in-flight on a Codespace or dev container, first inspect active `tmux` sessions. Run long‑running tasks (servers, experiments, watches) inside `tmux` so others can attach, observe logs, and reuse existing processes instead of starting competing ones.

## Core Roles
1. **Research & Strategy Agent** — Tracks device priorities, surveys APIs, validates feasibility, keeps `docs/research` current.
2. **Backend & ML Agent** — Designs the Codespaces-hosted transcription API, manages model/runtime choices, documents interfaces in `docs/architecture`.
3. **Client Integration Agents** — One per OS family; build lightweight record → send → clipboard flows and keep onboarding notes per platform.
4. **Documentation Steward** — Maintains the hub (`docs/`), ensures ADRs and worklogs stay accurate, and curates onboarding material.
5. **Automation & QA Agent** — Crafts test plans, regression scripts, and CI steps to validate transcription accuracy and clipboard delivery.

## Documentation Areas
- **`docs/context`** — Consume before any planning or implementation to stay aligned with user goals, device priority order, and assumptions. Update whenever scope, personas, or constraints shift.
- **`docs/research`** — Review ahead of proposing tooling or platform decisions. Add structured findings (template in README) with citations whenever you complete a spike or comparative study.
- **`docs/decisions`** — Scan for relevant ADRs prior to architecture/design work. Log every irreversible or high-impact decision using the ADR template; mark superseded items clearly.
- **`docs/actions`** — Daily working queue. Consult it to pull work, and append/edit entries as tasks are added, progressed, or completed. Tie each action to related context/research/decisions.
- **`docs/worklog`** — Read latest entries for situational awareness before standups or handoffs. Contribute concise daily notes capturing progress, blockers, and links to artefacts.
- **`docs/architecture`** — Reference diagrams and backend/client contracts during implementation. Update whenever APIs, sequencing, or infrastructure plans evolve.
- **`docs/onboarding`** — New collaborators start here; seasoned contributors update it whenever tooling, setup steps, or collaboration rules change to keep ramp-up under 15 minutes.
- **`docs/README.md`** — Entry point linking all sections; ensure new documents are referenced here for discoverability.

## Service Management (Codex Plugin)
- `scripts/service_manager.py` is the single orchestrator for backend lifecycle checks. Always run `python scripts/service_manager.py status` before backend-dependent work to confirm PID, tmux session, and public URL hint.
- Long-lived processes run inside the shared tmux session `backend_service`. Use `python scripts/service_manager.py attach` (or `tmux -S .run/tmux/backend_service.sock attach -t backend_service`) to inspect output. Never spawn duplicate uvicorns outside tmux.
- Control commands: `start`, `ensure`, `stop`, `restart`, and `logs`. Shell wrappers (`scripts/start_backend.sh`, `scripts/stop_backend.sh`) delegate to these.
- If the service is running but unreachable externally, mark Codespaces port 8000 as **Public** (Ports panel or `gh codespace ports visibility -c $CODESPACE_NAME 8000:public` after `gh auth login`).
- Capture restarts/failures in `docs/worklog` so others know what changed.

## Operating Principles
- **Source of Truth** lives in this repo; reflect important conversations in ADRs or worklogs.
- **Decision Hygiene**: capture rationale before coding; link ADR IDs in PR titles.
- **Small PRs, Clear Ownership**: each change identifies responsible agent + reviewer.
- **Device-first Thinking**: prioritize Android → iPad → Mac → Windows → Steam Deck unless INIT.md changes.
- **Clipboard Integrity**: every feature must describe how output lands in clipboard with minimal user interaction.

## Workflow
1. Start every session by reading `docs/actions/next-steps.md` to select an active task, then review all referenced documentation areas (`INIT.md`, `docs/context`, relevant research/decisions) before acting.
2. Propose plan in PR/issue, cite related research.
3. Keep task status updated in `docs/actions` and immediately edit/remove entries in `docs/actions/next-steps.md` once tasks are completed or re-scoped (no completed tasks should remain there).
4. Document unexpected findings in `docs/worklog` with date + owner.
5. When delivering code, update onboarding or architecture docs if behavior changes.

## Escalation
- Record blockers that require strategic input in `docs/decisions` (status: Proposed) and notify maintainers.
- Security or privacy issues escalate immediately through repo discussions and are logged in worklog + actions.

Following this guide keeps multi-agent collaboration predictable and searchable.
