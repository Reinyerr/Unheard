# T-003 — Implement v1 schemas, identity mapping and fixtures

**Status:** In review — implemented; automated tests explicitly skipped at user request.
**Priority:** P0  
**Owner:** Shared  
**Depends on:** `T-001`, `T-002`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Freeze language IDs and statuses so frontend and backend can work in parallel.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `backend/app/schemas/`
- `frontend/src/types/`
- `frontend/public/data/fixtures/`
- `docs/DATA_CONTRACTS.md (verified)`

## Step-by-step implementation plan

1. Define coverage, experiment and recovery status enums exactly as contract.
2. Build canonical language map from crosswalk, e.g. `mandarin_chinese` vs `cantonese`.
3. Create illustrative but clearly labelled fixture samples for UI unit tests only.
4. Validate generated static JSON on both sides and reject unknown/duplicate IDs.
5. Record schema version and prohibit numeric placeholders for missing results.

## Implementation guidance (illustrative, not built yet)

```python
# Pure guard, independent of framework
def valid_pair(auto, guided):
    return (auto["status"] == "completed" and
            guided["status"] == "completed" and
            auto["cer"] is not None and guided["cer"] is not None)
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Cantonese uses FLEURS code `yue` and must not alias to Mandarin `zh`.
- Keep fixture demonstration data visually labelled as mock until replaced by actual results.

## Acceptance tests

- [ ] Reject duplicate language IDs and invalid enum values.
- [ ] Missing CER is null when not_tested.
- [ ] Schema fixture round-trips frontend + backend.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

Implementation: Pydantic research schemas, matching TypeScript/Zod types and runtime
validators, crosswalk-derived shared language map, five explicitly MOCK fixtures,
and a Vite build guard for generated research artifacts. Duplicate/unknown IDs,
invalid enums, missing-outcome numeric metrics and broken bundle references are
rejected. Existing app shell remains unchanged. No tests were created or run;
acceptance/round-trip verification remains incomplete. Do not mark Done yet.
