# T-002 — Audit source archive, licenses and provenance

**Status:** Done (verified 2026-11-07)
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-001`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Make all data dependencies explicit and fail when required files/source rows are missing.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/audit_sources.py`
- `data/processed/source_manifest.json (generated later)`
- `docs/DATA_SOURCES.md (updated audit)`

## Step-by-step implementation plan

1. Locate files under exact archive root and avoid extracting 468 MB wholesale.
2. Validate census/coverage/crosswalk headers and FLEURS reference rows; record size/checksum/version.
3. Check 8 missing categories, 79,940 sum, 153,480 denominator.
4. Keep licensing attribution and redistribution permissions in an asset manifest.
5. Document out-of-scope raw 311 and non-commercial-only audio.

## Implementation guidance (illustrative, not built yet)

```python
missing = [r for r in coverage if r["has_service_request_audio"] == "False"]
assert len(missing) == 8
assert sum(int(r["city_home_speakers"]) for r in missing) == 79940
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Handle UTF-8 BOM, CSV missing/empty values and Boolean strings.
- Audit FLEURS reference rows without adding 560 source files to repository.

## Acceptance tests

- [x] Source checks produce exact expected totals.
- [x] Missing required column errors contain source path.
- [x] Manifest contains license links and confirms zero raw ZIP files committed in locally reachable history.

## Definition of done / sign-off

- [x] Actual code/files exist and satisfy the accepted v1 contracts (public contracts unchanged).
- [x] Each acceptance test run and **observed** results recorded (not just described).
- [x] Source facts and counts attributed; no spoken clips published.
- [x] Known provenance/licensing limits reported instead of filled with demo fiction.
- [x] `INDEX.md` changed after review of observed evidence; T-003 unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Executed evidence — 2026-11-07

Windows PowerShell, local Python 3.12.16. No new dependencies, commits or API
requests. Existing T-001 work and pre-existing `docs/README.md` deletion preserved.

Implemented files: `scripts/audit_sources.py`, `scripts/source_licenses.json`,
`scripts/tests/test_audit_sources.py`, `scripts/README.md`; updated root README,
`.env.example`, `docs/DATA_SOURCES.md`, decision clarification and ticket index.
Generated ignored `data/processed/source_manifest.json`. Source ZIP untouched;
no full extraction, public JSON, audio copies or experimental outputs.

| Command / inspection | Observed result |
|---|---|
| `backend/.venv/Scripts/python.exe scripts/audit_sources.py --source data/raw/Mississauga_Unheard_ElevenLabs_Track.zip` | Exit 0; actual 490,630,718-byte archive audited; 8 missing categories, 79,940/153,480, 11 corrected wards |
| Same command with `--output data/processed/source_manifest_repeat.json`, then compare parsed reports excluding `generated_at_utc` | Identical evidence; 560 FLEURS hashes, 2,653 audio references checked; six pilot languages share 40 IDs (as do all 14 supplied FLEURS languages) |
| `backend/.venv/Scripts/python.exe -m pytest scripts/tests -q` | 36 passed; synthetic fixtures only, separate from actual-archive preflight |
| Audit with `--source data/raw/does-not-exist.zip --output data/processed/missing_source_check.json` | Expected exit 1; explicit missing-source path and failed report |
| `backend/.venv/Scripts/python.exe -m pytest -c backend/pytest.ini backend/tests -q` | 8 passed; existing non-failing Starlette/httpx deprecation warning |
| `git check-ignore data/raw/Mississauga_Unheard_ElevenLabs_Track.zip data/processed/source_manifest.json` | Both ignored |
| `git ls-files '*.zip' '*.flac' '*.mp3' '*.wav' 'data/*'`; audit's current-index/reachable-history Git check | No tracked raw data/audio; 0 committed ZIP paths |
| `git diff --check` | Passed |
| Pack README/dictionary/license read directly from ZIP; upstream primary-source checks | License declarations recorded, upstream confirmations and unknowns separately documented in DATA_SOURCES.md |

The first source preflight correctly rejected an implementation assumption that
MInDS-14 would be 8 kHz. Direct inspection of all supplied FLAC headers established
16 kHz mono in this pack; the check was corrected and rerun successfully. No
source bytes were altered. The first inspection's Windows console encoding error
was resolved using UTF-8 output; source metadata itself decoded successfully.

Known limitations: format checks do not fully decode audio; no pack release or
upstream revision is pinned; outline DOCX was not found in the inspected workspace;
current Mississauga dataset-specific terms and the Accent Archive upstream license
need resolution before relevant public redistribution. They do not block local
schema/fixture development. Raw/optional tables are inventory-only in the reusable
audit; one-time parsed counts are separately documented. No claimed geographic
speech performance, no sample selection, no API preflight and no full Urdu demo.

Manual verification: run the real-source command, inspect manifest `status`,
`checks`, `metadata_files`, `datasets`, `licenses` and `provenance.git`; confirm
the documented archive SHA-256. If the source is elsewhere, supply that explicit
ZIP or extracted pack root; do not assume it exists in a fresh clone.

**Next:** T-003 prerequisites are satisfied. Implement v1 schemas and explicit
identity mappings using the verified original headers (not the ticket sketches),
with labelled minimal fixtures. T-004/T-005/T-006/T-007 remain dependent on T-003;
no unrelated ticket has been started.
