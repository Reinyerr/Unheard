# T-004 — Generate corrected ward language metrics

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-002`, `T-003`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Compute truthful 11-ward counts/shares from corrected data.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/prepare_census.py`
- `frontend/public/data/wards.v1.json`

## Step-by-step implementation plan

1. Read `01_people_census/derived/ward_language_profile_2021_corrected.csv`.
2. Extract 14 `home_*` fields, verify Ward IDs 1–11 exactly once.
3. Use the 8 missing task-request language IDs from the coverage file, not a separate guessed list.
4. Calculate sum for `gap_population`, and gap share from `population_language_base`.
5. Export versioned ward JSON and source provenance.

## Implementation guidance (illustrative, not built yet)

```python
def gap_share_pct(gap_population: int, population_language_base: int):
    if population_language_base <= 0:
        return None
    return 100 * gap_population / population_language_base
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Incorrect raw Ward 10 is prohibited.
- Zero/negative population base produces unavailable, never 0%.
- Avoid accidental sum of overlapping census categories without documenting assumptions.

## Acceptance tests

- [ ] 11 unique wards, Ward 10 source flagged corrected.
- [ ] All shares equal independently verified ratios.
- [ ] Missing denominator fixture returns None.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
