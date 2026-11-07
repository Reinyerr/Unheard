# T-019 — Audit licenses, secrets and publishable assets

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Shared  
**Depends on:** `T-002`, `T-007`, `T-013`, `T-015`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Ensure demos and future git publishing do not leak data or breach source constraints.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `docs/DATA_SOURCES.md (final)`
- `docs/attributions.md`
- `scripts/audit_publishable_assets.py`

## Step-by-step implementation plan

1. Audit every used FLAC/audio file license and include original source attribution and modifications.
2. Review generated TTS clips licensing/usage requirements and store only approved ones.
3. Search repository for .env keys, bulk ZIPs, 311 extracts, birth-city metadata or non-commercial audio.
4. Document why bank/assistant task audio was coverage evidence, not actual Mississauga 311.
5. Provide instructions to keep raw ZIP outside repository and prompt manual review before public deployment.

## Implementation guidance (illustrative, not built yet)

```python
# Guard concept: fail packaging if a private key or raw ZIP is staged
for path in staged_paths:
    assert not path.endswith(('.env','.zip'))
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Real `.env.example` is allowed, populated `.env` forbidden.
- Non-commercial/ShareAlike status may affect future use even if event is noncommercial.
- External polygon boundaries also need provenance and reuse check.

## Acceptance tests

- [ ] No unapproved raw audio/data or secrets staged.
- [ ] Every public clip has dataset attribution/licensing entry.
- [ ] Local data source files remain referenced and not copied wholesale.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
