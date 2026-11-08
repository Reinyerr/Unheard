"""Non-secret TTS catalog shared with React. dotenv is loaded by the existing entry points."""
import json
import os

from app.services.elevenlabs_adapter import REPO

CATALOG = json.loads((REPO / "shared/tts_prompts.json").read_text(encoding="utf-8"))
LANGUAGES = CATALOG["languages"]
MODEL = CATALOG["model_id"]
REVISION = CATALOG["prompt_revision"]
ATTRIBUTION = "AI-generated with ElevenLabs; UNHEARD-authored demo instruction, not the FLEURS speaker."


def settings(language: str) -> dict:
    if language not in LANGUAGES:
        raise ValueError("Select one of the six configured pilot languages")
    prompt = LANGUAGES[language]
    # Environment uses the existing backend dotenv convention. A differing value
    # is a configuration error, never permission to silently substitute a voice/model.
    if os.environ.get("ELEVENLABS_TTS_MODEL_ID", MODEL) != MODEL:
        raise ValueError("Only the selected eleven_v3 model is configured; no fallback")
    if os.environ.get(f"ELEVENLABS_TTS_VOICE_{language.upper()}", prompt["voice_id"]) != prompt["voice_id"]:
        raise ValueError("Voice environment setting differs from the explicitly selected voice")
    return prompt


def audio_path(language: str) -> str:
    if language not in LANGUAGES:
        raise ValueError("Unknown prompt language")
    return f"audio/prompts/{language}/confirm.mp3"
