# T-021 — Immersive guided hackathon demo

**Status:** In review — user approved implementation on 2026-11-08; local verification passed, human sign-off pending.
**Priority:** P1
**Owner:** Dev 2
**Implementation dependencies:** Existing T-011–T-016, T-018 and T-020 implementations; retain their unresolved review gates.
**Relevant decisions:** D-007, D-008, D-012, D-015–D-018, D-020–D-025.

## Outcome / scope approval

A first-time viewer understands UNHEARD's evidence gap, selects a visibly raised
ward, and follows Discover → Investigate → Demonstrate → Recommend using Next
and Back without scrolling between acts. Apply a restrained dark sci-fi visual
system with readable typography, subtle glow, depth and lightweight motion.

T-020 already implements accessibility, fragment navigation, SDG artwork and
ward zoom/popup. It does not explicitly specify a one-visible-act shell or
raised ward geometry. REQUIREMENTS.md defers 3D/advanced cinematic transitions.
Approval of this ticket authorizes a bounded presentation change: a screen-space
raised SVG ward effect within existing Leaflet, not a new 3D engine, geometry
dataset or integration. Record this clarification in DECISIONS.md and update the
deferred-scope wording in REQUIREMENTS.md only after approval. D-023's act order,
FR-A2's all-language initial/reset selection and explicit Urdu entry stay intact.

## Verified inputs / prerequisites

- Required project context and T-020 read on 2026-11-08; existing UI inspected on
  localhost. It currently renders all four acts with fragment links, a light
  magenta theme, and selected-ward zoom/popup rather than elevation.
- Installed frontend uses React 19.3.1 and Leaflet 1.9.4. Local Leaflet source
  exposes `createPane`, `Path.getElement` and `bringToFront`; verify actual
  rendering, zoom/pan alignment and hit targets before accepting elevation.
- Real corrected census, vetted geometry/status sidecar, frozen FLEURS samples
  and saved outcomes already exist locally. Validate their availability before
  implementation; never replace absent assets or outcomes with invented data.
- Existing supplied artwork: `frontend/src/assets/sdg10-reduced-inequalities.png`.
  Reuse unchanged, preserving original magenta, white artwork, aspect ratio and
  readable text. No generated substitute or new image dependency.
- Existing TTS approval/rights, partial pilot, independent rehearsal and review
  limitations remain open. UI work cannot certify them or require new synthesis.
- Existing worktree has uncommitted changes, including T-020; preserve them.

## Intended files

- `frontend/src/App.tsx`: active-act shell, progress, Next/Back, intro/final SDG
  framing and focus management.
- `frontend/src/components/JourneyNavigation.tsx` and
  `frontend/src/styles/journey.css` (new if useful): accessible navigation and
  viewport-aware layout.
- `frontend/src/styles.css`, `frontend/src/styles/sdg-theme.css`,
  `frontend/src/styles/accessibility.css`, `frontend/src/main.tsx`: cohesive
  theme, responsive styles and reduced-motion support as needed.
- `frontend/src/features/map/WardMap.tsx`, `WardExplorer.tsx`, `map.css`:
  raised selection, dimming, outline, clear control and progressive details.
- `frontend/src/features/speech-lab/SpeechLab.tsx`, `speech-lab.css`,
  `frontend/src/features/recovery/Recovery.tsx`, `recovery.css`,
  `frontend/src/features/recommendations/Recommendations.tsx`,
  `recommendations.css`: concise hierarchy, details, active-step audio handling
  and recovery continuation wiring as required. Confirm actual style filenames.
- `frontend/src/Regression.test.tsx`, focused journey/map tests and
  `frontend/e2e/demo.spec.ts`, `bootstrap.spec.ts`: acceptance/regression checks,
  including removal of obsolete shell-health expectations.
- `docs/DECISIONS.md`, `docs/REQUIREMENTS.md`, `docs/DEMO_RUNBOOK.md`,
  `docs/TEST_PLAN.md`, `docs/tickets/INDEX.md` and new
  `docs/test-evidence/guided-demo.md`: approved scope and actual evidence.

## Interaction and implementation plan

1. Discover opens with the supplied SDG image and the exact line: “Language
   should never be a barrier to being heard.” Explain the supplied task-audio
   evidence gap concisely, distinguish it from measured recognition failure,
   and keep the real map central. Retain all-language default and an explicit
   Urdu walkthrough choice; do not auto-select clips or autoplay audio.
2. Ward click, keyboard activation or table selection raises the selected ward
   visually with an anchored shadow/base, bright outline and smooth short lift.
   Subdue surrounding wards while retaining geographic context. Use separate
   SVG/pane layers as appropriate; preserve original coordinates and prevent
   decorative copies from gaining duplicate focus/hit targets. Keep a readable
   ward name/count/share/base panel and an obvious Clear selection control.
   Verify alignment across pan, zoom, reset, resize and return to Discover.
3. Keep one primary act visible. Persistent progress plus prominent Next/Back
   changes the active act directly and focuses its heading; no manual scrolling
   between acts. Keep fragment-based entry/continuation coherent, including
   Recovery's existing recommendations link. On laptops keep primary content
   and navigation in view where practical; allow vertical scrolling when needed
   for small screens, zoom, long transcripts or expanded evidence.
4. Preserve language, ward, metric, sample selection and recovery session across
   act navigation. Existing language-change invalidation still clears stale
   speech state. Inactive content is absent from keyboard/accessibility order;
   pause inactive audio without discarding session state. No hidden autoplay,
   provider replay or automatic change from saved to live.
5. Investigate foregrounds the chosen authentic recording and actual comparison.
   Demonstrate foregrounds explicit transcript review and confirmation outcomes.
   Keep essential origin, missing/error status and simulation notices visible;
   progressively disclose full sources, sample counts, methodology and caveats.
6. Recommend foregrounds consented future evaluation/recruitment. Reinforce:
   “UNHEARD explores gaps in speech technology that can leave language
   communities underserved.” Describe SDG 10 as alignment, without UN endorsement
   or a claim that this prototype proved reduced inequality.
7. Use dark surfaces, crisp type and limited accent lighting consistently across
   map, controls, tables, transcripts, tooltips, popups and loading/error states.
   Preserve readable RTL and native audio controls. Reduced motion uses immediate
   state changes and a static clear selected outline/depth cue.

## Contract impact and guardrails

No research JSON, geometry coordinates, API fields/enums, backend recovery rules,
ranking calculations, metrics, source hashes or audio approval changes. Only
frontend presentation/navigation state and internal component props may change.
Keep 79,940 / 153,480 across 14 tracked non-official categories and eight missing
task-audio categories accurate. Ward shares use `population_language_base`.
Keep geography independent from FLEURS outcomes. Preserve all explicit failure
statuses, actual n-selected/n-scored/n-paired, raw transcripts and provenance.
No auth, database, microphone, models, hosting or sponsor integration additions.

## Acceptance criteria

- [x] Only one act is visible/reachable at a time; Next/Back/progress and existing
  internal links navigate in D-023 order with appropriate heading focus.
- [x] Initial/reset language is all; explicit Urdu entry works. Ward, metric,
  sample and recovery session survive Next/Back. Language changes still clear
  stale results; inactive audio pauses; no requests replay on navigation.
- [x] Real ward click/keyboard/table selection visibly lifts one ward, dims the
  others, and shows readable name/count/share/base. Clear restores context.
  Pan/zoom/resize/step return remain aligned; no duplicate interactive geometry.
- [x] Missing/invalid geometry still exposes the labelled verified table fallback.
- [x] SDG image appears intentionally on Discover with exact requested alt text:
  “UN Sustainable Development Goal 10: Reduced Inequalities.” Original colors,
  proportions and readable text preserved; opening/final framing is accurate.
- [x] Each act has one clear message and primary action; source/methodology/sample
  details remain reachable. Missing outcomes and essential limitations stay clear.
- [x] Keyboard-only journey, focus visibility, readable contrast, RTL, reduced
  motion and layouts at 1366×768, 1440×900 and 390×844 verified; no clipped controls
  or mandatory horizontal page scrolling. Smaller screens can scroll vertically.
- [x] Existing Urdu saved audio/comparison/confirmation/acceptance/referral flow
  works, including backend unavailable and explicit browser-only cached route.
  Actual lack of a second usable retry clip remains disclosed, never fabricated.
- [x] Loading, audio failure, unavailable service, not-tested and incompatible
  outputs remain distinct; saved/live origin and simulation are understandable.
- [x] Frontend unit tests, appropriate browser regressions and production build
  pass; full journey and selected-ward effect manually inspected. Record actual
  results/screenshots and limitations in the evidence file.
- [x] Retain separate existing real provider preflight evidence; unit tests mock
  providers and this presentation ticket makes no new billable provider calls.
  Human listening/two-person rehearsal remain explicit pending gates if unobserved.

## Verification / handoff

Run `npm --prefix frontend test`, `npm --prefix frontend run build` and relevant
Playwright cases per installed configuration. Inspect real local Urdu saved
evidence with backend online and actually unavailable, keyboard-only controls,
responsive layouts, reduced motion and map alignment. Record commands, observed
passes/failures and evidence without claiming unrun checks. Update this ticket
and INDEX status accurately; Done requires acceptance evidence and reviewer
sign-off, not merely code. Use the AGENTS.md handoff format.

## Proposal evidence — 2026-11-08 (historical, before approval)

Documentation-only proposal. No application code, contracts or data changed.
Read-only source/installed-library inspection and localhost UI review performed;
no acceptance test, build, provider call or audio listening performed for T-021.
All previous ticket review gates remain unchanged. Await user approval.


## Implementation handoff — 2026-11-08

User explicitly approved this proposal before application coding. Existing
frontend/map/data/recovery prerequisites were present. No predecessor sign-off,
rights review or missing audio result was invented to remove a blocker.

Implemented App.tsx and sdg-theme.css, WardMap.tsx/WardExplorer.tsx,
SpeechLab.tsx, Recovery.tsx, Recommendations.tsx, App.test.tsx, both browser specs
and the local Playwright server-reuse setting. Updated requirements, decisions,
runbook, index and guided-demo evidence. Existing user worktree edits retained;
no new standalone navigation component/library was necessary.

One visible act now has Next/Back/progress, focus management and fragment-link
compatibility. Mounted hidden acts preserve selections/sessions; inactive audio
pauses and hidden recovery responses do not steal focus. The forced Leaflet SVG
renderer uses a 14 px screen-space lift over an inert footprint, outline/depth,
subdued neighbors, keyboard/clear controls and resize-safe reprojection. The
original city coordinates and independent demographic table remain intact.
Dark surfaces, responsive controls, original SDG artwork, exact requested alt
text/opening, final SDG framing and progressive evidence disclosure are present.

Contract changes: none to data/API/geometry/recovery rules. Internal `active`
prop prevents hidden recovery focus changes; no metrics or backend code changed.

Observed: 11 frontend unit tests, 14 browser cases, TypeScript/production build,
research bundle validation and diff checks passed. Laptop/mobile CUA visual
review passed for the inspected views; targeted contrast ratios exceed 4.5:1.
Full commands, failure corrections, screenshots and limitations are in
[guided-demo.md](../test-evidence/guided-demo.md). No provider calls were made.

Acceptance coverage above was exercised through automated tests and manual
inspection as detailed there; the list is not a claim of independent human
sign-off. Network failure was connection-refused in browser transport, not a
shutdown of the user's FastAPI. Screen-reader certification and two-person/native
language listening rehearsal were not performed. TTS remains text-only, and
Urdu's untested second clip cannot support a successful saved retry.

How to manually verify: run the frontend, Explore Urdu → Ward 10 → Next → select
1533/listen/compare → Next → Browser-only saved results → 1533 → Start → Correct →
Continue to recommendations. Use Back to verify preserved state; expand source,
summary, ward and plan details. Test Enter/Escape, Clear, reduced motion and mobile.

Ready/blocked next tickets: no new implementation ticket unblocked. T-021 awaits
human reviewer sign-off; T-018/T-020 human rehearsal and T-015/T-019 approval/rights
limitations remain open. This ticket is In review, not Done.

## User-requested minimalist refinement — 2026-11-08

Continue this one ticket with the existing implemented prerequisites. The user
explicitly supersedes the exact opening slogan above: remove promotional quotes,
use factual headings, preserve unchanged SDG artwork with a concise label, and
keep the single-act journey and SVG lift/dimming. Remove the empty ward card;
use the full-width map with a small instruction and compact selected-only values.
Reduce decorative surfaces, grid/glow and navigation emphasis.

Add shared recording-derived waveforms to the existing native audio players
(speech lab, recovery recording, and approved cached instruction). Installed
packages contain no audio library; use browser AudioContext.decodeAudioData for
whole-file peak extraction and HTMLMediaElement events/currentTime for playback.
Keep native play/pause controls, add keyboard/pointer waveform seeking, never
connect a second audible source, pause on inactive acts/unmount, abort stale
fetches and close decode contexts. Unsupported decode must preserve native audio
and explicit fallback. Never synthesize waveform peaks or replace missing audio.
No new dependencies, research/API/schema/approval/recovery-rule changes.

Acceptance: real Urdu bytes yield nonuniform peaks; waveform progress follows
play/pause/resume/seek/end and resets with recording identity; native fallback,
responsive ward selection, keyboard and reduced motion pass. Preserve separate
real provider evidence and all prior review/rights/listening gates. Record actual
results in test-evidence/minimalist-ui.md; retain In review status.

### WER display follow-up

At the user's request, remove WER values, unavailable notes and WER-specific UI
explanations from SpeechLab. Keep CER, provenance and sample counts. Preserve
existing research fields/validators and backend metric policy; no data-contract
change. Updated the existing Urdu browser comparison check accordingly.

### Discover shortcut follow-up

User explicitly requested removal of Explore Urdu. Remove its wrapper and unused
App selection hook; browser/unit walkthroughs select Urdu in the existing global
dropdown. No contract changes; In review with prior gates retained.

### Three-step visual redesign — 2026-11-09

The approved scope replaces the four-act journey with Discover, Investigate
and Demonstrate. The former Recommend fragment opens Discover. The coverage
figure uses the verified census/coverage artifacts. The old recommendation
component, ranking and exports remain available in the repository. Scope and
contract details are recorded in [DECISIONS.md](../DECISIONS.md).

Verified with 12 frontend unit tests, the production build and 16 offline
Chromium cases. The browser run used real local ward data and restored FLEURS
recordings. It covered keyboard selection, SVG alignment, reduced motion,
retained selections, saved acceptance/retry/referral, waveform seeking, missing
inputs and backend disconnection. Reviewed the selected map at 1440 and 390 px
and adjusted its height and reset label so the sticky footer leaves more room
for the legend. The browser run preceded those final visual adjustments.
No live provider calls. Prior reviewer, listening and accessibility sign-off
gates remain open. Status stays In review.

Verify locally by selecting Urdu, Ward 10 and Share of language base; then
select 1533 in Investigate, play/seek the recording, and use Browser-only saved
results in Demonstrate. Accept, return to the map and check Ward 10 remains
selected. Start another simulation to check the retry/referral path.
