# Next Steps Queue

**Usage instructions**
- Read this file before starting work. It lists the only active tasks.
- After identifying your task, review every documentation area referenced (context, research, decisions, etc.) so you work with current information.
- Execute the task, then immediately update this file: edit the description/status or remove the entry once finished.
- Treat this list as ephemeral—store only the tasks currently being worked on; completed items belong in `docs/worklog` or `docs/actions/README.md` archives.

1. **Implement whisper.cpp provider & abstraction** — Wire up whisper.cpp in Codespaces, expose `provider` request field, and document how additional providers will plug in.
2. **Map clipboard workflows per OS** — Capture exact APIs/permissions and automation hooks for Android, iOS/iPadOS, macOS, Windows, and Steam Deck (clients paste the backend text block).
3. **Outline Android MVP client** — Specify recording pipeline, mode selection UX, and clipboard write path.
4. **Establish QA/test strategy** — Determine regression tests for transcription accuracy and clipboard delivery, including automation hooks.
5. **Optimize GitHub Codespaces workflow** — Research and document:
   - How to SSH into a running Codespace reliably (including auth and setup).
   - How to define automatic port forwarding/exposure for backend services.
   - How to auto-start the backend service on Codespace creation (e.g. via `devcontainer.json`, `postCreateCommand`, or `postStartCommand`).
   Capture findings in `docs/research/codespaces-workflow.md` and propose any required repo config changes in `docs/decisions` if behavior becomes opinionated.

Feel free to edit, reorder, or expand this list as priorities evolve.
