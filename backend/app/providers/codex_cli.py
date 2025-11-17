from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from ..schemas import Mode
from .base import ProviderError, ProviderOptions, ProviderResult, TranscriptionProvider


class CodexProvider(TranscriptionProvider):
    """Delegates transcription to another provider and rewrites output via Codex CLI."""

    name = "codex"

    def __init__(
        self,
        transcription_provider: TranscriptionProvider,
        codex_binary: str = "codex",
        terminal_prompt: str | None = None,
    ) -> None:
        self.transcriber = transcription_provider
        self.codex_binary = shutil.which(codex_binary) or codex_binary
        self.terminal_prompt = terminal_prompt or (
            "You convert spoken requests into executable CLI commands. "
            "Return ONLY the commands, flags, and arguments the user must run. "
            "Do not add explanations, prose, confirmations, or code fences."
        )

    def transcribe(self, audio_bytes: bytes, options: ProviderOptions) -> ProviderResult:  # type: ignore[override]
        base_result = self.transcriber.transcribe(audio_bytes, options)
        mode = options.mode
        if mode is Mode.terminal:
            rewritten = self.rewrite(base_result.text, mode)
            return ProviderResult(
                text=rewritten,
                language_hint="shell",
                raw_segments=base_result.raw_segments,
            )
        return base_result

    def rewrite(self, text: str, mode: Mode) -> str:
        if mode is not Mode.terminal:
            raise ProviderError("Codex provider currently supports terminal mode only")
        return self._run_codex(transcript=text, prompt=self.terminal_prompt)

    def _run_codex(self, *, transcript: str, prompt: str) -> str:
        codex_path = shutil.which(self.codex_binary) or self.codex_binary
        if not Path(codex_path).exists():
            raise ProviderError("Codex CLI binary not found. Install @openai/codex or set CODEX_BINARY.")

        instructions = (
            f"{prompt}\n\n"
            "Transcribed request:\n"
            "```\n"
            f"{transcript.strip()}\n"
            "```\n\n"
            "Respond with only the CLI command(s):"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "codex_output.txt"
            cmd = [
                codex_path,
                "exec",
                "--skip-git-repo-check",
                "--output-last-message",
                str(output_file),
                "-",
            ]
            process = subprocess.run(
                cmd,
                input=instructions,
                capture_output=True,
                text=True,
                check=False,
            )
            if process.returncode != 0:
                stderr = process.stderr.strip() or process.stdout.strip()
                raise ProviderError(f"Codex CLI failed: {stderr}")
            if not output_file.exists():
                stdout = process.stdout.strip()
                stderr = process.stderr.strip()
                detail = stderr or stdout or "no output captured from Codex"
                raise ProviderError(f"Codex CLI produced no output: {detail}")
            output_text = output_file.read_text(encoding="utf-8").strip()
            if not output_text:
                raise ProviderError("Codex CLI returned empty output")
            return output_text
