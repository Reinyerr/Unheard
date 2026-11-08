# T-018 local integration evidence

Date: 2026-11-07, America/Toronto (EST). Operator: Codex automated execution,
**not either developer's independent human rehearsal**.
Branch: `feature/final-integration`; starting commit
`b7759d3b7a435966fa63b72c7201cc1c5f6ad6cd` (`T-017 & WIP T-018`).
This evidence describes that commit plus the T-018 working-tree changes listed
below; no commit was created by this session.
Environment: macOS arm64, Node v22.22.2, Python 3.14.7, Playwright 1.65.0,
full Chromium 158.0.8127.18 (build 1254). The existing venv exposes some base
packages; pinned pip installation succeeded but emitted an unrelated conda /
ruamel-yaml resolver warning. No system package changes were requested.

## Existing progress before this session

- All four modules, shared selection, real corrected census/map, saved comparison,
  recovery API/browser simulation, cache-only prompt gating and recommendations
  were implemented by T-001–T-017. They were preserved.
- b7759d3 added the eight-case `demo.spec.ts` partial T-018 suite and audio
  restoration helper, alongside T-017 tests. Prior T-017 evidence recorded 69
  Python tests, 13 frontend tests and two shell cases each online/offline; it did
  not record executing the new full demo suite.
- T-018 ticket/index were TODO; runbook was a proposed script, and this evidence
  file did not exist. No evidence established either developer's rehearsal.
- Dependencies exist in code and real artifacts. Their historical In review
  statuses, T-017 remote CI/live-review gate and T-015 audio approval gate were
  not treated as completed sign-off. User authorized this continuation of T-018.

## Commands and observed results

All commands below ran from repository root; no billable/provider command ran.
The actual source was the ignored external file
`/Users/rainierjorgejorda/Downloads/Mississauga_Unheard_ElevenLabs_Track.zip`.

| Command | Observed result |
|---|---|
| `backend/.venv/bin/python -m pytest backend/tests scripts/tests -q` (initial) | Failed: pytest missing from existing venv. |
| `backend/.venv/bin/python -m pip install -r backend/requirements.txt` | Initial sandbox network/DNS failure; permitted retry installed pinned dependencies successfully. |
| `PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" frontend/node_modules/.bin/playwright install chromium` | Full Chromium, standalone shell and FFmpeg installed in ignored workspace cache. |
| `backend/.venv/bin/python -m pytest backend/tests scripts/tests -q` | **70 passed**, no skips, 4.92s; one existing httpx/Starlette deprecation warning. Network blocked and providers mocked by fixtures. |
| `npm --prefix frontend test` | **13 passed**, 3 files, 1.80s. Includes approval/hash/playback-error gating with explicitly mocked bytes, not real TTS approval. |
| `npm --prefix frontend run build` | TypeScript and production artifact guard/build passed. Existing Vite native-loader future-compatibility and >500kB chunk warnings. |
| `backend/.venv/bin/python scripts/validate_exports.py --source /Users/rainierjorgejorda/Downloads/Mississauga_Unheard_ElevenLabs_Track.zip` | Passed: actual corrected census, coverage, ranks and seeded selection match exports; 560 metadata rows, 40 common IDs, 11 wards, 15 language IDs, 8 priorities, 48 samples / 96 explicit modes. |
| `backend/.venv/bin/python scripts/restore_demo_assets.py --source /Users/rainierjorgejorda/Downloads/Mississauga_Unheard_ElevenLabs_Track.zip` | Restored 48 verified local FLACs, attribution and frozen manifest; research JSON unchanged. Selection SHA-256 `59f8c23640f271eefa5787fdedd3833e0091af14e40e448e1f4c8a58584d886c`. |
| `ELEVENLABS_API_KEY='' backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000` | Sandbox bind initially denied; permitted run started real FastAPI. Health/capabilities HTTP 200, live_configured false. Original retained raw evidence made saved Urdu 1533 usable. |
| `PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" npm --prefix frontend run test:e2e -- --workers=1` (initial) | 4 passed / 6 failed: five Chromium standalone-shell ICU/GPU crashes; one incorrect test assumption that local saved Urdu evidence was absent. |
| Same browser command after fixes | **10 passed**, 36.0s with actual FastAPI. See coverage below. |
| Ctrl+C on the owned Uvicorn process | Clean shutdown observed, process exited 0 before offline suite; backend was actually stopped. |
| `EXPECT_BACKEND=offline PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" npm --prefix frontend run test:e2e -- --workers=1 --output=test-results/offline` | **10 passed**, 11.4s with actual FastAPI process stopped. |
| `backend/.venv/bin/python -m compileall -q backend/app scripts` | Passed. |
| `git diff --check` | Passed after final changes. |

Browser tests start/stop real Vite, interact with rendered UI and abort all
non-loopback browser traffic in demo cases. Invalid-data tests abort selected
local asset requests, never substitute fabricated data. Provider key was empty;
the direct live-origin missing-key preflight explicitly disabled saved fallback,
returned HTTP 503 / not_tested, and sent no provider request. Actual backend saved
start returned 200; rejection then missing second result returned 503/referral.
No API key, raw provider body or transcript was printed in this evidence.
Online screenshots were retained under ignored `frontend/test-results/online/`;
offline four-act screenshot is under `frontend/test-results/offline/` and the two
offline bootstrap screenshots are at `frontend/test-results/bootstrap-*-offline.png`.
Both owned servers were stopped at the end.

## Observed coverage

- Urdu Discover: real 11-ward geometry; Ward 10 count 4,520, share 6.12%,
  denominator 73,830; metric toggle and keyboard selection.
- Investigate: real `urdu-1533` FLAC decoded and currentTime advanced >0.1s,
  duration >0. Saved raw RTL outputs visible; auto/guided CER both 10.6%,
  delta 0.0 percentage points; WER unavailable. Selected n=8; auto/guided
  scored n=1 each, paired n=1. This is a tie, not evidence of improvement.
- Browser-only confirmation: explicit correct → accepted; separate simulation,
  reject → different `urdu-1537` retry → referral with no third retry. Clip 1537
  has no measured saved output; there was no second usable transcript to reject.
- Recommend: Urdu priority 1; independently ranked count/share wards; verified
  79,940 / 153,480 (52.1%) coverage context and limits.
- Urdu → Arabic disposes old player and clears Urdu text. English, Arabic,
  Punjabi, Mandarin outcomes Not tested; Tamil outside pilot. Cantonese auto
  incompatible/excluded, guided CER 10.0%. No missing outcome becomes 0%.
- Missing polygons: labelled verified table; failed FLAC: warning while saved
  transcripts/metrics remain. Missing wards, samples, experiments or
  recommendations: explicit unavailable states and independent views preserved.
- Backend route uses capabilities and actual saved evidence, reaches confirm,
  rejects once and exhausts retry on absent second result. Missing-key API state
  is explicitly not_tested. Browser route remains a separately chosen simulation.
- Existing Python suite checks mocked timeout/unsupported/quota, attempt bounds,
  transitions, invalid inputs and cached TTS gates. No new live provider preflight
  or real external-provider outage was exercised.

Export inspection: 96 modes comprise **3 completed, 1 incompatible_output,
92 not_tested**. Only Urdu has a comparable pair; no full six-language pilot is
claimed. WER currently has no measured English result and unvalidated tokenizers
for the other pilots. Source/license links, modifications and sample counts
remain in the original UI/artifacts. City geometry is a current-layer snapshot
with disclosed vintage/overlap/licence limits, not a certified 2021 edition.

## Fixes and changed files

- `frontend/playwright.config.ts`: full Chromium headless channel avoids observed
  macOS standalone-shell ICU/GPU crash.
- `frontend/e2e/demo.spec.ts`: inspect real saved capabilities before asserting
  confirm vs missing evidence; explicitly disable saved fallback for missing-key
  check so retained real evidence does not mask that failure state.
- `docs/DEMO_RUNBOOK.md`: actual setup/restoration/ports, truthful four-act path,
  failure reproduction and independent sign-off instructions.
- This file, T-018 ticket and index: actual observations and remaining gates.

No app/backend behavior, metric policy, data artifact or public contract changed;
no DECISIONS amendment is required. Restored audio/dependencies/screenshots are
ignored local assets. T-001–T-017 implementation and T-019/T-020 scope preserved.

## Acceptance and remaining manual work

| T-018 acceptance | Result |
|---|---|
| Both developers operate four acts without coaching | **Unverified**; only Codex automated rehearsal occurred. Each developer must follow runbook cold start, all acts and outage, then record name/date/revision/outcome below. |
| Backend unplugged map/speech/results usable | **Pass**, all 10 offline cases including four acts and real audio playback passed with FastAPI stopped. |
| Evidence includes run date and observations | **Pass**, this file. |

No approved prompt manifests/MP3s exist for any of six languages. Real approved
TTS playback and competent-language listening remain **blocked by unavailable
approved assets**, with text-only fallback observed. No generation/listening or
approval flag changes occurred. Two usable distinct Urdu recordings for a real
two-rejection rehearsal are unavailable; finite-state behavior is unit-tested,
and available-data failure/referral path is browser-tested. Full internet loss at
OS level was not induced; backend process was stopped and external browser
requests were blocked. Neither developer's clean-machine installation, remote CI,
independent live-evidence review nor reviewer sign-off was performed here.

T-018 stays **In review**, not Done. Final steps are in
[the runbook](../DEMO_RUNBOOK.md#final-human-sign-off). Do not mark complete based
on automated agent tests alone; no subsequent ticket is marked unblocked by this
session and T-019/T-020 were not implemented.

Human rehearsal record (deliberately unfilled):

| Operator | Date/environment/revision | Four acts | Backend stopped | Audible source clip | Errors/fixes/reviewer |
|---|---|---|---|---|---|
| Developer 1 | Pending | Pending | Pending | Pending | Pending |
| Developer 2 | Pending | Pending | Pending | Pending | Pending |
