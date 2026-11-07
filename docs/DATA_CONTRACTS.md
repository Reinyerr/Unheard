# Data contracts v1 — proposed schemas (implementation source of truth)

**Status:** proposed JSON/API schema, not output already generated. Any change requires compatible frontend/backend updates and ticket/decision log amendment. D-003–D-014 and D-017.

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

## Proposed local API endpoints (contracts, not implemented)

- `GET /health`: `{"status":"ok", "mode":"local"}`.
- `GET /api/recovery/capabilities`: supported selections and TTS configuration from verified backend setup, not guesses.
- `POST /api/recovery/start`: `{ "language_id": "urdu", "sample_id": "urdu-1511" }` → `{ "session_id": "...", "state":"confirm|retry_or_refer", "transcript": "...|null", "source":"live|saved", "attempts":1, "max_attempts":2, "prompt_audio_url": "...|null" }`.
- `POST /api/recovery/decision`: `{ "session_id":"...", "decision":"correct|incorrect" }` → updated state, retry availability and referral text. For retry state, frontend must select a **different** licensed/known sample ID via another controlled endpoint or a new start request; exact endpoint to be finalized in T-014.
- Failure: `{ "error": {"code":"unsupported_language|api_unavailable|invalid_sample|invalid_transition|quota_exhausted", "message":"...", "retryable":false} }` with proper HTTP status. All backend data types validated by Pydantic and limited to a dataset allowlist.

## Contract safeguards

1. Validate static JSON against schemas; fail build on bad foreign keys, duplicate IDs or enum values.
2. Preserve unknown/missing results distinctly. Never emit numeric result values for `not_tested` or `unsupported`.
3. Changing global selected language clears stale per-sample transcripts/results; changing ward only changes geographic metrics, not the experimental sample membership.
4. `schema_version` changed on incompatible modifications. Keep UI fixture in sync before merging.
5. Keep references to original file names, source paths and model request settings. Raw API JSON stored locally and redacted before public sharing.
