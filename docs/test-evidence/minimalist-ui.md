# T-021 minimalist UI and recording waveforms — 2026-11-08

Status: In review. User-requested refinement of the existing guided demo.
Existing uncommitted implementation work was preserved.

## Changes and contracts

- Factual Discover heading; removed opening slogan, promotional closing copy and
  repeated footer instructions. Original SDG image retained unchanged.
- Full-width map, subtle background and depth, small in-map selection instruction.
  No empty ward card. Selected-only compact demographics; selected SVG lift and
  dimming, verified table, source cautions and clear/reset remain.
- Shared AudioWaveform for speech-lab recordings, recovery recordings and approved
  cached instruction playback. Decode complete recording bytes into 160 equal-time
  peak bins across channels, scaled by the recording’s maximum peak for visibility;
  native audio remains the sole audible player.
  Native media events/currentTime drive the cursor, played region and state.
  Native controls plus accessible range support pointer/keyboard seeking.
- Abort stale fetches, bound decode fetch wait, close AudioContexts, cancel frames
  and pause on teardown; existing inactive-act pausing preserved. Loading, missing
  files and unsupported waveform decoding are explicit. No generated/random bars.
  No decorative animation; reduced motion retains accurate playback position.
- No research JSON, API, metric, ranking, retry/session or approval contract change.
  No dependencies or provider calls. Static sample count remains 48, eight common
  IDs per six pilot languages, seed 2026. Real Urdu ID 1533 retains 10.6% CER in
  each comparable saved mode; incomplete outcomes remain explicit.

## Verification

Commands from frontend:

- `npm test`: 12 tests passed (4 files), including peak-bin/silence/multichannel
  unit fixture, retained guided state and approved-prompt gating.
- `npm run build`: type check and production build passed. Existing Vite native
  config-import and >500 kB bundle warnings remain non-failing.
- `npm run test:e2e -- --workers=1 --timeout=60000`: 17 cases passed in Chromium.
  Actual running localhost backend used for the real capability/saved API case;
  separate connection-refused route proves browser-only Urdu recovery without
  provider replay. No new ElevenLabs requests or audio synthesis.
- `git diff --check`: passed.

Browser coverage: 1366×768, 1440×900 and 390×844 guided layouts; no horizontal
page overflow; one accessible act; Next/Back/hash focus and retained session;
Ward 10 keyboard selection and 4,520 / 6.12% / 73,830 census values; dimming/lift,
clear, Escape and unchanged geometry alignment after zoom/resize; reduced motion;
real Urdu native playback; saved acceptance/rejection/missing-result referral;
missing geometry/audio/data; language invalidation; waveform nonuniform peaks,
play/pause/frozen paused cursor, keyboard seeking, midpoint, resume, end, new clip
reset, recovery recording waveform and unsupported Web Audio native fallback.
The waveform fixtures do not fabricate provider outcomes.

Initial browser launch failed because Chromium was absent. Installation initially
reported ENOSPC, then succeeded on retry. A system Chrome run exposed broad old
label selectors matching both audio and new slider; made audio selectors exact.
Near-end playback checks now wait for native seek completion before resuming.
An offline-environment invocation correctly failed its offline assumption because
an existing backend was running; final run used the actual online environment.

Visual review used local Chromium screenshots of desktop unselected/selected map,
mobile selection and half-played Urdu waveform. Tightened laptop header/map fit
and moved methodology below the player so the audio visualization stays prominent.
Previews: `/private/tmp/unheard-minimal-discover.png`,
`/private/tmp/unheard-minimal-selected.png`,
`/private/tmp/unheard-minimal-mobile.png`,
`/private/tmp/unheard-minimal-waveform.png`. Browser suite screenshots are in ignored
frontend/test-results. No microphone, external basemap or new image generation.

Browser API verification: installed dependencies contain no audio library. Checked
[decodeAudioData](https://developer.mozilla.org/en-US/docs/Web/API/BaseAudioContext/decodeAudioData)
and [HTMLMediaElement](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement),
then verified actual local FLAC decode/playback in installed Chromium. Other browser
codec support may differ; native playback and decode fallback are separate paths.
Independent real provider preflight: [one-recording-pilot.md](one-recording-pilot.md).

## Manual reproduction and remaining gates

1. Start frontend (`npm --prefix frontend run dev`); open localhost:5173.
2. Select Urdu and Ward 10 with pointer or Enter; inspect lift/dimming, compact
   values, sources/table, Clear and Escape. Resize to mobile and enable reduced motion.
3. Next → Investigate → Urdu 1533. Play, pause, resume, click waveform, keyboard
   seek and let it end. Verify bars stay fixed while only played region/cursor
   advance. Switch clip: waveform and position belong to the new recording.
4. Next → Demonstrate → browser-only saved route → 1533 → Start saved simulation.
   Accept, then continue to recommendations. Back retains session and selections.
5. Stop/block backend: saved route still works; no provider replay.

Approved cached TTS is still absent, so real instruction waveform playback cannot
be certified; the same component is behind the existing tested approval/hash gate.
No new human listening, screen-reader certification, independent team rehearsal,
public redistribution clearance or predecessor sign-off is claimed. No second
usable Urdu result is invented. T-021 remains In review; no new implementation
ticket is ready and existing rights/audio/review gates remain blocked/open.

## WER UI follow-up

User requested removal of WER. SpeechLab now shows CER only; removed WER values,
unavailable notes, explanation and WER-specific source-policy paragraph. Research
JSON/validators/backend metrics remain unchanged. Updated existing Urdu browser
comparison assertion to require no WER label. Observed: 12 unit tests passed,
type/production build passed, targeted real Urdu four-act browser case passed
(1/1), and diff whitespace check passed. Existing non-failing build warnings and
T-021 review gates remain. Manually inspect Investigate → Urdu 1533 comparison;
CER and sample counts remain and WER is absent. No next ticket unblocked.

## Discover shortcut removal

Removed Explore Urdu and its empty wrapper at user request. Removed the unused
App selection hook; existing walkthrough tests now select Urdu using the global
dropdown. Updated ticket/index/decision/runbook accordingly. No data/API contract
change. Observed: 12 unit tests passed, type/production build passed, all five
responsive/keyboard/guided-shell browser cases passed and diff check passed.
Manual verification: Discover has no Explore Urdu button; select Urdu using
Selected language and activate Ward 10 as before. Prior review gates remain; no
new implementation ticket is unblocked.
