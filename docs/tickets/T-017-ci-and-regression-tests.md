# T-017 — Automate high-risk validation and unit checks

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Shared  
**Depends on:** `T-004`, `T-005`, `T-010`, `T-011`, `T-012`, `T-014`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Prevent demonstrably wrong data and schema regressions.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `backend/tests/`
- `frontend/src/**/*.test.tsx`
- `.github/workflows/ci.yml`
- `scripts/validate_exports.py`

## Step-by-step implementation plan

1. Implement QA matrix DATA-01..04, GEO-01..02, SAMPLE-01, CER-01..03, PAIR-01..02.
2. Mock Scribe/TTS in backend tests, never spend credits on CI.
3. Verify frontend not_tested, language switch clearing, count/share formatting.
4. Run lint/type checks and static-export schema validation on pull requests.
5. Require human-reviewed real API preflight as separate evidence.

## Implementation guidance (illustrative, not built yet)

```python
def test_cer_simple_substitution():
    assert cer(list('abc'), list('adc')) == 1/3

def test_missing_denominator():
    assert gap_share_pct(10, 0) is None
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Floating point comparisons use tolerance if appropriate.
- Do not use fabricated responses as released research results.
- CI must not require missing local raw ZIP or secret to run pure tests.

## Acceptance tests

- [ ] All tests pass locally and in GitHub Actions.
- [ ] Intentional invalid dataset fails CI with actionable error.
- [ ] No live API request is issued by CI.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
