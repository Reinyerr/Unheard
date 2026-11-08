# T-014 — Implement deterministic confirmation/retry/referral API

**Status:** In review — implemented; manual saved-mode HTTP proof recorded; automated tests skipped at user request.
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-001`, `T-003`, `T-008`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Provide predictable safety-oriented verification without autonomous municipal actions.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `backend/app/routes/recovery.py`
- `backend/app/services/recovery_state.py`
- `backend/tests/test_recovery.py`

## Step-by-step implementation plan

1. Define states and validated transitions per ARCHITECTURE and DATA_CONTRACTS.
2. Accept only known curated sample IDs and valid selected language; restrict payload sizes.
3. Use verified ElevenLabs output or clearly marked saved result to enter confirmation state.
4. Accept explicit correct/incorrect, permit one additional attempt with a *different* clip.
5. After attempts exhausted return a referral message—no pretend call to a live 311 representative.

## Implementation guidance (illustrative, not built yet)

```python
if state == 'confirm' and decision == 'incorrect':
    next_state = 'retry_or_refer' if attempts < 2 else 'referral'
elif state == 'confirm' and decision == 'correct':
    next_state = 'accepted'
else:
    raise InvalidTransition()
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Two total attempts means one retry; no infinite loop.
- Confirm cannot occur before a usable transcript.
- Handle sessions without exposing speech metadata or keys to browser.

## Acceptance tests

- [ ] Correct transitions yield accepted.
- [ ] Two rejections yield referral, no further retry.
- [ ] Unknown sample, invalid transition and API error return meaningful 4xx/5xx with safe details.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.


## Implementation evidence — 2026-11-07

Branch feature/data-backend. T-001 health bootstrap, T-003 shared identities/
state/status/origin enums, and T-008 restricted adapter with real Urdu/Cantonese
preflight are present. Their remaining review gates were preserved. No commit
created; previous uncommitted ticket work left intact.

Created backend/app/schemas/recovery.py, backend/app/routes/__init__.py,
backend/app/routes/recovery.py and backend/app/services/recovery_state.py.
Updated app/main.py to register routes and permit POST/Content-Type on the same
localhost CORS origins; /health response remains unchanged. Updated final API
contracts, decision clarification, usage and index. No React/static research
schema changes, sponsor additions, datasets, TTS, mic capture, databases or auth.
The suggested test file was not created under the explicit no-tests instruction.

Contract impact explicitly identified before coding: finalize optional source/
mode/fallback inputs and nullable actual origin on failure; add /retry preserving
session/attempt count plus /sessions/{id} retrieval; add refer decision and typed
capability/session fields. Existing shared enums stay unchanged. The frontend
has no implemented recovery endpoint types to modify; T-015 will consume the
concrete API described in DATA_CONTRACTS.md/OpenAPI.

Behavior: explicit confirmation alone accepts; one retry uses a different known
same-language clip; second rejection/failure leads to referral; terminal sessions
cannot retry. Provider/config/saved-result failures return safe HTTP error plus
session state. Same sample/mode saved fallback is labelled saved with reason.
Saved evidence verifies frozen provenance/options/audio hash and actual retained
response strings; manual/automatic incompatibility exclusions are honored.
No invented transcript or reference-as-provider-output. Selected audio itself is
size/hash/FLAC checked before starting/retrying. Live guided requests require
recorded accepted support. Unknown guidance and missing key stay not_tested.

State is in-memory, bounded (128 sessions/1800-second idle TTL), concurrency
reservations prevent double attempts, and transcribing rejects decisions/retries.
POSTs accept only <=4096-byte JSON; extra fields, arbitrary paths/uploads and
invalid enums/IDs are rejected. Errors expose no key, raw response/path or speaker
metadata. TTS is unavailable with null prompt_audio_url. Simulated confirmation
and no-real-contact referral notices are included on every session response.

Runtime initially lacked FastAPI/Uvicorn/dotenv. Installed only those existing
production dependencies at repository-pinned versions into ignored backend/.venv
with --system-site-packages (plus their required transitive dependencies). No
requirements/lockfile changes or test dependency installation. Observed Python
3.14.7, FastAPI 0.162.2, Uvicorn 0.54.0, dotenv 1.2.4; inherited Pydantic 2.13.5
and httpx, rather than a clean install of all pinned backend dependencies.

Production start command:

```sh
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Restricted loopback binding/requests initially failed with environment permission
errors. With authorized loopback access the server started and manual curl calls
observed:

- /health 200 with unchanged ok/local response.
- /capabilities 200: 48 selected IDs, no live key configured, no warnings; usable
  saved Urdu auto/guided and Cantonese guided sample 1533, no incompatible auto.
- Saved Urdu start 200: confirm, source saved, attempts 1/max 2, completed.
- Explicit live Urdu start with no key 200: confirm from same saved result,
  requested_source live, source saved, fallback_reason api_unavailable.
- Explicit correct decision 200: accepted, attempts 1, retry_available false,
  TTS unavailable/audio URL null. Server was stopped after manual inspection.

No ElevenLabs requests, automated tests/test files or test suites were run.
Manual curl usage is production inspection, not acceptance-suite verification.
No full two-usable-clip/two-rejection rehearsal, malformed-body/error/CORS race
coverage, new live-provider call, TTS or integrated frontend/outage demo was run.
One saved Urdu clip is available, so a distinct second saved Urdu success cannot
be fabricated; a missing saved result returns a recoverable failure/referral.
These limitations keep the ticket In review, not Done.

Manual start/curl/retry commands are in backend/README.md. Use real IDs from
capabilities and current session IDs; source saved needs no key, while source
live can incur a provider request. Run one worker and expect sessions to disappear
on restart. No later ticket was implemented. Next implementation handoff: T-015
for UI/TTS, still blocked by T-012/T-013. T-017 remains blocked by its outstanding
frontend prerequisites; no additional ready unimplemented Dev 1 ticket remains.
