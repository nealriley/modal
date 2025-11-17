from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class Mode(str, Enum):
    terminal = "terminal"
    code = "code"
    creative = "creative"


class ClipboardPayload(BaseModel):
    text: str
    language_hint: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class TranscriptionResponse(BaseModel):
    id: str
    status: str
    mode: Mode
    duration_s: float
    clipboard: ClipboardPayload
    raw_transcript: str
    confidence: Optional[float] = None
    created_at: datetime
    provider: str


class TranslateRequest(BaseModel):
    prompt: str = Field(..., description="Text to transform into clipboard-ready output")
    mode: Mode = Field(Mode.terminal, description="Target presentation mode")
    provider: Optional[str] = Field(
        None, description="Optional provider override (defaults to Codex)"
    )


class TranslateResponse(BaseModel):
    mode: Mode
    provider: str
    text: str
