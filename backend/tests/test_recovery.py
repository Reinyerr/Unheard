"""MOCK provider/catalog at I/O boundaries; real routes, validation and state machine."""
import hashlib
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.schemas.research import Sample
from app.services import recovery_state as recovery


@pytest.fixture
def client(tmp_path, monkeypatch):
    samples, assets = [], {}
    for i in (1, 2):
        sample = Sample(sample_id=f"urdu-{i}", language_id="urdu", fleurs_id=i,
                        audio_path=f"audio/mock-{i}.flac", raw_reference_transcript="MOCK",
                        reference_transcript="MOCK", gender="other", duration_sec=None)
        raw = b"fLaC" + bytes(64)  # MOCK header, not playable speech
        path = tmp_path / "frontend/public" / sample.audio_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        samples.append(sample)
        assets[sample.sample_id] = {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    saved = {(s.sample_id, "auto"): {"status": "completed", "transcript_raw": "سلام"} for s in samples}
    monkeypatch.setattr(recovery, "REPO", tmp_path)
    monkeypatch.setattr(recovery, "catalog", lambda: (SimpleNamespace(samples=samples), assets, "mock-selection"))
    monkeypatch.setattr(recovery, "saved_evidence", lambda *args: (saved, {"urdu"}, []))
    monkeypatch.setattr(recovery, "cached_prompt", lambda language: None)
    adapter = Mock()
    adapter.transcribe.return_value.to_dict.return_value = {"status": "technical_error", "transcript_raw": None, "error_code": "timeout", "retryable": True}
    app = create_app()
    app.state.recovery_service = recovery.RecoveryService(adapter_factory=lambda: adapter)
    return TestClient(app), adapter


def start(client, **overrides):
    return client.post("/api/recovery/start", json={"language_id": "urdu", "sample_id": "urdu-1", **overrides})


def test_explicit_confirmation_and_terminal_session(client):
    http, adapter = client
    first = start(http).json()
    assert first["state"] == "confirm" and first["attempts"] == 1
    assert first["tts_status"] == "unavailable" and first["prompt_audio_url"] is None
    assert "simulation" in first["simulation_notice"]
    identity = first["session_id"]
    assert http.post("/api/recovery/decision", json={"session_id": identity, "decision": "correct"}).json()["state"] == "accepted"
    assert http.post("/api/recovery/retry", json={"session_id": identity, "sample_id": "urdu-2"}).status_code == 409
    assert http.get(f"/api/recovery/sessions/{identity}").json()["attempts"] == 1
    adapter.transcribe.assert_not_called()


def test_two_rejections_different_clip_then_referral(client):
    http, _ = client
    identity = start(http).json()["session_id"]
    decision = {"session_id": identity, "decision": "incorrect"}
    first = http.post("/api/recovery/decision", json=decision).json()
    assert first["retry_available"] and first["retry_sample_ids"] == ["urdu-2"]
    assert http.post("/api/recovery/decision", json=decision).status_code == 409
    assert http.post("/api/recovery/retry", json={"session_id": identity, "sample_id": "urdu-1"}).status_code == 409
    assert http.post("/api/recovery/retry", json={"session_id": identity, "sample_id": "urdu-2"}).json()["attempts"] == 2
    final = http.post("/api/recovery/decision", json=decision).json()
    assert final["state"] == "referral" and not final["retry_available"]
    assert "has not contacted" in final["referral_message"]
    assert http.post("/api/recovery/retry", json={"session_id": identity, "sample_id": "urdu-1"}).status_code == 409


@pytest.mark.parametrize("status,error_code,http_status", [("technical_error", "timeout", 503), ("technical_error", "quota_exceeded", 503), ("unsupported", "unsupported", 422)])
def test_provider_failures_are_explicit_and_bounded(client, status, error_code, http_status):
    http, adapter = client
    adapter.transcribe.return_value.to_dict.return_value = {"status": status, "transcript_raw": None, "error_code": error_code, "retryable": True}
    response = start(http, source="live", allow_saved_fallback=False)
    assert response.status_code == http_status
    session = response.json()["session"]
    assert session["state"] == "retry_or_refer" and session["transcription_status"] == status
    assert session["transcript"] is None
    assert http.post("/api/recovery/decision", json={"session_id": session["session_id"], "decision": "correct"}).status_code == 409
    assert http.post("/api/recovery/decision", json={"session_id": session["session_id"], "decision": "refer"}).json()["state"] == "referral"
    adapter.transcribe.assert_called_once_with("urdu-1", "auto")
    adapter.close.assert_called_once()


def test_live_failure_same_mode_saved_fallback(client):
    http, adapter = client
    response = start(http, source="live").json()
    assert response["state"] == "confirm" and response["source"] == "saved"
    assert response["requested_source"] == "live" and response["fallback_reason"] == "api_unavailable"
    adapter.transcribe.assert_called_once()


def test_invalid_inputs_and_audio_integrity(client, tmp_path):
    http, _ = client
    assert start(http, sample_id="../../secret").status_code == 400
    assert start(http, sample_id="urdu-99").status_code == 400
    assert start(http, language_id="arabic").status_code == 400
    assert http.post("/api/recovery/start", content="x" * 4097, headers={"Content-Type": "application/json"}).status_code == 413
    assert http.post("/api/recovery/start", content="{}").status_code == 415
    (tmp_path / "frontend/public/audio/mock-1.flac").write_bytes(b"corrupt")
    assert start(http).json()["error"]["code"] == "sample_unavailable"
