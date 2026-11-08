"""MOCK MP3 header and approval metadata; no generated or playable audio."""
import hashlib
import json

from app.services import tts_adapter as tts
from app.services.tts_config import ATTRIBUTION, LANGUAGES, MODEL, REVISION, audio_path


def test_only_exact_approved_cache_is_available(tmp_path, monkeypatch):
    language = "urdu"
    config = LANGUAGES[language]
    raw = b"ID3" + bytes(200)
    manifest = dict(schema_version="2.0", language_id=language, language_code=config["language_code"],
        text=config["text"], voice_id=config["voice_id"], model_id=MODEL, prompt_revision=REVISION,
        provider="elevenlabs", audio_path=audio_path(language), origin="saved", rights_reviewed=True,
        attribution=ATTRIBUTION, generated_at_utc="2026-11-07T00:00:00Z", audio_sha256=hashlib.sha256(raw).hexdigest(),
        verification=dict(synthesis_http_status=200, model_language_advertised=True, voice_access="accessible"),
        review_status="approved", human_listened=True, language_reviewed=True, approved_at_utc="2026-11-07T00:00:00Z")
    monkeypatch.setattr(tts, "PUBLIC", tmp_path)
    directory = tmp_path / language
    directory.mkdir()
    assert tts.cached_prompt(language) is None
    (directory / "confirm.mp3").write_bytes(raw)
    path = directory / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert tts.cached_prompt(language) == manifest
    for key, value in [("review_status", "pending_review"), ("human_listened", False), ("language_reviewed", False),
                       ("voice_id", "wrong"), ("language_id", "english"), ("audio_sha256", "0" * 64)]:
        path.write_text(json.dumps({**manifest, key: value}), encoding="utf-8")
        assert tts.cached_prompt(language) is None, key
