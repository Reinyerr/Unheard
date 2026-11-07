# T-006 — Source and validate real Mississauga ward polygons

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 2  
**Depends on:** `T-002`, `T-003`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Enable truthful ward choropleth without guessed boundaries.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/public/data/mississauga_wards.geojson (if validated)`
- `scripts/validate_wards.py`
- `docs/DATA_SOURCES.md (geometry attribution)`

## Step-by-step implementation plan

1. Obtain credible official/reliable GeoJSON 11-ward boundaries with source and vintage.
2. Identify feature property containing ward IDs, normalize safely to integers 1–11.
3. Confirm exact match with corrected census wards, no duplicates or omissions.
4. Record source URL, date, license, geographic coordinate reference and coverage.
5. If matching fails, expose a known error and switch frontend to labelled ward chart.

## Implementation guidance (illustrative, not built yet)

```python
ward_ids = [int(feature["properties"]["ward"]) for feature in geojson["features"]]
assert sorted(ward_ids) == list(range(1, 12))
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- `ward` is an **example** property: inspect real GeoJSON first.
- No neighbourhood mapping in MVP.
- GeoJSON CRS and geometry validity must be checked; do not infer from file name.

## Acceptance tests

- [ ] Every 1..11 ward appears once and polygon geometry valid.
- [ ] A simulated missing Ward 10 blocks choropleth.
- [ ] Fallback table renders without any GeoJSON.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
