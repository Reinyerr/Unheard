"""Cache-only multilingual demo TTS. Explicit CLI authorization, one POST, no retries.

Official references: /docs/api-reference/text-to-speech/convert, /models/list,
/voices/get and /docs/overview/models at https://elevenlabs.io (2026-11-07).
No arbitrary text, dataset transcript, replacement voice or cloning endpoint.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os

import httpx

from app.services.elevenlabs_adapter import API, REPO
from app.services.tts_config import ATTRIBUTION, LANGUAGES, MODEL, REVISION, audio_path, settings

LOCAL = REPO / "data/local/tts"
PUBLIC = REPO / "frontend/public/audio/prompts"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mp3_signature(raw: bytes) -> bool:
    return 128 < len(raw) <= 2_000_000 and (raw.startswith(b"ID3") or raw[0] == 255 and raw[1] & 224 == 224)


def validate_manifest(manifest: dict, raw: bytes, language: str, approved: bool) -> bool:
    prompt = settings(language)
    return (manifest["schema_version"] == "2.0" and manifest["language_id"] == language
            and manifest["language_code"] == prompt["language_code"] and manifest["text"] == prompt["text"]
            and manifest["prompt_revision"] == REVISION and manifest["model_id"] == MODEL
            and manifest["voice_id"] == prompt["voice_id"] and manifest["provider"] == "elevenlabs"
            and manifest["audio_path"] == audio_path(language) and manifest["origin"] == "saved"
            and manifest["rights_reviewed"] is True and manifest["attribution"] == ATTRIBUTION
            and bool(manifest["generated_at_utc"]) and mp3_signature(raw)
            and hashlib.sha256(raw).hexdigest() == manifest["audio_sha256"]
            and manifest["verification"]["synthesis_http_status"] == 200
            and manifest["verification"]["model_language_advertised"] is True
            and manifest["verification"]["voice_access"] == "accessible"
            and (not approved or (manifest["review_status"] == "approved"
                                 and manifest["human_listened"] is True
                                 and manifest["language_reviewed"] is True and bool(manifest["approved_at_utc"]))))


def cached_prompt(language: str) -> dict | None:
    if language not in LANGUAGES:
        return None
    try:
        manifest = json.loads((PUBLIC / language / "manifest.json").read_bytes())
        raw = (PUBLIC / language / "confirm.mp3").read_bytes()
        return manifest if validate_manifest(manifest, raw, language, approved=True) else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def inspect(client: httpx.Client, model: dict, language: str) -> dict:
    prompt = settings(language)
    advertised = model.get("can_do_text_to_speech") is True and prompt["language_code"] in {
        row["language_id"] for row in model.get("languages", [])}
    result = {"model_id": MODEL, "voice_id": prompt["voice_id"], "language_code": prompt["language_code"],
              "model_language_advertised": advertised, "voice_access": "not_checked",
              "voice_model_compatibility": "unconfirmed", "checked_at_utc": now(),
              "note": "Metadata access is not synthesis, pronunciation or playback verification"}
    response = client.get(f"/voices/{prompt['voice_id']}")
    result["voice_http_status"] = response.status_code
    if response.status_code != 200:
        result["voice_access"] = "inaccessible"
        return result
    voice = response.json()
    if voice.get("voice_id") != prompt["voice_id"]:
        result["voice_access"] = "identity_mismatch"
        return result
    result["voice_access"] = "accessible"
    result["voice_category"] = voice.get("category")
    verification = voice.get("voice_verification") or {}
    result["voice_permission_blocked"] = verification.get("requires_verification") is True and verification.get("is_verified") is not True
    if MODEL in (voice.get("high_quality_base_model_ids") or []) or any(
        row.get("model_id") == MODEL and row.get("language") == prompt["language_code"]
        for row in voice.get("verified_languages") or []
    ):
        result["voice_model_compatibility"] = "advertised_by_voice_metadata"
    # These metadata lists are not exhaustive allowlists. A missing model is
    # unconfirmed, not unsupported; an authorized synthesis is the next evidence.
    return result


def prepare(languages: list[str], live: bool, rights_reviewed: bool) -> dict:
    report = {"schema_version": "2.0", "model_id": MODEL, "checked_at_utc": now(), "languages": {}}
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        report["status"] = "blocked_missing_credentials"
        report["languages"] = {language: {"voice_id": settings(language)["voice_id"],
            "voice_access": "not_checked", "model_language_advertised": None,
            "voice_model_compatibility": "unconfirmed"} for language in languages}
        return report
    with httpx.Client(base_url=API, headers={"xi-api-key": key}, timeout=40, follow_redirects=False) as client:
        response = client.get("/models")
        response.raise_for_status()
        model = next((row for row in response.json() if row.get("model_id") == MODEL), {})
        for language in languages:
            result = inspect(client, model, language)
            report["languages"][language] = result
            if live:
                if not result["model_language_advertised"] or result["voice_access"] != "accessible" or result["voice_permission_blocked"]:
                    raise ValueError("Model/language or voice access not established; no synthesis requested")
                generate(client, language, result, rights_reviewed)
    report["status"] = "metadata_checked" if not live else "pending_review"
    return report


def generate(client: httpx.Client, language: str, verification: dict, rights_reviewed: bool) -> None:
    if not rights_reviewed:
        raise ValueError("Account/voice rights review required")
    prompt = settings(language)
    stage = LOCAL / language
    stage.mkdir(parents=True, exist_ok=True)
    payload = {"text": prompt["text"], "model_id": MODEL, "language_code": prompt["language_code"]}
    # Exclusive marker remains after any timeout/failure. Never automatically
    # replay a potentially billed request or overwrite a staged/approved sample.
    with (stage / "attempt.json").open("x", encoding="utf-8") as marker:
        json.dump({"started_at_utc": now(), "voice_id": prompt["voice_id"], "request": payload,
                   "explicit_billable_authorization": True}, marker, ensure_ascii=False)
    with client.stream("POST", f"/text-to-speech/{prompt['voice_id']}",
                       params={"output_format": "mp3_44100_128"}, json=payload) as response:
        response.raise_for_status()
        if response.status_code != 200 or response.headers.get("content-type", "").split(";")[0] != "audio/mpeg":
            raise ValueError("Provider returned no MP3; prompt remains unavailable")
        raw = bytearray()
        for chunk in response.iter_bytes():
            raw.extend(chunk)
            if len(raw) > 2_000_000:
                raise ValueError("Prompt exceeds audio size limit")
    if not mp3_signature(raw):
        raise ValueError("Provider audio has no MP3 signature")
    (stage / "confirm.mp3").write_bytes(raw)
    manifest = {"schema_version": "2.0", "language_id": language, "language_code": prompt["language_code"],
        "text": prompt["text"], "prompt_revision": REVISION, "provider": "elevenlabs", "model_id": MODEL,
        "voice_id": prompt["voice_id"], "origin": "saved", "generated_at_utc": now(),
        "verification": {**verification, "synthesis_http_status": response.status_code,
                         "request_id": response.headers.get("request-id")},
        "audio_path": audio_path(language), "audio_sha256": hashlib.sha256(raw).hexdigest(),
        "review_status": "pending_review", "human_listened": False, "language_reviewed": False,
        "approved_at_utc": None, "rights_reviewed": True, "attribution": ATTRIBUTION}
    write_json(stage / "manifest.json", manifest)


def approve(language: str, digest: str) -> None:
    settings(language)
    stage = LOCAL / language
    manifest = json.loads((stage / "manifest.json").read_bytes())
    raw = (stage / "confirm.mp3").read_bytes()
    if digest != hashlib.sha256(raw).hexdigest() or not validate_manifest(manifest, raw, language, approved=False):
        raise ValueError("Approval must identify the exact reviewed language/voice/model/prompt/audio checksum")
    manifest.update(review_status="approved", human_listened=True, language_reviewed=True, approved_at_utc=now())
    target = PUBLIC / language
    target.mkdir(parents=True, exist_ok=True)
    (target / "confirm.mp3").write_bytes(raw)
    write_json(target / "manifest.json", manifest)
    if cached_prompt(language) is None:
        (target / "manifest.json").unlink(missing_ok=True)
        raise ValueError("Prompt provenance validation failed")
    write_json(stage / "manifest.json", manifest)


def main() -> None:
    from dotenv import load_dotenv
    load_dotenv(REPO / "backend/.env")
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Metadata GETs only; no synthesis")
    group.add_argument("--live", action="store_true", help="Prepare exactly one language; requires explicit billed-request authorization")
    group.add_argument("--approve", metavar="SHA256", help="Approve the exact listened-to MP3 checksum")
    parser.add_argument("--language", choices=list(LANGUAGES))
    parser.add_argument("--authorize-billable", action="store_true", help="Explicitly authorize one billed request for --language")
    parser.add_argument("--rights-reviewed", action="store_true")
    parser.add_argument("--language-reviewed", action="store_true", help="Attest caption/labels, spoken language, pronunciation and meaning were manually reviewed")
    args = parser.parse_args()
    try:
        if args.check:
            report = prepare([args.language] if args.language else list(LANGUAGES), False, False)
            LOCAL.mkdir(parents=True, exist_ok=True)
            write_json(LOCAL / "preflight.json", report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            if report["status"].startswith("blocked"):
                parser.exit(1, "No metadata requests made: server credentials unavailable.\n")
        elif args.live:
            if not args.language or not args.authorize_billable or not args.rights_reviewed:
                raise ValueError("Select one language and explicitly authorize its billed request and rights review")
            report = prepare([args.language], True, True)
            if report["status"] != "pending_review":
                raise ValueError("Missing credentials; no synthesis requested")
            print("One prompt staged pending manual listening/language review. No demo playback enabled.")
        else:
            if not args.language or not args.language_reviewed:
                raise ValueError("Approval requires one language and manual listening/language review")
            approve(args.language, args.approve)
            print("Approved exact cached prompt for localhost playback.")
    except (OSError, ValueError, KeyError, TypeError, httpx.HTTPError) as exc:
        if args.check:
            # Replace stale metadata success with a safe failure, without storing
            # provider response bodies, headers, credentials or voice-owner data.
            LOCAL.mkdir(parents=True, exist_ok=True)
            write_json(LOCAL / "preflight.json", {"schema_version": "2.0", "model_id": MODEL,
                "checked_at_utc": now(), "status": "blocked_metadata_error",
                "language_ids": [args.language] if args.language else list(LANGUAGES),
                "http_status": exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None})
        parser.exit(1, "TTS unavailable: configuration, access, existing attempt or cache/provider failure. No fallback/retry. Check server configuration and retained local metadata.\n")


if __name__ == "__main__":
    main()
