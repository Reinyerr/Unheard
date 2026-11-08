# Local four-act demonstration runbook — T-018

Run from the repository root on `feature/final-integration`. This is a localhost
research prototype. Use the same computer's browser at http://127.0.0.1:5173;
other devices cannot reach this loopback address. Team submission work is D-024.
Observed runs and remaining sign-off: [local-smoke.md](test-evidence/local-smoke.md).

## Cold start

Required: Node >=22.12, Python with the pinned requirements, the committed
`frontend/public/data` artifacts, and the original supplied source ZIP for audio
restoration. A clone has no FLACs, server raw-response cache or approved TTS audio.
Do not regenerate experiments, change the frozen selection or manufacture caches.

macOS/Linux, first setup only (preserve existing environments/configuration):

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

Restore the existing selection only if audio/local manifest is absent, using the
actual location of the supplied ZIP (example path below). This verifies provenance,
references and all 48 asset hashes before installation; it leaves research JSON
unchanged and makes no provider request:

```sh
backend/.venv/bin/python scripts/restore_demo_assets.py --source /path/to/Mississauga_Unheard_ElevenLabs_Track.zip
backend/.venv/bin/python scripts/validate_exports.py --source /path/to/Mississauga_Unheard_ElevenLabs_Track.zip
```

The source check expects 560 metadata rows, 40 common IDs and eight selected IDs
1533, 1537, 1566, 1587, 1608, 1632, 1635, 1651 across six languages (48 clips).
If the ZIP is unavailable, static census/results still load; audio restoration and
playback are blocked. A hash mismatch must be investigated, never bypassed.

Terminal 1, repository root — explicitly disable billed provider calls:

```sh
ELEVENLABS_API_KEY='' backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Terminal 2, repository root:

```sh
npm --prefix frontend run dev
```

Open http://127.0.0.1:5173. Health is http://127.0.0.1:8000/health;
expect `{"status":"ok","mode":"local"}`. The recovery capabilities endpoint
`/api/recovery/capabilities` should report 48 samples and `live_configured:false`.
The backend actually reads **backend/.env**; exporting an empty key overrides it.
Frontend `VITE_API_BASE_URL` defaults to http://127.0.0.1:8000. Keep secrets out of
`VITE_` settings. One backend worker owns ephemeral sessions; restart loses them.
Stop servers with Ctrl+C; resolve occupied ports rather than using a different port.

Windows PowerShell equivalents: use `py -3.12 -m venv backend/.venv`,
`backend/.venv/Scripts/python.exe` and `npm.cmd`. Set
`$env:ELEVENLABS_API_KEY=''` before starting Uvicorn; ensure backend/.env also has
no nonempty key, since Windows may remove an empty environment variable. No key
is needed for the saved route. Existing README installation instructions provide
additional Windows setup details.

## Four acts (each developer performs independently)

1. **Discover:** select global **Urdu**, select Ward 10 on the map (keyboard Enter
   works), and toggle **Share of language base**. Expect 4,520 home speakers,
   6.12%, denominator 73,830 from the corrected 2021 census. Count is the initial
   default. All-language coverage gap is 79,940 / 153,480 across 14 tracked
   non-official categories, eight without supplied task-request audio (52.1%).
   Retain the City attribution and geometry vintage/overlap/licence caveats.
2. **Investigate:** choose `urdu-1533`, play the actual FLEURS clip, inspect the
   reference and both saved raw RTL outputs. Both CERs display 10.6%; paired
   difference is 0.0 percentage points, a tie. WER is unavailable because Urdu
   tokenization is unvalidated. The Urdu summary is selected n=8, scored auto n=1,
   guided n=1, comparable pairs n=1. No claim of improvement or ward performance.
3. **Demonstrate:** choose **Browser-only saved results**, Automatic detection,
   `urdu-1533`, then **Start saved simulation**. Expect confirm and explicit
   saved/simulation labels. Read the displayed transcript and text-only instruction;
   **Correct** leads to accepted. Start a separate saved browser simulation, select
   `urdu-1533`, start, choose **Incorrect**, select different clip `urdu-1537`, then
   **Try Different Sample**. This second clip has no saved result: expect referral
   after attempt 2 and no third retry. Referral only suggests human assistance;
   no municipality is contacted. This is rejection then unavailable retry, not two
   usable-clip rejections. The latter remains a real-data limitation.
4. **Recommend:** expect **Urdu: evaluation priority 1**, separate count/share ward
   lists (Ward 10 in count leaders), source limits and distinct exploratory pilot
   evidence. Ranks concern missing evaluation coverage and population, not failures.

The confirmation prompt is a fixed authored instruction to review displayed text;
it does **not** read the transcript aloud. All six languages currently have no
approved generated prompt. Text-only is the expected fallback. Do not call voice
configuration verified, edit approval flags, or generate TTS during rehearsal.
If an approved cache is later supplied through T-015's exact-hash/listening approval
process, independently check playback, caption meaning, attribution and playback-error
fallback; record reviewer/language/hash. No billable generation is authorized here.
FLEURS attribution: Google / Conneau et al. (2022), CC BY 4.0; links and modification
notice are in the UI, sample artifact and `frontend/public/audio/FLEURS_ATTRIBUTION.txt`.

## Outage and missing-data rehearsal

- Stop FastAPI completely; retain Vite. Reload, observe **Backend unavailable**,
  press **Retry connection**, and repeat all four acts with **Browser-only saved
  results**. Audio/results/map/recommendations must remain usable. Restarting the
  backend and refreshing availability should restore the local route.
- With FastAPI running and no key, choose **Local backend**, saved `urdu-1533`.
  When the original local raw evidence exists, confirm is available; without it,
  expect explicit unavailable result and retry/referral. The browser route uses
  matching committed real exports and works independently of server raw evidence.
  Never describe saved output as a fresh API call. Provider outage/unsupported
  responses are mocked in Python tests; no external provider outage was induced.
- Switch Urdu → Arabic while playing: Urdu player/transcript must clear. Arabic,
  English, Punjabi and Mandarin have Not tested outcomes; Cantonese 1533 automatic
  is incompatible and excluded, guided CER is 10.0%. Select Tamil: no pilot,
  **Not tested**, no numeric CER. Unsupported guidance is not automatic-mode data.
- Browser fault tests below abort only selected requests (no invented responses):
  missing polygons yields the verified ward table; invalid FLAC yields an audio
  warning with saved text retained; missing wards/samples/experiments/recommendations
  each yields explicit unavailable data and preserves independent views.

## Reproduce automated verification

After dependencies and audio are available, install the full Chromium bundle once:

```sh
PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" frontend/node_modules/.bin/playwright install chromium
backend/.venv/bin/python -m pytest backend/tests scripts/tests -q
npm --prefix frontend test
npm --prefix frontend run build
```

Stop manually started Vite: Playwright owns port 5173. With the key-disabled
backend running, then stopped, run respectively:

```sh
PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" npm --prefix frontend run test:e2e -- --workers=1 --output=test-results/online
EXPECT_BACKEND=offline PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" npm --prefix frontend run test:e2e -- --workers=1 --output=test-results/offline
```

PowerShell: set `$env:PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright"` and
`$env:EXPECT_BACKEND='offline'` separately; remove EXPECT_BACKEND for online.
Full Chromium headless is configured because standalone headless shell crashed
with ICU/GPU errors on this Mac. Screenshots/logs are ignored local evidence.
Tests play/decode real FLAC and check elapsed time; this is not human listening.

## Final human sign-off

Developer 1 and Developer 2 each use this runbook from cold start without coaching.
Record name, date, environment, revision, acts, outage result, audible clip check,
errors and fixes in local-smoke.md. Reviewer then verifies the evidence and ticket
status. Automated agent execution cannot certify either developer's rehearsal.
T-018 remains In review until both have passed; T-019/T-020 are outside this work.

## T-020 timing and accessibility handoff

Implementation only, 2026-11-07; the following timings are rehearsal targets,
not measured results. The initial all-language view remains required by FR-A2.
Choose **Start Urdu walkthrough** to select Urdu and focus Discover; this does
not start playback, choose a recording or make a provider request. The selector
and **Reset selection** retain optional exploration across all tracked languages.

| Act | Target | Explain and demonstrate |
|---|---|---|
| Discover | 45 seconds | Read the act question and nearby limit; Urdu Ward 10 count/share, coverage gap versus recognition performance. |
| Investigate | 75 seconds | Choose Urdu 1533, play only a short excerpt, use reference/comparison jump links; explain CER, missing WER and the partial n=1 pair without claiming improvement. |
| Demonstrate | 60 seconds | Browser-only saved route, explicit confirmation, separate rejection/retry/referral path; fixed instruction is text-only until approved audio exists. |
| Recommend | 45 seconds | Language evaluation priority, independent count/share tables and limitations; future recruitment, no ward performance prediction. |

Total target: 3 minutes 45 seconds, including a short source-audio excerpt.
Stop or pause audio explicitly before speaking or changing acts. No autoplay or
cinematic transition is added; caveats and unavailable/error states remain visible.

Manual review (not performed in the T-020 implementation session):

1. Start the frontend with `npm --prefix frontend run dev`. FastAPI is optional
   for the browser-only route; for local API review use the key-disabled startup
   command above. No live transcription or TTS generation is required.
2. With keyboard only: use the skip link, Urdu walkthrough link, language selector,
   each act link, metric buttons and ward table; select Urdu 1533, follow **Read
   reference transcript** and **Compare saved transcriptions**, then reach recovery
   and recommendations with **Next**. Confirm visible focus and no keyboard trap.
   **Change language** should focus the selection section even if data is unavailable.
3. At a narrow viewport and 200% browser zoom, check text wrapping, native audio
   controls, form labels, caveats, scrollable tables and focus outlines. Focus each
   table region and use arrow keys to inspect columns. Check actual contrast with
   a suitable reviewer tool; no contrast-ratio/WCAG conformance result is claimed.
4. Enable system reduced motion; navigate all acts and use map keyboard panning,
   zoom and reset. CSS animations/transitions are suppressed; Leaflet panning is
   immediate and inertial dragging disabled. Ensure all evidence is readable with
   motion disabled, and review forced-colour mode where supported.
5. Use Urdu/Arabic references, saved outputs and recovery reference text to review
   RTL order with a competent reader. Read text without playing audio. If source
   audio fails, the reference and explicit unavailable state must still be available.
   Confirmation audio remains text-only when absent/unapproved; do not change flags.
6. Use a screen reader to check act headings, navigation landmarks, table captions,
   transcript jump targets, audio labels, status messages and changed selection.
   Capture actual browser/reader/version, errors and observed results.
7. Both developers rehearse the timed narrative and existing outage path without
   coaching; record actual timing, comprehension and issues. T-018's historical
   browser evidence predates these UI changes and is not a T-020 acceptance result.

T-020 remains In review until manual keyboard/reading/motion and two-person
explanation acceptance is observed. No tests, build, browser interaction, audio
listening or contrast measurement was performed for this implementation handoff.
