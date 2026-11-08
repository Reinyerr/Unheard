# T-012 — Connect modules with safe global language selection

**Status:** In review (implemented; acceptance incomplete)
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

## Implementation evidence — 2026-11-07

Prerequisites T-003/T-004/T-005 exist: shared TS/Zod contracts and actual generated
wards, languages and recommendations assets. T-007/T-009/T-010 saved experiments
also supply availability context. No backend or shared JSON schema changes.

SelectionProvider owns canonical language/all, census ward and map metric. A
language change clears selected sample/result and advances a revision guard for
late responses; ward/metric changes preserve speech state. Reset is explicit;
anchor navigation preserves selection. Unknown IDs return to all with a notice.
ResearchProvider validates real static resources and isolates optional evidence
and recommendation failures from census availability. Shared selector and module
eligibility/status displays use these providers; playback and recommendation
detail controls remain subsequent tickets.

Observed local browser review: Tamil updates census and shows Not tested without
CER; Urdu shows 2 completed and 14 not_tested recording modes across 8 clips.
Selecting Ward 10 retains these counts and shows 4,520 speakers / 6.12% /
73,830 language base. Anchor navigation retains Urdu. Backend was unavailable;
static census and saved evidence remained usable. Screenshot: ignored local
`.cache/t012-selection.jpg`.

`npm --prefix frontend run build` passed (TypeScript, existing asset build guard,
Vite). No automated tests were created or run, per the task instruction. Full
acceptance remains unverified: no playback/comparison controls exist yet to
exercise stale audio clearing; unknown-ID/late-response guards and optional-file
failure branches were code-reviewed only. Keep In review, not Done.

Manual verification: run `npm --prefix frontend run dev`, open localhost:5173,
select Tamil, Urdu, Ward 10, then Arabic and navigate the four anchors. Confirm
language-specific eligibility, no fabricated scores, and census-only ward scope.
T-013 is the next implementation handoff; T-016 also has implementation inputs.
