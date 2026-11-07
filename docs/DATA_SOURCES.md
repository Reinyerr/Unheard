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
| `05_city_311_requests/` | service context | Toronto detailed requests ≠ Mississauga; Mississauga daily contact-centre call statistics for 2017/2018 only |
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

## T-002 executed local audit — 2026-11-07

The source archive was actually present at
`data/raw/Mississauga_Unheard_ElevenLabs_Track.zip` (ignored by Git).
It was read in place with Python `zipfile`; **nothing was extracted or copied to
the frontend**. This is a local availability finding, not a promise that clones
contain the source. The outline DOCX was not found in the inspected repository or
archive; the accepted project documents govern this ticket.

- Archive root: `Mississauga_Unheard_ElevenLabs_Track/`, exactly.
- ZIP size: **490,630,718 bytes** (approximately 467.90 MiB).
- SHA-256: `db3bd4f8469a7302d5c6c2d013661a065c3cd6b90728fc8930a113828e4c4052`.
- Inventory: **2,675 files**, plus 38 directory entries; **593,876,605** uncompressed bytes.
- Formats: 2,185 FLAC, 468 MP3, 17 CSV, 3 Markdown, 1 text, 1 PDF.
- No GeoJSON, shapefile or GeoPackage entries; geometry remains T-006 work.
- No declared pack release number or pinned upstream dataset commit was found in
  the pack documentation. The manifest leaves the version **null** and uses hashes
  to identify the exact supplied snapshot. Retrieval date, original splits and
  audio conversion commands are not reconstructed or invented.

Run from the repository root:

```powershell
backend/.venv/Scripts/python.exe scripts/audit_sources.py --source data/raw/Mississauga_Unheard_ElevenLabs_Track.zip
backend/.venv/Scripts/python.exe -m pytest scripts/tests -q
```

The generated **local-only** `data/processed/source_manifest.json` has status
`passed`, UTC generation time, source/script/policy hashes, selected input hashes,
CSV headers and row counts, an inventory, per-FLEURS-file hashes and format
metadata, coverage checks, dataset counts, license policy links and Git evidence.
Two executions produced identical evidence apart from the timestamp. It is not a
public research data export, and contains no transcript or speaker-background
values. See `scripts/README.md` for extracted-root/environment configuration,
failure semantics and test instructions.

### Verified required inputs

| File | Rows | SHA-256 |
|---|---:|---|
| `language_crosswalk.csv` | 15 | `0f23d538843bcd9f2993c842bcb08201134aaf89c0bfeba059e0fad5c136aad9` |
| `01_people_census/derived/language_coverage.csv` | 15 | `6f372c5ff5994d7907c166356d9cce41e27f7e29f94b88403f34b4aa75377de4` |
| `01_people_census/derived/ward_language_profile_2021_corrected.csv` | 11 | `69ad3fc72a1887fec8917a4cb99970e51f2ad54faa391d7fe1b623722c5dd0fc` |
| `02_speech_home_languages_FLEURS/metadata.csv` | 560 | `af9e839657ff16029fde74cf131e46dc46461b26e7f1b6a10e435f341d4926c7` |
| `03_accented_english_SpeechAccentArchive/metadata.csv` | 468 | `9820aa2d6085318f1ab079103e1ac67d17a0217b1465659ad1f298204fddc769` |
| `04_spoken_requests/minds14/metadata.csv` | 1,050 | `6e0b008a4c334d277becfb3b8782a7dce418c3a28a95b4ed7a853214cebcf83a` |
| `04_spoken_requests/speech_massive/metadata.csv` | 575 | `acfae4cdb8311a00bbe7c63e82220190f7bf790f4dc4ee8487f040347049f253` |

The required CSVs decode with `utf-8-sig` (accepting an optional BOM). Parsing
rejects duplicate/missing headers, inconsistent row widths, empty required values
and invalid numeric/Boolean fields rather than substituting zero. Exact original
headers are retained in the manifest. Important adapters for T-003:

- Ward key is **`ward`**, not `ward_id`; denominator is `population_language_base`.
  Ward 10 is flagged `ward10_corrected=True`, with Urdu **4,520** and denominator
  **73,830**. Corrected ward sums match coverage for all 14 home-language columns.
- Crosswalk has `language`, `census_home_column`, `fleurs_config`,
  `speech_accent_archive_native_language`, `minds14_locale`,
  `speech_massive_locale`, `iso639_1`. Canonical `language_id` does **not** exist in
  the source; T-003 must map it explicitly. Mandarin uses `home_mandarin`.
- Coverage has `language`, `census_home_column`, `city_home_speakers`,
  `fleurs_clips`, `accent_archive_speakers`, `minds14_calls`,
  `speech_massive_commands`, `has_service_request_audio`. Boolean strings are
  `True`/`False`. English's census column/population are blank; preserve missing
  population and exclude English from the **153,480** denominator.
- Recomputed gap: **8** categories, **79,940 / 153,480 = 52.08496221005994%**.
  Each dataset's metadata language counts match the corresponding coverage counts.
- FLEURS columns: `file`, `language`, **`lang_config`**, `iso639_1`, `variety_note`,
  `fleurs_id`, `gender`, `duration_sec`, **`transcription`**, **`raw_transcription`**.
  Both references are nonempty in all 560 rows. Paths are relative to the FLEURS
  directory, start with `audio/`, and resolve to existing unique entries.
- All 14 supplied FLEURS languages have the **same 40 unique sentence IDs**,
  including all six pilot languages. No eight-ID selection has been made.
  Cantonese is `yue` / `yue_hant_hk`; Mandarin is `zh` / `cmn_hans_cn`.
  Bengali is absent only from this pack's FLEURS subset, not a claim about the
  upstream dataset. Arabic, Punjabi and Urdu each have 40 female-labelled clips.

### Audio and optional-source inspection limits

All **2,653** audio references exist and match the per-dataset audio inventories.
Every **2,185 FLAC** has a valid STREAMINFO header; inspection found **mono,
16 kHz, 16-bit** throughout. FLEURS durations agree with metadata within 0.02 s.
All **468 MP3** files have an MP3/ID3 signature. Only the 560 FLEURS audio files
are individually SHA-256 hashed; the complete ZIP hash covers the pack bytes.
These are format/header checks, **not a full decode or listening test**.

The supplied MInDS-14 FLACs are **16 kHz**, whereas the
[upstream dataset card](https://huggingface.co/datasets/PolyAI/minds14/raw/main/README.md)
describes 8 kHz. Preserve the pack format in provenance; the conversion method is
unknown. Do not assume resampling restores information absent from phone audio.

One-time inspection also decoded the other CSVs without extracting them: long
form has 700 rows, neighbourhood profile 56, Toronto request-level CSV **500,269**
rows (75,106,250 bytes), Toronto type/ward summaries 539/178, and Mississauga
2017/2018 call files 303/262 parsed records (including incomplete rows). These are
not cleaned usable counts. The reusable audit inventories those optional/raw files
without semantic validation or bulk 311 processing. The pack dictionary flags
2017 blank rows/typo dates and incompatible year-to-year headers. Raw 311 and
accent analysis are outside MVP; no speaker age/birthplace fields are exported.

### License review and publication gates

`LICENSES.md` was read from the ZIP and hashed:
`6e6c79efdb5f2710e8570d30054745a6b3c19585efcea4e83348e0bb8981eea5`.
The local license policy distinguishes its declarations from independent checks:

| Dataset | Check on 2026-11-07 | Public asset action |
|---|---|---|
| FLEURS | [Google card](https://huggingface.co/datasets/google/fleurs/raw/main/README.md) corroborates CC BY 4.0 | Later curated clips need attribution, source/license links and modification notices; none copied now |
| MInDS-14 | [PolyAI card](https://huggingface.co/datasets/PolyAI/minds14/raw/main/README.md) corroborates CC BY 4.0 | Coverage metadata only for MVP |
| Speech-MASSIVE | [FBK project](https://mt.fbk.eu/speech-massive/) corroborates CC BY-NC-SA 4.0 | No public MVP audio/transcripts; retain noncommercial/ShareAlike restrictions |
| Speech Accent Archive | Pack declares CC BY-NC-SA 4.0; upstream terms were not independently retrieved | Excluded from MVP audio; resolve upstream terms before reuse |
| Mississauga | Pack declares City open-data terms; [older city-hosted terms](https://www.mississauga.ca/file/COM/CityOfMississaugaTermsOfUse.pdf) contain inconsistent city naming, so they do not conclusively establish the applicable dataset terms | Retain attribution; resolve current dataset-specific terms before public export |
| Toronto | [Official licence](https://open.toronto.ca/open-data-licence/) reviewed | Raw 311 remains excluded; attribution required for later reuse |

This ticket records restrictions and unknowns; it does not approve public assets.
Upstream checks do not establish the precise revision used to assemble this pack.
The pack README's broader suggestions about geographic recognition risk and
global dataset absence are **not** adopted; accepted D-001–D-014 still govern.

### Verification and T-003 handoff

- **36 audit tests passed**, using labelled synthetic CSV/header-only audio
  fixtures. Coverage includes BOM/Boolean handling, missing columns with paths,
  absent rows/files, changed totals, duplicate IDs, bad headers, traversal,
  license changes, Git ZIP checks and stale-success replacement.
- **Real-source preflight passed**; repeated manifests matched except timestamp.
  A deliberately missing source exited **1** with a named path and `failed` report.
- **8 backend regression tests passed** (existing non-failing httpx deprecation
  warning). No frontend code changed; the later Urdu/cached speech demo is not yet
  implemented and cannot be claimed as rehearsed.
- Git current index and locally reachable `--all` history contain **zero ZIPs**;
  no raw data/audio are tracked. Archive and generated manifest are ignored.
  This does not inspect remote or unreachable Git objects.

**T-003 is ready:** T-001 and T-002 are complete. Use the verified headers and
hashes above to implement the approved v1 schemas and identity adapters, with
explicitly labelled minimal fixtures. Keep source access configured locally,
preserve English/Bengali missing fields, distinguish Cantonese/Mandarin, and keep
local source-manifest schema separate from public research contracts. Public
asset licensing, geometry acquisition, sampling and speech API validation retain
their later-ticket gates. No T-003 implementation was included here.
