# Ticket index — source of truth for implementation

**Latest T-020 implementation handoff (2026-11-07):** Dev 2 accessibility and
demo polish implemented: act questions/limits, explicit Urdu walkthrough entry,
keyboard jump targets/table regions, shared motion/focus/reading styles and
supplied recovery reference text. FR-A2 all-language initial/reset selection,
data/contracts and recovery rules preserved. Timing/manual-review instructions
are in [DEMO_RUNBOOK.md](../DEMO_RUNBOOK.md). No automated tests, build or manual
browser/audio/accessibility checks ran. **In review**, not Done; T-015 approved
audio and two-person/reviewer gates remain open. No further unimplemented ticket
in T-001–T-020 is ready; proceed only with pending reviews/verification when authorized.

**Latest T-019 implementation handoff (2026-11-07):** read-only package audit,
48-clip attribution ledger and source/privacy/package notes implemented. No
automated tests, build or new audit command run by user instruction. **In review**
pending manual audit and reviewer sign-off; applicable City terms and provider
account/output rights remain unresolved. Runtime/contracts unchanged; existing
T-018 work preserved. T-020 is the next Developer 2 implementation candidate,
with T-015 audio/review gates still open; not started here.

**Latest T-018 continuation (2026-11-07):** continued committed WIP `b7759d3`;
70 Python and 13 frontend tests, build/source checks, 10 online and 10 actually
backend-stopped browser cases passed. Filled [demo runbook](../DEMO_RUNBOOK.md)
and [observed evidence](../test-evidence/local-smoke.md). T-018 is **In review**:
both developers' independent rehearsal and reviewer sign-off remain pending;
approved TTS and a second usable Urdu result remain unavailable. No new provider
requests or public-contract changes; T-019/T-020 not implemented. Historical
dependency review gates remain as recorded below.

**Latest T-017 handoff (2026-11-07):** implementation dependencies T-001–T-016
are merged per the user. T-017 now has 69 passing Python tests, 13 passing frontend
tests, 2 offline and 2 online browser smoke cases, passing build/type/export/source
checks and an offline GitHub Actions workflow. It remains **In review**, not Done:
the new workflow has not run remotely and independent live-evidence review remains
open. T-018 is next after that sign-off and its real audio/evidence prerequisites;
T-018/T-019/T-020 were not implemented. Earlier notes below are historical.

**T-001 and T-002 are Done (verified 2026-11-07).** T-003, T-004, T-005, T-006, T-007, T-009, T-010, T-011, T-012 and T-014 are implemented and In review; tests were explicitly skipped at user request. T-004/T-005 generated real corrected ward, language and recommendation JSON with production schema validation; acceptance and integration sign-off remain pending. T-007 also generated the frozen 48-record FLEURS selection and selected local audio. T-008 has real small-preflight evidence (In review); T-010 exported its measured outcomes with missing modes explicit. The cached runner is implemented with real offline preflight import; the full live paired pilot remains unrun; remaining tickets retain their dependencies.

| Ticket | Feature | Priority | Owner | Depends on | Status |
|---|---|---|---|---|---|
| [T-001](T-001-project-bootstrap.md) | Initialize repo, local Vite/FastAPI and safe defaults | P0 | Shared | — | Done |
| [T-002](T-002-source-and-license-audit.md) | Audit source archive, licenses and provenance | P0 | Dev 1 | T-001 | Done |
| [T-003](T-003-data-schema-and-fixtures.md) | Implement v1 schemas, identity mapping and fixtures | P0 | Shared | T-001, T-002 | In review |
| [T-004](T-004-corrected-census-processing.md) | Generate corrected ward language metrics | P0 | Dev 1 | T-002, T-003 | In review |
| [T-005](T-005-coverage-and-recommendation-ranking.md) | Build coverage model and language-first ranks | P0 | Dev 1 | T-002, T-003, T-004 | In review |
| [T-006](T-006-ward-geometry-validation.md) | Source and validate real Mississauga ward polygons | P0 | Dev 2 | T-002, T-003 | In review |
| [T-007](T-007-reproducible-fleurs-sampling.md) | Generate 48-record FLEURS sample manifest | P0 | Dev 1 | T-002, T-003 | In review |
| [T-008](T-008-elevenlabs-scribe-preflight.md) | Validate real Scribe requests, language hints and credits | P0 | Dev 1 | T-001, T-003, T-007 | In review |
| [T-009](T-009-paired-transcription-runner.md) | Run cached paired ElevenLabs pilot and track failures | P0 | Dev 1 | T-007, T-008, T-010 | In review |
| [T-010](T-010-cer-wer-and-paired-analysis.md) | Calculate multilingual CER/WER and paired summaries | P0 | Dev 1 | T-003, T-007, T-008 | In review |
| [T-011](T-011-ward-map-and-metric-toggle.md) | Implement corrected ward map and count/share toggle | P0 | Dev 2 | T-003, T-004, T-006 | In review |
| [T-012](T-012-global-selection-and-empty-states.md) | Connect modules with safe global language selection | P0 | Dev 2 | T-003, T-004, T-005 | In review — implemented; acceptance incomplete |
| [T-013](T-013-speech-lab-playback-and-comparison.md) | Build authentic-audio speech laboratory | P0 | Dev 2 | T-003, T-007, T-010, T-012 | In review — implemented; acceptance incomplete |
| [T-014](T-014-fastapi-confirmation-state-machine.md) | Implement deterministic confirmation/retry/referral API | P0 | Dev 1 | T-001, T-003, T-008 | In review |
| [T-015](T-015-spoken-recovery-ui-and-tts.md) | Build the demo confirmation flow and spoken prompts | P0 | Dev 2 (UI) + Dev 1 (TTS) | T-012, T-013, T-014 | In review — six voices configured; account/audio verification blocked |
| [T-016](T-016-priority-recommendations-ui.md) | Implement research-backed language/ward recommendations | P0 | Dev 2 | T-005, T-011, T-012 | In review — implemented; acceptance incomplete |
| [T-017](T-017-ci-and-regression-tests.md) | Automate high-risk validation and unit checks | P0 | Shared | T-004, T-005, T-010, T-011, T-012, T-014 | In review — local checks pass; remote CI/reviewer gate pending |
| [T-018](T-018-integrated-local-demo-and-outage.md) | Rehearse full four-act localhost and offline scenarios | P0 | Shared | T-011, T-013, T-015, T-016, T-017 | In review — online/outage checks pass; independent human rehearsal pending |
| [T-019](T-019-attribution-privacy-and-package-audit.md) | Audit licenses, secrets and publishable assets | P0 | Shared | T-002, T-007, T-013, T-015 | In review — implementation only; manual audit and rights/sign-off pending |
| [T-020](T-020-ui-accessibility-and-demo-polish.md) | Finish approachable, accessible visual storytelling | P1 | Dev 2 | T-011, T-013, T-015, T-016 | In review — implemented; manual accessibility and two-person rehearsal pending |

## Status convention

Latest handoff: T-015 has six exact configured voices, draft multilingual
prompts, eleven_v3 metadata/preparation CLI and schema-2.0 per-language approval
caches. Developer 1 reviewed the backend/UI boundary; T-014 state rules remain.
Build/syntax passed; metadata-only check stopped for missing server credentials
with zero requests. No generated/approved audio exists; all languages remain
text-only. No automated tests or other tickets were implemented. T-015 is not
Done; multilingual/Urdu voice and recovery acceptance remains pending. T-017 is
still the next Shared implementation ticket when its test scope is authorized.
Earlier handoffs below describe prior states.

T-016 now supplies source-grounded language priorities, independent count/share
ward lists and separate pilot evidence (In review; automated acceptance skipped).
Next implementation handoff is T-015: UI prerequisites T-012/T-013/T-014 exist;
verified voice/TTS remains shared Dev 1 work. T-020 still depends on T-015.

T-013 now provides authentic local playback, saved paired transcript comparison
and exploratory summaries (In review). T-016 is next ready for Dev 2; T-015's UI
inputs exist, with the shared voice/TTS handoff still required. No automated
acceptance or full offline rehearsal has run.

T-012 now supplies shared language/ward/metric selection and explicit module
availability states (In review). T-013 is the next Dev 2 implementation ticket;
T-016 also has implementation prerequisites. Acceptance sign-off remains pending.

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
T-013 also has backend sample/metric inputs but still needs T-012; T-011 now has
T-006 geometry/loader inputs, and T-016 needs T-011/T-012. No downstream feature was implemented.


T-014 provides backend capabilities/start/decision/retry/session routes. T-015
UI/TTS is the next handoff, still requiring T-012/T-013; T-017 still needs its
listed frontend prerequisites. No unimplemented ticket exclusively assigned to
Dev 1 is currently ready; review/live-pilot gates on implemented work remain open.


T-006 (Dev 2, same branch) now exports 11 individually valid official polygons
joined exactly to T-004 IDs, with provenance/status/hash and a fail-closed frontend
loader. Source vintage/licence/overlap warnings are explicit. No backend/UI/test
changes. T-006 is In review; T-011 is next ready for Dev 2, then T-012. Automated
and browser/fallback acceptance checks remain unrun; neither next ticket started.


T-011 is now implemented and In review: Leaflet ward choropleth, local language/
count-share selection, complete value/context tooltips and an independent verified
table fallback. Production build passed; limited manual Urdu/Ward-10 inspection
observed actual counts/share/denominator while FastAPI was unavailable. No tests
were written/run. T-012 is next ready for Developer 2; no global selection or
later UI modules were implemented in T-011. T-006 source warnings remain visible.
