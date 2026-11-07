# Product requirements — UNHEARD v1

**Status:** approved design; implementation and experiments are pending. Source: 25-question grill-me session and attached Sheridan outline / challenge data ZIP.

## Personas and job to be done

- **Primary:** municipal language-accessibility/service-design evaluator.
- **Core decision:** Which tracked languages require additional task-oriented voice evaluation, and which wards offer sensible recruitment focus?
- **Secondary:** hackathon judges explore the evidence through a guided four-act interaction; researchers may inspect experiment provenance.
- **Non-goal:** resident-facing 311 replacement, actual municipal routing, automatic claim of voice-AI failures or individual language ability.

## Research finding and claims policy

- In supplied MInDS-14 and Speech-MASSIVE clips, **eight tracked languages have zero labelled spoken-request recordings**. Summed home-language population is **79,940**; this is **52.1% of 153,480 speakers across the 14 tracked non-official home-language categories**.
- This is **an evidence-coverage gap**, not a measure of inability to use ElevenLabs, not a count of affected 311 callers, and not a model error rate.
- Geography is based on 2021 Mississauga census. FLEURS speech was **not** recorded from identified Mississauga wards.

## Functional requirements (MVP)

### A. Invisible City

- **FR-A1**: Load 11 corrected ward profiles, language crosswalk, and trustworthy ward boundaries or a prominently labelled non-map fallback if boundary matching fails.
- **FR-A2**: Default to `all` tracked languages; the **coverage-gap layer** totals only the eight unmeasured task-request categories. Do not visually imply the other six are uncovered.
- **FR-A3**: Global language selection updates applicable map/chart/detail/recommendation views, and does not fabricate speech results when a language is untested.
- **FR-A4**: Toggle **counts** (default) and **share**. Every tooltip provides both. Share denominator is `population_language_base`; zero denominator = unavailable, not 0%.
- **FR-A5**: Show language-specific home speakers by ward. If a covered language is selected, show its distribution and **covered** status instead of calling it a gap.

### B. Hear What AI Hears

- **FR-B1**: Pilot 6 languages: English, Urdu, Punjabi, Cantonese, Arabic, Mandarin Chinese.
- **FR-B2**: Seeded, reproducible sample of eight unique shared FLEURS sentence IDs across all six languages (48 clips). Preserve sample manifest and model/settings provenance.
- **FR-B3**: Compare automatic detection vs **correct-language guidance if supported** for the identical audio; target 96 requests, subject to actual support and API credits.
- **FR-B4**: Play permitted authentic audio; show raw/reference/automatic/guided transcriptions, highlighted differences, CER, eligible WER, completion and missing statuses.
- **FR-B5**: Apply documented normalization and appropriate script diagnostics. Do not translate or transliterate as a silent preprocessing step.
- **FR-B6**: Show per-language sample sizes, per-clip paired differences, mean CER difference, improved/worse/tied counts, and uncertainty / interpretation limits.

### C. A Second Chance

- **FR-C1**: Prerecorded sample in supported selected language; use Scribe for transcription and ElevenLabs TTS for confirmation where verified available.
- **FR-C2**: A **confirmation-first** state machine allows Correct / Incorrect, one retry, and a human-assistance **referral option**. It must never claim a real 311 agent was contacted.
- **FR-C3**: For prerecorded third-party speakers, judge confirmation is an **interaction simulation**, not the original speaker's consent.
- **FR-C4**: Backend errors must not trap users; use saved actual result + cached licensed/generated prompt if available, clearly marked prerecorded/offline.
- **FR-C5**: No automatic service execution, no live microphone or ElevenLabs Agents required for MVP.

### D. Where Should We Test Next?

- **FR-D1**: Rank by *missing supplied request evaluation coverage* then home-language population (not by assumed model failure risk).
- **FR-D2**: For a priority language, show wards by home-speaker **count** and **share** as independent views and propose realistic next-step testing/recruitment.
- **FR-D3**: Show actual ElevenLabs pilot results separately from demographic rankings; no invented combined risk score.
- **FR-D4**: Explain limitations, caveats, sample size and no-resident-level inference.

## Non-functional requirements

- **NFR-01**: Hackathon operates on **localhost**; React/Vite frontend and local FastAPI are sufficient. Cloudflare is later; a public service is **not** part of this MVP.
- **NFR-02**: Research maps and saved experiment results work without a live ElevenLabs connection.
- **NFR-03**: API key server-side only; limit input to known sample files; no secrets in Git.
- **NFR-04**: Responsive, accessible controls; keyboard navigation, visible focus, captions/transcripts for audio, contrast and reduced-motion consideration.
- **NFR-05**: Reproducible preprocessing and experiments, schema validation, seeded sampling, explicit statuses, reliable tests and provenance.
- **NFR-06**: No misleading 0% for unavailable or incomparable results; avoid unsupported geographic performance claims.
- **NFR-07**: Respect upstream licenses and separate noncommercial-only datasets from publishable MVP materials.

## Deferred/stretch

Neighbourhood choropleth, accented-English experiment, task-intent evaluation, live microphone, Gemini clarification, ElevenLabs conversational Agents, 3D/advanced cinematic transitions, expanded samples, database/authentication, Vultr or public backend deployment.

## Constraints and open technical validations

- Source archive lacks verified ward boundary polygons. **GeoJSON acquisition + label audit required**; blocked map is not a license to invent boundaries.
- ElevenLabs Scribe exact model/version, language guidance support **particularly Cantonese `yue`**, TTS voice coverage, rate limits and credits: **unverified until preflight**.
- If an API option is unsupported, keep the raw automatic result and mark guided comparison unsupported; never switch modes invisibly.
- Dataset speakers, scripts and dialects are not representative of Mississauga; pilot n=8 per language is exploratory.
- Team handles Devpost, GitHub publishing, video, and submission separately; these are **not coding-agent delivery responsibilities**.
