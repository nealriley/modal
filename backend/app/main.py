from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from .config import get_settings
from .providers.codex_cli import CodexProvider
from .providers.registry import ProviderRegistry
from .providers.whisper_cpp import WhisperCppProvider
from .schemas import Mode, TranscriptionResponse, TranslateRequest, TranslateResponse
from .service import TranscriptionService

app = FastAPI(title="Audio Clipboard Backend", version="0.1.0")


def _build_registry() -> ProviderRegistry:
    settings = get_settings()
    whisper_provider = WhisperCppProvider(
        binary_path=settings.whisper_cpp_binary,
        model_path=settings.whisper_cpp_model,
        extra_args=settings.whisper_cpp_args,
        ffmpeg_binary=settings.ffmpeg_binary,
    )
    codex_provider = CodexProvider(
        transcription_provider=whisper_provider,
        codex_binary=settings.codex_binary,
        terminal_prompt=settings.codex_terminal_prompt,
    )
    return ProviderRegistry([whisper_provider, codex_provider])


_settings = get_settings()
_registry = _build_registry()
_service = TranscriptionService(_registry, default_provider=_settings.default_provider)


def get_transcription_service() -> TranscriptionService:
    return _service


def get_provider_registry() -> ProviderRegistry:
    return _registry


def _get_codex_provider(registry: ProviderRegistry, name: str) -> CodexProvider:
    provider = registry.get(name)
    if not isinstance(provider, CodexProvider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{name}' is not Codex-capable",
        )
    return provider


@app.post("/v1/transcriptions", response_model=TranscriptionResponse)
async def create_transcription(
    audio: UploadFile = File(..., description="Audio snippet to transcribe"),
    mode: Mode = Form(..., description="Extraction mode: terminal|code|creative"),
    provider: str | None = Form(None, description="Transcription provider override"),
    language: str | None = Form(None, description="Language hint"),
    device_id: str | None = Form(None, description="Device identifier for logging"),
    client_version: str | None = Form(None, description="Client version"),
    service: TranscriptionService = Depends(get_transcription_service),
):
    del device_id, client_version  # placeholders until logging/metrics pipeline is added
    audio_bytes = await audio.read()
    response = service.transcribe(
        audio_bytes=audio_bytes,
        mode=mode,
        provider_name=provider,
        language=language,
    )
    headers = {"X-Transcription-Provider": response.provider}
    return JSONResponse(
        status_code=200, content=response.model_dump(mode="json"), headers=headers
    )


@app.post("/v1/translate", response_model=TranslateResponse)
async def translate_prompt(
    payload: TranslateRequest,
    registry: ProviderRegistry = Depends(get_provider_registry),
):
    provider_name = payload.provider or _settings.default_translate_provider
    if payload.mode is not Mode.terminal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Translate endpoint currently supports mode=terminal only.",
        )
    provider = _get_codex_provider(registry, provider_name)
    text = provider.rewrite(payload.prompt, payload.mode)
    return TranslateResponse(mode=payload.mode, provider=provider.name, text=text)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
