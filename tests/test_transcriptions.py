from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app, get_provider_registry
from backend.app.providers.codex_cli import CodexProvider
from backend.app.providers.registry import ProviderRegistry
from backend.app.providers.base import ProviderOptions, ProviderResult, TranscriptionProvider


class _EchoProvider(TranscriptionProvider):
    name = "echo"

    def __init__(self, text: str) -> None:
        self._text = text

    def transcribe(self, audio_bytes: bytes, options: ProviderOptions) -> ProviderResult:  # type: ignore[override]
        del audio_bytes, options
        return ProviderResult(text=self._text)

def _fake_audio() -> tuple[str, bytes, str]:
    return ("sample.wav", b"RIFF....", "audio/wav")


def test_transcription_terminal_mode_formats_commands(client: TestClient):
    response = client.post(
        "/v1/transcriptions",
        data={"mode": "terminal"},
        files={"audio": _fake_audio()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["clipboard"]["text"] == "ls -la\ngit status"
    assert body["clipboard"]["language_hint"] == "shell"
    assert response.headers["X-Transcription-Provider"] == "stub"


def test_transcription_allows_provider_override(client: TestClient):
    response = client.post(
        "/v1/transcriptions",
        data={"mode": "code", "provider": "alt"},
        files={"audio": _fake_audio()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "alt"
    assert body["clipboard"]["language_hint"] == "python"
    assert "print('hello world')" in body["clipboard"]["text"]


def test_invalid_provider_returns_400(client: TestClient):
    response = client.post(
        "/v1/transcriptions",
        data={"mode": "code", "provider": "missing"},
        files={"audio": _fake_audio()},
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_health_endpoint(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_translate_endpoint_returns_cli_only(client: TestClient):
    codex_stub = Path("tests/fakes/codex_stub.py").resolve()
    base_transcriber = _EchoProvider("tell me git status")
    codex_provider = CodexProvider(
        transcription_provider=base_transcriber,
        codex_binary=str(codex_stub),
        terminal_prompt="Return git commands only.",
    )
    registry = ProviderRegistry([codex_provider])
    app.dependency_overrides[get_provider_registry] = lambda: registry

    response = client.post(
        "/v1/translate",
        json={"prompt": "can you check git status", "mode": "terminal"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "git status"
    assert body["mode"] == "terminal"
    assert body["provider"] == "codex"
