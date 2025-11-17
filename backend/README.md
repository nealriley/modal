# Backend Service (Placeholder)

This folder will contain the transcription + mode-aware formatting service that runs in GitHub Codespaces. Upcoming deliverables:

1. **API Contract** — HTTP endpoint for uploading audio and specifying extraction mode.
2. **Transcription Engine** — OpenAI Whisper API or self-hosted model, configurable per ADR.
3. **Post-processing** — Mode-specific filters for terminal commands, code, and creative text.
4. **Clipboard Delivery Hooks** — Response schema optimized for client clipboard writers.
5. **Testing & Monitoring** — Latency metrics, regression tests, and observability hooks.

Document implementation details in `docs/architecture/backend.md` once coding begins.
