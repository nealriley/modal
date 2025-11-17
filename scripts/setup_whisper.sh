#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
DEPS_DIR="$ROOT_DIR/.deps"
WHISPER_SRC_DIR="$DEPS_DIR/whisper.cpp"
WHISPER_TAG=${WHISPER_CPP_VERSION:-v1.6.2}
BIN_DIR="$ROOT_DIR/backend/bin"
MODEL_DIR="$ROOT_DIR/backend/models"
WHISPER_BIN="$BIN_DIR/whisper"
MODEL_NAME=${WHISPER_CPP_MODEL_NAME:-ggml-base.en.bin}
MODEL_URL=${WHISPER_CPP_MODEL_URL:-https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$MODEL_NAME}

mkdir -p "$DEPS_DIR" "$BIN_DIR" "$MODEL_DIR"

if [ ! -d "$WHISPER_SRC_DIR" ]; then
  echo "Cloning whisper.cpp ($WHISPER_TAG)..."
  git clone --branch "$WHISPER_TAG" --depth=1 https://github.com/ggerganov/whisper.cpp.git "$WHISPER_SRC_DIR"
else
  echo "whisper.cpp source already present at $WHISPER_SRC_DIR"
fi

if [ ! -x "$WHISPER_SRC_DIR/main" ]; then
  echo "Building whisper.cpp..."
  make -C "$WHISPER_SRC_DIR"
fi

cp "$WHISPER_SRC_DIR/main" "$WHISPER_BIN"
chmod +x "$WHISPER_BIN"
echo "whisper binary copied to $WHISPER_BIN"

MODEL_PATH="$MODEL_DIR/$MODEL_NAME"
if [ ! -f "$MODEL_PATH" ]; then
  echo "Downloading model $MODEL_NAME..."
  curl -L "$MODEL_URL" -o "$MODEL_PATH"
else
  echo "Model already present at $MODEL_PATH"
fi

echo "whisper.cpp setup complete."
