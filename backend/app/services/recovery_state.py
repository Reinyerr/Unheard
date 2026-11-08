"""Bounded in-memory confirmation sessions over curated prerecorded speech."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from threading import RLock
import time
import unicodedata
import uuid

from app.schemas.recovery import (
    CapabilitiesResponse, DecisionRequest, LanguageCapability, RecoveryErrorDetail,
    RecoveryResponse, RetryRequest, StartRequest,
)
from app.schemas.research import ExperimentStatus, Origin, RecoveryState
from app.services.tts_adapter import cached_prompt
from app.services.tts_config import LANGUAGES
from app.services.elevenlabs_adapter import (
    MODEL_ID, REPO, ConfigurationError, ElevenLabsAdapter, load_selection, request_options,
)

NOTICE = ("Prerecorded third-party speech. Confirmation is a simulation by the current user, "
          "not the original speaker's consent. No municipal service is contacted.")
REFERRAL = ("Consider requesting human assistance through the municipality's official service channels. "
            "This prototype has not contacted or connected you to a representative.")
ALIASES = {"english": {"en", "eng"}, "urdu": {"ur", "urd"}, "punjabi": {"pa", "pan"},
           "arabic": {"ar", "ara"}, "cantonese": {"yue"}, "mandarin_chinese": {"zh", "zho", "cmn"}}
SCRIPTS = {"english": "LATIN", "urdu": "ARABIC", "arabic": "ARABIC", "punjabi": "GURMUKHI",
           "cantonese": "CJK", "mandarin_chinese": "CJK"}


class RecoveryError(Exception):
    def __init__(self, code: str, message: str, status: int = 409, *, retryable: bool = False,
                 session: RecoveryResponse | None = None):
        super().__init__(message)
        self.detail = RecoveryErrorDetail(code=code, message=message, retryable=retryable)
        self.status, self.session = status, session


def decision_state(state: RecoveryState, attempts: int, decision: str) -> RecoveryState:
    if decision == "refer" and state in {RecoveryState.confirm, RecoveryState.retry_or_refer}:
        return RecoveryState.referral
    if state != RecoveryState.confirm:
        raise RecoveryError("invalid_transition", "Only a usable transcript awaiting confirmation can be marked correct or incorrect")
    if decision == "correct":
        return RecoveryState.accepted
    if decision == "incorrect":
        return RecoveryState.referral if attempts >= 2 else RecoveryState.retry_or_refer
    raise RecoveryError("invalid_transition", "Unknown confirmation decision")


def usable(attempt: dict, language: str) -> bool:
    text = attempt.get("transcript_raw")
    if attempt.get("status") != "completed" or not isinstance(text, str) or not text.strip():
        return False
    if attempt.get("review_flags"):
        return False
    if attempt.get("detected_language_code") and attempt["detected_language_code"] not in ALIASES[language]:
        return False
    letters = [ch for ch in text if unicodedata.category(ch).startswith("L")]
    return bool(letters) and sum(SCRIPTS[language] in unicodedata.name(ch, "") for ch in letters) >= len(letters) / 2


def catalog():
    try:
        return load_selection()
    except (OSError, ValueError, KeyError, TypeError):
        raise RecoveryError("data_unavailable", "Verified prerecorded sample data is unavailable", 503) from None


def saved_evidence(samples, assets, selection_sha: str) -> tuple[dict, set[str], list[str]]:
    """Only saved provider responses with matching frozen audio/options are eligible."""
    by_id = {sample.sample_id: sample for sample in samples.samples}
    saved, guided, warnings, blocked = {}, set(), [], set()
    for relative in ("data/processed/experiment_attempts.json", "data/local/preflight_log.json"):
        path = REPO / relative
        if not path.exists():
            continue
        try:
            report = json.loads(path.read_bytes())
            if report.get("selection_sha256") != selection_sha or report.get("model_id") != MODEL_ID:
                raise ValueError("mismatched provenance")
            exclusions = {(finding["sample_id"], mode)
                          for finding in report.get("response_review", {}).get("findings", [])
                          if finding.get("comparability_status") == "incompatible_output"
                          for mode in finding.get("modes", [finding.get("mode")])}
            blocked.update(exclusions)
            for key in exclusions:
                saved.pop(key, None)
            for attempt in report["attempts"]:
                sample = by_id.get(attempt.get("sample_id"))
                mode = attempt.get("mode")
                if sample is None or mode not in {"auto", "guided"}:
                    continue
                key = sample.sample_id, mode
                if (attempt.get("audio_sha256") != assets[sample.sample_id]["sha256"]
                        or attempt.get("model_id") != MODEL_ID
                        or attempt.get("request_options") != request_options(sample.language_id, mode)):
                    continue
                raw_relative = attempt.get("raw_response_path")
                if not raw_relative:
                    continue
                raw_path = (REPO / raw_relative).resolve()
                if not raw_path.is_relative_to(REPO / "data/local"):
                    continue
                raw = raw_path.read_bytes()
                if attempt.get("raw_response_sha256") and hashlib.sha256(raw).hexdigest() != attempt["raw_response_sha256"]:
                    continue
                payload = json.loads(raw)
                http_status = attempt.get("http_status") or 0
                if not 200 <= http_status < 300 or payload.get("text") != attempt.get("transcript_raw"):
                    continue
                if mode == "guided" and attempt.get("guidance_acceptance") == "accepted_by_api":
                    guided.add(sample.language_id.value)
                if attempt.get("status") == "incompatible_output" or attempt.get("review_flags"):
                    blocked.add(key)
                    saved.pop(key, None)
                if key not in blocked and usable(attempt, sample.language_id):
                    saved.setdefault(key, attempt)
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            warnings.append("Some local saved evidence could not be verified")
    return saved, guided, sorted(set(warnings))


@dataclass
class Session:
    session_id: str
    language_id: str
    mode: str
    requested_source: Origin
    allow_saved_fallback: bool
    selection_sha: str
    sample_ids: tuple[str, ...]
    state: RecoveryState = RecoveryState.ready
    sample_id: str = ""
    attempts: int = 0
    used_ids: list[str] = field(default_factory=list)
    transcript: str | None = None
    source: Origin | None = None
    transcription_status: ExperimentStatus = ExperimentStatus.not_tested
    fallback_reason: str | None = None
    touched: float = field(default_factory=time.monotonic)


class RecoveryService:
    def __init__(self, *, adapter_factory=ElevenLabsAdapter):
        self._adapter_factory = adapter_factory
        self._sessions: dict[str, Session] = {}
        self._lock = RLock()

    def _cleanup(self) -> None:
        for identity, session in list(self._sessions.items()):
            if session.state != RecoveryState.transcribing and time.monotonic() - session.touched > 1800:
                del self._sessions[identity]

    def _session(self, identity: str) -> Session:
        self._cleanup()
        session = self._sessions.get(identity)
        if session is None:
            raise RecoveryError("session_not_found", "Session is unknown or expired; start a new simulation", 404)
        session.touched = time.monotonic()
        return session

    def _view(self, session: Session) -> RecoveryResponse:
        retry_ids = [identity for identity in session.sample_ids if identity not in session.used_ids]
        retry_available = session.state == RecoveryState.retry_or_refer and session.attempts < 2 and bool(retry_ids)
        prompt = cached_prompt(session.language_id) if session.state == RecoveryState.confirm else None
        return RecoveryResponse(
            session_id=session.session_id, state=session.state, language_id=session.language_id,
            sample_id=session.sample_id, mode=session.mode, transcript=session.transcript,
            source=session.source, requested_source=session.requested_source,
            transcription_status=session.transcription_status, attempts=session.attempts,
            retry_available=retry_available, retry_sample_ids=retry_ids if retry_available else [],
            confirmation_prompt=(LANGUAGES[session.language_id]["text"]
                                 if session.state == RecoveryState.confirm else None),
            referral_message=REFERRAL if session.state in {RecoveryState.retry_or_refer, RecoveryState.referral} else None,
            simulation_notice=NOTICE, fallback_reason=session.fallback_reason,
            prompt_audio_url=prompt["audio_path"] if prompt else None,
            tts_status="cached" if prompt else "unavailable",
            prompt_caption=LANGUAGES[session.language_id]["text"] if session.state == RecoveryState.confirm else None,
            tts_attribution=prompt["attribution"] if prompt else None,
        )

    def capabilities(self) -> CapabilitiesResponse:
        samples, assets, digest = catalog()
        saved, guided, warnings = saved_evidence(samples, assets, digest)
        languages = []
        for language in sorted({sample.language_id for sample in samples.samples}):
            ids = [sample.sample_id for sample in samples.samples if sample.language_id == language]
            languages.append(LanguageCapability(language_id=language, sample_ids=ids,
                saved_sample_ids_by_mode={mode: [identity for identity in ids if (identity, mode) in saved]
                                          for mode in ("auto", "guided")}, guided_verified=language in guided))
        cached_languages = [language for language in LANGUAGES if cached_prompt(language)]
        return CapabilitiesResponse(available=True, selected_sample_count=len(samples.samples),
            live_configured=bool(os.environ.get("ELEVENLABS_API_KEY", "").strip()),
            languages=languages, simulation_notice=NOTICE, warnings=warnings,
            tts_status="cached" if cached_languages else "unavailable",
            tts_language_ids=cached_languages)

    @staticmethod
    def _check_sample(sample_id: str, language: str, samples, assets) -> None:
        sample = next((sample for sample in samples.samples if sample.sample_id == sample_id), None)
        if sample is None or sample.language_id != language:
            raise RecoveryError("invalid_sample", "Sample must be a curated recording in the selected language", 400)
        path = REPO / "frontend/public" / sample.audio_path
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(REPO / "frontend/public"):
                raise ValueError("unsafe sample")
            asset = assets[sample_id]
            if path.stat().st_size != asset["size_bytes"] or path.stat().st_size > 16 * 1024 * 1024:
                raise ValueError("bad size")
            raw = path.read_bytes()
            if not raw.startswith(b"fLaC") or hashlib.sha256(raw).hexdigest() != asset["sha256"]:
                raise ValueError("bad hash")
        except (OSError, ValueError):
            raise RecoveryError("sample_unavailable", "Selected verified audio is unavailable", 503) from None

    def start(self, request: StartRequest) -> RecoveryResponse:
        samples, assets, digest = catalog()
        self._check_sample(request.sample_id, request.language_id, samples, assets)
        with self._lock:
            self._cleanup()
            if len(self._sessions) >= 128:
                raise RecoveryError("session_capacity", "Local session capacity reached; retry after sessions expire", 503, retryable=True)
            session = Session(uuid.uuid4().hex, request.language_id.value, request.mode, request.source,
                              request.allow_saved_fallback, digest,
                              tuple(sample.sample_id for sample in samples.samples if sample.language_id == request.language_id))
            self._sessions[session.session_id] = session
        return self._attempt(session.session_id, request.sample_id, samples, assets, digest)

    def get(self, session_id: str) -> RecoveryResponse:
        with self._lock:
            return self._view(self._session(session_id))

    def decide(self, request: DecisionRequest) -> RecoveryResponse:
        with self._lock:
            session = self._session(request.session_id)
            session.state = decision_state(session.state, session.attempts, request.decision)
            return self._view(session)

    def retry(self, request: RetryRequest) -> RecoveryResponse:
        samples, assets, digest = catalog()
        with self._lock:
            session = self._session(request.session_id)
            language = session.language_id
        self._check_sample(request.sample_id, language, samples, assets)
        return self._attempt(request.session_id, request.sample_id, samples, assets, digest, retry=request)

    def _attempt(self, identity: str, sample_id: str, samples, assets, digest: str,
                 retry: RetryRequest | None = None) -> RecoveryResponse:
        with self._lock:
            session = self._session(identity)
            if session.selection_sha != digest:
                raise RecoveryError("invalid_session", "Frozen sample selection changed; start a new simulation", 409)
            expected = RecoveryState.retry_or_refer if retry is not None else RecoveryState.ready
            if session.state != expected or session.attempts >= 2:
                raise RecoveryError("invalid_transition", "This session cannot transcribe another clip")
            if sample_id in session.used_ids:
                raise RecoveryError("invalid_sample", "Retry must use a different curated clip", 409)
            if retry is not None:
                if retry.source is not None:
                    session.requested_source = retry.source
                if retry.allow_saved_fallback is not None:
                    session.allow_saved_fallback = retry.allow_saved_fallback
            session.attempts += 1
            session.sample_id = sample_id
            session.used_ids.append(sample_id)
            session.transcript, session.source, session.fallback_reason = None, None, None
            session.transcription_status = ExperimentStatus.not_tested
            session.state = RecoveryState.transcribing
        saved, guided, _ = saved_evidence(samples, assets, digest)
        fallback = saved.get((sample_id, session.mode))
        attempt = None
        failure_status = ExperimentStatus.not_tested
        code, message, http_status, retryable = "api_unavailable", "No verified saved result is available for this clip/mode", 503, False
        if session.requested_source == Origin.saved:
            attempt = fallback
            if attempt:
                session_source = Origin.saved
        else:
            adapter = None
            try:
                if session.mode == "guided" and session.language_id not in guided:
                    raise ConfigurationError("Guidance is not verified", "guidance_not_verified")
                adapter = self._adapter_factory()
                attempt = adapter.transcribe(sample_id, session.mode).to_dict()
                session_source = Origin.live
                if attempt["status"] == "unsupported":
                    code, message, http_status = "unsupported_language", "Provider rejected language guidance for this recording", 422
                elif attempt["status"] == "incompatible_output":
                    code, message, http_status = "incompatible_output", "The provider output is not usable for confirmation", 422
                elif attempt["status"] == "completed" and not usable(attempt, session.language_id):
                    code, message, http_status = "unusable_transcript", "No usable transcript can be confirmed; retry or request human assistance", 422
                    if isinstance(attempt.get("transcript_raw"), str) and attempt["transcript_raw"].strip():
                        attempt["status"] = "incompatible_output"
                elif attempt["status"] == "technical_error":
                    code, message = "api_unavailable", "Live transcription is unavailable; retry or request human assistance"
                    retryable = bool(attempt.get("retryable"))
                    if any(word in (attempt.get("error_code") or "") for word in ("quota", "credit")):
                        code, message = "quota_exhausted", "Provider quota is unavailable; use a saved clip or human-assistance referral"
            except ConfigurationError as exc:
                attempt = None
                failure_status = ExperimentStatus.not_tested
                if exc.code == "guidance_not_verified":
                    code, message, http_status = "guidance_not_verified", "Live guidance has not been verified for this language", 422
                else:
                    code, message = "api_unavailable", "Live transcription is not configured or verified audio is unavailable"
            except (OSError, ValueError, KeyError):
                attempt = None
            finally:
                if adapter is not None:
                    adapter.close()
            if (attempt is None or not usable(attempt, session.language_id)) and session.allow_saved_fallback and fallback:
                attempt, session_source = fallback, Origin.saved
                with self._lock:
                    session.fallback_reason = code
        with self._lock:
            session.transcription_status = ExperimentStatus(attempt["status"]) if attempt else failure_status
            if attempt:
                session.source = session_source
            if attempt and usable(attempt, session.language_id):
                session.transcript = attempt["transcript_raw"]
                session.state = RecoveryState.confirm
                return self._view(session)
            session.state = RecoveryState.referral if session.attempts >= 2 else RecoveryState.retry_or_refer
            raise RecoveryError(code, message, http_status,
                                retryable=retryable and session.attempts < 2, session=self._view(session))
