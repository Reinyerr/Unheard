# T-011 — Implement corrected ward map and count/share toggle

**Status:** In review — production map/table implemented; build passed, limited manual browser proof; automated tests skipped.
**Priority:** P0  
**Owner:** Dev 2  
**Depends on:** `T-003`, `T-004`, `T-006`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Make geographically accurate and understandable demographic gap data interactive.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/features/map/`
- `frontend/src/components/WardTooltip.tsx`

## Step-by-step implementation plan

1. Choose one map library (Leaflet or MapLibre); load vetted polygons and ward JSON.
2. Default metric `count`; allow `share` toggle and bind color scale to selected metric.
3. Use `population_language_base` and always show count, share, denominator, and language context in tooltips.
4. Show all-gap layer with eight unmeasured categories; selected covered languages show population without the gap label.
5. If geometry absent/invalid, render labelled ward bars or table instead of a fake choropleth.

## Implementation guidance (illustrative, not built yet)

```typescript
const value = metric === 'count' ? ward.gap_population : ward.gap_share_pct;
const label = value == null ? 'No population data' : formatMetric(value, metric);
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Zero denominators show no data, not zero.
- Do not draw FLEURS speaker dots on wards.
- No polygon border/area rank as proxy for speaker population.

## Acceptance tests

- [ ] Toggle and tooltip values verified from source for sample wards.
- [ ] Invalid polygon input triggers chart fallback.
- [ ] Ward selection filters demographics only, never fabricated local ASR errors.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.


## Implementation evidence — 2026-11-07 (America/Toronto)

Branch feature/data-backend, continuing Developer 2's assigned same-branch work.
T-003 schemas, T-004 real corrected wards, T-005 real language coverage, and T-006
GeoJSON/status/loader exist. Prior review gates and existing uncommitted T-006 work
were preserved. No backend code, research assets, shared contracts or fixtures
were modified. No T-012 global state or other module behavior was implemented.

Created frontend/src/features/map/{data.ts,metrics.ts,WardMap.tsx,WardExplorer.tsx,
map.css} and frontend/src/components/WardTooltip.tsx. Mounted only the Discover
feature in App.tsx; removed the now-false bootstrap data-pending banner and made
its backend-health text accurate for independent static census exploration.
Added exact Leaflet 1.9.4 runtime and @types/leaflet 1.9.21 development dependency
through npm; installed the existing frontend dependency set. Package/lockfile
and frontend usage notes updated. No test files were created or changed.

Behavior: real 11-ward polygons join on numeric ward_id; default count uses only
the eight missing task-audio categories. Local language selection shows each
language's counts, unavailable English counts and covered-language status without
a gap label. Share is recomputed from the selected count/population_language_base,
with null for missing/nonpositive base/count. Every tooltip/detail/table shows
count, share, denominator and language/coverage context. All displayed city/ward
values come from generated assets; loaders reconcile gap IDs/sums and city totals.
No missing outcome is coerced to zero. No speech outcomes or speaker-location
markers enter the map.

Five equal-interval colors recompute for the current language/metric, with grey
for unavailable values and a labelled scale. Geometry/status/hash rejection or
Leaflet initialization failure returns a labelled table fallback. The verified
table is always usable independently of geometry; invalid census data blocks
numbers instead of substituting fixtures. Ward selection updates only demographic
details. The local selector/state is scoped to this feature, pending T-012.

Leaflet is used without external tile requests; all boundaries are the local
T-006 asset. Source/vintage/licence/overlap caveats are retained in the UI's
Sources details with a visible boundary-snapshot notice. Polygon interaction and
table buttons support click/keyboard selection; details use a live region, count/
share controls are labelled, and the table scrolls within narrow layouts. React
portals populate Leaflet tooltips safely with actual values. Resize/reset and
map cleanup support layout changes and React development remounting.

Executed production command:

```sh
npm --prefix frontend run build
```

Observed TypeScript and Vite build success, including the existing five-artifact
validation guard. Initial compile found the Leaflet GeoJSON base-interface excess
property issue; corrected using the installed FeatureCollection type, rebuilt
successfully. Non-failing Vite warnings about future native config loading are
pre-existing T-003 configuration and were left untouched.

Started actual Vite with npm --prefix frontend run dev and manually inspected
http://127.0.0.1:5173/#discover in the browser, with FastAPI unavailable:
all-gap layer displayed 79,940; changing the local selector to Urdu displayed
22,535 and actual ward counts. Toggling share changed scale maximum to 6.12%.
Selecting Ward 10 showed count 4,520, share 6.12%, language base 73,830 in both
polygon tooltip and selected detail. Table values matched the displayed source
context. Narrow viewport inspection exposed an overly narrow tooltip; set an
explicit bounded width and re-inspected the expanded content. Screenshot retained
in ignored .cache/t011-ward-map.jpg. No automated browser/test suite ran.

Manual instructions are in frontend/README.md. Missing/invalid GeoJSON fallback,
zero-base/English-unavailable and covered-language branches, full keyboard flow,
all responsive widths, independent ratio recalculation and Urdu/speech integration
regression were not exercised as an acceptance suite. No automated tests/test files
or mock fixtures were created/run; acceptance checkboxes remain open. T-011 stays
In review, not Done. No provider requests, backend/UI connections beyond existing
health or public hosting were introduced.

Next ready Developer 2 ticket: T-012 (T-003/T-004/T-005 inputs present), which can
lift/link this feature's state. Stop after T-011; T-012 and later modules remain
unimplemented.
