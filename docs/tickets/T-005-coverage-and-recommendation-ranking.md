# T-005 — Build coverage model and language-first ranks

**Status:** TODO (not implemented)  
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
