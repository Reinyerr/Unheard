# T-010 — Calculate multilingual CER/WER and paired summaries

**Status:** TODO (not implemented)  
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
