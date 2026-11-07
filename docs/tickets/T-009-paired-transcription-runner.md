# T-009 — Run cached paired ElevenLabs pilot and track failures

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-007`, `T-008`, `T-010`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Produce authentic results for both conditions on each selected sample when supported.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/run_experiments.py`
- `data/local/raw_scribe_responses/ (ignored)`
- `data/processed/experiment_attempts.json`

## Step-by-step implementation plan

1. Iterate deterministic frozen manifest, call the adapter for auto and verified guided modes.
2. Cache by sample hash + model ID + normalized config; resume safely without re-paying for identical completed requests.
3. Retry only transient failures, with bounded backoff and attempt log.
4. Persist `completed`, `technical_error`, `unsupported`, `incompatible_output` and raw responses.
5. Track selected, attempted, completed, failed counts per language; export immutable provenance.

## Implementation guidance (illustrative, not built yet)

```python
for sample in samples:
    for mode in ("auto", "guided"):
        if cache.has_success(sample, mode, model_id):
            continue
        result = attempt_with_bounded_retry(sample, mode)  # mock in CI
        save_status_and_raw_response(sample, mode, result)
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Quota exhausted mid-run should leave valid partial results.
- Guidance unsupported must not silently fall back to auto.
- An API success with empty speech content is distinguishable from HTTP failure.

## Acceptance tests

- [ ] No duplicate remote request when cache already valid.
- [ ] Repeated execution produces same selection and honors completed statuses.
- [ ] Failed modes remain visible and cannot produce fabricated paired deltas.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
