# Ticket index — source of truth for implementation

**T-001 and T-002 are Done (verified 2026-11-07).** T-003, T-004, T-005, T-007, T-009, T-010 and T-014 are implemented and In review; tests were explicitly skipped at user request. T-004/T-005 generated real corrected ward, language and recommendation JSON with production schema validation; acceptance and integration sign-off remain pending. T-007 also generated the frozen 48-record FLEURS selection and selected local audio. T-008 has real small-preflight evidence (In review); T-010 exported its measured outcomes with missing modes explicit. The cached runner is implemented with real offline preflight import; the full live paired pilot remains unrun; remaining tickets retain their dependencies.

| Ticket | Feature | Priority | Owner | Depends on | Status |
|---|---|---|---|---|---|
| [T-001](T-001-project-bootstrap.md) | Initialize repo, local Vite/FastAPI and safe defaults | P0 | Shared | — | Done |
| [T-002](T-002-source-and-license-audit.md) | Audit source archive, licenses and provenance | P0 | Dev 1 | T-001 | Done |
| [T-003](T-003-data-schema-and-fixtures.md) | Implement v1 schemas, identity mapping and fixtures | P0 | Shared | T-001, T-002 | In review |
| [T-004](T-004-corrected-census-processing.md) | Generate corrected ward language metrics | P0 | Dev 1 | T-002, T-003 | In review |
| [T-005](T-005-coverage-and-recommendation-ranking.md) | Build coverage model and language-first ranks | P0 | Dev 1 | T-002, T-003, T-004 | In review |
| [T-006](T-006-ward-geometry-validation.md) | Source and validate real Mississauga ward polygons | P0 | Dev 2 | T-002, T-003 | TODO |
| [T-007](T-007-reproducible-fleurs-sampling.md) | Generate 48-record FLEURS sample manifest | P0 | Dev 1 | T-002, T-003 | In review |
| [T-008](T-008-elevenlabs-scribe-preflight.md) | Validate real Scribe requests, language hints and credits | P0 | Dev 1 | T-001, T-003, T-007 | In review |
| [T-009](T-009-paired-transcription-runner.md) | Run cached paired ElevenLabs pilot and track failures | P0 | Dev 1 | T-007, T-008, T-010 | In review |
| [T-010](T-010-cer-wer-and-paired-analysis.md) | Calculate multilingual CER/WER and paired summaries | P0 | Dev 1 | T-003, T-007, T-008 | In review |
| [T-011](T-011-ward-map-and-metric-toggle.md) | Implement corrected ward map and count/share toggle | P0 | Dev 2 | T-003, T-004, T-006 | TODO |
| [T-012](T-012-global-selection-and-empty-states.md) | Connect modules with safe global language selection | P0 | Dev 2 | T-003, T-004, T-005 | TODO |
| [T-013](T-013-speech-lab-playback-and-comparison.md) | Build authentic-audio speech laboratory | P0 | Dev 2 | T-003, T-007, T-010, T-012 | TODO |
| [T-014](T-014-fastapi-confirmation-state-machine.md) | Implement deterministic confirmation/retry/referral API | P0 | Dev 1 | T-001, T-003, T-008 | In review |
| [T-015](T-015-spoken-recovery-ui-and-tts.md) | Build the demo confirmation flow and spoken prompts | P0 | Dev 2 (UI) + Dev 1 (TTS) | T-012, T-013, T-014 | TODO |
| [T-016](T-016-priority-recommendations-ui.md) | Implement research-backed language/ward recommendations | P0 | Dev 2 | T-005, T-011, T-012 | TODO |
| [T-017](T-017-ci-and-regression-tests.md) | Automate high-risk validation and unit checks | P0 | Shared | T-004, T-005, T-010, T-011, T-012, T-014 | TODO |
| [T-018](T-018-integrated-local-demo-and-outage.md) | Rehearse full four-act localhost and offline scenarios | P0 | Shared | T-011, T-013, T-015, T-016, T-017 | TODO |
| [T-019](T-019-attribution-privacy-and-package-audit.md) | Audit licenses, secrets and publishable assets | P0 | Shared | T-002, T-007, T-013, T-015 | TODO |
| [T-020](T-020-ui-accessibility-and-demo-polish.md) | Finish approachable, accessible visual storytelling | P1 | Dev 2 | T-011, T-013, T-015, T-016 | TODO |

## Status convention

- `TODO`: not started; dependencies may still be blocked.
- `In progress`: actively being implemented.
- `Blocked`: prerequisite/data/API missing; log evidence and defined fallback.
- `In review`: implementation complete, awaiting test evidence and integration review.
- `Done`: acceptance criteria and integration verified, docs updated.

## Suggested starting sequence

Start T-001 → T-002 → T-003, then data branch T-004/T-005 and speech branch T-007/T-008 with geographic branch T-006. Build one Urdu vertical slice (T-011/T-013) **before** expanding experimentation. Continue via dependency graph in `../ROADMAP.md`.

**Do not mark T-008 or T-009 Done** until at least one real verified ElevenLabs call and correct exception/status handling are recorded. T-017 automated tests do not replace real API preflight.

T-004/T-005 provide census/coverage/recommendations, T-007 frozen samples, T-008
real Urdu/Cantonese preflight, and T-010 measured-outcome export. All five public
artifacts now exist and production Python bundle validation passed. No frontend
build or automated tests were run; existing review gates remain open.

T-009 runner is implemented and In review. Offline production import/cache/export
recorded four real modes, 92 not_tested and zero new POSTs; no automated tests or
full live pilot ran. Four other languages still need guidance preflight evidence;
credit/rate and script-review limits remain. T-014 is now implemented and In
review, with manual saved Urdu confirmation and explicit live-to-saved fallback
proof, no automated tests and no new ElevenLabs requests.
T-013 also has backend sample/metric inputs but still needs T-012; T-011 needs
T-006, and T-016 needs T-011/T-012. No downstream feature was implemented.


T-014 provides backend capabilities/start/decision/retry/session routes. T-015
UI/TTS is the next handoff, still requiring T-012/T-013; T-017 still needs its
listed frontend prerequisites. No unimplemented ticket exclusively assigned to
Dev 1 is currently ready; review/live-pilot gates on implemented work remain open.
