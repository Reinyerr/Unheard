# T-006 — Source and validate real Mississauga ward polygons

**Status:** In review — production geometry validation/export implemented; automated tests and UI acceptance checks skipped.
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


## Implementation evidence — 2026-11-07 (America/Toronto)

Branch feature/data-backend, as explicitly requested by Developer 2. T-002 audit,
T-003 canonical ward/schema conventions and the actual T-004 wards.v1.json asset
exist; T-003/T-004 review gates remain open. No backend code or demographic/
coverage/experiment assets were changed. No T-011/T-012 UI implementation added.

Created scripts/validate_wards.py, scripts/geometry-requirements.txt,
frontend/public/data/mississauga_wards.geojson,
frontend/public/data/ward_geometry_status.json and
frontend/src/data/wardGeometry.ts. Added the separate .geometry-venv directory
pattern to .gitignore and documented geometry provenance/contracts/usage. Only
Shapely 2.1.2 and its required NumPy dependency were installed in the separate
ignored scripts/.geometry-venv; the teammate's backend runtime was untouched.

Official source: City of Mississauga / MississaugaData, ArcGIS item
f1cad02b3a40422dac2ea99b59cc36a5, Ward_Boundaries FeatureServer layer **2**.
An initial assumed layer 0 returned an actual missing-layer error; inspected
service metadata established layer 2 and source WARD string property.
Civic attributes (councillor/contact/photo) are omitted from output; canonical
integer ward_id and original source_ward are retained. No invented geometry.

Production commands executed:

```sh
scripts/.geometry-venv/bin/python scripts/validate_wards.py --refresh
scripts/.geometry-venv/bin/python scripts/validate_wards.py
```

The first pipeline execution correctly rejected an unexpected legacy crs member.
Actual metadata specified EPSG:4326; the adapter now explicitly permits that
verified value and removes the legacy member in output without changing any
coordinates. Topology inspection also found source interior-overlap slivers:
wards 7/1, 3/1, and 8/2, largest fraction of the smaller polygon approximately
0.000001849 (0.0001849%). Individual polygons are valid. The extra cross-feature
diagnostic is retained as a source warning, not silently repaired or treated as
proof of disjoint city coverage. No intersection area is a demographic measure.

Final production validation exited 0: exactly 11 distinct Polygon features,
integer IDs 1–11 exactly matching corrected T-004 census IDs; finite geographic
coordinates, closed rings, positive geometry, GEOS/Shapely individual validity,
and bounds matching official EPSG:3857 layer extent after WGS84 export. Source
geometry was not simplified/repaired. Raw snapshots and retrieval/hash evidence
are ignored under data/raw/ward_geometry; no real sources were placed in fixtures.
Public output includes attribution, source URLs/IDs, dates, CRS, input/census/
validator hashes, source overlap diagnostics and limitations. The status sidecar
binds the exact GeoJSON SHA-256 and enables local map use only after validation.

City eMaps labels the ward scheme Municipal Wards (2006-). ArcGIS item/feature
metadata was edited in June 2024, not a guaranteed immutable 2021 boundary
snapshot. This is supporting scheme evidence, not a historical boundary-change
or census-source equivalence audit. The linked dataset Terms of Use PDF returned
HTTP 403; its exact terms remain unverified. Local-prototype asset only pending
T-019 redistribution review; no public hosting or licence approval is claimed.

The frontend loader checks status, digest, geometry structure and exact ward IDs
against the supplied real census asset. It returns an explicit unavailable branch
on missing/failed/hash-mismatched/missing-ward geometry. Script validation errors
remove stale public GeoJSON and publish map_ready=false. Actual chart/table
rendering and map interactions belong to T-011; T-006 adds no React UI.

No automated tests/test files, simulated missing-Ward-10 execution, frontend
build/typecheck/browser inspection or fallback rendering checks were run. The
current checkout has no frontend node_modules/compiler installation; none was
installed for this geometry-only ticket. No full Urdu/demo regression performed.
All acceptance checkboxes remain open; status In review, not Done.

Manual reproduction: follow scripts/README.md, run offline validation using the
saved sources or --refresh against official endpoints, inspect both output files
and warnings, and compare IDs with wards.v1.json. Independent missing/invalid
geometry and fallback UI verification remain outstanding. Next ready ticket is
T-011 using the real T-004 counts and this geometry/loader; then T-012 using
T-004/T-005. Stop here; neither was implemented.
