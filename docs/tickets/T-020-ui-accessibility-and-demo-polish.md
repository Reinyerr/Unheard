# T-020 — Finish approachable, accessible visual storytelling

**Status:** TODO (not implemented)  
**Priority:** P1  
**Owner:** Dev 2  
**Depends on:** `T-011`, `T-013`, `T-015`, `T-016`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Make the evidence understandable without letting animations displace credibility.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/styles/`
- `frontend/src/components/AccessibilityNotice.tsx`
- `docs/DEMO_RUNBOOK.md (timing)`

## Step-by-step implementation plan

1. Ensure every page shows one clear question and limits near displayed results.
2. Provide focus states, keyboard controls, audio transcripts, readable contrast and aria labels.
3. Support reduced motion and correct RTL text direction.
4. Create 4-act navigation with Urdu as safe default and accessible optional exploration.
5. Polish only after M1 real vertical slice and basic integration are completed.

## Implementation guidance (illustrative, not built yet)

```typescript
// Accessible button sketch
<button type="button" aria-label="Play selected Urdu recording"
        disabled={!audioAvailable}>Play audio</button>
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- No cinematic transition may obscure a statistical caveat or error state.
- Ensure clip playback permitted and no autoplay surprises.
- Charts also provide tabular numerical details.

## Acceptance tests

- [ ] Keyboard-only flows can reach transcript, comparison and recommendations.
- [ ] Text remains legible without animation; reduced-motion honored.
- [ ] 2-person team can explain demo confidently without relying on visual flourish.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
