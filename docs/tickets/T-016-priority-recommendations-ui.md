# T-016 — Implement research-backed language/ward recommendations

**Status:** In review (implemented; acceptance incomplete)
**Priority:** P0  
**Owner:** Dev 2  
**Depends on:** `T-005`, `T-011`, `T-012`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Turn evidence and demographics into actionable evaluation priorities.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/features/recommendations/`
- `frontend/src/components/PriorityTable.tsx`

## Step-by-step implementation plan

1. Render language coverage first, home-language population second; show actual sample evidence in a different section.
2. For selected priority language, show top wards by **count** and **share** with transparent ranking criteria.
3. Generate concise recommended actions: collect consented task-specific recordings; test dialects/speakers, then validate safeguards.
4. Explain failure/evidence distinction and limits of non-local recordings.
5. If no polygon, still show source-grounded ward ranking table.

## Implementation guidance (illustrative, not built yet)

```typescript
const missing = languages
  .filter(x => x.coverage_status === 'no_task_audio')
  .sort((a,b) => b.city_home_speakers - a.city_home_speakers);
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Measured CER does not silently change population-based rank.
- A user selecting covered Arabic can still view demographics and measured experiment, but no missing badge.
- No recommendation that a 311 bot should act on unconfirmed request.

## Acceptance tests

- [ ] Rank order matches coverage CSV; Urdu first.
- [ ] Changing language updates ward recommendations without changing audio geo assignment.
- [ ] Wording consistently recommends **testing**, not forecast failures.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Implementation evidence — 2026-11-07

Prerequisites T-005/T-011/T-012 are implemented and In review: actual generated
recommendations/coverage/corrected ward assets, shared ward count/share functions
and global selection. No backend, shared schema, generated dataset or dependency
change. No new raw data or fixtures.

Recommendations renders the eight exported language priorities in rank order;
coverage precedes population and CER is never a ranking input. Runtime checks
require matching corrected census source hash, coverage/rank/count agreement and
count-ranked suggested ward IDs. Mismatch withholds ranks with an explicit error.
Selecting a table language updates global selection. Selected language details
show source-generated actions, consent/dialect/speaker/safeguard guidance, and
separate top-three count/share tables derived from all 11 corrected ward rows.
Shares use positive population_language_base; unavailable values are excluded,
unrounded values rank, ascending ward ID breaks ties. Each table retains count,
share and denominator; no geometry fetch is needed. Ward links select census
context without modifying speech membership. Covered languages retain demographic
and separate saved pilot evidence, without a missing-coverage rank/badge.

The separate pilot section shows actual scored/paired n, mean CER and paired
delta, missing/exclusion reasons and limitations; null metrics stay unavailable.
Source details retain census/task provenance, input hash, row counts, export time
and licence caveats. No provider request, combined score, forecast failure or
municipal service action is introduced.

Observed manual browser review with backend unavailable: eight-language order is
Urdu, Punjabi, Cantonese, Tagalog, Tamil, Hindi, Gujarati, Bengali; Urdu first at
22,535. Coverage context shows 79,940 / 153,480 across 14 tracked non-official
categories (52.1%), not city population. Urdu has top count/share wards 10/6/11;
Ward 10 retains 4,520 / 6.12% / 73,830. Selecting Arabic changes ward details,
shows covered status and separate unavailable scored evidence, while preserving
the eight-language priority order. Local ignored screenshot:
`.cache/t016-priorities.jpg`.

`npm --prefix frontend run build` passed TypeScript, existing asset build guard
and Vite. No automated tests created/run by user instruction. Full acceptance is
not verified: independent ranking audit, deliberate missing/invalid artifacts,
geometry outage, full keyboard/mobile and audio-geo regression checks remain
unrun. Existing config-loader and bundle-size warnings are nonblocking.

Manual commands: `npm --prefix frontend run dev` and
`npm --prefix frontend run build`. Open localhost:5173/#recommend; select Urdu,
Cantonese (different count/share lists), Tamil (Not tested) and covered Arabic.
Follow a ward link to census, then return to verify language context. Review
failure/geometry-outage branches before sign-off. Next: T-015 (shared UI/TTS;
backend TTS preflight/cached voice remains required). Stop here.
