from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.main import app, get_transcription_service
from backend.app.providers.base import ProviderOptions, ProviderResult, TranscriptionProvider
from backend.app.providers.registry import ProviderRegistry
from backend.app.service import TranscriptionService


class DummyProvider(TranscriptionProvider):
    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self._text = text

    def transcribe(self, audio_bytes: bytes, options: ProviderOptions) -> ProviderResult:  # type: ignore[override]
        del audio_bytes, options
        return ProviderResult(text=self._text, language_hint="python")


@pytest.fixture
def stub_service() -> TranscriptionService:
    registry = ProviderRegistry(
        [
            DummyProvider(name="stub", text="ls -la; git status"),
            DummyProvider(name="alt", text="print('hello world')"),
        ]
    )
    return TranscriptionService(registry, default_provider="stub")


@pytest.fixture
def client(stub_service: TranscriptionService):
    app.dependency_overrides[get_transcription_service] = lambda: stub_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
