from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from .formatting import format_for_mode
from .providers.base import ProviderError, ProviderOptions
from .providers.registry import ProviderRegistry
from .schemas import ClipboardPayload, Mode, TranscriptionResponse


class TranscriptionService:
    """Coordinates providers and output formatting."""

    def __init__(self, registry: ProviderRegistry, default_provider: str) -> None:
        self.registry = registry
        self.default_provider = default_provider

    def transcribe(
        self,
        *,
        audio_bytes: bytes,
        mode: Mode,
        provider_name: Optional[str] = None,
        language: Optional[str] = None,
    ) -> TranscriptionResponse:
        provider_key = provider_name or self.default_provider
        try:
            provider = self.registry.get(provider_key)
        except ProviderError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        start = time.perf_counter()
        try:
            provider_result = provider.transcribe(
                audio_bytes,
                ProviderOptions(language=language, mode=mode),
            )
        except ProviderError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        duration = time.perf_counter() - start
        clipboard_text, language_hint = format_for_mode(
            provider_result.text, mode, provider_result.language_hint
        )
        response = TranscriptionResponse(
            id=f"job_{uuid.uuid4().hex}",
            status="completed",
            mode=mode,
            duration_s=duration,
            clipboard=ClipboardPayload(
                text=clipboard_text,
                language_hint=language_hint,
                metadata={"provider": provider.name, "mode": mode.value},
            ),
            raw_transcript=provider_result.text,
            confidence=None,
            created_at=datetime.now(timezone.utc),
            provider=provider.name,
        )
        return response
