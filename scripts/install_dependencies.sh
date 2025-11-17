#!/usr/bin/env bash
set -euo pipefail

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo not available; cannot install dependencies." >&2
  exit 1
fi

echo "[deps] Installing ffmpeg via apt..."
sudo apt-get update
sudo apt-get install -y ffmpeg

echo "[deps] Installing Codex CLI via npm..."
if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to install @openai/codex" >&2
  exit 1
fi
npm install -g @openai/codex

echo "[deps] Dependencies installed."
