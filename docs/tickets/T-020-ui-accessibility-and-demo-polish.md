# T-020 — Finish approachable, accessible visual storytelling

**Status:** In review — implementation only; manual accessibility and two-person rehearsal pending.
**Priority:** P1  
**Owner:** Dev 2  
**Depends on:** `T-011`, `T-013`, `T-015`, `T-016`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Make the evidence understandable without letting animations displace credibility.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/styles/`
- `frontend/src/components/AccessibilityNotice.tsx`
- `docs/DEMO_RUNBOOK.md (timing)`

## Step-by-step implementation plan

1. Ensure every page shows one clear question and limits near displayed results.
2. Provide focus states, keyboard controls, audio transcripts, readable contrast and aria labels.
3. Support reduced motion and correct RTL text direction.
4. Create 4-act navigation with Urdu as safe default and accessible optional exploration.
5. Polish only after M1 real vertical slice and basic integration are completed.

## Implementation guidance (illustrative, not built yet)

```typescript
// Accessible button sketch
<button type="button" aria-label="Play selected Urdu recording"
        disabled={!audioAvailable}>Play audio</button>
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- No cinematic transition may obscure a statistical caveat or error state.
- Ensure clip playback permitted and no autoplay surprises.
- Charts also provide tabular numerical details.

## Acceptance tests

- [ ] Keyboard-only flows can reach transcript, comparison and recommendations.
- [ ] Text remains legible without animation; reduced-motion honored.
- [ ] 2-person team can explain demo confidently without relying on visual flourish.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Implementation handoff — 2026-11-07

Continued `feature/final-integration` from `b7759d3` plus existing uncommitted
T-018/T-019 work, which was preserved. T-011/T-013/T-015/T-016 code prerequisites
exist; T-018 recorded the real Urdu vertical slice and basic integration. Their
review gates remain open, including T-015's unavailable approved TTS audio.

Implemented only frontend accessibility/storytelling and rehearsal guidance:

- `App.tsx`: one question and visible limit per act, focusable fragment targets,
  explicit Urdu walkthrough entry, next-act and language-selection links.
- `components/AccessibilityNotice.tsx`, `styles/accessibility.css`, `main.tsx`:
  keyboard/audio/reading instructions, focus/target sizing, narrow-screen and RTL
  reading styles, reduced motion and forced-colour focus/selection affordances.
- `components/LanguageSelector.tsx`, `components/PriorityTable.tsx`,
  `features/recommendations/Recommendations.tsx`: reliable selection jump target
  and keyboard-focusable scroll regions with accessible labels.
- `features/speech-lab/SpeechLab.tsx`: plain CER/WER interpretation and native
  focusable reference/comparison jump links.
- `features/recovery/Recovery.tsx`: supplied recording reference text with
  language/direction, clearly separate from the transcript being confirmed.
- `features/map/WardMap.tsx`: immediate JavaScript panning and no inertia, retaining
  keyboard selection and existing zoom/fallback behavior.
- `docs/DEMO_RUNBOOK.md`: 3:45 target narrative, exact manual review steps and
  outstanding evidence. `docs/DECISIONS.md` and ticket index record the handoff.

Initial/reset selection remains all languages per FR-A2; the user's explicit
Urdu entry satisfies the guided path without silently changing accepted defaults.
No autoplay, new metrics/assets, source edits, backend/API changes or public
contract changes. Missing data, saved/live labels and text-only prompts remain.

No automated tests were written/run; no build, browser, screen-reader, contrast,
listening or two-person presentation check ran, per implementation-only scope.
Acceptance boxes remain open; previous T-018 results do not verify these changes.

Manual startup from repository root:

```sh
npm --prefix frontend run dev
# Optional local backend, in a separate terminal; keep live provider key disabled:
ELEVENLABS_API_KEY='' backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Open http://127.0.0.1:5173 and follow the T-020 section of DEMO_RUNBOOK.md. Run
keyboard/RTL/zoom/reduced-motion/screen-reader review and both developers' timed
explanations before reviewer sign-off. Actual TTS playback still requires approved
assets and competent-language listening review outside this implementation.

Next ready implementation ticket: none in T-001–T-020; remaining work is review,
manual verification and the already recorded data/audio/rights blockers. No new
ticket or scope expansion is introduced.
