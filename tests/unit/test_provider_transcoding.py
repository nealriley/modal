from __future__ import annotations

from pathlib import Path
import shutil

import pytest

from backend.app.providers.base import ProviderOptions
from backend.app.providers.whisper_cpp import WhisperCppProvider

AUDIO_FILENAMES = [
    "Recording.m4a",
    "Recording.mp3",
    "Recording.webm",
    "Recording.flac",
]


@pytest.fixture(scope="session")
def whisper_provider() -> WhisperCppProvider:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        pytest.skip("ffmpeg is required for transcoding tests")

    binary_path = Path("tests/fakes/whisper_stub.py").resolve()
    model_path = Path("tests/fakes/model.bin").resolve()
    return WhisperCppProvider(
        binary_path=str(binary_path),
        model_path=str(model_path),
        extra_args=[],
        ffmpeg_binary=ffmpeg_path,
    )


@pytest.mark.parametrize("filename", AUDIO_FILENAMES)
def test_provider_transcribes_common_audio_formats(whisper_provider: WhisperCppProvider, filename: str) -> None:
    audio_path = Path("tests/content") / filename
    audio_bytes = audio_path.read_bytes()

    result = whisper_provider.transcribe(audio_bytes, ProviderOptions(language=None))

    assert result.text == "stub transcript"
