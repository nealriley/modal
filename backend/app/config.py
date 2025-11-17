from __future__ import annotations

import os
import shlex
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List

DEFAULT_CLI_PROMPT = (
    "You are a command-line transcription specialist. "
    "Given a noisy spoken instruction, output exactly the CLI command(s) the user meant to run. "
    "Return only the commands with necessary flags/arguments, no prose, comments, or code fences. "
    "If multiple commands are required, put each on its own line."
)

@dataclass
class Settings:
    """Runtime configuration loaded from environment variables."""

    default_provider: str = os.getenv("DEFAULT_TRANSCRIPTION_PROVIDER", "whisper_cpp")
    default_translate_provider: str = os.getenv("DEFAULT_TRANSLATE_PROVIDER", "codex")
    whisper_cpp_binary: str = os.getenv("WHISPER_CPP_BINARY", "./backend/bin/whisper")
    whisper_cpp_model: str = os.getenv("WHISPER_CPP_MODEL", "./backend/models/ggml-base.en.bin")
    whisper_cpp_args: List[str] = field(
        default_factory=lambda: shlex.split(os.getenv("WHISPER_CPP_ARGS", "--no-prints"))
    )
    ffmpeg_binary: str = os.getenv("FFMPEG_BINARY", "ffmpeg")
    codex_binary: str = os.getenv("CODEX_BINARY", "codex")
    codex_terminal_prompt: str = os.getenv("CODEX_TERMINAL_SYSTEM_PROMPT", DEFAULT_CLI_PROMPT)


@lru_cache
def get_settings() -> Settings:
    return Settings()
