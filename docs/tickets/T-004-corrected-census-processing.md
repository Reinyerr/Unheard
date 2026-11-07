# T-004 — Generate corrected ward language metrics

**Status:** In review — implemented on real source; tests skipped at user request.
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

## Implementation evidence — 2026-11-07

Branch: `feature/data-backend`; working-tree changes, no commit created.
T-001 bootstrap and T-002 audit code/evidence exist. T-003 Python schemas,
shared language map and TypeScript contracts exist, but T-003 remains In review
with tests skipped. Those implementation prerequisites were used without
claiming their pending verification was complete.

Implemented `scripts/prepare_census.py`, generated
`frontend/public/data/wards.v1.json`, and updated script usage and ticket index.
No shared-contract, UI, dependency or product-scope changes. All provenance fits
the existing string-valued `source` metadata contract. No decision amendment is
needed. No tests or test files were created or run, per the explicit user rule.

Observed production command (macOS, available Python 3.14.7/Pydantic 2.13.5;
the pinned backend environment was not installed for this task):

```sh
python3 scripts/prepare_census.py --source '/Users/rainierjorgejorda/Downloads/Mississuaga File/Mississauga_Unheard_ElevenLabs_Track'
```

Exited 0 and generated 11 schema-validated wards, 14 tracked home-language
categories, eight coverage-derived missing-request categories, and summed
gap/category counts 79,940/153,480. The three actual input hashes match T-002's
recorded crosswalk/coverage/corrected-census hashes. Production guards enforce
unique IDs 1–11, correction flags, corrected Ward 10 baseline (Urdu 4,520;
denominator 73,830), exact category mappings and city/ward reconciliation.
Shares use unrounded ratios; unavailable bases become null. These guards and
schema validation are part of production generation, not acceptance test runs.

Manual verification: run the command above using the backend Python environment,
inspect the output's `source` hashes/counts and Ward 10, and independently compare
each ward's gap to the sum of its eight listed missing categories and its share
to 100 × gap / `population_language_base`. Missing/zero/negative-denominator
acceptance cases and independent ratio verification remain unverified.

Known limits: public municipal redistribution terms remain unresolved (local
prototype only); no full Urdu/cached speech demo exists to rehearse. The unchanged
T-003 Vite guard rejects a partial bundle containing only the ward artifact;
later tickets must supply the remaining real artifacts. No tests, frontend build
or demo/outage checks were run. Do not mark this ticket Done.

T-005's implementation inputs are available; T-003/T-004 review gates remain
open. T-005 and all other tickets were left unimplemented.
