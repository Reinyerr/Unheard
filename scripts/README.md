# Reproducible processing scripts

T-002 supplies the read-only source audit. T-004 exports corrected ward aggregates
and T-005 exports language coverage and recruitment priorities using the T-003
schemas. T-007 freezes attributed FLEURS samples; experiments belong to later tickets.

From the repository root (Python 3.12, no additional runtime dependencies):

```powershell
backend/.venv/Scripts/python.exe scripts/audit_sources.py --source data/raw/Mississauga_Unheard_ElevenLabs_Track.zip
backend/.venv/Scripts/python.exe -m pytest scripts/tests -q
```

The script does not assume this ZIP exists. Alternatively set a shell environment
variable pointing to the ZIP or the **exact extracted pack directory**:

```powershell
$env:UNHEARD_DATA_ROOT="C:/your-local-source/Mississauga_Unheard_ElevenLabs_Track"
backend/.venv/Scripts/python.exe scripts/audit_sources.py
```

`--source` overrides the environment. The standard-library script does not load
`.env` automatically. No whole-archive extraction or copying audio is needed.
Leave the original archive where it is; never add it to Git.

The default output is ignored `data/processed/source_manifest.json`. Exit code 0
means the required source checks passed; 1 means failed. A failed attempt writes a
new **failed** report instead of leaving stale successful evidence at that path.
Optional `--output` must remain under this repository's `data/processed/` and end
in `.json`. Do not publish the local inventory. Errors name the source path.

The manifest contains archive and selected-file hashes, sizes, CSV headers/row
counts, coverage totals, metadata/audio reference checks, audio header formats,
FLEURS common-ID availability, license/attribution policies and Git ZIP checks.
No transcripts, speaker background or raw audio bytes are exported. FLEURS
audio is hashed individually. Other audio gets format-header checks only; raw
census/311/optional tables are inventory-only. Audio is not decoded for playback.
License review metadata is maintained in `source_licenses.json`; running the audit
does not refresh upstream websites or grant redistribution permission.

Tests generate explicitly synthetic CSV and header-only audio fixtures in temporary
directories. They do not require the real archive or network. The separate command
against the actual archive is the live local integration preflight. See
`docs/DATA_SOURCES.md` for the observed audit and unresolved provenance limits.

## Corrected census export (T-004)

Use Python 3.12+ with the existing backend requirements installed. From the root:

```sh
python3 scripts/prepare_census.py --source '/Users/rainierjorgejorda/Downloads/Mississuaga File/Mississauga_Unheard_ElevenLabs_Track'
# Alternatively, read the original ZIP without extraction:
python3 scripts/prepare_census.py --source '/Users/rainierjorgejorda/Downloads/Mississauga_Unheard_ElevenLabs_Track.zip'
```

Replace these machine-local paths as needed. `UNHEARD_DATA_ROOT` is also supported;
`.env` is not loaded automatically. Only the corrected ward table, coverage table,
and crosswalk are read. Their SHA-256 hashes, row/category counts, provider
attribution, correction status and limitations are included in `source` metadata.
No source CSVs or audio are copied; the explicitly MOCK fixture directory is untouched.

Output: `frontend/public/data/wards.v1.json`, ordered by numeric ward ID, with all
14 mapped home-language counts, eight coverage-derived gap IDs, ward gap totals,
and unrounded percentages using `population_language_base`. English is excluded
from the tracked census counts. Blank/zero/negative denominators become null;
malformed values, duplicate wards, incorrect Ward 10 flags, unmapped categories,
changed crosswalk identity and city/ward total discrepancies fail explicitly.
The known corrected Ward 10 baseline remains mandatory. Census category sums
describe the supplied categories, not unique people or ASR failure rates.

The script validates with the existing Pydantic `Wards` schema before atomically
replacing output. Exit 0 means generation succeeded; exit 1 means an input/export
failure, leaving any previous file unchanged. A previous export is historical
output, not evidence that a later failed run succeeded; inspect exit status and
generation time. CLI argument errors exit 2. No network or API calls are made.

This artifact is for the local prototype. Dataset-specific municipal
redistribution terms remain unresolved in `docs/DATA_SOURCES.md`; this export
does not grant public redistribution approval.

**Integration limit:** the T-003 Vite build guard requires all five artifacts as
soon as any root-level artifact exists. The current census/coverage checkout consequently
has an incomplete bundle and cannot pass that guard until later tickets supply
the other real artifacts. Do not fill them with fixtures or invented results.
No frontend logic or build guard is changed here. Acceptance tests were neither
created nor run at user request; production generation is not full sign-off.

## Coverage and recruitment priorities (T-005)

Run after the T-004 census export, with the same source and Python environment:

```sh
python3 scripts/prepare_coverage.py --source '/Users/rainierjorgejorda/Downloads/Mississuaga File/Mississauga_Unheard_ElevenLabs_Track'
```

An explicit ZIP or exported `UNHEARD_DATA_ROOT` also works. This command reuses
T-004's real-source guards and requires the existing ward export's values and
three input hashes to match. Missing/stale/fixture ward artifacts fail explicitly;
rerun `prepare_census.py` first. It does not rewrite ward output.

Outputs are `frontend/public/data/languages.v1.json` (all 15 source languages,
including English with null census population and six selected pilot languages)
and `recommendations.v1.json` (only the eight missing-task-audio categories).
Rank is descending city home-speaker count, then ascending canonical language ID
for ties. Covered languages remain explorable in the language artifact and have
no unmeasured-category recommendation. The 79,940/153,480 subtotal excludes English.

For each recommended language, `suggested_action` labels two independently
calculated top-three lists with values: count for recruitment volume and share
for concentration. Share is 100 × language count / `population_language_base`;
unavailable denominators are excluded, and ties use ascending ward ID. Ranking
uses unrounded ratios; displayed shares use two decimals. `suggested_ward_ids`
contains the count-ranked list. The existing shared schema has one ward-ID list,
so the share list is supplied as labelled text without adding contract fields.
No combined score, experiment metrics or claim of geographic ASR failure is made.

Provenance includes input/script/ward-export hashes, row/category counts,
selection policies, provider attribution, license restrictions and `not_tested`
experiment status. No audio/transcripts or new dependencies are added. Both
schema-validated outputs are staged before replacement; each replacement is
atomic, but the pair is not a filesystem transaction. If a write fails, fix the
error and rerun before consuming the pair. Exit codes: 0 success, 1 processing
failure, 2 argument error. No tests were created or run for this implementation.

Manual review: inspect the two JSON files, confirm Urdu is first of eight with
22,535 home speakers, sum recommendation populations to 79,940, check English's
null population, and independently compare count/share ward ordering against
`wards.v1.json`. Confirm recruitment language and limitations are preserved.
The partial-bundle frontend guard and public municipal licensing limits above
remain unresolved; no frontend logic is changed.


## Frozen FLEURS samples (T-007)

Use the same Python environment and explicit source configuration:

```sh
python3 scripts/sample_fleurs.py --source '/Users/rainierjorgejorda/Downloads/Mississuaga File/Mississauga_Unheard_ElevenLabs_Track'
```

ZIP input and `UNHEARD_DATA_ROOT` also work. No full extraction, network requests,
new dependencies or API credentials are needed. The script validates all 560
metadata rows, identities, 40 IDs per supplied language, verbatim references and
referenced FLAC headers/durations. Eight numeric IDs are drawn from the sorted
six-pilot intersection with `random.Random(2026)`.

Outputs:

- Ignored `data/processed/sampling_manifest.json`: frozen inputs, selection,
  48 records, selected audio paths/sizes/hashes and selection-content digest.
- `frontend/public/data/samples.v1.json`: existing T-003 schema, 48 actual records
  with reference texts, gender, duration and attributed provenance.
- 48 local `frontend/public/audio/<config>/<config>_<id>.flac` files copied
  byte-for-byte after FLEURS-only license/selection review, plus
  `frontend/public/audio/FLEURS_ATTRIBUTION.txt`. Audio remains Git-ignored;
  regenerate on each machine or review deliberate packaging under T-019.

Matching reruns preserve the first generation timestamp and content digest,
allowing byte-stable manifest/public JSON. Changed frozen source/selection/audio
is rejected. Do not delete the manifest or reselect after observing outcomes.
No reselection override is provided. Generation exits 0 on success, 1 for input/
export failure, 2 for argument errors. Exports are individually atomic, not one
transaction; fix any interrupted-copy failure and rerun the same frozen selection.

Manual reproducibility commands (not run as tests here):

```sh
shasum -a 256 data/processed/sampling_manifest.json frontend/public/data/samples.v1.json
python3 scripts/sample_fleurs.py --source '/Users/rainierjorgejorda/Downloads/Mississuaga File/Mississauga_Unheard_ElevenLabs_Track'
shasum -a 256 data/processed/sampling_manifest.json frontend/public/data/samples.v1.json
```

Compare digests, inspect eight shared IDs across all six languages and 48 unique
sample IDs, compare source references and manifest audio hashes, and listen to
clips. Header validation is not full decoding/acoustic review. n=8 and script/
gender differences limit generalization; no ward residence inference is allowed.
No outcomes/metrics are generated. T-008 is next; the frontend build guard still
needs the real experiment artifact. No automated tests were created or run.

## Small live Scribe preflight (T-008)

Uses the existing backend `httpx` dependency and the frozen T-007 manifest/audio.
It reads the exported server environment only; it does not load `.env` or accept
keys on the command line. From the root in zsh:

```sh
read -rs 'ELEVENLABS_API_KEY?ElevenLabs API key: '
export ELEVENLABS_API_KEY
python3 scripts/preflight_scribe.py
```

Default: first frozen ID for Urdu and Cantonese, auto and guided (4 POSTs), plus
two small subscription GETs if the run completes. Each POST uses identical
audio/options apart from the guided candidate `language_code`. Documented model
alias is `scribe_v2`; fixed endpoint is HTTPS API v1. No automatic fallback,
retries, metrics or batch experiment runner. Optional explicit subset:

```sh
python3 scripts/preflight_scribe.py --languages english arabic punjabi mandarin_chinese
```

That subset makes eight POSTs. Each invocation can bill again; there is no
experiment cache yet. Rate/credential/permission/quota failures stop further
POSTs; partial results remain. Network timeouts have unknown provider billing;
do not assume an error means no charge. Remaining/unselected guidance is
not_tested, never implicitly supported. Numeric allowance snapshots may be
unavailable with restricted key permissions and do not certify pilot affordability.

The adapter takes only allowlisted sample IDs, validates frozen identities and
audio hashes/size/signature, and exposes an injectable HTTP client for later
mocking. Local `ScribeAttempt` includes raw text, statuses, options, timestamps,
request IDs, safe rate/error metadata and retryability. The adapter does not
retry; T-009 can later use these results. Empty successful transcript is distinct
from HTTP failure. Explicit guided language rejection is unsupported; generic
HTTP errors are technical_error; malformed success is incompatible_output.
Script/translation review is deferred to T-010, with no metrics filled in here.

Inspect ignored `data/local/preflight_log.json` and the corresponding
`data/local/preflight_runs/<run_id>/` report/raw response files. Reports are
incrementally saved; each invocation creates separate evidence and replaces the
latest log from the start. No headers containing credentials or full account
profiles are saved. Known-key text is redacted; stdout contains only IDs/status.
Treat raw transcripts as local research evidence, not frontend assets.

Exit 0 (`recorded`) means an automatic transcript and accepted/rejected guidance
evidence were captured for selected probes; independently inspect response
quality/language and request settings before sign-off. Exit 1 means blocked or
incomplete; exit 2 means argument error. Missing key is a configuration error,
not a failed recognition or zero CER. This implementation's observed execution
was blocked by missing key, with no network/provider requests. No tests were
written/run. Finish live verification before T-010, then T-009.


## Offline metrics and paired summaries (T-010)

From the repository root with the existing backend Python dependencies:

```sh
python3 scripts/calculate_metrics.py
```

Default input is ignored `data/local/preflight_log.json`, using recorded T-008
responses; no key, network, new dependencies or API calls. Explicit later input:

```sh
python3 scripts/calculate_metrics.py --input data/processed/experiment_attempts.json
```

The future T-009 runner must supply a report containing selection_sha256,
model_id, api_version and an attempts array with one final entry per sample/mode,
using the existing adapter's evidence fields plus raw_response_path. Completed
outcomes need retained JSON response evidence under data/local, matching frozen
sample/audio/model identities, HTTP success and raw transcript. Full retry logs
must remain separate; duplicate terminal entries are rejected. Unknown samples,
changed selection/model/settings and broken raw evidence fail explicitly.
Paired request options may differ only in language_code. No runner is added here.

Outputs: `frontend/public/data/experiments.v1.json` and ignored
`data/processed/metric_details.json`. All 48 samples remain present even when
unattempted; missing outcomes are not_tested with null metrics. Existing full
five-artifact bundle validation runs as a production guard before public output
replacement. This is not a test-suite run or frontend build. Each output is
individually atomic; rerun after an output-write failure. Exit codes: 0 success,
1 processing/validation failure, 2 CLI misuse. Input failures preserve old exports,
which remain historical rather than evidence of a successful new run.

Policy `nfc_codepoints_punctuation_space_english_casefold_v1`:

- NFC preserves scripts/combining marks; punctuation becomes spaces, whitespace
  collapses, and only English is casefolded. No diacritic removal, transliteration,
  translation or simplified/traditional conversion.
- CER uses Unicode code points after whitespace removal; edit distance uses unit
  insertion/deletion/substitution costs. Divide by reference length; do not cap
  ratios. Valid empty successful text has full-deletion CER; empty normalized
  references are incompatible, never scored as zero.
- WER uses English whitespace tokens only. Other five languages return null until
  tokenization is separately validated. This conservative MVP policy is explicit.
- Expected script must form at least half of reference/output letters, allowing
  minority loanwords/acronyms. Unexpected script/detected-language mismatch and
  saved manual exclusions yield incompatible_output and null CER/WER. Automatic
  same-script translation and Chinese variant detection are not provided; retain
  manual review. Recorded Cantonese auto's simplified/traditional mismatch is
  excluded without conversion. Raw outputs remain untouched.
- Delta is autoCER minus guidedCER only for comparable modes of the same clip.
  Positive means lower guided CER. Per-language means are unweighted clip means;
  mean delta uses paired clips only. Completion counts mean scored comparable
  outcomes, not all HTTP successes. Ties use tolerance 1e-12. Unpaired reasons
  count once per clip/status, with overlap across reasons explicitly allowed.

Public source metadata contains input/selection/raw-response/script hashes,
normalization/tokenization policy, flags, counts and interpretation limits. Local
metric details retain raw/reference/normalized strings, edits and evidence paths.
Raw reference strings are also preserved in the sample artifact. Never infer
ward-level performance or population effects; the preflight has only one paired
Urdu clip, not a completed n=8 pilot. No confidence intervals/significance claims.

Manual review: inspect Urdu raw/reference/normalized strings and edit counts,
independently recompute its ratios/delta, inspect Cantonese auto flags/null metrics,
and confirm 48 records/6 summaries retain all selected and unattempted modes.
No automated tests were written/run. The pinned runtime, frontend build and full
Urdu/cached demo remain unverified. T-009 is next; no later ticket was implemented.


## Cached paired pilot runner (T-009)

From the root, using existing backend Python dependencies and the real local
manifest, audio and preflight evidence:

```sh
python3 scripts/run_experiments.py
```

Default is offline: import the latest real T-008 report, verify raw evidence,
cache terminal results, resolve all 96 frozen modes and export through T-010.
No key/network is needed. Existing completed results and review exclusions are
reused. Output is local data/processed/experiment_attempts.json plus per-run
snapshots, local cache/history/raw files and the existing public experiments JSON.
There are 48 selected clips, not 48 completed experiments; inspect actual counts.

For new paid requests, export the server key securely, then explicitly run:

```sh
python3 scripts/run_experiments.py --live --max-requests 12
```

The cap includes retries; default cap is 96 new POST attempts per invocation.
--languages urdu cantonese restricts sends to those languages without changing
any selected IDs. Each pending mode allows at most three sends by default
(--max-attempts 1/2/3). Only transient failures retry with backoff/Retry-After.
Known successful, incompatible and unsupported results are never re-purchased.
A previous retryable technical failure requires --retry-failed; permanent errors
remain explicit. Provider timeouts have unknown billing and a retry can bill
again; no provider idempotency claim is made. Retry-After over 30 seconds pauses
for later resume; credential/permission/quota and exhausted rate errors stop sends.

Guided requests require real accepted language/model/hint evidence from retained
preflight/cache records, not a dataset code or documentation list. Urdu/Cantonese
currently have evidence. To complete the other guidance probes with the existing
T-008 tool, explicitly run:

```sh
python3 scripts/preflight_scribe.py --languages english arabic punjabi mandarin_chinese
python3 scripts/run_experiments.py
```

The first command makes up to eight new POSTs; the second imports them without
new calls. Earlier cached Urdu/Cantonese results remain. Optional --preflight
accepts a local report path and may be repeated to import multiple evidence files.
Inputs must remain under data/local or data/processed. Changed model/config/audio
or corrupt evidence fails explicitly; no guessed transcript or support state.
Unknown/rejected guidance is skipped, remains visible, and never falls back to auto.

Cache keys hash frozen audio bytes, endpoint/API/model and canonical form options.
Both adapter and runner use the same request-options function. No new provider
model or hidden settings are introduced. Raw redacted provider responses and
immutable attempt envelopes live under data/local/raw_scribe_responses; checksum
histories under data/local/experiment_cache. Cache import retains provider_status
separately from script/comparability exclusions. Cached review_flags flow to T-010.

Before every send an in-flight journal is persisted. Interrupted calls are not
automatically replayed: inspect the cache, corresponding raw/provider evidence,
and data/local/experiment_run.lock. Confirm no runner is active before removing
a stale lock. Resolve any uncertain request manually; do not blindly clear its
journal. No automatic force-reset option is supplied. Reports with unresolved
in-flight requests do not replace public metrics. The local lock protects runner
concurrency; it cannot guarantee remote exactly-once billing.

Terminal report: one attempts entry per observed sample/mode, 96 mode_states,
guidance evidence, per-language selected/attempted/provider-completed/comparable-
completed/failed/not_tested counts, unresolved journals, config, events and hashes.
Full retry history is retained outside the terminal export. Valid partial output
is usable by calculate_metrics.py; missing/unsupported/errors never receive zero
metrics. Interrupted/blocked input preserves previous public exports. Outputs
are individually atomic, not a transaction across all files. Completed run
snapshots stop changing; latest report is replaced on later invocations.

Exit 0 covers successful offline processing, partial evidence or a planned/live
pause (inspect status/stop_reason); it does not mean 96 requests succeeded. Exit 1
means blocked/interrupted/invalid evidence or export failure; 2 is CLI misuse.
Default production processing observed four real cached modes, 92 not_tested,
zero new POSTs. No tests, paid full-pilot run, error-path rehearsal or frontend
build were performed. T-009 is In review; T-014 is the next Dev 1 implementation.
