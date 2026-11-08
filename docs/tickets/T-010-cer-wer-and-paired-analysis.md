# T-010 — Calculate multilingual CER/WER and paired summaries

**Status:** In review — implemented using real preflight evidence; automated tests skipped at user request.
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-003`, `T-007`, `T-008`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Implement and validate reusable per-clip CER/WER + export logic on a real preflight sample, so the UI vertical slice is not blocked by the full pilot.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/calculate_metrics.py`
- `frontend/public/data/experiments.v1.json`
- `backend/tests/test_metrics.py`

## Step-by-step implementation plan

1. Preserve raw/reference outputs, normalize Unicode/punctuation/case/whitespace using documented language-appropriate policy.
2. Implement Levenshtein edit distance on defined character units; record this policy explicitly.
3. Calculate CER primary; WER only if reliable tokenization exists; mark otherwise null/unavailable.
4. Flag unexpected script/translation for review before comparable CER.
5. Compute paired `autoCER-guidedCER` with `n_paired`, improved/worsened/tied counts and uncertainty wording. Validate on one real preflight sample; rerun the exporter on the completed T-009 pilot.

## Implementation guidance (illustrative, not built yet)

```python
def cer(reference_units, hypothesis_units):
    if not reference_units: return None  # investigate invalid reference
    return levenshtein(reference_units, hypothesis_units) / len(reference_units)

paired_delta = auto_cer - guided_cer  # if both comparable
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- CER may exceed 1 when insertions dominate: do not cap.
- Unicode combining marks, right-to-left text and Chinese word segmentation need explicit rules.
- n=8 gives descriptive pilot, not citywide estimates or fairness proof.

## Acceptance tests

- [ ] abc vs adc CER=1/3; hello vs blank CER=1.
- [ ] Auto .20 guided .10 paired improvement +.10.
- [ ] Missing/unsupported status excluded with reason counts.
- [ ] One real preflight recording can be exported for the initial vertical slice; the full pilot is deferred to T-009.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.


## Implementation evidence — 2026-11-07

Branch `feature/data-backend`. T-003 shared schemas, T-007 frozen 48 samples,
and T-008 adapter plus actual Urdu/Cantonese preflight are present. Their review
and wider validation gates remain open. Before starting, reverted only the
previous interrupted turn's T-009 recheck note/header and index append, preserving
prior T-008 work. No commit created.

Created `scripts/calculate_metrics.py`, generated
`frontend/public/data/experiments.v1.json` and ignored local
`data/processed/metric_details.json`. Updated processing/normalization docs,
shared-contract usage notes, decision clarification and dependency statuses.
No public fields/enums, React components, dependencies or provider code changed.
The ticket's suggested test file was intentionally not created under the user's
explicit no-tests instruction. No automated tests or live API requests were run.

Observed production command (available Python 3.14.7/Pydantic 2.13.5):

```sh
python3 scripts/calculate_metrics.py
```

Exit 0. Exported all 48 frozen records and six summaries; existing Pydantic full
bundle validation passed, including foreign keys across the five real artifacts.
Four terminal preflight modes were recorded: Urdu auto/guided are scored with one
paired clip and mean delta CER 0.0 (a tie, not evidence about guidance overall);
Cantonese guided is scored; Cantonese auto is incompatible_output with null
CER/WER/delta due to the saved script-variant review and detected-language
mismatch. All 92 unattempted sample/mode combinations remain not_tested with
null metrics. Every language retains n_selected=8; n_paired is 1 for Urdu and 0
elsewhere. No confidence intervals, significance or geographic performance claim.

Reusable functions implement Levenshtein unit edits, uncapped ratios, explicit
Unicode normalization, per-mode script review, paired delta and per-language
summaries. Policy: NFC, punctuation to spaces, collapsed whitespace; English
casefold only. CER removes whitespace and counts Unicode code points, retaining
combining marks, symbols/digits and script identity. No translation, transliteration,
script conversion or silent removal of diacritics. WER uses English whitespace
tokens only; all other languages remain null pending validated tokenization.
Successful empty recognition is scored against a valid nonempty reference;
empty normalized references and flagged outputs are excluded, never zero-filled.

Script guard requires expected-script letters to be at least half of letters
in reference/nonempty letter-bearing output (Latin/Arabic/Gurmukhi/Han as mapped).
Detected-language mismatch and recorded manual script exclusions block scoring.
This is a conservative diagnostic, not a translation detector. Same-script
translation and simplified/traditional variants still require human review;
the real Cantonese exclusion is explicitly imported from T-008. Public source
metadata retains flags/policy and the local audit retains raw/reference strings,
normalizations, edit counts and raw-response links. Original response files are
untouched. Provider success is preserved separately from metric comparability.

Input report must match the frozen selection/audio/model, one terminal record
per sample/mode, with raw response evidence for completed results. Duplicate
retry records must be resolved by the future runner before export; no new retry
or cache logic is implemented. Paired settings must differ only in language_code.
Input JSON must reside under data/local or data/processed; default is the real
preflight log. Source hashes bind exact input, raw responses, selection and
metrics implementation. Full bundle validation occurs before public replacement.

Manual review: run the command, inspect public records/summaries and local
metric_details.json, independently recalculate Urdu edits and the paired delta,
confirm Cantonese auto's flags/null metrics, and verify 48 records/6 summaries
including absent outcomes. Acceptance examples, error-path coverage, pinned
runtime verification, frontend build, listening and Urdu/cached demo regression
remain unrun. Ticket stays In review, not Done.

Next ready Dev 1 implementation is T-009. Its full pilot still requires explicit
handling/preflight for remaining unverified language guidance and credit/rate
limits (subscription allowance was unavailable). No T-009 runner or additional
experiment was implemented.
