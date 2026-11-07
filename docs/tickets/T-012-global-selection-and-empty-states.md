# T-012 — Connect modules with safe global language selection

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 2  
**Depends on:** `T-003`, `T-004`, `T-005`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Synchronize modules by canonical language IDs without mismatching ward and speech data.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/state/selection.ts`
- `frontend/src/components/LanguageSelector.tsx`
- `frontend/src/components/EmptyState.tsx`

## Step-by-step implementation plan

1. Implement `language_id = all|one canonical ID`, `ward_id?`, map metric state.
2. Change language updates map, speech lab eligibility and recommendations.
3. Clear stale selected audio/result on each language change; restrict ward selection to census displays.
4. Gracefully render not_tested, unsupported, API error and unavailable data states.
5. Keep selected language stable through navigation unless explicit reset.

## Implementation guidance (illustrative, not built yet)

```typescript
function changeLanguage(nextId: string) {
  setLanguageId(nextId);
  setSelectedSampleId(null); // prevent cross-language transcript leak
}
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Tamil has demographic data but no planned pilot; must say Not tested.
- English has no city-home-speaker count in source; do not display 0 residents.
- Unknown language ID displays non-breaking error and fallback selection.

## Acceptance tests

- [ ] Selecting Urdu then Arabic clears stale recording and comparison.
- [ ] No simulated CER 0% for not_tested.
- [ ] Selecting a ward never modifies experiment metrics.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
