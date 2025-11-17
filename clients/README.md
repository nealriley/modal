# Client Integrations

Lightweight apps/automations for each priority platform. Each subdirectory will hold platform-specific code, setup notes, and test plans.

## Subdirectories
- `android/` — Kotlin app or Jetpack Compose service with microphone + clipboard permissions.
- `ios/` — Shortcut or SwiftUI utility for iPad/iPhone capture and clipboard updates.
- `macos/` — Menu bar utility with global hotkey, microphone capture, and NSPasteboard writes.
- `windows/` — Tray app (WinUI/.NET) with audio capture + clipboard API usage.
- `steamdeck/` — Linux client (Qt/PySide) tuned for SteamOS controls.

Each client should reference shared API contracts from `backend/` and document unique constraints inside `docs/context` or `docs/research` as needed.
