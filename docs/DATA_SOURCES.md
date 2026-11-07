# Source audit and licensing — supplied challenge data

**Source of truth:** `Mississauga_Unheard_ElevenLabs_Track.zip` supplied by the user, plus `Sheridan Hackathon Ideas Outline.docx`. These inputs are **not bundled with this documentation ZIP**; do not assume they are available to every clone. Paths below are relative to the source archive root `Mississauga_Unheard_ElevenLabs_Track/`.

## Verified source inventory (reviewed 2026-11-07)

| Source path | Role | Source-supplied observations |
|---|---|---|
| `01_people_census/derived/language_coverage.csv` | language evidence coverage | 14 non-official categories + English; 8 with no request clips; 79,940/153,480 ≈52.1% |
| `01_people_census/derived/ward_language_profile_2021_corrected.csv` | ward demographics | 11 wards; use corrected Ward 10 |
| `01_people_census/derived/geo_language_long.csv` | geography/language long form | 700 records: 11 wards ×14, 39 inhabited neighbourhoods ×14; contains a crosswalk join; audit before aggregation |
| `01_people_census/neighbourhood_language_profile_2021.csv` | stretch only | 56 neighbourhood rows, including 17 zero-population areas |
| `language_crosswalk.csv` | canonical language mapping | Cantonese FLEURS `yue_hant_hk`, dataset code `yue`; Mandarin `cmn_hans_cn`, code `zh` |
| `02_speech_home_languages_FLEURS/metadata.csv` | multilingual speech | 560 rows; 40 common `fleurs_id` values × 14 languages; no Bengali |
| `02_speech_home_languages_FLEURS/audio/` | real prerecorded clips | FLAC files referenced by metadata; no requirement to package all clips in repo |
| `03_accented_english_SpeechAccentArchive/metadata.csv` | optional accent study | 468 clips/records; accent attribution needs nuance |
| `04_spoken_requests/minds14/metadata.csv` | task request coverage | 1,050 labelled bank request clips in selected languages |
| `04_spoken_requests/speech_massive/metadata.csv` | task request coverage | 575 voice-command clips in selected languages |
| `05_city_311_requests/` | service context | Toronto detailed requests ≠ Mississauga; Mississauga annual historical call volumes only |
| `README.md`, `DATA_DICTIONARY.md`, `LICENSES.md` | pack documentation | explains corrections, scripts/varieties, clip provenance and reuse conditions |

**Corrected math:** 8 categories have `has_service_request_audio=False`: Urdu 22,535; Punjabi 15,025; Cantonese 10,765; Tagalog 10,695; Tamil 7,420; Hindi 6,640; Gujarati 4,345; Bengali 2,515. Sum = **79,940**. Sum of all 14 *tracked non-official* category counts = **153,480**. Ratio = **52.08496% ≈52.1%**. None of these are a citywide count of persons who cannot use English or a predictive failure count.

**Pilot input availability:** six selected languages (`English`, `Urdu`, `Punjabi`, `Cantonese`, `Arabic`, `Mandarin Chinese`) have 40 FLEURS clips each and share the same 40 IDs. Sampling manifest is **not yet generated**. Urdu, Punjabi and Arabic are recorded by female speakers only within this pack, making any demographic generalization inappropriate.

## Geographic caution

The pack does **not** include vetted choropleth polygon GeoJSON. Obtain a credible Mississauga ward boundary file separately, examine its vintage and ward labels, and match to census IDs exactly. A map of inferred shapes is forbidden. If no validated polygon available, show a ward-level table/bars until suitable geometry is found. Ward 10 **must not** be derived from the incorrect raw ward data.

## Legal/reuse guide (from `LICENSES.md`, not legal advice)

| Data source | Stated license | MVP action |
|---|---|---|
| Mississauga census and municipal 311 | City of Mississauga open data terms | attribute data provider; review redistribution requirements |
| FLEURS | CC BY 4.0 | attribute Google / Conneau et al. (2022), source, link and modifications; curate only necessary clips |
| MInDS-14 | CC BY 4.0 | attribute PolyAI / Gerz et al. (2021); task audio **metadata** sufficient for MVP coverage |
| Speech Accent Archive | CC BY-NC-SA 4.0 | stretch only; do not republish carelessly; no commercial use without permission |
| Speech-MASSIVE | CC BY-NC-SA 4.0 | use for count/coverage; if deriving/releasing audio/transcripts, respect ShareAlike/noncommercial conditions |
| Toronto 311 | Open Government Licence - Toronto | city context only; do not conflate Toronto with Mississauga |

Links from supplied LICENSES file: FLEURS <https://huggingface.co/datasets/google/fleurs>; MInDS-14 <https://huggingface.co/datasets/PolyAI/minds14>; Speech Accent Archive <https://accent.gmu.edu>; Speech-MASSIVE <https://huggingface.co/datasets/FBK-MT/Speech-MASSIVE>; Mississauga <https://data.mississauga.ca>; Toronto <https://open.toronto.ca>.

## Data minimization / packaging

- Keep source archive and high-volume/raw 311 CSV **out of git**. Local-only raw folder ignored by default.
- Copy only a vetted small subset of permitted FLAC clips to public/frontend path after attribution and redistribution review; safe public outputs may include aggregate JSON and derived metrics.
- Avoid keeping speaker birthplace/age or other unnecessary personal fields in public JSON.
- No live microphone is part of the MVP; if later introduced, get meaningful consent and disclose ElevenLabs transmission.
- Record source dataset/version, crosswalk, normalization, model/version and sampling IDs in a provenance manifest.

## Caveats for judges

This is a **coverage-gap** research prototype, not a demonstration of which Mississauga residents *actually* fail with AI. Non-local FLEURS is not a representative resident or 311 sample. Task audio sources represent bank/assistant requests, not actual Mississauga 311 calls. Script differences and speaker imbalances limit CER comparability. Guidance improvement and live voice demo are hypothetical until the experiment is run and verified.
