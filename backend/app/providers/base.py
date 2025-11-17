from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from ..schemas import Mode


class ProviderError(RuntimeError):
    """Raised when a provider fails to produce a transcription."""


@dataclass
class ProviderOptions:
    language: Optional[str] = None
    mode: Optional[Mode] = None


@dataclass
class ProviderResult:
    text: str
    language_hint: Optional[str] = None
    raw_segments: List[str] = field(default_factory=list)


class TranscriptionProvider(ABC):
    name: str

    @abstractmethod
    def transcribe(self, audio_bytes: bytes, options: ProviderOptions) -> ProviderResult:
        """Run transcription and return normalized text."""
        raise NotImplementedError
