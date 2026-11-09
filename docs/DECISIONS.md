# Decision record — 25-question grill-me

**Status:** Approved through Question 25, with explicit amendments. These are decisions, **not claims that implementation/tests are complete**.

| ID | Topic | Confirmed choice / amendment |
|---|---|---|
| D-001 | Core purpose | Evidence-based voice accessibility investigation + tested language-guidance intervention / separate fallback demo; not a 311 replacement. |
| D-002 | Primary user | Municipal language-accessibility and service-design teams. |
| D-003 | Core outcome | Recommend which language communities need task-specific evaluation and where recruitment could focus. |
| D-004 | Prioritization order | Identify language-level evidence gaps **first**; use geography second. |
| D-005 | Ranking | Missing task-request recordings in supplied pack, then home-language population; show experiment CER separately, no weighted failure score. |
| D-006 | Geographic granularity | 11 Mississauga wards required for MVP; neighbourhood map is stretch; boundary validation mandatory. |
| D-007 | Map metrics | Display count (default) and share; always show both; use `population_language_base`; absent denominator = unavailable. |
| D-008 | Interaction | Global language selector joins module views at *language* level; do **not** join speech outcomes to ward residency. Missing experiment → `not_tested`. |
| D-009 | Pilot languages | English, Urdu, Punjabi, Cantonese, Arabic, Mandarin Chinese; **Cantonese replaces Polish**. |
| D-010 | Sampling | Fixed seed `2026`, eight common FLEURS sentence IDs per language; 48 clips × 2 modes = planned 96 requests; no cherry-picking. |
| D-011 | Metrics | CER primary; WER only with reliable language-specific tokenization; paired within-language comparisons, script flags. |
| D-012 | Failures | Retry transient API errors; preserve failed/unsupported/incompatible results explicitly; saved demo if API unavailable. |
| D-013 | Success criterion | Exploratory results: promising improvement, mixed/inconclusive, or no improvement; report sample sizes/uncertainty, no population-level proof. |
| D-014 | Recovery | Confirmation-first transcription + one retry + human-assistance referral; no intent-routing claim. |
| D-015 | Audio input | Prerecorded clips MVP, microphone stretch; third-party clip confirmation is explicitly simulated. |
| D-016 | AI architecture | Deterministic FastAPI state machine + Scribe + TTS; ElevenLabs Agents stretch, not required. |
| D-017 | Repo & contracts | One GitHub monorepo; stable schema; static research JSON independent of live API; local FastAPI for dynamic requests. |
| D-018 | MVP freeze | Four lean modules and one integrated Urdu research/demo narrative before adding polish or stretch features. |
| D-019 | Ownership | Developer 1 data/AI/backend, Developer 2 frontend/visuals; three integration checkpoints; shared review, fallback rules. |
| D-020 | QA | Risk-based tests, mocked API in CI, GitHub Actions, independent real API preflight and complete local demo rehearsal. |
| D-021 | **Amended deployment** | **Localhost for hackathon** (React/Vite + FastAPI); defer Cloudflare until **after hackathon**. Earlier Cloudflare-now and GitHub-Pages-now proposals were rejected. No mandatory public-hosted backend. |
| D-022 | Data protection | Attributed FLEURS samples MVP, minimal experiment metadata, no unnecessary PII, comply with licenses, no unconsented live recording. |
| D-023 | Storytelling | Guided four acts: Discover → Investigate → Demonstrate → Recommend; Urdu first, optional free exploration. |
| D-024 | **Amended submission ownership** | **Team handles** GitHub/Devpost/video/submission and event logistics itself. Coding assistant produces implementation and guidance, not submission materials unless separately requested. Earlier assistant-owned submission framing rejected. |
| D-025 | **Amended implementation workflow** | Documentation-first, ticket-driven development. Create `AGENTS.md`, roadmap, requirements, architecture, contracts, tests and per-feature ticket specifications **before coding**. |

## Conflict-resolution order

1. Latest explicit amendment overrides earlier proposals (especially D-021/D-024/D-025).
2. Confirmed decisions override optional suggestions in the original Sheridan outline.
3. Source dataset facts and license conditions override speculative claims; document discrepancies rather than silently replacing them.
4. Implementation choices not decided in the interview are marked as **proposed**, and can be refined in the appropriate ticket without altering product intent.

## What is *not* an accepted fact

- Successful ElevenLabs guided-language experiments, CER statistics, confidence intervals, or evidence of improvement. **Not run in this documentation package.**
- Verified local deployment, working map GeoJSON, functional recovery demo, or public website. **Not built yet.**
- Exact supported Scribe language hints / model-version API syntax or multilingual TTS support. **Requires real preflight.**
- Official submission deadlines or sponsor requirements beyond the provided pack. Team independently checks its event portal.

## Implementation clarification — T-002 (2026-11-07)

No product-scope or public-contract amendment. The source audit now emits a
**local-only** `source_audit` manifest (`schema_version: "1.0"`) under ignored
`data/processed/`. It records observed file hashes, counts, formats and license
restrictions, not public application artifacts or redistribution approval.
Missing pack/upstream version is `null`; hashes identify the supplied bytes.
Audit failure replaces stale success with `status: "failed"` and a path-specific
error. The audit accepts an explicit ZIP or exact extracted root, reads without
extraction and makes no API requests. In the observed pack MInDS-14 FLAC headers
are 16 kHz, despite the upstream card's 8 kHz description; conversion history is
unknown. See `DATA_SOURCES.md` for evidence and unresolved publication gates.


## Implementation clarification — T-007 (2026-11-07)

No public-contract or product-scope amendment. The ignored local
`sampling_manifest.json` (`schema_version: "1.0"`) freezes all 48 sample records,
source hashes and selected audio path/size/checksum provenance before experiments.
Its content digest excludes generation time; matching reruns retain the original
timestamp. Changed frozen inputs are rejected without a reselection override.
The public export uses the existing `Samples` contract. Curated FLEURS assets
retain attribution, source/license links and modification notice; no other source
audio is approved and no provider outcomes are generated. T-019 remains open.

## Implementation clarification — T-008 (2026-11-07)

No public-contract or product-scope amendment. Local-only `preflight_log.json`
and per-run reports (`schema_version: "1.0"`) record exact options, frozen
selection/audio hashes, attempts, response evidence, numeric allowance snapshots
and guidance-parameter acceptance. Raw response files are ignored and known-key
redacted. Documented provider hints are candidates until real HTTP evidence;
acceptance does not establish script comparability or quality. No retries/cache
are introduced here; T-009 owns those. Missing server credentials are a blocked
configuration state with zero attempts and not_tested guidance, never a metric.


## Implementation clarification — T-010 (2026-11-07; review pending)

No public schema fields/enums or product scope changed. Metric policy v1 uses
NFC Unicode code points, punctuation-to-space, English-only casefolding and
whitespace-free CER; preserves diacritics/scripts with no translation or variant
conversion. WER is enabled only for English whitespace tokens until other
language tokenizers are validated. Script/code/manual-review flags exclude
incompatible outputs with null metrics; raw outcomes remain intact. Empty valid
recognition is scored, empty normalized reference excluded. Clip means are
unweighted; paired delta is autoCER-guidedCER with tie tolerance 1e-12. No
confidence intervals or significance claims from the tiny partial preflight.

Existing public source metadata carries policies, flags and hashes. Local-only
metric_details.json (schema_version 1.0) preserves raw/reference/normalized strings,
edit counts and evidence paths. Summary completion counts refer to comparable
scored modes; exclusion statuses count once per clip/status and may overlap.
Input terminal reports reuse T-008's attempt fields (one entry per sample/mode),
plus existing selection/model provenance. T-009 must resolve retries before export;
no runner/cache is introduced here. Review and automated verification remain open.


## Implementation clarification — T-009 (2026-11-07; review pending)

No public schema, identity, selection or ranking change. Local cache identity is
SHA-256 of audio hash + provider endpoint/API version + model alias + canonical
request options shared with the adapter. Historical provider alias weight
revisions remain unknown. Matching completed/incompatible/unsupported responses
are reused; immutable local attempt/raw evidence and checksummed histories remain
separate from the latest terminal export. Original provider status is preserved
separately from T-010 comparability and review flags. T-010 accepts optional local
review_flags on terminal attempts; the existing public source metadata carries
those flags without new public fields.

The local experiment_attempts envelope (schema_version 1.0) retains T-008's
selection/model/attempt shape, plus all 96 mode states, per-language counts,
run config/events and import/script provenance. Retry histories stay outside the
one-terminal-entry-per-mode export. Default execution is offline; --live permits
bounded sends only for automatic and live-evidenced guided modes. Unknown guidance
stays not_tested; never silently switch settings. No resampling after outcomes.

Transient retries are capped per invocation/mode and by total new-POST budget;
previous failures require explicit retry selection. Unknown interrupted calls
are journalled and not automatically replayed. A local exclusive lock protects
concurrent runners, not provider-side idempotency; timeout retries can still bill
again. These are implementation policies, not claimed crash/retry test evidence.
All automated tests and the full live pilot remain unperformed by user instruction.


## Implementation clarification — T-014 (2026-11-07; review pending)

No product-scope or shared static-schema amendment. The previously proposed
recovery API is finalized in DATA_CONTRACTS.md and backend recovery schemas:
explicit saved/live origin, optional same-mode saved fallback, one session-
preserving retry endpoint with a different curated clip, and an explicit refer
choice. Two total attempts per session; accepted/referral terminal. Confirmation
is always the current user's simulation over third-party recordings, never
original-speaker consent or municipal action. TTS remains unavailable under this
ticket, with null audio URL, pending T-015.

Sessions use a 128-entry in-memory store with 1800-second idle expiry; deployment
is one localhost worker, with no database/auth or persistent user data. Body
limit is 4096 JSON bytes, strict IDs/enums/fields, no uploads. Live calls use the
T-008 restricted adapter without automatic network retries; saved fallback never
switches language guidance modes. Only matching real saved evidence and usable
nonempty script-compatible text can enter confirm. Configuration/guidance without
an attempted provider result remains not_tested, not fabricated numeric success.
Live errors return safe details plus a recoverable session/referral state.


## Implementation clarification — T-006 (2026-11-07; review pending)

No product-scope or existing research/backend schema amendment. Geometry uses
the official City ArcGIS layer 2 snapshot, not inferred ward shapes. A separate
geometry/status sidecar (schema_version 1.0) binds 11 individual polygon-valid
ward IDs to corrected census IDs. A typed frontend loader returns an explicit
unavailable branch for missing/invalid geometry; T-011 owns fallback rendering.
Coordinates are preserved without repair; observed cross-ward overlap slivers
remain disclosed diagnostics. Vintage is a current-layer snapshot with City
2006-onward scheme evidence, not a certified immutable 2021 edition. Linked
terms returned HTTP 403 and public redistribution approval remains deferred to
T-019. These caveats must accompany the later map. Tests/visual acceptance remain
unrun, so T-006 stays In review. No backend or T-011/T-012 implementation added.


## Implementation clarification — T-011 (2026-11-07; review pending)

No public contract/backend or scope amendment. The ward view uses Leaflet 1.9.4
with only vetted local GeoJSON, no external basemap tiles. Count is default;
share uses population_language_base. Five equal color intervals are recalculated
per metric/language and grey indicates unavailable data; colors are not a combined
risk score. Tooltip/detail/table always retain count/share/denominator/context.
An independent ward table renders if geometry is missing/invalid or map rendering
fails. T-006 source/vintage/licence/overlap caveats remain visible. This ticket's
language/ward/metric state is local to Discover; T-012 owns cross-module linkage.
No experiment outcome is joined to residency. Automated acceptance remains unrun.

## Implementation clarification — T-012 (2026-11-07; review pending)

No shared JSON/API schema or product-scope amendment. A React selection provider
now replaces Discover-local state: language/all synchronizes module eligibility,
while ward selection remains census-only. Language changes clear sample/result
and advance a revision token; async consumers must retain the request's token
when accepting results. Unknown language IDs fall back to all with a notice.
Static census, saved experiment and recommendation resources use existing v1
validators, with optional failures isolated. Missing evidence stays unavailable;
recorded failure statuses and Not tested never become numeric zero. Playback,
comparison and recommendation detail UI remain subsequent tickets. Build and
limited browser review passed; stale playback and failure-path acceptance remain
unverified, with no automated tests written/run at the user's request.

## Implementation clarification — T-013 (2026-11-07; review pending)

No public schema, metric policy, backend or product-scope amendment. The speech
lab reads the frozen local sample manifest and saved experiment artifacts;
matching selection hashes/identities gate comparisons. Raw-text highlighting
uses graphemes (Intl.Segmenter), separate from exported normalized code-point
CER; unsupported segmentation/large texts fall back to raw output. No translation
or metric recalculation. Audio/sample/result selection is language-only and
clears on language change; native controls pause on player unmount. Saved origins,
all missing/failure statuses, uncapped ratio percentages, paired percentage-point
deltas, scored denominators and tiny-sample limitations remain explicit. Build
and limited Urdu RTL/playback/language-switch inspection passed; acceptance,
native-language readback and independent outage rehearsal remain incomplete.

## Implementation clarification — T-016 (2026-11-07; review pending)

No public schema, backend, ranking policy or product-scope amendment. Frontend
recommendations preserve T-005's exported language ranks and check census source
hash/coverage/count agreement. Ward tables independently rank corrected counts
and unrounded shares, with ascending ward ID ties and unavailable values excluded.
Suggested IDs retain count-ranking semantics. These tables do not depend on
polygons. Covered languages expose demographic context without a missing badge;
actual pilot summaries remain a separate section and never affect priorities.
Actions recommend consented task evaluation/recruitment and safeguard validation,
not forecast failure or service execution. Build and limited Urdu/Arabic browser
inspection passed; no automated tests were created/run; full acceptance remains
incomplete.

## Implementation clarification — T-015 (2026-11-07; review pending)

No product-scope or static research schema amendment. Recovery now has a UI for
T-014's actual API and an explicitly separate browser-only saved simulation.
The latter uses matching frozen manifests and exported real comparable outcomes;
missing/flagged/empty results cannot enter confirmation. Each simulation allows
at most two attempts with a different clip on retry. Neither route treats a
judge's action as original-speaker consent or a municipal service action.
Unknown backend response/timeout is never automatically replayed; explicit new
saved simulation is separate from the potentially completed server session.

TTS runtime is cache-only. Additive API fields allow cached/unavailable status,
relative public audio path, authored caption and attribution; capabilities list
cached languages. A deliberately bounded preparation CLI verifies the candidate
English model-language and premade voice via actual GET responses, then permits
one fixed authored English instruction POST without retries. It stages audio
locally; exact-hash manual listening approval is required before public-local
copying. UI independently checks the manifest/hash and handles playback errors.
The fixed prompt instructs review of displayed text; it does not read arbitrary
transcripts and is only offered for English. Other language voices/translations
have no verification evidence and stay text-only. No cloning or new sponsor.
This implementation is based on official API references, not a live support claim.

No key/voice is configured, so no live TTS preflight, generation or audio approval
occurred. Prompt attribution and account/voice usage review precede generation;
T-019 public packaging review remains required. Build/syntax and limited manual
saved Urdu flow review passed; automated tests were explicitly prohibited by the
user. Full outage, two-usable-clip rejection and spoken-prompt acceptance remain
open. T-015 is In review with actual TTS blocked, not Done.

## T-015 multilingual continuation — 2026-11-07 (review pending)

At the user's explicit request, this supersedes T-015's English-only prompt /
premade-only implementation restriction, not any accepted product decision.
Six exact user-selected voices and language-specific authored draft instructions
now share one non-secret catalog. eleven_v3 is preferred and the only configured
model; official docs list all six target codes. Existing httpx conversion endpoint
supports its request shape. No v2 fallback or replacement voice is inferred.
Runtime remains cache-only and T-014 transitions, retries/referral and attempt
limits are unchanged. Model advertisement, voice GET access, successful synthesis,
manual language/listening review and approved playable cache are distinct states.

Each single-language billed preparation needs explicit --authorize-billable and
rights review. It stages one prompt as pending_review; exact-hash approval plus
manual language/listening review is needed before playback. Caption translations
are authored drafts, not verified language quality; they cannot be treated as
research evidence. No dataset transcript, microphone input or cloned voice is
sent. Per-language prompt sidecar advances to 2.0; public research/API schema
fields remain compatible. Fixed instructions ask users to review displayed text,
not arbitrary transcript readback. Urdu remains first for manual preparation.

Developer 1 reviewed the boundary and identified the former frontend/contract
English-only gate; this continuation updates those together, with exact identity
and approval checks. No T-014 rewrite. The example-file key-shaped value was
removed; a real exposed credential must be rotated separately. No server key is
configured. Metadata-only CLI recorded blocked_missing_credentials, zero requests;
no audio generated/approved. Build/syntax passed; no automated tests. New manual
multilingual/Urdu recovery/audio/outage acceptance remains open, so not Done.

## Implementation clarification — T-019 (2026-11-07; review pending)

No product-scope or public JSON/API contract change. The new read-only package
audit emits a local report (schema_version 1.0) with target local/public, timestamp,
Git HEAD, frozen selection hash/count, inspected counts, audio inventory and
path/code findings. It never packages files or changes approval metadata. Existing
frozen FLEURS and TTS validators govern asset identity/local approval; public
redistribution is a separate manual rights decision. Unresolved applicable City
terms and provider-account output rights deliberately block the public target.
Current index/worktree/public/dist inspection is not Git-history review or legal
clearance. No tests/build/audit command ran under this implementation-only request.

## Implementation clarification — T-020 (2026-11-07; review pending)

No public contract, data, metric, API or recovery-rule change. FR-A2's initial
all-language selection and reset remain intact; the explicit Urdu walkthrough
link is the guided entry required by T-020, not an automatic language override.
It does not choose clips or trigger audio/provider requests. Shared accessibility
styles, focusable native fragment targets, act questions/limits, scrollable table
regions and supplied recovery reference text improve the existing four acts.
Map pans are immediate with inertia disabled; CSS reduced-motion rules apply
throughout. No tests/build/manual browser or listening review ran, so accessibility
and two-person presentation acceptance remain pending rather than certified.

## T-020 visual continuation — 2026-11-08

Explicit user request supersedes the earlier all-pans-immediate presentation:
remove the old hero/event line/server-health panel, use supplied SDG 10 artwork
and magenta theme with a Target 10.2 inclusion framing, and make the verified
ward map the main view. Ward selection now flies to its real bounds and opens
an animated census popup. Reduced-motion preferences disable CSS reveal and use
immediate map fitting; toggling reduction during a ward flight stops it. Reset
clears selection and restores city bounds. No data/API/schema change; counts,
shares/denominators, source caveats, fallback table and speech/geography separation
remain. Target 10.2 is thematic context, not a measured SDG indicator or UN endorsement.
The recovery module retains its own backend-capability handling; the removed
landing-page health polling is no longer needed. No provider calls introduced.

## T-021 approved guided presentation — 2026-11-08

User explicitly approved the proposed T-021 before implementation. This refines
D-023's presentation without changing its Discover → Investigate → Demonstrate →
Recommend order: one visible act, persistent Next/Back/progress, focused headings,
retained component/session state and paused inactive audio. Existing fragment
continuations remain compatible. Initial/reset language remains all; Urdu is an
explicit exploration choice, not an automatic selection or audio trigger.

The formerly deferred cinematic scope is narrowed to permit a lightweight
screen-space ward lift in existing Leaflet 1.9.4's SVG renderer. A decorative,
noninteractive footprint uses the same vetted coordinates; CSS translates only
the selected rendered path, with outline/depth and subdued neighbors. This
supersedes T-020's selection flight/popup presentation; the readable adjacent
ward panel and Clear/reset controls retain count/share/language-base context.
No actual elevation, geographic risk score, geometry mutation or 3D engine.
Reduced motion disables transitions, retaining a static selection/depth cue.

The supplied SDG artwork remains byte-for-byte unchanged. Opening/final framing
describes alignment with SDG 10, without UN endorsement or a proven inequality
outcome. Progressive disclosure retains source metadata, failure statuses,
sample counts, methodology, raw outcomes and full recruitment plans. No research
JSON, API, metric, ranking, backend, retry or audio approval contract changed.

Observed frontend tests/build, 14 real-local-artifact browser cases, responsive
and visual review are recorded in `test-evidence/guided-demo.md`. No provider
requests or new audio generation. Human rehearsal/listening, prior review and
rights gates remain open; T-021 is In review rather than automatically Done.

## T-021 minimalist refinement — 2026-11-08

The user's explicit refinement request supersedes T-021's exact opening slogan
and promotional framing. Retain the guided acts, original SDG artwork, SVG ward
lift/dimming and evidence disclosures; use factual headings, full-width map and
selected-only compact ward details. Shared native audio controls gain whole-file
waveforms decoded from each recording's own bytes; native currentTime/events
control the seek position. Decoding never creates a second playback source.
Decode/browser failures retain native playback and explicit fallback. This is
presentation-only; research JSON, data counts, APIs, recovery and TTS approval
contracts remain unchanged. No dependency or provider request is introduced.

## T-021 language shortcut removal

At the user's explicit request, remove Discover's Explore Urdu shortcut. This
supersedes the earlier dedicated Urdu-entry button requirement; Urdu remains an
explicit choice in the persistent language dropdown. All-language initial/reset
selection, guided order and data/API contracts remain unchanged.

## T-021 three-step visual redesign — 2026-11-09

The user approved Discover → Investigate → Demonstrate as the public journey,
superseding the four-act presentation in D-023. Recommend is no longer mounted
in the journey. Its datasets, ranking implementation and export contracts remain
available for research. The old fragment opens Discover. The recovery simulation
ends on acceptance or referral and links back to the map.

Discover carries the citywide supplied task-audio coverage finding using the
validated census and coverage artifacts. Ward selection, count/share, sample
selection, playback, recovery routes and state transitions retain their existing
behavior. The dark map and waveform surfaces sit within a light reading layout;
ward, layer and outcome motion follows system reduced-motion settings. No API,
data, metric or geometry contracts change.

### T-021 dark palette and plain-language comparison

The user restored the dark presentation and removed the standalone boundary,
accessibility, pilot-summary and metric/source panels from Discover and
Investigate. The ward table, map attribution, FLEURS credits, sample counts,
reference transcript and keyboard/audio interactions remain available. The
comparison calls the two modes “Without a language hint” and “With a language
hint” and interprets only the exported per-clip paired difference. Data,
metric and API contracts are unchanged.

### T-021 ward coverage and waveform controls

Discover switches its task-audio coverage figure from the citywide tracked
categories to the selected ward. For a ward, the numerator covers all eight
gap categories and the denominator is the ward's census language base. Clearing
the ward restores the citywide figure. Investigate links to the audio attribution
file in place of the long credit line.

The shared recording waveform now includes playback, seeking, mute and volume
controls. Native controls are the fallback when waveform decoding is unavailable.
Playback still uses the same media element and pauses on navigation. Data, metrics,
geometry, and backend contracts are unchanged.
