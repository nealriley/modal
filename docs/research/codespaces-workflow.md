# GitHub Codespaces Workflow

Covers SSH access, automated setup, backend startup, and public port exposure so external devices (e.g., Android CLI) can hit the transcription API.

## 1. Create / Resume the Codespace
1. Open the repo in GitHub and choose *Code → Codespaces* → create or resume.
2. The `.devcontainer/devcontainer.json` uses the `mcr.microsoft.com/devcontainers/universal:2` image (includes GitHub CLI, tmux, and common tooling) and runs `scripts/setup_whisper.sh` after the container is created. This script clones/builds `whisper.cpp`, copies the `main` binary to `backend/bin/whisper`, and downloads `ggml-base.en.bin` to `backend/models/`.
3. On every start, `python scripts/service_manager.py ensure` runs automatically to install deps (if needed) and launch `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` in the background. Logs live under `.logs/backend.log`.

## 2. Manual Control (tmux-backed)
- **Status**: `python scripts/service_manager.py status` (shows PID, tmux session, public URL hint, log tail).
- **Start / Ensure / Restart**: `python scripts/service_manager.py start|ensure|restart`.
- **Stop**: `python scripts/service_manager.py stop` (sends Ctrl+C to the tmux session then kills it).
- **Logs**: `python scripts/service_manager.py logs --tmux -n 80` for live pane output, or `tail -f .logs/backend.log` for file-based logs.
- **Attach**: `python scripts/service_manager.py attach` (or `tmux -S .run/tmux/backend_service.sock attach -t backend_service`) to watch real-time output / send keystrokes.
- If you need to rebuild whisper or swap models, delete `.deps/whisper.cpp`, `backend/bin/whisper`, or `backend/models/*` and rerun `scripts/setup_whisper.sh`.

## 3. SSH into Codespaces
1. Install the GitHub CLI locally: `https://cli.github.com/`.
2. Authenticate: `gh auth login`.
3. List codespaces: `gh codespace list` and grab the name/id.
4. SSH: `gh codespace ssh <name>` (adds entry to local SSH config). This gives shell access for troubleshooting or tunneling.

## 4. Port Forwarding & Public Access
1. Codespaces auto-forwards port 8000 per `forwardPorts` in the devcontainer file.
2. In VS Code / web UI, open the *Ports* tab, locate port 8000 (label `backend`).
3. Click the lock icon → **Make Public** so external devices can reach it.
4. Copy the public URL shown (e.g., `https://<id>-8000.app.github.dev`). This is the base URL to use from your Android device.

## 5. Testing from Codespaces
```bash
curl -sSf https://<id>-8000.app.github.dev/healthz
```
should return `{ "status": "ok" }`.

To submit audio:
```bash
curl -X POST https://<id>-8000.app.github.dev/v1/transcriptions \
  -H 'Authorization: Bearer dev-token' \
  -F mode=terminal \
  -F audio=@sample.wav
```
Replace `sample.wav` with the path to your audio snippet (<= ~60s for synchronous response).

## 6. Environment Variables
Set in Codespaces *Secrets* or `.devcontainer/devcontainer.json` if needed:
- `DEFAULT_TRANSCRIPTION_PROVIDER` (default `whisper_cpp`)
- `WHISPER_CPP_BINARY` / `WHISPER_CPP_MODEL`
- `PORT` if you need to run on a different port (update `forwardPorts` accordingly).

## 7. Troubleshooting
- Whisper download blocked? set `WHISPER_CPP_MODEL_URL` before running setup script (e.g., to a mirror) or manually place the model in `backend/models`.
- `scripts/start_backend.sh` says backend already running but port unreachable: check `.logs/backend.log` for stack traces, or `bash scripts/stop_backend.sh` before restarting.
- Public port 8000 not accessible: ensure Codespace is awake and the *Ports* entry is public; GitHub auto-sleeps inactive codespaces.

Keep this document updated as automation evolves (e.g., custom devcontainer features, additional telemetry scripts).
