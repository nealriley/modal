# Backend API Contract

Central HTTP+JSON interface for converting short audio clips into constrained text blocks and delivering clipboard-ready payloads. Designed for GitHub Codespaces hosting but deployable elsewhere.

## Guiding Goals
- **Low-latency synchronous flow** for <60s recordings, with optional async polling for longer jobs.
- **Mode-aware formatting** so clients can request `terminal`, `code`, or `creative` outputs.
- **Simple auth** (Bearer tokens for now) until we introduce per-device credentials.
- **Structured clipboard-ready text** — backend returns a single text block per request; clients own clipboard interactions.
- **Pluggable transcription engines** with whisper.cpp running locally in Codespaces as the default provider.

## Non-goals (for now)
- Streaming/WebSocket transcription; all requests are batch uploads with optional async polling.
- Transcript redaction or selective masking; clients receive full text output.

## Authentication
- All protected endpoints require `Authorization: Bearer <token>`.
- Tokens managed via repo secrets and distributed to clients through secure channels (document in onboarding when ready).
- Unauthenticated requests return `401` with error payload below.

## Content Types
- Primary upload uses `multipart/form-data` with fields:
  - `audio` (required): binary audio file (`audio/wav`, `audio/mpeg`, `audio/webm`, `audio/ogg`).
  - `mode` (required): `terminal | code | creative`.
  - `language` (optional): BCP-47 tag to hint transcription model.
  - `device_id` (optional): stable identifier for logging/routing.
  - `client_version` (optional): semantic version string for compatibility checks.
- Alternative JSON body with `audio_url` (pre-signed storage) is allowed for async workflows.

## Transcription Engines
- **Default**: whisper.cpp compiled in the Codespace container, using GPU acceleration when available.
- **Provider abstraction**: backend accepts optional `provider` field (`whisper_cpp` default). Future providers (OpenAI, AssemblyAI, etc.) can be registered behind a common interface.
- **Switching providers**: if `provider` present in the request and allowed for the token, the backend routes audio to that engine without changing API responses.
- **Extensibility hooks**: add `X-Transcription-Provider` header in responses for observability; document constraints/flags per provider in `docs/research`.

## Endpoints

### `POST /v1/transcriptions`
Create a transcription job. Automatically runs synchronously if estimated duration < 60s, else returns `202 Accepted` with `status=pending`.

**Request:**
- Headers: `Authorization`, `Content-Type` (`multipart/form-data` or `application/json`).
- Body fields as noted above.

**Synchronous Response (200 OK):**
```json
{
  "id": "job_123",
  "status": "completed",
  "mode": "terminal",
  "duration_s": 17.3,
  "clipboard": {
    "text": "git clone https://...\ncd repo",
    "language_hint": "shell",
    "metadata": {
      "cursor": null,
      "line_endings": "unix"
    }
  },
  "raw_transcript": "Open Terminal and type git clone ...",
  "confidence": 0.92,
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Async Response (202 Accepted):**
```json
{
  "id": "job_124",
  "status": "pending",
  "mode": "creative",
  "poll_after_s": 5
}
```

### `GET /v1/transcriptions/{id}`
Retrieve job state or final payload.

**Response (200):** same schema as synchronous response plus `status` values `pending|processing|completed|failed`.

### `POST /v1/transcriptions/{id}/cancel`
Allow clients to stop queued jobs.
- Returns `200` with `status="canceled"` or `409` if already finalized.

### `GET /healthz`
Unauthenticated liveness probe returning `200` and `{ "status": "ok", "uptime_s": 12345 }`.

## Modes & Formatting Rules
| Mode | Description | Clipboard expectations |
| ---- | ----------- | ---------------------- |
| `terminal` | Extract shell/CLI commands only, each on its own line. Remove narration/filler. | Backend returns newline-delimited commands as plain text; clients copy verbatim. |
| `code` | Preserve indentation and language tokens. Detect language when possible. | Return formatted snippet with optional `language_hint` for syntax-highlighting clients. |
| `creative` | Deliver cleaned prose with sentence casing and punctuation. | Return paragraph text separated by blank lines. |

Backend responsibility ends at returning the `clipboard.text` block; each client must handle writing to its OS clipboard.

### `POST /v1/translate`
Text-to-text endpoint that skips Whisper entirely. It hands the provided prompt to the Codex provider (non-interactive CLI) and returns a clipboard-ready snippet. Primary use case: instant CLI command generation without an audio recording.

**Request**
- Content-Type: `application/json`
- Body:
  ```json
  {
    "prompt": "list files then check git status",
    "mode": "terminal",
    "provider": "codex"
  }
  ```
  - `prompt` (required): free-form text to transform.
  - `mode` (required for now): only `terminal` is supported; additional modes will be added later.
  - `provider` (optional): defaults to `codex`. Must reference a Codex-capable provider.

**Response (200 OK)**
```json
{
  "mode": "terminal",
  "provider": "codex",
  "text": "ls -la\ngit status"
}
```

**Integration notes**
- iOS Shortcut / Android client can hit this endpoint directly when they already have text (e.g., clipboard or typed prompt) instead of audio; it’s a single JSON POST followed by copying `text` to the clipboard.
- Codex requires prior `codex login` in the deployment environment; the service fails fast with `422` if credentials are missing.
- Enforce `mode=terminal` until alternative prompts are defined; clients should gate the UI accordingly.

### Provider Registry & Codex usage
- Whisper remains the default `/v1/transcriptions` provider, but specifying `provider=codex` runs the result through Codex’s CLI prompt so the returned clipboard text contains only deterministic commands (no narration).
- `/v1/translate` always routes to Codex unless overridden; we expose `DEFAULT_TRANSLATE_PROVIDER` to keep environment config explicit.

## Error Handling
All error responses use:
```json
{
  "error": {
    "code": "string",
    "message": "human readable",
    "details": { ... }
  }
}
```

Common cases:
- `400 INVALID_ARGUMENT` — missing `mode`, unsupported audio mime, duration limit exceeded.
- `401 UNAUTHENTICATED` — missing/invalid token.
- `403 PERMISSION_DENIED` — token lacks device scope.
- `413 PAYLOAD_TOO_LARGE` — audio exceeds configured size/duration.
- `415 UNSUPPORTED_MEDIA_TYPE` — unsupported encoding.
- `429 RATE_LIMITED` — include `Retry-After` header.
- `500 INTERNAL` — unexpected failure.

## Latency & Timeouts
- Target <3s for synchronous completion (assuming short clips).
- Client timeout recommendation: 15s.
- Async jobs expire after 24h; stale jobs return `410 Gone`.

## Logging & Observability (future work)
- Emit structured logs per request (`device_id`, `mode`, latency, model version).
- Capture metrics for queue depth and error rates; expose via `/metrics` when infra is ready.

## Open Questions
- Should authentication eventually use per-device signed requests instead of static tokens?
- What rate limits or quotas do we need per device/user?
- How will we distribute new provider binaries or API credentials securely?

Document answers via ADRs as decisions are made.
