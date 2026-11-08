# Data contracts v1 — proposed schemas (implementation source of truth)

**Status:** proposed JSON/API schema, not output already generated. Any change requires compatible frontend/backend updates and ticket/decision log amendment. D-003–D-014 and D-017.

T-003 implementation: `backend/app/schemas/research.py` and
`frontend/src/types/research.ts` implement the five static artifact contracts;
`shared/language_map.json` is derived from the audited source crosswalk. Tests and
fixture round-trips were skipped at user request; these are not yet verified.
Each artifact requires `source` metadata. Only explicitly labelled fixtures
(`is_fixture: true`, `fixture_label` starting with `MOCK`) may have a null generation
time. Loaders reject fixtures unless explicitly opted in. Fixtures under
`frontend/public/data/fixtures/` contain synthetic references, no audio, and no
experimental metrics; future fixture views must display `fixture_label`.
Validate complete exports with `validate_bundle` / `validateBundle` to check
foreign keys. Vite builds reject incomplete/invalid generated artifact bundles
when root-level `public/data/*.v1.json` artifacts exist; fixtures are excluded.
Blank crosswalk fields become null, including English's census column and
Bengali's FLEURS config. Public field names and status enums remain unchanged.

## Normalized identity rules

- `language_id`: stable lowercase ASCII slug: `english`, `urdu`, `punjabi`, `cantonese`, `arabic`, `mandarin_chinese`, plus remaining tracked categories from crosswalk. **Not** the FLEURS config or presumed ElevenLabs hint.
- Keep explicit mappings: `fleurs_config` and `dataset_language_code` from the crosswalk (Cantonese `yue`, FLEURS `yue_hant_hk`). **Verify** the distinct actual ElevenLabs parameter support before API use.
- `ward_id`: integer 1 through 11; store as number in all JSON. Polygons must expose a verified join property mapped to integer ward IDs.
- `sample_id`: stable string e.g. `urdu-1511` (language + shared `fleurs_id`); `fleurs_id` serialized as integer, sorted numerically for reproducibility.
- All percentages: `0..100` in displayed/public JSON; all raw CER and WER: unitless **ratios**, not percentages (`0.12` = 12%). Ratios may exceed 1 due to insertions. UI must format correctly.
- No magic `-1`, `'N/A'` or numeric `0` meaning missing. Use null and a status.
- All emitted files contain `schema_version`, `generated_at_utc`, `source`/`provenance` metadata. Hash selected source inputs if feasible.

## Shared enums

```text
coverage_status = no_task_audio | has_task_audio
experiment_status = not_tested | completed | technical_error |
                    unsupported | incompatible_output
origin = live | saved
map_metric = count | share
recovery_state = select_language | ready | transcribing | confirm |
                 accepted | retry_or_refer | referral
```

An API timeout is `technical_error`; an API success containing an empty text for valid audible speech may be a `completed` recognition result with CER computed. Wrong-script or translated responses should carry `incompatible_output` until reviewed with transparent rules; preserve raw response regardless.

## Static artifact: `languages.v1.json`

```json
{
  "schema_version": "1.0",
  "generated_at_utc": null,
  "languages": [
    {"language_id":"urdu", "display_name":"Urdu", "census_home_column":"home_urdu",
     "city_home_speakers":22535, "coverage_status":"no_task_audio",
     "request_clip_counts":{"minds14":0,"speech_massive":0},
     "fleurs_config":"ur_pk", "dataset_language_code":"ur", "pilot_selected":true}
  ]
}
```

*The Urdu source count is grounded in the supplied CSV; `generated_at_utc: null` signifies this **illustrative contract snippet**, not a generated artifact.* Additional languages must be generated from `language_crosswalk.csv`/coverage, not typed in by hand.

## Static artifact: `wards.v1.json`

```json
{
  "schema_version":"1.0", "generated_at_utc":null,
  "source_file":"01_people_census/derived/ward_language_profile_2021_corrected.csv",
  "missing_request_language_ids":["urdu","punjabi","cantonese","tagalog","tamil","hindi","gujarati","bengali"],
  "wards":[
    {"ward_id":10,"population_language_base":73830,
     "gap_population":null,"gap_share_pct":null,
     "home_speakers_by_language":{"urdu":4520}}
  ]
}
```

`gap_population` and `gap_share_pct` are **null placeholders** in this proposed sample, not actual Ward 10 output. The pipeline must compute them from all eight missing languages. Ward 10 Urdu count and denominator above come from corrected ward CSV. Required invariant: `gap_share_pct = 100 * gap_population / population_language_base` when denominator positive; otherwise `null`.

## Static artifact: `samples.v1.json`

```json
{
  "schema_version":"1.0", "selection":{"seed":2026,"strategy":"common_fleurs_ids_random_sample","ids":[]},
  "samples":[
    {"sample_id":"urdu-1511","language_id":"urdu","fleurs_id":1511,
     "audio_path":"audio/ur_pk/ur_pk_1511.flac",
     "raw_reference_transcript":"<read from metadata; not invented>",
     "reference_transcript":"<read from metadata>",
     "gender":"female","duration_sec":null}
  ]
}
```

The placeholder transcript and null duration are **schema examples only**. Never deploy this JSON verbatim as verified output. The pipeline copies the metadata's actual `file`, transcription and speaker metadata fields; public audio path must be rewritten only after license review / deliberate asset selection.

## Static artifact: `experiments.v1.json`

```json
{
  "schema_version":"1.0", "generated_at_utc":null,
  "model":{"provider":"elevenlabs","model_id":null,"api_version":null},
  "records":[
    {"sample_id":"urdu-1511","language_id":"urdu","fleurs_id":1511,
     "auto":{"status":"not_tested","transcript_raw":null,"cer":null,"wer":null,"request_id":null},
     "guided":{"status":"not_tested","language_hint":null,"transcript_raw":null,"cer":null,"wer":null,"request_id":null},
     "paired_delta_cer":null,
     "provenance":{"source_dataset":"FLEURS","evaluated_at_utc":null}}
  ],
  "summaries":[]
}
```

In populated records: `paired_delta_cer = auto.cer - guided.cer` **only** when both values are comparable and valid. An unrelated API error is not an error rate. Summary fields: `language_id`, `n_selected`, `n_auto_completed`, `n_guided_completed`, `n_paired`, `mean_auto_cer`, `mean_guided_cer`, `mean_delta_cer`, `improved_count`, `worsened_count`, `unchanged_count`, `unpaired_reasons`. Prefer sample means for per-clip reporting; disclose weighting if using pooled rates. No manufactured confidence intervals.

## Static artifact: `recommendations.v1.json`

```json
{
  "schema_version":"1.0", "generated_at_utc":null,
  "method":"missing_task_audio_then_city_home_speakers_desc",
  "items":[
    {"language_id":"urdu","reason":"No labelled spoken-request audio in supplied task datasets",
     "city_home_speakers":22535,"rank":1,"suggested_action":"Collect consented realistic municipal request samples",
     "suggested_ward_ids":[],"limitations":["No measured ward-specific recognition rate"]}
  ]
}
```

`Suggested_ward_ids` is populated from *verified* ward-specific counts and/or shares. Recommendations should name the selection criterion (most speakers vs highest concentration), not invent an overall risk score.

## Local recovery API — T-014 (implemented, In review)

Static research v1 fields/enums are unchanged. API examples were previously
proposals; T-014 now defines concrete backend schemas in
`backend/app/schemas/recovery.py`. Frontend integration remains a separate ticket.

- `GET /health`: unchanged `{"status":"ok","mode":"local"}`.
- `GET /api/recovery/capabilities`: actual frozen language/sample IDs, per-mode
  usable saved sample IDs, guided-verification flags, selected_sample_count,
  live_configured (key presence, not connectivity/credit proof), TTS unavailable,
  simulation notice and session limits. No keys, raw paths or provider metadata.
- `POST /api/recovery/start`: required language_id/sample_id; optional source
  (`saved` default or explicit `live`), mode (`auto` default or `guided`), and
  allow_saved_fallback (true default). Creates a new simulation/session and
  consumes its first attempt. Inputs are curated IDs, never uploads/paths.
- `POST /api/recovery/decision`: session_id and decision correct/incorrect/refer.
  Correct/incorrect require confirm. Correct accepts only explicit confirmation;
  first rejection allows retry_or_refer, rejection after attempt 2 gives referral.
  Refer is allowed from confirm/retry_or_refer. Accepted/referral are terminal.
- **Concrete retry addition:** `POST /api/recovery/retry` accepts session_id and
  a different unused sample_id in the same language. It preserves attempts and
  mode; optional source/allow_saved_fallback explicitly change those choices.
  Only retry_or_refer permits retry, with at most two total attempts. A new start
  creates a separate simulation; it is not an in-session retry/reset.
- `GET /api/recovery/sessions/{session_id}` reads the current session, including
  transcribing while a provider request is in progress.

Successful responses contain session_id, state, language_id, sample_id, mode,
transcript (usable text or null), source (actual live/saved or null when none),
requested_source, transcription_status (existing experiment status), attempts,
max_attempts=2, retry_available/retry_sample_ids, confirmation_prompt,
referral_message, simulation_notice and fallback_reason. prompt_audio_url is
null and tts_status is unavailable; T-015 owns TTS. Retry IDs are unused curated
clips, not a guarantee that saved responses exist; inspect capabilities per mode.

Saved responses require frozen identity/audio/options and retained real raw
provider evidence; source is always saved. Live fallback uses the identical
sample/mode only and is explicitly labelled saved with a reason. Incompatible,
flagged or empty text cannot enter confirm. Valid empty provider recognition is
not a technical error or usable confirmation; wrong-script output is incompatible.
Missing configuration/unverified guidance remains not_tested with no metrics.
No transcript/reference, demographic, experiment-metric or speech metadata is
returned beyond the selected transcript/IDs and requested mode/provenance label.

Error shape: `{"error":{"code":"...","message":"...","retryable":false}}`.
After a consumed failed attempt, also includes session with retry/referral state,
so the user is not trapped. Invalid IDs/payloads return 400/422, unknown/expired
sessions 404, invalid transitions/repeated clips 409, payload >4096 bytes 413,
non-JSON/compressed bodies 415, unavailable data/provider/saved result or capacity
503. Explicit provider guidance rejection returns 422 unsupported_language;
unverified guidance is a distinct 422 guidance_not_verified. Failed attempts
consume the session's two-attempt budget; invalid request/sample selection does
not. Error messages never include secrets, provider bodies or local paths.

Sessions are bounded in-memory per process (128 sessions, 1800-second idle TTL),
reset on restart, and require one localhost Uvicorn worker. No persistence/auth,
mic capture, intent routing, agent or real municipal contact is introduced.

## Contract safeguards

1. Validate static JSON against schemas; fail build on bad foreign keys, duplicate IDs or enum values.
2. Preserve unknown/missing results distinctly. Never emit numeric result values for `not_tested` or `unsupported`.
3. Changing global selected language clears stale per-sample transcripts/results; changing ward only changes geographic metrics, not the experimental sample membership.
4. `schema_version` changed on incompatible modifications. Keep UI fixture in sync before merging.
5. Keep references to original file names, source paths and model request settings. Raw API JSON stored locally and redacted before public sharing.


## T-010 export policy clarification (no field/schema change)

The experiment exporter now populates the existing schema from actual saved
provider outcomes. n_selected includes all eight frozen samples per language;
untested modes remain not_tested with null metrics. Summary completion counts
refer to comparable scored outcomes, excluding incompatible_output even when
HTTP succeeded. Unpaired reasons count once per clip/status and can overlap.
Raw/reference strings remain in samples/local metric details; review flags and
normalization/tokenization/interpretation policies use existing string-valued
source metadata. WER is currently English whitespace tokens only; other pilot
languages have null WER pending validated tokenization. See DECISIONS.md and
scripts/README.md for the explicit code-point CER and script-review policies.


## T-009 local runner integration (public v1 fields unchanged)

The ignored experiment_attempts.json report reuses the T-008 terminal-attempt
shape accepted by T-010, bound to selection_sha256/model_id/api_version. attempts
contains at most one observed terminal result per sample/mode; mode_states covers
all 96 planned modes with explicit not_tested/missing reasons. Local attempt
extensions include provider_status, review_flags, origin, cache_key and response
hash/path. T-010 preserves those review flags in existing source metadata. Raw
responses, retry history, locks/in-flight journals and evidence stay local.
Cache completion means a retained provider result, not a comparable CER success.
No frontend types, statuses or schema version were changed.
