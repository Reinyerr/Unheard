# T-015 — Build the demo confirmation flow and spoken prompts

**Status:** TODO (not implemented)  
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
- [ ] Offline mode and text fallback visibly labelled.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
