# T-014 — Implement deterministic confirmation/retry/referral API

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-001`, `T-003`, `T-008`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Provide predictable safety-oriented verification without autonomous municipal actions.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `backend/app/routes/recovery.py`
- `backend/app/services/recovery_state.py`
- `backend/tests/test_recovery.py`

## Step-by-step implementation plan

1. Define states and validated transitions per ARCHITECTURE and DATA_CONTRACTS.
2. Accept only known curated sample IDs and valid selected language; restrict payload sizes.
3. Use verified ElevenLabs output or clearly marked saved result to enter confirmation state.
4. Accept explicit correct/incorrect, permit one additional attempt with a *different* clip.
5. After attempts exhausted return a referral message—no pretend call to a live 311 representative.

## Implementation guidance (illustrative, not built yet)

```python
if state == 'confirm' and decision == 'incorrect':
    next_state = 'retry_or_refer' if attempts < 2 else 'referral'
elif state == 'confirm' and decision == 'correct':
    next_state = 'accepted'
else:
    raise InvalidTransition()
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Two total attempts means one retry; no infinite loop.
- Confirm cannot occur before a usable transcript.
- Handle sessions without exposing speech metadata or keys to browser.

## Acceptance tests

- [ ] Correct transitions yield accepted.
- [ ] Two rejections yield referral, no further retry.
- [ ] Unknown sample, invalid transition and API error return meaningful 4xx/5xx with safe details.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
