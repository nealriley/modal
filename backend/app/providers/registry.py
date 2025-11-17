from __future__ import annotations

from typing import Dict, Iterable, List

from .base import ProviderError, TranscriptionProvider


class ProviderRegistry:
    """Lightweight registry to store and retrieve transcription providers."""

    def __init__(self, providers: Iterable[TranscriptionProvider] | None = None) -> None:
        self._providers: Dict[str, TranscriptionProvider] = {}
        if providers:
            for provider in providers:
                self.register(provider)

    def register(self, provider: TranscriptionProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> TranscriptionProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise ProviderError(f"Provider '{name}' is not registered") from exc

    def list(self) -> List[str]:
        return sorted(self._providers.keys())
