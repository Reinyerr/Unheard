# T-015 — Build the demo confirmation flow and spoken prompts

**Status:** In review — multilingual voices configured; account/audio verification blocked

**Priority:** P0  
**Owner:** Dev 2 (UI) + Dev 1 (TTS)  
**Depends on:** `T-012`, `T-013`, `T-014`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Demonstrate safe confirm/retry/referral in judge-controlled prerecorded audio workflow.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/features/recovery/`
- `backend/app/services/tts_adapter.py`
- `frontend/public/audio/prompts/ (vetted only)`

## Step-by-step implementation plan

1. Add selected-language prompt and sample flow; display transcript and clarify that confirmation is simulated.
2. Verify TTS supports selected language/voice before claiming spoken confirmation.
3. Generate/cache an ElevenLabs audio prompt for known example text, preserving origin/attribution metadata.
4. Build Correct, Incorrect, Try Different Sample, Referral actions with state visibility and keyboard access.
5. If TTS unavailable use explicit text-only fallback; if backend down use labelled saved-result route.

## Implementation guidance (illustrative, not built yet)

```typescript
// State-driven control sketch
const canConfirm = state === 'confirm';
const canRetry = state === 'retry_or_refer' && attempts < 2;
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- The person clicking Correct is a judge, not the original FLEURS speaker.
- Different sample after rejection is a demo retry, not speech-correction proof.
- Generated TTS in unsupported languages must not be faked.

## Acceptance tests

- [ ] Reject path reaches referral after one retry.
- [ ] TTS plays only if real/cached playable output exists.
- [x] Offline mode and text fallback visibly labelled (limited interactive review; independent outage rehearsal pending).

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Implementation handoff — 2026-11-07

Continued on `feature/data-backend`; no commit created. T-012 global selection,
T-013 real manifests/exports/audio and T-014 backend routes exist (all retain
their review gates). Implemented only T-015; pre-existing edits were preserved.

- `frontend/src/features/recovery/`: backend and explicit browser-only saved
  routes, curated sample/mode selection, simulated confirmation, single
  different-clip retry, explicit acceptance/referral, bounded pending requests,
  unavailable/unknown-response handling and language-reset/audio cleanup.
- `frontend/src/App.tsx`: wires Demonstrate into the existing journey.
- `backend/app/services/tts_adapter.py`: cache-only runtime, opt-in fixed English
  instruction preparation, observed model-language/premade-voice checks, one
  bounded synthesis POST without retries, staging and exact-hash listening
  approval. No arbitrary text/transcript or voice cloning. See backend README.
- Backend recovery schema/service: additive cached-prompt metadata; no static
  research schema or recovery transition/attempt policy changes. Public prompt
  directory contains instructions only; no audio/provider evidence was invented.

Observed: `npm --prefix frontend run build` passed (existing Vite future-loader
and large-chunk warnings); Python compilation passed for the touched backend
modules. Interactive localhost review showed Urdu 1533 saved confirmation and
text-only notice, Incorrect → retry_or_refer → Urdu 1537 missing saved output →
referral at attempt 2; no third retry. Separate browser-only saved Urdu 1533
confirmation → Correct → accepted also observed. This is limited manual review,
not full acceptance or an independent outage rehearsal. No automated tests were
written/run; no provider calls or new speech metrics were generated.

**Blocker:** neither server API key nor TTS voice is configured. No actual TTS
audio exists, and advertised support alone would not prove playback or language
quality. English prompt generation/listening approval remains unperformed;
Urdu and other languages explicitly remain text-only. The fixed English
instruction does not read the transcript and is offered only for English.
Two-rejection acceptance with two usable clips cannot be observed with the
current single usable saved Urdu clip. Other playback/language-switch/keyboard,
real outage and independent acceptance checks remain pending. Ticket is not Done.

Manual commands/steps are in `frontend/README.md` and `backend/README.md`.
Next ready implementation ticket: T-017 (Shared), subject to existing review
gates and a new instruction permitting automated tests. T-018 integration remains
dependent on T-017 and unresolved T-015 voice/acceptance work; T-019/T-020 can
begin from implemented artifacts with those limitations retained. No next ticket
was started.

## Multilingual continuation — 2026-11-07

The user's exact six voice IDs are configured in shared/tts_prompts.json and safe
backend dotenv defaults. The existing TTS adapter now supports metadata-only
checking, one explicitly authorized language generation, pending-review staging,
and exact-hash listening/language approval for all six. Preferred/sole selected
model eleven_v3 and POST /v1/text-to-speech/{voice_id} were checked against current
official docs; the docs list ur/pa/yue/ar/zh/en, but account/voice access remains
unconfirmed. No substitute voice/model is used.

Shared authored draft prompts/labels cover Urdu, Punjabi, Cantonese, Arabic,
Mandarin Chinese and English; native-language review is required. React validates
schema-2.0 per-language approved metadata and audio hashes. Backend changes are
limited to TTS configuration/adapter and localized caption/cache lookups; T-014
routes/state transitions/attempt limits are retained. Developer 1 reviewed this
boundary and the prior English-only frontend gate; frontend/contracts were
updated together. See backend/README.md for exact preparation/approval commands.

Observed: build and Python syntax checks passed. Metadata-only --check exited 1
with blocked_missing_credentials for all six and zero provider requests. No
billable audio or automated tests were created/run. No approved audio exists;
all languages remain text-only. Previous limited interactive Urdu results are
historical, not new multilingual acceptance evidence. Required manual checks
include native-language caption/labels, voice quality, approved playback, language
switching, recovery/retry/referral and outage. Ticket is not fully verified.

The key-shaped value found in .env.example was replaced with an empty placeholder;
if real, rotate the exposed credential. Server reads backend/.env/exported vars,
never example-file credentials. The outstanding blocker is valid server-only
credentials/voice permissions, followed by explicit per-language audio generation
and approval (Urdu first). No other ticket implemented.
