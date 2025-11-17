#!/usr/bin/env bash
set -euo pipefail

# Setup CLI tools needed in the devcontainer

# Update package lists
sudo apt-get update

# Install tmux and jq if not already installed
sudo apt-get install -y tmux jq

# Install global npm CLIs
if command -v npm >/dev/null 2>&1; then
	npm install -g @openai/codex
fi
