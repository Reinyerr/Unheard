# T-007 — Generate 48-record FLEURS sample manifest

**Status:** In review — implemented on real source; automated tests skipped at user request.
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


## Implementation evidence — 2026-11-07

Branch `feature/data-backend`; working-tree implementation, no commit created.
T-002 source audit and T-003 schemas/shared identities exist; T-003 remains In review.

Created `scripts/sample_fleurs.py`, ignored local
`data/processed/sampling_manifest.json`, `frontend/public/data/samples.v1.json`,
48 selected local FLACs and `frontend/public/audio/FLEURS_ATTRIBUTION.txt`.
Updated processing docs, source notes, decision clarification and index. No React,
shared-contract, dependency, test-file or experiment changes; no provider requests.

Executed once with available Python 3.14.7/Pydantic 2.13.5:

```sh
python3 scripts/sample_fleurs.py --source '/Users/rainierjorgejorda/Downloads/Mississuaga File/Mississauga_Unheard_ElevenLabs_Track'
```

Observed exit 0: 560 metadata rows, 14 languages with 40 unique numeric IDs each,
40 shared pilot IDs, and 48 schema-validated selected records. Eight selected IDs:
`1533, 1537, 1566, 1587, 1608, 1632, 1635, 1651`.
Selection content SHA-256:
`59f8c23640f271eefa5787fdedd3833e0091af14e40e448e1f4c8a58584d886c`.
Audio folder occupies approximately 7.8 MiB. Ignore inspection confirmed selected
FLACs and local manifest remain ignored; public JSON and attribution text are not.

Production checks cover identity mappings, duplicate IDs/paths, nonempty references,
all referenced FLAC headers/durations, source hashes and selected audio checksums.
References are preserved verbatim. Samples are ordered by canonical language ID,
then numeric ID. The local manifest freezes selection before exports. Matching
reruns preserve its original timestamp; changed frozen content fails explicitly.
Interrupted copying can leave incomplete assets; rerun to repair the same selection.

Permitted-asset review: pack license hash matches T-002. FLEURS CC BY 4.0 was
corroborated upstream in that audit. Only these 48 FLEURS clips/references are
selected, with author/source/license links and modification notice in the JSON
and attribution text. Clips are copied byte-for-byte; no resampling, translation
or normalization. Pack conversion history is unknown. This narrow review does
not approve other datasets or close T-019's later package/privacy audit.

No automated tests or repeat/checksum comparison were written/run. Acceptance
checkboxes remain open. No full decode/listening, pinned-environment verification,
frontend build or Urdu/demo regression was performed. Script/gender caveats are
retained. Independent reproducibility verification remains pending.

Manual review: run the command, inspect eight IDs per language and 48 unique
sample IDs, compare references and audio hashes with source, listen to clips,
and rerun while comparing manifest/public JSON SHA-256 values (commands in
`scripts/README.md`). Keep the original frozen manifest; never reselect after
observing outcomes. Ignored manifest/audio must be regenerated or deliberately
transferred on other machines; a Git clone does not bundle them. The frontend
build guard still needs the later real `experiments.v1.json` export.

Next ready Dev 1 implementation: T-008, subject to open T-003/T-007 review gates.
Credentials, guidance support and credits remain T-008 preflight checks, not
verified capabilities. T-009/T-010 retain their listed prerequisites. No later
ticket was implemented; T-007 is not marked Done.
