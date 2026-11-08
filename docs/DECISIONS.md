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
