# T-008 — Validate real Scribe requests, language hints and credits

**Status:** Blocked — adapter/preflight implemented; live verification requires a server API key.
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

## Implementation evidence — 2026-11-07

On `feature/data-backend`, T-001 health bootstrap, T-003 schemas/identities and
T-007's frozen 48-sample manifest/public audio exist. T-003/T-007 review gates
remain open. No commit created and no unrelated implementation added.

Created `backend/app/services/__init__.py`,
`backend/app/services/elevenlabs_adapter.py` and `scripts/preflight_scribe.py`.
Updated script usage, server-key example, local-schema decision clarification
and index. Generated ignored `data/local/preflight_log.json` and per-run evidence
under `data/local/preflight_runs/`. No React/public-contract changes or new
dependencies. Existing `httpx` is used directly with an injectable client.

Documentation reviewed: official [conversion reference](https://elevenlabs.io/docs/api-reference/speech-to-text/convert),
[STT language list](https://elevenlabs.io/docs/overview/capabilities/speech-to-text/),
and [subscription endpoint](https://elevenlabs.io/docs/api-reference/user/subscription/get).
Adapter uses `scribe_v2`, multipart FLAC upload, API v1 and documented candidate
ISO-639-3 hints (eng/urd/pan/yue/ara/zho). These choices are documentation-based,
not yet verified live. Provider model alias is recorded; an immutable underlying
model revision is unknown. No SDK syntax or dataset hint support is presumed.

The adapter accepts only frozen sample IDs, checks manifest/public agreement,
all six × eight identities and selected audio size/hash/signature, and never
accepts arbitrary uploads. Auto omits `language_code`; guided adds only its
documented candidate. It returns explicit status, options, timestamps, raw
transcript/response, detected code, safe request/rate headers and provider error
code. No fallback or retries. Empty successful text remains completed; malformed
successful output is incompatible_output; explicit language rejection is
unsupported; HTTP/transport failures are technical_error. Script/translation
comparability remains T-010 review. API acceptance alone is not quality proof.

Default CLI plans first frozen Urdu and Cantonese clips, auto and guided (4
POSTs); `--languages` allows a chosen subset up to all six (12 POSTs maximum).
It collects numeric subscription snapshots before/after where permitted, without
account/profile details; this does not establish STT cost or 96-request budget.
It stops on authentication/permission/rate/quota failures, preserving partial
evidence. It saves each response locally with known-key redaction, logs only
allowlisted headers, and never prints transcripts, key or raw exception text.
Each invocation has a separate run directory; the latest log is replaced from
the start to prevent stale success. There is no cache: reruns with a key can bill
again; T-009 owns resumable experiment caching.

Observed production command, available Python 3.14.7/httpx environment:

```sh
python3 scripts/preflight_scribe.py
```

Exit 1; blocked with `missing_api_key`, zero attempts, all guidance not_tested.
Neither exported key nor root `.env` was present. No remote requests, credit
usage, successful transcripts or supported/rejected guidance were observed.
The pinned backend environment was not installed. No automated tests/test files
were created or run, per user instructions; acceptance checkboxes remain open.

Manual live preflight (zsh, from repository root; hidden input avoids key history):

```sh
read -rs 'ELEVENLABS_API_KEY?ElevenLabs API key: '
export ELEVENLABS_API_KEY
python3 scripts/preflight_scribe.py
```

Review `data/local/preflight_log.json` and the linked raw local response files.
Verify actual transcript/language and HTTP/options/IDs; inspect separate guidance
acceptance for Urdu/Cantonese, rate/quota fields and allowance snapshots. A run
status of recorded means evidence captured, not human sign-off. To probe remaining
pilot languages later, explicitly choose them with `--languages`; unprobed
languages remain not_tested. Do not publish the local logs or copy a key here.

Blocker: configure the server environment key and perform/review real preflight.
T-010 is next after that evidence exists; T-009 remains blocked by live T-008
verification and missing T-010. No later ticket was implemented and T-008 is not
marked Done. Urdu/cached demo regression and automated error-path tests remain
unperformed.
