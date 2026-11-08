# Local frontend

From the repository root:

```sh
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open http://127.0.0.1:5173/#discover. FastAPI is optional for the static census
explorer; no ElevenLabs requests are made by the map. The source assets are the
actual generated wards.v1.json/languages.v1.json plus the T-006 local geometry
and validation sidecar. Fixtures are not accepted by this feature.

Production build (does not run a test suite):

```sh
npm --prefix frontend run build
```

T-013 Investigate: choose a pilot language globally, then any of its eight frozen
recordings. Native controls play the curated local FLAC; raw reference and saved
automatic/guided outputs include grapheme highlights, status, CER, eligible WER
and paired delta. The language summary retains actual completion/paired sample
counts and exclusions. Source details show attribution, selection and metric
policy. No speech API call is made. Select Urdu / urdu-1533 for the saved pair;
Cantonese / cantonese-1533 retains incompatible automatic output. Other missing
outcomes remain Not tested. Language switching removes the player/comparison;
ward selection cannot filter speech. Missing audio/codec shows unavailable.
The 48 audio files are Git-ignored: another checkout must acquire the same vetted
T-007 selection before playback; no audio is synthesized as a substitute.
Build and limited browser review passed; automated acceptance was not run.

T-016 Recommend uses the actual generated eight-language priorities, independent
top-three ward tables for count/share and a separate saved pilot summary. Select
a priority language in the table or any covered language globally; ward links
open census context only. Urdu is first (22,535); its Ward 10 values are 4,520 /
6.12% / 73,830. Cantonese and Tamil illustrate different count/share ward lists;
Arabic remains covered and unranked. CER never alters demographic priorities.
Source/hash/rank checks fail closed, and tables work independently of polygons
or FastAPI. Review missing-artifact/outage, keyboard and mobile cases separately
before sign-off. No automated tests were created/run for this ticket.

Discover supports a shared language selector, speaker-count default and
share toggle, clickable/keyboard-selectable ward boundaries, full-value tooltips
and selected-ward details. The verified table remains available independently;
if geometry fails status/hash/ID checks or Leaflet cannot initialize, it becomes
the labelled fallback. If census/coverage validation fails, no numbers are shown.
T-012 connects language, census ward and metric state through a shared provider.
Only language affects speech eligibility and recommendation context; ward stays
in census displays. Selected sample/result are cleared on language changes,
with a revision guard for late results. Anchor navigation preserves selection;
Reset selection restores all languages, no ward, and count.

Manual review:

1. Start with all tracked languages. Only the eight missing-request categories
   contribute to the coverage-gap layer (city subtotal 79,940 in the actual pack).
2. Select Urdu and Ward 10. Count is 4,520, share rounds to 6.12%, population
   language base is 73,830. Toggle count/share; tooltips and detail retain all three.
3. Select Arabic (covered) and English (no supplied census home-language count).
   Covered languages show distribution/covered status; unavailable values stay
   unavailable, with no invented zero percentages.
4. Use table buttons or Tab/Enter/Space to select wards; reset map view if needed.
   Narrow layouts keep map/detail stacked and the table horizontally scrollable.
5. Independently inspect the missing/invalid-geometry fallback and denominator
   edge cases before sign-off. No simulated fixture or automated acceptance
   execution was included. See T-006 for geometry re-acquisition/validation.

Sources details retain attribution and boundary vintage/overlap/licence warnings.
The boundary snapshot is not a certified immutable 2021 edition; public
redistribution approval remains unresolved. No basemap tiles, FLEURS dots,
ward-level recognition rates or speech results are invented. Optional saved
evidence/recommendation failures have separate unavailable states. Tamil shows
Not tested, while actual saved experiment statuses remain explicit. Playback,
comparison and full recommendation controls are later tickets. This is a local research prototype with remaining
review/acceptance gates, not a verified municipal service.

## T-015 Demonstrate: simulated confirmation

Start the backend with the command in backend/README.md and frontend with
`npm --prefix frontend run dev`; open http://127.0.0.1:5173/#demonstrate.
Select Urdu globally, then choose urdu-1533 under Demonstrate's Prerecorded
sample. Start saved simulation: the actual saved transcript appears with its
origin, attempt count and simulation notice. Correct explicitly accepts;
Incorrect permits one different-clip retry. Select urdu-1537 and Try Different
Sample: its missing result is Not tested, leading to referral at attempt 2,
with no invented transcript or further retry. Human-assistance referral option
is available directly from confirmation/retry; no service is contacted.

Select Browser-only saved results before starting to use matching exported actual
evidence without FastAPI. An explicit separate saved simulation is also offered
after completion or uncertain backend response; it never replays/migrates a
possibly completed backend request. For an outage review stop FastAPI, refresh
backend availability, then select this saved route. Missing/mismatched artifacts
fail closed. Current saved evidence has only one usable Urdu clip, so two usable
rejections cannot yet be rehearsed without additional genuine provider results.
English/other missing samples are not substituted with their human references.

Live source is opt-in and may incur charges; it requires backend configuration
and verified guidance for guided mode. Backend key presence does not establish
credits or connectivity. Attempts preserve source/mode and use same-mode saved
fallback only when available. Ward selection cannot change speech membership;
changing language resets the recovery flow, aborts pending UI work and disposes
players. Backend requests already sent may complete after a UI abort.

Six configured voices and authored prompts now share `shared/tts_prompts.json`
with the backend. Model: eleven_v3; IDs exactly match the user's selection.
Prompt preview shows draft text before confirmation, with Urdu/Arabic RTL,
Punjabi Gurmukhi, Cantonese Traditional and Mandarin Simplified scripts. Confirm
shows localized Correct/Incorrect labels alongside English. These are authored
UI drafts, not verified native-language translations or dataset transcriptions.

No audio is generated or approved. All six languages explicitly use text-only
fallback. Follow backend/README.md for metadata-only checking, single-language
billable authorization, staging and exact-hash listening/language approval.
Only approved schema-2.0 language/code/voice/model/text/revision/path/hash matches
can play; cached availability never follows merely from a configured voice ID.
Missing/invalid/unapproved audio and browser playback errors retain text. Runtime
never sends a TTS request. The instruction does not read the transcript or claim
to be the original speaker. Existing confirmation/retry/referral flow is retained.

Limited interactive review observed saved Urdu confirmation, rejection/missing
retry/referral, and browser-only acceptance; build passed. No automated tests were
written/run. Audio listening, keyboard/mobile/language-switch cases, two usable
rejections, actual backend outage and independent full demo remain for review.

Multilingual continuation: build and Python syntax checks passed; metadata-only
CLI stopped with blocked_missing_credentials and zero provider requests.
No automated tests or audio generation/approval were run. Recheck the multilingual
captions, controls, playback, language switching, Urdu recovery and outage paths
manually before sign-off; earlier limited Urdu review predates this extension.
