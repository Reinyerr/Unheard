# Local confirmation/retry/referral API

T-014 implementation uses the existing FastAPI/Pydantic/httpx runtime and T-008
restricted Scribe adapter. No microphone, uploads, intent routing, autonomous
actions, database, auth or TTS is implemented. Frontend integration is T-015.

From the repository root, with the existing backend runtime installed:

```sh
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

One process owns bounded in-memory sessions (128 maximum; 1800-second idle TTL).
Restart/reload loses sessions. No API key is required for real saved outcomes.
The server reads the existing root `.env`/exported environment; keys stay server
side. Explicit `source: live` can incur charges; no automatic network retries.

In another terminal, inspect the actual curated/saved choices and start Urdu:

```sh
curl --silent http://127.0.0.1:8000/api/recovery/capabilities
curl --silent -H 'Content-Type: application/json' --data '{"language_id":"urdu","sample_id":"urdu-1533"}' http://127.0.0.1:8000/api/recovery/start
```

Default `source` is saved, `mode` is auto, allow_saved_fallback is true. Existing
saved evidence currently supports Urdu 1533 in both modes and Cantonese 1533 in
guided mode. All other frozen sample IDs are known but do not yet have usable
saved output. Capabilities list selected IDs separately from saved IDs; key
presence is not proof of working credentials/credit allowance. Missing source
data does not prevent /health startup; recovery endpoints return safe errors.

Copy the returned session_id into this shell variable (replace the placeholder):

```sh
RECOVERY_SESSION_ID='replace-with-returned-32-character-session-id'
curl --silent -H 'Content-Type: application/json' --data "{\"session_id\":\"$RECOVERY_SESSION_ID\",\"decision\":\"correct\"}" http://127.0.0.1:8000/api/recovery/decision
```

Only explicit correct from confirm accepts. Instead choose incorrect to enter
retry_or_refer after attempt 1. Retry preserves the session and mode, consumes
the second/final attempt and requires a different curated same-language clip:

```sh
curl --silent -H 'Content-Type: application/json' --data "{\"session_id\":\"$RECOVERY_SESSION_ID\",\"decision\":\"incorrect\"}" http://127.0.0.1:8000/api/recovery/decision
curl --silent -H 'Content-Type: application/json' --data "{\"session_id\":\"$RECOVERY_SESSION_ID\",\"sample_id\":\"urdu-1537\"}" http://127.0.0.1:8000/api/recovery/retry
```

These are alternative paths: incorrect after already accepting is invalid. With
current evidence the second command has no saved Urdu 1537 result and returns a
safe 503 plus session in referral, not an invented transcript. To confirm two
usable distinct clips, first obtain permitted real results or explicitly choose
live with a valid server key. Missing saved outcomes and provider failures count
toward two total attempts; invalid IDs/transitions do not. Two rejections also
lead to referral. A third retry is rejected. A fresh start creates a separate
simulation; it is not a retry/reset of the previous session.

The user can choose refer from confirm/retry_or_refer without further requests:

```sh
curl --silent -H 'Content-Type: application/json' --data "{\"session_id\":\"$RECOVERY_SESSION_ID\",\"decision\":\"refer\"}" http://127.0.0.1:8000/api/recovery/decision
curl --silent "http://127.0.0.1:8000/api/recovery/sessions/$RECOVERY_SESSION_ID"
```

Accepted/referral sessions are terminal. During a live transcription decisions
and retries are rejected. Retry IDs are unused curated clips, not promises of
saved/provider availability. Changing source on retry requires explicit source
in that retry request; mode and selected language remain fixed.

For same-clip fallback, start with `source: live`. If the provider/key is unavailable
and a verified same-mode saved response exists, the response labels source saved,
requested_source live and fallback_reason. Set allow_saved_fallback false to
receive the provider/config error instead. Guided live mode requires recorded
language support; the service does not infer support from dataset codes and does
not silently switch guided to auto. Failed calls include a usable session ID and
retry/referral state. Raw provider paths/headers, speech metadata and keys are
never returned. No new live outcome is persisted as research/demo cache here.

Only strict JSON bodies up to 4096 bytes are accepted; no uploads/arbitrary paths,
compressed content or extra fields. Errors have a safe error envelope, plus
session after a consumed failed attempt. See docs/DATA_CONTRACTS.md for fields,
statuses and HTTP codes; interactive OpenAPI is at http://127.0.0.1:8000/docs.

Every session labels third-party confirmation as a simulation. Referral only
suggests official human-assistance channels; it never claims to connect a call.
Text confirmation is available, prompt_audio_url is null and tts_status is
unavailable pending T-015. Review gates remain open: no automated tests were
written/run, no new ElevenLabs/TTS calls or full two-clip/frontend/outage rehearsal
were performed. Manual HTTP proof covers health, capabilities, saved Urdu,
explicit saved fallback with missing key and correct-to-accepted only.

## T-015 multilingual cached recovery instructions

All six exact user-selected voice IDs and draft authored prompts are in
`shared/tts_prompts.json`, consumed by backend `tts_config.py` and React. The
existing dotenv entry points read `backend/.env` (or exported server variables).
`.env.example` contains a blank key plus non-secret voice/model defaults; never
load it as credentials or expose a key through `VITE_`. Conflicting voice/model
environment values fail closed. `eleven_v3` is the sole selected model; no silent
model or voice substitutions. Prior English-only/premade restrictions are
superseded by the user-selected multilingual configuration; no cloning is added.

Official references checked 2026-11-07:
[model language list](https://elevenlabs.io/docs/overview/models),
[convert endpoint](https://elevenlabs.io/docs/api-reference/text-to-speech/convert),
[model metadata](https://elevenlabs.io/docs/api-reference/models/list), and
[voice metadata](https://elevenlabs.io/docs/api-reference/voices/get).
The docs list ur, pa, yue, ar, zh and en for eleven_v3. Availability to this
account and voice compatibility remain unconfirmed until actual evidence.

From the repository root, inspect metadata only (one model GET and six voice
GETs; zero audio POSTs), or add `--language urdu` for just the priority voice:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.services.tts_adapter --check
```

The ignored `data/local/tts/preflight.json` records minimal observations. A
successful voice GET means accessible, not verified speech quality or synthesis
permission. Voice model metadata is advisory; absent model entries remain
unconfirmed, not automatically unsupported. No API key is configured currently:
observed preflight exited 1 with blocked_missing_credentials and zero requests.

Only after explicit authorization for the chosen language and review of the
account/voice usage terms, prepare one short sample (Urdu first):

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.services.tts_adapter --language urdu --live --authorize-billable --rights-reviewed
open data/local/tts/urdu/confirm.mp3
cat data/local/tts/urdu/manifest.json
```

This checks model-advertised language and exact voice access, then sends at most
one `POST https://api.elevenlabs.io/v1/text-to-speech/{assigned_voice_id}` with
`output_format=mp3_44100_128` and JSON `text`, `model_id=eleven_v3`,
`language_code=ur` (or pa/yue/ar/zh/en for the chosen language). No retries.
The explicit authorization flag applies to this one selected language only;
there is no bulk generation command. It sends only the fixed authored
instruction, not a dataset transcript or recording. Provider rejection leaves
text fallback; it never silently changes voice/model/language.

Audio and metadata are staged under `data/local/tts/{language_id}/`, marked
pending_review. Review the entire audio and draft caption/button labels with a
speaker competent in that language; check pronunciation, language, meaning and
playability. Then approve its exact audio_sha256 from the local manifest:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.services.tts_adapter --language urdu --approve REPLACE_WITH_LISTENED_AUDIO_SHA256 --language-reviewed
```

For another language replace `urdu` in commands/paths with exactly `punjabi`,
`cantonese`, `arabic`, `mandarin_chinese`, or `english`, obtaining separate explicit
billable authorization and manual approval each time. These commands were not
run for generation/approval. All six currently remain text-only.

Approval copies only the exact approved MP3 and schema-2.0 provenance to
`frontend/public/audio/prompts/{language_id}/confirm.mp3` and `manifest.json`.
Runtime endpoints never generate audio. React independently checks the exact
language/code/voice/model/text/revision/path, approval flags, generation evidence
and SHA-256 before offering native playback in confirm state. Decode/playback
failure returns to text-only. A caption is an instruction to review the displayed
transcript, not a readback or the FLEURS speaker's voice. Existing T-014 transitions,
two-attempt budget, retries/referral and saved transcription provenance remain.
Capabilities enumerate only approved cached languages, never merely configured
voices. Backend outage still permits separately labelled saved browser sessions.

An exclusive attempt marker prevents replay or overwrite after interruption,
failure or success; inspect retained evidence before arranging any separately
authorized regeneration. Do not delete the marker to retry blindly. MP3/raw
staging remains ignored. T-019 public-package/licence review still applies.
No verified audio is supplied. Build/syntax checks passed; automated tests were
explicitly prohibited. New multilingual listening/playback, real outage and the
full recovery acceptance walkthrough remain pending.
