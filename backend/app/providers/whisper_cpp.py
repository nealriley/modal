from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from .base import ProviderError, ProviderOptions, ProviderResult, TranscriptionProvider


class WhisperCppProvider(TranscriptionProvider):
    name = "whisper_cpp"

    def __init__(
        self,
        binary_path: str,
        model_path: str,
        extra_args: Optional[List[str]] = None,
        ffmpeg_binary: str = "ffmpeg",
    ) -> None:
        self.binary_path = Path(binary_path)
        self.model_path = Path(model_path)
        self.extra_args = extra_args or []
        self.ffmpeg_binary = shutil.which(ffmpeg_binary) or ffmpeg_binary

    def transcribe(self, audio_bytes: bytes, options: ProviderOptions) -> ProviderResult:
        if not audio_bytes:
            raise ProviderError("Audio payload is empty")
        if not self.binary_path.exists():
            raise ProviderError(
                f"whisper.cpp binary not found at {self.binary_path}. Install/build whisper.cpp and update WHISPER_CPP_BINARY."
            )
        if not self.model_path.exists():
            raise ProviderError(
                f"Model file not found at {self.model_path}. Download ggml model and set WHISPER_CPP_MODEL."
            )

        ffmpeg_path = shutil.which(self.ffmpeg_binary)
        if ffmpeg_path is None:
            raise ProviderError(
                f"ffmpeg binary '{self.ffmpeg_binary}' not found. Install ffmpeg or set FFMPEG_BINARY."
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_input = Path(tmpdir) / "input.orig"
            tmp_input.write_bytes(audio_bytes)
            tmp_audio = Path(tmpdir) / "input.wav"

            self._transcode_to_wav(ffmpeg_path, tmp_input, tmp_audio)
            output_prefix = Path(tmpdir) / "out"

            cmd = [
                str(self.binary_path),
                "-m",
                str(self.model_path),
                "-f",
                str(tmp_audio),
                "-of",
                str(output_prefix),
                "--output-txt",
            ]
            if options.language:
                cmd.extend(["--language", options.language])
            cmd.extend(self.extra_args)

            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            if process.returncode != 0:
                details = stderr or stdout or "no additional diagnostics"
                raise ProviderError(f"whisper.cpp failed: {details}")

            txt_path = Path(f"{output_prefix}.txt")
            if not txt_path.exists():
                detail_parts = []
                if stdout:
                    detail_parts.append(f"stdout: {stdout}")
                if stderr:
                    detail_parts.append(f"stderr: {stderr}")
                detail_suffix = f" ({'; '.join(detail_parts)})" if detail_parts else ""
                raise ProviderError(
                    f"whisper.cpp did not produce .txt output{detail_suffix}"
                )

            text = txt_path.read_text(encoding="utf-8").strip()

        return ProviderResult(text=text, language_hint=options.language)

    def _transcode_to_wav(self, ffmpeg_path: str, src: Path, dst: Path) -> None:
        cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(src),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-f",
            "wav",
            str(dst),
        ]
        process = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if process.returncode != 0:
            stderr = process.stderr.strip()
            stdout = process.stdout.strip()
            details = stderr or stdout or "no additional diagnostics"
            raise ProviderError(f"ffmpeg failed to transcode audio: {details}")
        if not dst.exists():
            raise ProviderError("ffmpeg did not produce WAV output")
