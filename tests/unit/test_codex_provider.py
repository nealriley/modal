from __future__ import annotations

from pathlib import Path

from backend.app.providers.base import ProviderOptions, ProviderResult, TranscriptionProvider
from backend.app.providers.codex_cli import CodexProvider
from backend.app.schemas import Mode


class EchoProvider(TranscriptionProvider):
    name = "echo"

    def __init__(self, text: str) -> None:
        self._text = text

    def transcribe(self, audio_bytes: bytes, options: ProviderOptions) -> ProviderResult:  # type: ignore[override]
        del audio_bytes, options
        return ProviderResult(text=self._text, language_hint="shell")


def test_codex_provider_rewrites_terminal_text(tmp_path) -> None:
    base = EchoProvider("list the repo status")
    codex_stub = Path("tests/fakes/codex_stub.py").resolve()
    provider = CodexProvider(
        transcription_provider=base,
        codex_binary=str(codex_stub),
        terminal_prompt="Return git commands only.",
    )

    result = provider.transcribe(b"", ProviderOptions(language=None, mode=Mode.terminal))

    assert result.text == "git status"
    assert result.language_hint == "shell"
