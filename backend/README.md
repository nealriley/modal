# Backend Service

FastAPI application that exposes `/v1/transcriptions`, `/v1/translate`, and `/healthz` as described in `docs/architecture/backend.md`. The current implementation ships with:

- Provider registry abstraction with **whisper.cpp** configured as the default engine (see environment variables below) plus a **Codex** provider that rewrites CLI requests via `codex exec`.
- Mode-aware formatting to emit clipboard-ready text blocks for `terminal`, `code`, and `creative` requests.
- Pytest suite covering provider overrides, formatting, and health probes.

## Develop locally / in Codespaces

```bash
pip install -r backend/requirements.txt
./scripts/install_dependencies.sh    # installs ffmpeg + Codex CLI
uvicorn backend.app.main:app --reload --port 8000
```

Submit requests via `curl` or HTTP clients using `multipart/form-data`:

```bash
curl -X POST http://localhost:8000/v1/transcriptions \
  -H 'Authorization: Bearer dev-token' \
  -F mode=terminal \
  -F provider=whisper_cpp \
  -F audio=@sample.wav
```

Call the text-to-text translator (Codex) to turn prompts into CLI commands:

```bash
curl -X POST http://localhost:8000/v1/translate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"list files then check git status","mode":"terminal"}'
```

## Configuration

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `DEFAULT_TRANSCRIPTION_PROVIDER` | Provider name to use when request omits `provider`. | `whisper_cpp` |
| `WHISPER_CPP_BINARY` | Path to the compiled `main` binary from whisper.cpp. | `./backend/bin/whisper` |
| `WHISPER_CPP_MODEL` | Path to ggml model. | `./backend/models/ggml-base.en.bin` |
| `WHISPER_CPP_ARGS` | Extra CLI args appended when invoking whisper.cpp. | `--no-prints` |
| `DEFAULT_TRANSLATE_PROVIDER` | Provider used by `/v1/translate` when none is specified. | `codex` |
| `FFMPEG_BINARY` | Executable used to transcode uploads into 16 kHz mono WAV. | `ffmpeg` |
| `CODEX_BINARY` | Path to the Codex CLI (`@openai/codex`). | `codex` |
| `CODEX_TERMINAL_SYSTEM_PROMPT` | System prompt used when Codex rewrites terminal/CLI text. | opinionated default |

Ensure the binary/model exist in Codespaces or update paths accordingly.

## Testing

```
pytest
```

Tests live in `tests/` and rely on stub providers, so they run without invoking whisper.cpp.

## Automation Helpers
- `scripts/setup_whisper.sh` — clones/builds whisper.cpp and downloads the default ggml model (runs automatically in Codespaces `postCreate`).
- `scripts/service_manager.py` — tmux-backed CLI for lifecycle management. Usage:

  ```bash
  python scripts/service_manager.py status    # PID, tmux session, log tail, public URL hint
  python scripts/service_manager.py ensure    # start backend inside tmux if not already running
  python scripts/service_manager.py logs --tmux  # live tmux pane output
  python scripts/service_manager.py attach    # jump into shared tmux session
  ```
- Shell wrappers (`scripts/start_backend.sh`, `scripts/stop_backend.sh`) call the manager and are referenced by the devcontainer `postStartCommand`.
- Port 8000 is forwarded by `.devcontainer/devcontainer.json`; mark it **Public** in the Ports tab (or via `gh codespace ports visibility ...`) to test from external devices.
