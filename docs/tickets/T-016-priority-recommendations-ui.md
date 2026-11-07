# T-016 — Implement research-backed language/ward recommendations

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 2  
**Depends on:** `T-005`, `T-011`, `T-012`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Turn evidence and demographics into actionable evaluation priorities.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/features/recommendations/`
- `frontend/src/components/PriorityTable.tsx`

## Step-by-step implementation plan

1. Render language coverage first, home-language population second; show actual sample evidence in a different section.
2. For selected priority language, show top wards by **count** and **share** with transparent ranking criteria.
3. Generate concise recommended actions: collect consented task-specific recordings; test dialects/speakers, then validate safeguards.
4. Explain failure/evidence distinction and limits of non-local recordings.
5. If no polygon, still show source-grounded ward ranking table.

## Implementation guidance (illustrative, not built yet)

```typescript
const missing = languages
  .filter(x => x.coverage_status === 'no_task_audio')
  .sort((a,b) => b.city_home_speakers - a.city_home_speakers);
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Measured CER does not silently change population-based rank.
- A user selecting covered Arabic can still view demographics and measured experiment, but no missing badge.
- No recommendation that a 311 bot should act on unconfirmed request.

## Acceptance tests

- [ ] Rank order matches coverage CSV; Urdu first.
- [ ] Changing language updates ward recommendations without changing audio geo assignment.
- [ ] Wording consistently recommends **testing**, not forecast failures.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
