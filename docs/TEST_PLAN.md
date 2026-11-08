# Verification plan — correctness before visuals

**Status:** T-017 automated regression checks verified locally on 2026-11-07;
remote CI, independent live review and full T-018 rehearsal remain open. See D-020
and [T-017 command/results evidence](tickets/T-017-ci-and-regression-tests.md).

Observed: 69 Python tests, 13 frontend unit tests, 2 offline and 2 online existing
browser smoke cases passed; no skips. Export/schema/source validation and frontend
type/build checks passed. DATA-01..04, GEO-01..02, SAMPLE-01, CER-01..03,
PAIR-01..02 and critical recovery/TTS/UI gates have automated checks; seeded
selection and source reconciliation also have a separate optional real-source
preflight. Browser smoke does not claim DEMO-01 or full OFFLINE-01 acceptance.
All external providers are mocked in unit tests; no API credits are used in CI.

## Test levels / suggested tools

- Unit/data: Python `pytest`, `pandas`, pure helper functions. Run without network or real API secrets.
- Backend: FastAPI `TestClient`, mocked ElevenLabs adapter, restricted allowlist and finite-state transitions.
- Frontend: Vitest + React Testing Library for selectors, metrics formatting, player errors, and missing-data state.
- Contract validation: Pydantic/JSON Schema plus TypeScript types (manual or generated); immutable known fixture snapshots.
- E2E: human-tested full localhost Urdu path plus deliberate outage/invalid-data paths. Browser automation is optional, not mandatory.
- CI: lint/typecheck + unit tests + schema checks on pull requests; **no live ElevenLabs calls in CI**.

## Release-blocking acceptance matrix

| ID | Test / method | Expected behaviour |
|---|---|---|
| DATA-01 | Recompute coverage from supplied `language_coverage.csv` | exactly 8 missing-task-audio tracked languages; sum 79,940; 14 non-official population subtotal 153,480; ratio ≈52.1% |
| DATA-02 | Validate corrected ward data | 11 unique wards 1–11; Ward 10 uses corrected source; percentages based on `population_language_base` |
| DATA-03 | Validate language crosswalk | all tracked IDs resolve exactly once; `yue` Cantonese not mistaken for Mandarin `zh` |
| DATA-04 | Zero population base fixture | `gap_share_pct` null; not 0, infinity, or NaN |
| GEO-01 | Ward polygons and census join | 11 polygon IDs exactly match 11 wards, no silent drops or duplicates |
| GEO-02 | Missing polygon fixture | switch to labelled ward chart and show explanation |
| SAMPLE-01 | Seeded selection | same eight **common** sentence IDs repeated for all six languages; no duplicates; exact 48 rows |
| API-01 | Real preflight, manual only | one real recording processed (auto); guidance supported/rejected state evidenced from real response |
| API-02 | Mock timeout / unsupported / quota | logged distinct status; no fake metric; bounded retry |
| CER-01 | `reference='abc'`, `hypothesis='adc'` | CER = 1/3 |
| CER-02 | `reference='hello'`, `hypothesis=''` | CER = 1 if valid empty recognition; technical failures excluded |
| CER-03 | Insertions test | CER can be >1; avoid capping at 100% |
| PAIR-01 | auto .20 guided .10 | `paired_delta_cer`=+.10 or +10 percentage points displayed |
| PAIR-02 | one side technical error | no paired delta; `n_paired` excludes it; exclusion counts retained |
| TEXT-01 | Chinese/Arabic/Urdu fixtures | Unicode normalization keeps meaningful scripts; WER unavailable without appropriate tokenization |
| UI-01 | Select Tamil (if untested) | label `Not tested`, no 0% CER |
| UI-02 | Select Urdu then Arabic | no stale Urdu transcript, state and sample cleared/updated |
| UI-03 | Count / share toggle | tooltip always shows both verified values and denominator |
| REC-01 | Accepted confirmation | user explicitly confirms, state moves to `accepted` |
| REC-02 | Rejected twice / invalid transition | one retry allowed then referral; cannot infinite-loop or confirm before STT |
| REC-03 | Judge presses Confirm on third-party clip | interface labels interaction as simulated confirmation |
| SEC-01 | inspect frontend bundle / git | no ElevenLabs secret or raw unapproved user recording |
| OFFLINE-01 | disable backend/internet | static map/recommendations/saved clips+real results remain usable |
| DEMO-01 | independent teammate rehearsal | complete four-act localhost flow from cold start; observed outcome recorded |

## Manual checks after each milestone

**M0:** both local dev environments can start; schema fixture validates. **M1:** one real Urdu clip and valid ward join; exact model/version recorded. **M2:** language selector and all six pilot rows (or explicit actual incompleteness); WER/normalization decision documented. **M3:** full confirmation and simulated rejection path, offline-safe. **M4:** no console crashes, external assets missing, or deceptive claims; both developers operate demo without coaching.

## Metric interpretation

- For each selected clip calculate raw CER/eligible WER. Only matched completed auto + guided pairs support paired comparisons.
- Track selection denominator (`n_selected`), attempted, succeeded and failed; do not silently drop failed samples from reports.
- For `n_paired`, report mean paired difference, clip-level improvements/worsenings/ties; optionally bootstrap a descriptive CI with cautious caveat (`n=8` per language).
- No p-value threshold or strong fairness claim is pre-agreed. Research language is exploratory and calibrated.

## Test evidence / handoff template

```text
Date / environment:
Ticket / commit:
Command or manual steps:
Expected:
Observed:
Pass / fail / blocked:
Evidence (test log, screenshot, request-ID redacted):
Remaining risk:
```

**Definition of release-ready**: No release-blocking data-integrity error; a real ElevenLabs integration tested at least once; demonstrated results are verifiably actual; app works locally; offline saved-results route functioning; no public credentials or disallowed audio in repository.


## T-021 guided presentation regression — 2026-11-08

See [observed evidence](test-evidence/guided-demo.md). App shell tests now cover
one accessible act, Next/Back/fragment focus, preservation of language/ward/metric/
sample/session and inactive audio pause. Obsolete removed-shell health assertions
were replaced; actual recovery capability checks remain. Browser cases cover
real Leaflet lift/dimming/clear/base identity after zoom/resize, reduced motion,
1366×768/1440×900/390×844 layouts, Urdu saved playback/comparison/acceptance/referral,
missing inputs, stale language state and connection-refused backend fallback.
Mocks never invent metrics; existing provider preflight remains separate. No
live-source choice or billed provider request belongs in these UI regressions.
T-021 does not certify human rehearsal, TTS listening or screen-reader acceptance.

## T-021 waveform / minimalist continuation

`e2e/waveform.spec.ts` exercises real Urdu FLAC decode, nonuniform peak bins,
native play/pause/resume/end, keyboard seek, midpoint cursor, recording reset,
recovery player and Web Audio fallback under normal/reduced motion. Existing
guided tests retain 1366/1440/390 layouts, raised ward selection, map alignment,
Urdu saved acceptance/referral, state retention and unavailable-source behavior.
Peak extraction unit fixture checks time bins, silence and multiple channels.
No fabricated provider outcomes. Independent provider preflight remains in
`test-evidence/one-recording-pilot.md`; no new billed request for UI-only work.
