# T-005 — Build coverage model and language-first ranks

**Status:** In review — implemented on real data; automated tests skipped at user request.
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-002`, `T-003`, `T-004`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Rank unmeasured task-request categories without claiming proven ASR failure.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/prepare_coverage.py`
- `frontend/public/data/languages.v1.json`
- `frontend/public/data/recommendations.v1.json`

## Step-by-step implementation plan

1. Read coverage `minds14_calls`, `speech_massive_commands`, `has_service_request_audio`.
2. Separate `no_task_audio` vs `has_task_audio`; verify 8 missing counts sum 79,940.
3. Rank missing languages by descending city home speakers; use stable language ID tie-break.
4. From ward data compute per-language top wards by count, and separately by share.
5. Generate recommendation text about future consented request testing, not guaranteed model improvement.

## Implementation guidance (illustrative, not built yet)

```python
missing = sorted(
    [x for x in languages if x["coverage_status"] == "no_task_audio"],
    key=lambda x: (-x["city_home_speakers"], x["language_id"]))
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- English lacks census home speaker count in supplied coverage; do not coerce to zero.
- A covered language can be explored but is not ranked as unmeasured.
- Avoid equating absent supplied request audio to no recordings anywhere.

## Acceptance tests

- [ ] Urdu ranks first among 8; overall missing sum 79,940.
- [ ] All rank values unique with stable tie-handling.
- [ ] Ward top-by-count and top-by-share may differ and both criteria labelled.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Implementation evidence — 2026-11-07

Branch `feature/data-backend`; working-tree implementation, no commit created.
T-002 audit code/evidence, T-003 schemas/shared identities and T-004 census
pipeline/real ward export are present. T-003/T-004 remain In review, with their
acceptance verification pending. No prerequisite statuses were promoted.

Created `scripts/prepare_coverage.py`, `frontend/public/data/languages.v1.json`
and `frontend/public/data/recommendations.v1.json`; updated script instructions
and ticket index. Existing T-004 work was preserved. No React, shared-schema,
dependency or unrelated feature changes. No scope/decision amendment required.

The existing contract supports one `suggested_ward_ids` list. It now contains the
top three wards by home-speaker count; `suggested_action` independently labels
top-three count and share rankings with values. Shares use language-specific
counts over `population_language_base`; unavailable bases are excluded. Numeric
ward ID breaks ties; share ranking uses unrounded ratios. No new contract fields
or blended risk scores were introduced.

Executed production generation with available Python 3.14.7/Pydantic 2.13.5
(the pinned backend environment was not installed during this task):

```sh
python3 scripts/prepare_coverage.py --source '/Users/rainierjorgejorda/Downloads/Mississuaga File/Mississauga_Unheard_ElevenLabs_Track'
```

Observed exit 0: 15 language rows, six pilot selections and eight ranked
recommendations. Urdu is rank 1 (22,535); order continues Punjabi, Cantonese,
Tagalog, Tamil, Hindi, Gujarati, Bengali. Missing-category subtotal is 79,940
of 153,480 across 14 tracked non-official categories. Urdu count-ranked wards
are 10, 6, 11. Production generation revalidates the corrected source and checks
the existing ward export's values/input hashes before schema-validating outputs.
English's census population remains null; covered languages have no unmeasured
recommendation. Source provenance records attribution, hashes, counts and limits.

No automated tests/test files were created or run. Production schema/source guards
are not acceptance-test sign-off; all acceptance checkboxes remain open. Manual
review instructions are in `scripts/README.md`, including independent count/share
recalculation and total/rank inspection. No frontend build, pinned-environment
verification or Urdu/cached demo regression was performed.

Known limits: municipal redistribution terms remain unresolved; local prototype
only pending the license gate. The unchanged T-003 frontend build guard requires
all five artifacts, while this checkout has only census/coverage/recommendations.
Sampling and experiment assets must come from their assigned tickets. The two
output files are individually replaced atomically, not a multi-file transaction;
rerun after any write error before consumption.

Next ready Dev 1 implementation: T-007, subject to existing T-003 review. T-012
also has its implementation inputs for Dev 2; T-016 still needs T-011/T-012. No
other ticket was implemented and T-005 is not marked Done.
