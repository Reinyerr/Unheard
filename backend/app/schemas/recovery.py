"""T-014 local API contracts; reuse shared identity/state/origin enums."""
from typing import Annotated, Literal

from pydantic import Field, StrictBool, StrictStr

from app.schemas.research import ExperimentStatus, LanguageId, Model, Origin, RecoveryState

SessionId = Annotated[StrictStr, Field(pattern=r"^[a-f0-9]{32}$")]
SampleId = Annotated[StrictStr, Field(min_length=1, max_length=80)]
Mode = Literal["auto", "guided"]


class StartRequest(Model):
    language_id: LanguageId
    sample_id: SampleId
    source: Origin = Origin.saved
    mode: Mode = "auto"
    allow_saved_fallback: StrictBool = True


class DecisionRequest(Model):
    session_id: SessionId
    decision: Literal["correct", "incorrect", "refer"]


class RetryRequest(Model):
    session_id: SessionId
    sample_id: SampleId
    source: Origin | None = None
    allow_saved_fallback: StrictBool | None = None


class RecoveryErrorDetail(Model):
    code: StrictStr
    message: StrictStr
    retryable: StrictBool = False


class RecoveryResponse(Model):
    session_id: SessionId
    state: RecoveryState
    language_id: LanguageId
    sample_id: SampleId
    mode: Mode
    transcript: StrictStr | None
    source: Origin | None
    requested_source: Origin
    transcription_status: ExperimentStatus
    attempts: Annotated[int, Field(strict=True, ge=0, le=2)]
    max_attempts: Literal[2] = 2
    retry_available: StrictBool
    retry_sample_ids: list[SampleId]
    prompt_audio_url: None = None
    tts_status: Literal["unavailable"] = "unavailable"
    confirmation_prompt: StrictStr | None
    referral_message: StrictStr | None
    simulation_notice: StrictStr
    fallback_reason: StrictStr | None


class LanguageCapability(Model):
    language_id: LanguageId
    sample_ids: list[SampleId]
    saved_sample_ids_by_mode: dict[Mode, list[SampleId]]
    guided_verified: StrictBool


class CapabilitiesResponse(Model):
    available: StrictBool
    selected_sample_count: Annotated[int, Field(strict=True, ge=0)]
    live_configured: StrictBool
    languages: list[LanguageCapability]
    default_source: Literal["saved"] = "saved"
    max_attempts: Literal[2] = 2
    tts_status: Literal["unavailable"] = "unavailable"
    session_ttl_seconds: int = 1800
    max_sessions: int = 128
    simulation_notice: StrictStr
    warnings: list[StrictStr]
