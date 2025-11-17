# Multiplatform Audio-to-Clipboard Workspace

This repository hosts planning, documentation, and future code for a service that turns short audio snippets into tightly scoped text (terminal commands, code, or creative writing) and ships the result straight into each device's clipboard.

## Repository Structure

```
.
├── backend/           # Codespaces-hosted API + transcription pipeline
├── clients/           # Device-specific integrations (Android, iOS/iPadOS, macOS, Windows, Steam Deck)
├── docs/              # Documentation hub (decisions, actions, context, research, onboarding, worklog, architecture)
├── AGENTS.md          # Collaboration contract for human + AI agents
├── INIT.md            # Original user goals and constraints
└── README.md          # You are here
```

Start in [`docs/README.md`](docs/README.md) to find decisions, research, and onboarding resources, then drill into `backend/` or `clients/` as implementation begins.
