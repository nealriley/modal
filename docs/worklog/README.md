# Worklog

Chronological record of what happened, when, and by whom. Each entry should contain:

```
## 2025-01-01
- Summary of progress
- Links to PRs / issues / documents
- Blockers or decisions needed
```

Encourage short daily notes to make onboarding and retrospectives easier.

## 2025-11-17
- Drafted backend API contract covering endpoints, auth, request/response schema, and error handling (`docs/architecture/backend.md`).
- Updated `docs/actions/next-steps.md` to remove the completed API contract task per AGENTS workflow.
- Captured decisions to default to whisper.cpp, keep provider abstraction, drop streaming/redaction, and clarified clipboard responsibilities in backend design. Updated next steps to focus on implementation work.
- Implemented FastAPI backend scaffold with provider registry, whisper.cpp integration points, and formatting logic. Added pytest suite covering provider overrides, terminal formatting, and health checks.
- Documented clipboard workflows per OS (`docs/research/clipboard-workflows.md`) and trimmed the next-steps queue accordingly.
- Built Codex Service Manager (`scripts/service_manager.py`) plus devcontainer automation to keep whisper.cpp + backend in sync, and documented the workflow in `docs/research/codespaces-workflow.md`/`AGENTS.md`.
- Reworked service manager to run exclusively via a shared tmux session (`backend_service`), updated AGENTS/backend docs with the new workflow, and verified pytest + tmux startup behavior.
- Added devcontainer automation plus helper scripts to build whisper.cpp, start/stop the backend, and ignore generated artifacts. Authored Codespaces workflow doc detailing SSH access, port exposure, and testing instructions; provided curl example for Android CLI usage.
