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
