# T-002 — Audit source archive, licenses and provenance

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-001`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Make all data dependencies explicit and fail when required files/source rows are missing.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/audit_sources.py`
- `data/processed/source_manifest.json (generated later)`
- `docs/DATA_SOURCES.md (updated audit)`

## Step-by-step implementation plan

1. Locate files under exact archive root and avoid extracting 468 MB wholesale.
2. Validate census/coverage/crosswalk headers and FLEURS reference rows; record size/checksum/version.
3. Check 8 missing categories, 79,940 sum, 153,480 denominator.
4. Keep licensing attribution and redistribution permissions in an asset manifest.
5. Document out-of-scope raw 311 and non-commercial-only audio.

## Implementation guidance (illustrative, not built yet)

```python
missing = [r for r in coverage if r["has_service_request_audio"] == "False"]
assert len(missing) == 8
assert sum(int(r["city_home_speakers"]) for r in missing) == 79940
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Handle UTF-8 BOM, CSV missing/empty values and Boolean strings.
- Audit FLEURS reference rows without adding 560 source files to repository.

## Acceptance tests

- [ ] Source checks produce exact expected totals.
- [ ] Missing required column errors contain source path.
- [ ] Manifest contains license links and confirms zero raw ZIP files committed.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
