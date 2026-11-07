# T-008 — Validate real Scribe requests, language hints and credits

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-001`, `T-003`, `T-007`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Validate actual supported ElevenLabs behavior before building a 96-request pipeline.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `backend/app/services/elevenlabs_adapter.py`
- `scripts/preflight_scribe.py`
- `data/local/preflight_log.json (ignored)`

## Step-by-step implementation plan

1. Load ElevenLabs API key from environment, never frontend.
2. Use a selected real FLAC sample and current official Scribe documentation to verify model ID, upload format, request and response shape.
3. Try auto detection and correct-language guidance in controlled small pilot (including Cantonese if supported).
4. Record exact API options, language support/unsupported, response IDs, timestamps, quota/rate/error codes.
5. Keep request logic behind injectable adapter that unit tests can mock.

## Implementation guidance (illustrative, not built yet)

```python
# PSEUDOCODE — verify SDK/API field names before implementing
def transcribe(sample, language_hint=None):
    payload = build_verified_scribe_request(sample, language_hint)
    return elevenlabs_adapter.send(payload)
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Cantonese code `yue` in dataset is NOT proof ElevenLabs accepts it.
- No API key is a configuration error, not 0% accuracy.
- Bound requests to preapproved local sample IDs; avoid arbitrary uploads.

## Acceptance tests

- [ ] One actual auto transcription verified and recorded.
- [ ] Supported or unsupported guidance response documented, not inferred.
- [ ] Unit mock for timeout/rate limit returns explicit status and does not leak secrets.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
