# T-021 — observed guided-demo evidence

Date: 2026-11-08, America/Toronto. Environment: local macOS, installed Node/Vite,
React 19.3.1, Leaflet 1.9.4 and Playwright Chromium 1254. Existing working tree
already contained T-020/SDG/source-audit edits; these were preserved. No commit,
public deployment, research-data change or provider request was made.

## Commands and observed results

| Check | Observed result |
|---|---|
| `npm --prefix frontend test` | 11 tests passed across 3 files |
| `npm --prefix frontend run build` | TypeScript, real research-bundle validation and Vite production build passed |
| `PLAYWRIGHT_BROWSERS_PATH=/private/tmp/unheard-playwright npm --prefix frontend run test:e2e -- --workers=2` | 14 tests passed in 15.5 seconds |
| `git diff --check` | Passed, no whitespace errors |

The first unit run exposed six obsolete shell-health expectations, already
documented as stale by T-020. They were replaced with actual navigation,
state-preservation, focus and invalid-artifact tests. Initial browser execution
could not launch because the matching Chromium binary was absent. The official
Playwright binary was installed in temporary storage. Later failures were stale
table/label selectors, ambiguous region selectors and an obsolete assumption
that the user's backend had no key configured; these were corrected. The tests
never select live origin or make a live provider POST. A final browser-history edge case (Back to the initial URL without a fragment)
was fixed and covered by the fourteenth browser case. Final results above are
actual complete runs, not a count of written assertions.

Build still reports the existing Vite future-native-config import warnings and
the >500 kB bundle warning (about 545 kB minified / 163 kB gzip). No animation
library, browser runtime dependency or new map/3D engine was added.

## Browser coverage on real local artifacts

- 1366×768, 1440×900 and 390×844: one visible act, all-language initial selection,
  explicit Urdu entry, correct SDG alt text, visible navigation, retained ward,
  sample and confirmation session on Next/Back; no horizontal page overflow.
- Ward 10 selected with Enter: selected SVG has 14 px upward screen translation,
  outline and depth; other fills become 0.24 opacity. Clear restores 0.94 and
  deselects. All 11 decorative base paths are aria-hidden and have no tabindex.
  Installed SVG `d` paths for surface/base remain equal after zoom and resize.
- Browser Back/Forward from the initial URL keeps the act/progress synchronized.
- Reduced motion: zero transition duration; static lifted selection remains.
  Enter activates navigation, heading receives focus; Escape clears the ward.
- Real Urdu 1533 audio decodes and advances playback. Automatic/guided CER each
  shows 10.6%, WER unavailable, paired delta 0.0 percentage points; selected n=8,
  scored automatic/guided/paired n=1. Inactive playback pauses.
- Saved browser simulation reaches confirm and explicit accepted. Rejection
  allows a different sample once; the actually untested Urdu 1537 cannot fabricate
  a transcript and leads to explicit referral. No representative is contacted.
- The real running backend's saved-only route is also checked using its actual
  capabilities. Key presence is read as configuration, never connectivity proof.
- Network-outage case aborts localhost backend requests with connection-refused:
  real static map/audio/comparisons/recommendations and explicit saved browser
  confirmation remain usable, including accepted-state preservation on Back.
  Observed backend POST count is zero in that case. This is a browser transport
  fault test; the user's existing FastAPI process was not stopped.
- Missing geometry exposes an open verified table; missing/invalid audio keeps
  saved text and reports failure. Missing wards/samples/experiments/recommendations
  isolate failures explicitly. Arabic/English/Punjabi/Mandarin 1537 remain Not
  tested; Cantonese's automatic exclusion remains incompatible, never numeric 0.
- Existing recommendation ranks/counts/shares are retained behind progressive
  details. The coverage cards still derive 8, 79,940 and 52.1% from verified data,
  with 153,480 across 14 tracked non-official categories as the denominator.

Screenshots from browser tests are under ignored `frontend/test-results/`, with
`raised-ward-1366.png`, `raised-ward-1440.png`, `raised-ward-390.png` and
`four-acts.png` in their respective test output folders.

## Manual visual review

CUA localhost inspection observed the complete Discover → Investigate →
Demonstrate → Recommend path, Urdu reference/raw comparison in RTL, explicit saved
confirmation/acceptance, the recovery recommendations link, heading focus, and
preserved Ward 10 on return. Inspected laptop views and the 390×844 mobile view.
Mobile allows page scrolling; laptop keeps navigation outside the scrollable
act, and long/expanded content can scroll. The full selected ward remains visible
with its adjacent values and clear control. Resizing refits geometry once the map
is visible; there is no fly-to animation or source-coordinate modification.

The supplied magenta SDG image remains unmodified and proportionate, with readable
white artwork. Opening/final text frames alignment, not endorsement or measured
inequality reduction. Final recommendation cards and progressive plan details
were visually inspected. Review preview: `/private/tmp/unheard-t021-discover.jpg`.

Targeted contrast calculations from the actual CSS tokens: body 15.69:1, muted
text on the tinted surface 7.25:1, primary-button text 6.10:1, mint accent 11.54:1,
warning text 12.38:1. This is token/visual verification, not a full accessibility
audit or screen-reader certification.

## Preserved limitations and independent evidence

- No approved cached TTS exists; text-only state stays explicit. No synthesis,
  native-language listening or caption approval occurred here.
- The pilot is partial. No second usable Urdu result was invented to stage a
  successful retry; no recognition or SDG impact claim was added.
- Independent real provider evidence remains in
  [one-recording-pilot.md](one-recording-pilot.md), separate from mocked unit tests
  and this presentation regression suite. No fresh billed preflight is necessary
  for a presentation-only change.
- Two-person rehearsal, screen-reader/human listening review, municipal/provider
  rights and prior ticket sign-offs remain open. Public hosting remains deferred.
- T-021 is **In review**, not Done; this evidence does not close predecessor gates.

## Manual reproduction

1. Run `npm --prefix frontend run dev`; open `http://127.0.0.1:5173`.
2. Confirm all-language start, SDG artwork and exact opening sentence. Choose
   Explore Urdu, then Ward 10 by pointer or keyboard. Inspect rise/context and
   4,520 / 6.12% / 73,830; Clear selection restores the map. Expand the ward table
   and Sources for independent values/geometry caveats.
3. Next → Investigate; select Urdu 1533, play audio, inspect the reference and
   saved comparisons. Open pilot summary/metric/source details as needed.
4. Next → Demonstrate; choose Browser-only saved results, Urdu 1533 and Start
   saved simulation. Choose Correct, then follow Continue to recommendations.
   Use Back to verify the session and speech selection remain.
5. For rejection, start a separate saved simulation and reject 1533. Select
   different clip 1537: its missing result produces referral, not invented speech.
6. Test mobile scroll, Tab/Enter/Escape, OS reduced motion, resize and zoom. For
   automatic fault coverage, run the browser suite above. Human rehearsal remains
   a separate sign-off.
