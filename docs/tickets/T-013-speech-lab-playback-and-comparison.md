# T-013 — Build authentic-audio speech laboratory

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 2  
**Depends on:** `T-003`, `T-007`, `T-010`, `T-012`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Let judges hear and inspect real paired model performance.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/features/speech-lab/`
- `frontend/src/components/TranscriptDiff.tsx`

## Step-by-step implementation plan

1. Render selected language sample manifest and an audio player for vetted local FLAC clips.
2. Show human reference, auto raw transcript, guided raw transcript with status labels.
3. Use grapheme/token-safe diff presentation and correct RTL direction for Arabic/Urdu.
4. Display CER as a ratio formatted percent, paired delta in **percentage points**, eligible WER or unavailable note.
5. Add per-language n, improved/worsened/tied counts and model/source citation.

## Implementation guidance (illustrative, not built yet)

```typescript
const cerPercent = cer == null ? 'Not available' : `${(cer * 100).toFixed(1)}%`;
const deltaPP = pairedDelta == null ? null : pairedDelta * 100;
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Audio file missing/unsupported browser codec: show error; source must remain truthful.
- Never present saved results as new live API output.
- A diff UI cannot silently auto-translate to manufacture equivalence.

## Acceptance tests

- [ ] Readback of sample ID matches displayed reference and result.
- [ ] Missing audio / guided unsupported render explicit states.
- [ ] Right-to-left transcripts remain readable without reversing semantic order.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
