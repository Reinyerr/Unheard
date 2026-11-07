# T-007 — Generate 48-record FLEURS sample manifest

**Status:** TODO (not implemented)  
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-002`, `T-003`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Select unbiased paired multilingual samples before observing AI outcomes.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/sample_fleurs.py`
- `data/processed/sampling_manifest.json`
- `frontend/public/data/samples.v1.json (after permitted asset review)`

## Step-by-step implementation plan

1. Load all 560 FLEURS metadata rows and verify 40 IDs per chosen language.
2. Intersect IDs across English/Urdu/Punjabi/Cantonese/Arabic/Mandarin Chinese.
3. Sort IDs; sample 8 without replacement using `random.Random(2026)`.
4. Write all 48 language–ID rows with actual reference transcription, file path, speaker gender and provenance.
5. Freeze selection manifest prior to running first experiment.

## Implementation guidance (illustrative, not built yet)

```python
import random
common_ids = sorted(set.intersection(*(ids_by_lang[x] for x in PILOT_LANGUAGES)))
selected_ids = sorted(random.Random(2026).sample(common_ids, 8))
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Convert IDs to int *before sorting* to avoid inconsistent ordering.
- Do not pick new IDs after observing failures.
- Different script and gender distributions still limit generalization.

## Acceptance tests

- [ ] Exactly eight shared IDs, 48 unique sample IDs.
- [ ] Running twice yields identical manifest/checksum.
- [ ] Referenced audio exists and transcripts are nonempty in source metadata.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
