"""Restricted synchronous Scribe adapter; provider acceptance requires live evidence.

Reference: https://elevenlabs.io/docs/api-reference/speech-to-text/convert
No retries, caching, metrics or automatic-to-guided fallback in this adapter.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Literal

import httpx

from app.schemas.research import Samples, validate_artifact

REPO = Path(__file__).resolve().parents[3]
API = "https://api.elevenlabs.io/v1"
MODEL_ID = "scribe_v2"
# Documented candidate hints, distinct from the dataset's ISO mappings.
# These are NOT proof of verified support for this account/model/recording.
GUIDANCE_CANDIDATES = {
    "english": "eng", "urdu": "urd", "punjabi": "pan", "cantonese": "yue",
    "arabic": "ara", "mandarin_chinese": "zho",
}
Mode = Literal["auto", "guided"]


def request_options(language_id: str, mode: Mode) -> dict[str, str]:
    """Canonical request settings shared by the adapter and experiment cache."""
    if language_id not in GUIDANCE_CANDIDATES or mode not in {"auto", "guided"}:
        raise ConfigurationError("Unknown language or transcription mode")
    options = {"model_id": MODEL_ID, "file_format": "other", "diarize": "false",
               "tag_audio_events": "false", "timestamps_granularity": "none", "webhook": "false"}
    if mode == "guided":
        options["language_code"] = GUIDANCE_CANDIDATES[language_id]
    return options


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConfigurationError(ValueError):
    """A local prerequisite is absent or inconsistent; no provider result implied."""

    def __init__(self, message: str, code: str = "invalid_local_configuration"):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ScribeAttempt:
    sample_id: str
    language_id: str
    mode: Mode
    model_id: str
    audio_sha256: str
    request_options: dict[str, str]
    started_at_utc: str
    finished_at_utc: str
    status: str
    transcript_raw: str | None
    http_status: int | None
    request_id: str | None
    response_headers: dict[str, str]
    error_code: str | None
    retryable: bool
    raw_response: str | None
    detected_language_code: str | None
    guidance_acceptance: str

    def to_dict(self) -> dict:
        return asdict(self)


def load_selection() -> tuple[Samples, dict[str, dict], str]:
    manifest_path = REPO / "data/processed/sampling_manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    content = {key: manifest[key] for key in ("schema_version", "source", "selection", "samples", "assets")}
    digest = hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if digest != manifest.get("selection_sha256"):
        raise ConfigurationError("Frozen sampling manifest checksum mismatch")
    samples = validate_artifact("samples", json.loads((REPO / "frontend/public/data/samples.v1.json").read_bytes()))
    if (samples.selection.model_dump(mode="json") != manifest["selection"]
            or [s.model_dump(mode="json") for s in samples.samples] != manifest["samples"]
            or samples.source.get("selection_sha256") != digest):
        raise ConfigurationError("Public samples disagree with frozen manifest")
    ids = samples.selection.ids
    if (len(ids) != 8 or len(samples.samples) != 48
            or {(s.language_id.value, s.fleurs_id) for s in samples.samples}
            != {(language, sentence) for language in GUIDANCE_CANDIDATES for sentence in ids}):
        raise ConfigurationError("Expected exactly eight frozen IDs across six pilot languages")
    assets = {asset["sample_id"]: asset for asset in manifest["assets"]}
    if len(assets) != 48 or len(manifest["assets"]) != 48 or set(assets) != {s.sample_id for s in samples.samples}:
        raise ConfigurationError("Frozen audio asset IDs disagree with samples")
    for sample in samples.samples:
        if assets[sample.sample_id]["audio_path"] != sample.audio_path:
            raise ConfigurationError("Frozen audio asset path disagrees with sample")
    return samples, assets, digest


class ElevenLabsAdapter:
    def __init__(self, *, client: httpx.Client | None = None):
        self._api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        if not self._api_key:
            raise ConfigurationError("ELEVENLABS_API_KEY is missing; configure it in the server environment",
                                     "missing_api_key")
        self.samples, self._assets, self.selection_sha256 = load_selection()
        self._by_id = {sample.sample_id: sample for sample in self.samples.samples}
        self._client = client or httpx.Client(timeout=httpx.Timeout(60, connect=10),
                                             follow_redirects=False, trust_env=False)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _safe(self, text: str) -> str:
        return text.replace(self._api_key, "[REDACTED]")

    def _audio(self, sample_id: str) -> bytes:
        if sample_id not in self._by_id:
            raise ConfigurationError("Unknown sample ID; only the frozen 48 samples are accepted")
        sample = self._by_id[sample_id]
        public = REPO / "frontend/public"
        path = public / sample.audio_path
        if path.is_symlink() or not path.resolve().is_relative_to(public.resolve()):
            raise ConfigurationError("Selected audio path escapes public asset directory")
        asset = self._assets[sample_id]
        if path.stat().st_size != asset["size_bytes"] or path.stat().st_size > 16 * 1024 * 1024:
            raise ConfigurationError("Selected audio size mismatch or exceeds 16 MiB limit")
        audio = path.read_bytes()
        if not audio.startswith(b"fLaC") or hashlib.sha256(audio).hexdigest() != asset["sha256"]:
            raise ConfigurationError("Selected audio is not the frozen FLAC")
        return audio

    def validate_sample(self, sample_id: str) -> None:
        """Verify an allowlisted clip without sending it to the provider."""
        self._audio(sample_id)

    def transcribe(self, sample_id: str, mode: Mode) -> ScribeAttempt:
        if mode not in {"auto", "guided"}:
            raise ConfigurationError("Expected auto or guided mode")
        audio = self._audio(sample_id)
        sample = self._by_id[sample_id]
        options = request_options(sample.language_id, mode)
        started = now()
        result = dict(sample_id=sample_id, language_id=sample.language_id.value, mode=mode,
                      model_id=MODEL_ID, audio_sha256=hashlib.sha256(audio).hexdigest(),
                      request_options=options, started_at_utc=started, status="technical_error",
                      transcript_raw=None, http_status=None, request_id=None, response_headers={},
                      error_code=None, retryable=False, raw_response=None,
                      detected_language_code=None, guidance_acceptance="not_tested")
        try:
            response = self._client.post(
                API + "/speech-to-text", headers={"xi-api-key": self._api_key}, data=options,
                files={"file": (Path(sample.audio_path).name, audio, "audio/flac")},
            )
            raw = self._safe(response.text)
            headers = {key: self._safe(value) for key, value in response.headers.items()
                       if key in {"request-id", "x-request-id", "retry-after", "x-ratelimit-limit",
                                  "x-ratelimit-remaining", "x-ratelimit-reset"}}
            result.update(http_status=response.status_code, raw_response=raw, response_headers=headers,
                          request_id=headers.get("request-id") or headers.get("x-request-id"))
            try:
                payload = json.loads(raw)
            except ValueError:
                payload = None
            if response.is_success:
                if mode == "guided":
                    result["guidance_acceptance"] = "accepted_by_api"
                if isinstance(payload, dict) and isinstance(payload.get("text"), str):
                    result.update(status="completed", transcript_raw=payload["text"])
                    if isinstance(payload.get("language_code"), str):
                        result["detected_language_code"] = payload["language_code"]
                else:
                    result.update(status="incompatible_output", error_code="unexpected_response_shape")
            else:
                detail = payload.get("detail") if isinstance(payload, dict) else None
                code = detail.get("status") if isinstance(detail, dict) else None
                code = code if isinstance(code, str) else f"http_{response.status_code}"
                result.update(error_code=code, retryable=(response.status_code == 429 or response.status_code >= 500))
                if "quota" in code or "credit" in code:
                    result["retryable"] = False
                # Only explicit language-option rejection establishes unsupported guidance.
                invalid_field = (isinstance(detail, list) and any(
                    isinstance(item, dict) and "language_code" in item.get("loc", []) for item in detail))
                if (mode == "guided" and response.status_code in {400, 422}
                        and (invalid_field or ("language" in code and any(
                            word in code for word in ("unsupported", "invalid", "not_supported"))))):
                    result.update(status="unsupported", guidance_acceptance="rejected_by_api", retryable=False)
        except httpx.TimeoutException:
            result.update(error_code="timeout", retryable=True)
        except httpx.TransportError:
            result.update(error_code="transport_error", retryable=True)
        return ScribeAttempt(**result, finished_at_utc=now())

    def subscription_snapshot(self) -> dict:
        """Keep numeric allowance evidence only; never export account/profile details."""
        result = {"observed_at_utc": now(), "http_status": None, "character_count": None,
                  "character_limit": None, "error_code": None}
        try:
            response = self._client.get(API + "/user/subscription", headers={"xi-api-key": self._api_key})
            result["http_status"] = response.status_code
            if response.is_success:
                payload = response.json()
                for key in ("character_count", "character_limit"):
                    if isinstance(payload, dict) and type(payload.get(key)) is int:
                        result[key] = payload[key]
                if any(result[key] is None for key in ("character_count", "character_limit")):
                    result["error_code"] = "unexpected_subscription_shape"
            else:
                result["error_code"] = f"http_{response.status_code}"
        except (httpx.TransportError, ValueError):
            result["error_code"] = "subscription_unavailable"
        return result
