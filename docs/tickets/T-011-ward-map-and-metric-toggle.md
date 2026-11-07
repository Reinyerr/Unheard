# T-011 — Implement corrected ward map and count/share toggle

**Status:** TODO (not implemented)  
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
