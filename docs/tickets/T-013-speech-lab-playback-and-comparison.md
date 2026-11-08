# T-013 — Build authentic-audio speech laboratory

**Status:** In review (implemented; acceptance incomplete)
**Priority:** P0  
**Owner:** Dev 2  
**Depends on:** `T-003`, `T-007`, `T-010`, `T-012`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Let judges hear and inspect real paired model performance.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/src/features/speech-lab/`
- `frontend/src/components/TranscriptDiff.tsx`

## Step-by-step implementation plan

1. Render selected language sample manifest and an audio player for vetted local FLAC clips.
2. Show human reference, auto raw transcript, guided raw transcript with status labels.
3. Use grapheme/token-safe diff presentation and correct RTL direction for Arabic/Urdu.
4. Display CER as a ratio formatted percent, paired delta in **percentage points**, eligible WER or unavailable note.
5. Add per-language n, improved/worsened/tied counts and model/source citation.

## Implementation guidance (illustrative, not built yet)

```typescript
const cerPercent = cer == null ? 'Not available' : `${(cer * 100).toFixed(1)}%`;
const deltaPP = pairedDelta == null ? null : pairedDelta * 100;
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Audio file missing/unsupported browser codec: show error; source must remain truthful.
- Never present saved results as new live API output.
- A diff UI cannot silently auto-translate to manufacture equivalence.

## Acceptance tests

- [ ] Readback of sample ID matches displayed reference and result.
- [ ] Missing audio / guided unsupported render explicit states.
- [ ] Right-to-left transcripts remain readable without reversing semantic order.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Implementation evidence — 2026-11-07

Prerequisites implemented (In review): T-003 schemas/build validation, T-007
48-record frozen sample manifest with all 48 local FLAC files present, T-010
exported records/summaries, T-012 shared selection. Actual sample/experiment
selection hashes match. No new datasets, dependencies, backend or schema changes.

SpeechLab loads the real manifest, validates sample identity/selection provenance
before comparisons, and offers all eight selected clips per pilot language.
Audio is keyed to sample and paused on unmount. Global language changes clear
selection/result and remove the previous player; ward selection is never read.
Saved results, human original/reference input, raw automatic/guided output,
statuses, review flags, uncapped CER/WER and paired percentage-point deltas are
explicit. Summary uses exported scored/paired denominators, means, improved/
worsened/tied counts and unpaired reasons. No new live requests or metrics.

Raw reference-input/output differences use Intl.Segmenter graphemes and grouped
insertion/deletion runs, explicit Urdu/Arabic RTL, preserved semantic order and
no normalization/translation. Unsupported grapheme segmentation or large text
falls back to unchanged raw output with a notice. These display differences are
separate from the backend's normalized code-point CER policy. Attribution,
CC BY 4.0, modifications, selection hash, model/API and metric limitations appear
in source details. Audio errors retain the reference/results and show unavailable.

Observed manual browser review with backend unavailable: Urdu-1533 selector,
heading and audio identity agree; playback controls changed to pause and enabled
the scrubber. Both saved CERs are 10.6%, paired delta 0.0 percentage points,
summary n_selected=8 / scored 1 per mode / paired 1 / tied 1. RTL comparison was
visually inspected. Switching to Arabic removes the Urdu recording/comparison,
restores Choose a recording and shows null summary metrics as Not available.
Local ignored screenshot: `.cache/t013-urdu.jpg`. This is playback/UI inspection,
not independent native-language reference readback or full listening validation.

`npm --prefix frontend run build` passed TypeScript, the existing asset bundle
guard and Vite. No automated tests were created/run by explicit user instruction.
Full acceptance remains incomplete: missing/unsupported codec, unsupported guided
and technical-error branches, every clip/browser, native-language readback and
independent offline rehearsal remain unverified. Current bundle has Vite's
nonblocking >500 kB warning and pre-existing config-loader warnings.

Manual review: `npm --prefix frontend run dev`, open localhost:5173, select Urdu,
Investigate, urdu-1533; play and inspect source/reference/results, then switch to
Arabic/Tamil and verify no stale content or invented scores. Cantonese-1533
retains incompatible automatic output and a scored guided result. Review missing
audio and unsupported statuses separately before sign-off. T-016 is the next
standalone Dev 2 ticket; T-015 has UI prerequisites but voice/TTS still needs the
shared Dev 1 handoff. Neither is implemented here.
