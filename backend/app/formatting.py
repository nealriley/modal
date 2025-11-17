from __future__ import annotations

import re
from typing import Optional, Tuple

from .schemas import Mode


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _split_commands(value: str) -> list[str]:
    parts = re.split(r"[\n;]+", value)
    return [part.strip() for part in parts if part.strip()]


def format_for_mode(raw_text: str, mode: Mode, provider_language: Optional[str]) -> Tuple[str, Optional[str]]:
    text = raw_text.strip()
    if mode is Mode.terminal:
        commands = _split_commands(text)
        return ("\n".join(commands), "shell")
    if mode is Mode.code:
        return (text, provider_language or "code")
    if mode is Mode.creative:
        paragraphs = [
            _normalize_whitespace(chunk)
            for chunk in re.split(r"\n{2,}", text)
            if _normalize_whitespace(chunk)
        ]
        return ("\n\n".join(paragraphs), "plain")
    return (text, provider_language)
