# T-017 — Automate high-risk validation and unit checks

**Status:** In review — local verification passed; GitHub Actions and independent live-preflight review pending.
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

## T-017 implementation and verification — 2026-11-07

Branch `feature/final-integration`, based on `675ad43`; changes are uncommitted.
T-001 through T-016 are merged per the user's handoff. Required implementation
dependencies exist; their historical review notes are not silently promoted to Done.
No application behavior, public schema, research output or accepted decision changed.
T-018/T-019/T-020 were not implemented.

Implemented files:

- `.github/workflows/ci.yml`: PR/branch Python tests, export validation, Python
  syntax checks, frontend tests, TypeScript/Vite build and whitespace checks.
  Uses existing pinned dependencies, no secrets, raw ZIP, provider calls or deployment.
- Root `pytest.ini` replaces `backend/pytest.ini`; root `conftest.py` supplies
  import paths and blocks external socket connections. Loopback is allowed for
  Windows asyncio's internal socketpair; HTTP provider calls remain mocked.
- `backend/tests/test_metrics.py`, `test_recovery.py`, `test_tts.py`:
  CER/normalization/WER eligibility, missing/unsupported pairs, real FastAPI routes,
  explicit confirmation, one different-clip retry, terminal referral, timeout/quota/
  unsupported errors, same-mode saved fallback, restricted inputs and audio hashes,
  exact multilingual prompt approval/hash gates. Synthetic text/header bytes are
  confined to tests and temporary directories, never released as research/audio.
- `scripts/validate_exports.py`, `scripts/tests/test_exports.py`: read-only five-file
  schema/identity validation, corrected ward totals and shares, coverage totals,
  priorities, 48 common-ID samples, outcome summaries/provenance, fixture rejection
  and a subprocess proving corrupted exports exit 1 with an actionable error.
  Optional `--source` independently checks the local source and seeded selection.
- `frontend/src/Regression.test.tsx`, `features/recovery/PromptAudio.test.tsx`:
  map/table selection and formatting, missing polygon fallback, Tamil Not tested,
  language switch/stale result clearing, saved Urdu recovery with unavailable retry,
  approved prompt playback/error/disposal and unapproved text-only fallback.
  Read-only real JSON is separate from transport mocks and synthetic prompt bytes.
- Updated existing `frontend/src/App.test.tsx` and `frontend/e2e/bootstrap.spec.ts`
  to assert the implemented application rather than removed bootstrap placeholders.
- Updated this ticket, `INDEX.md` and `TEST_PLAN.md` with observed evidence.

### Exact verification commands and final results

Commands run from repository root in Windows PowerShell, Python 3.12,
pytest 9.2.0, FastAPI 0.162.2, Pydantic 2.14.3, httpx 0.28.1, Node 24.21.0:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests scripts/tests -q
# 69 passed, 0 failed, 0 skipped; 11.35 seconds.
npm.cmd --prefix frontend test
# 13 passed across 3 files, 0 failed, 0 skipped.
npm.cmd --prefix frontend run build
# TypeScript --noEmit, real artifact guard and Vite production build passed.
backend/.venv/Scripts/python.exe scripts/validate_exports.py
# Passed: 11 wards, 15 languages, 14 census categories, 8 priorities, 48 samples/96 modes.
backend/.venv/Scripts/python.exe scripts/validate_exports.py --source data/raw/Mississauga_Unheard_ElevenLabs_Track.zip
# Passed: corrected source/coverage/ranks match; 560 metadata rows, 40 common IDs,
# seed 2026 reproduces the 8 selected IDs. No source/output files changed.
backend/.venv/Scripts/python.exe -m compileall -q backend/app scripts
git diff --check
# Both passed. No existing lint tool/config was present; no new lint dependency added.

$env:PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/playwright"
$env:EXPECT_BACKEND='offline'
npm.cmd --prefix frontend run test:e2e
# 2 passed: existing shell/static-data smoke at 1280px and 375px with backend down.
backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
# Run in a separate terminal for the following command.
$env:EXPECT_BACKEND='online'
npm.cmd --prefix frontend run test:e2e
# 2 passed: same existing smoke with real local FastAPI health.
```

The invalid-export test executes `python scripts/validate_exports.py --data-dir
<temporary-directory>` against a removed ward. Observed exit 1:
`Export validation failed: Recommendation references missing ward`. The same test
is included in CI. It does not mutate released research data.

Earlier failures were not ignored: baseline Python had 44 passing tests; initial
frontend collection failed for missing installed Leaflet. `npm --prefix frontend
test` was blocked by PowerShell execution policy, so commands use `npm.cmd`.
`npm.cmd --prefix frontend ci` failed on the restricted global npm cache;
`npm.cmd --prefix frontend ci --cache .cache/npm --no-audit --no-fund` succeeded.
Initial new tests exposed test-harness/import/expectation issues (Windows socketpair,
Vitest file URL, test selector typing and documented 400/schema validation order),
all corrected and rerun. Targeted diagnostic commands also run were
`python -m pytest backend/tests/test_health.py -xq` and
`python -m pytest backend/tests scripts/tests/test_exports.py -q` using the same
backend Python executable. No application bug fix or unrelated refactor was needed.

Initial browser run had 2 launch failures because Chromium was absent.
`node frontend/node_modules/@playwright/test/cli.js install chromium` was blocked
by the global cache directory. With `PLAYWRIGHT_BROWSERS_PATH` set as above, that
same install succeeded and both browser modes passed. Sandbox process cleanup
required stopping only the Vite processes started by these runs. `python -m pip
check` was unavailable because this existing venv has no pip; dependency versions
were inspected with `importlib.metadata`, and test/build execution succeeded.

### Remaining gates and limitations

- **Not Done:** GitHub Actions has not executed these uncommitted/unpushed changes.
  Local CI-equivalent commands pass; a remote green run and reviewer sign-off are
  still required by the literal acceptance criteria. No push/PR was performed.
- Independent live Scribe preflight remains separate: retain
  `scripts/preflight_scribe.py` and the historical human-reviewed response findings
  in T-008 (run `cf7414d01a52458cb5a7ba56f1596bb0`, four HTTP 200 responses).
  This checkout lacks `data/local/preflight_log.json`, retained raw responses and
  `data/processed/sampling_manifest.json`; therefore those claims cannot be
  independently revalidated here. No billed calls were made. Restore verified
  local evidence/assets before a new authorized manual preflight/rehearsal.
  During the online smoke, `/health` returned 200 and recovery capabilities
  returned 503 because the verified local catalog is unavailable. This is an
  actual demo prerequisite blocker, not a successful backend recovery rehearsal.
- Approved TTS audio is absent. Tests verify the approval gate with MOCK bytes;
  they do not establish playable audio, pronunciation or human language approval.
- Existing non-failing warnings: Starlette/httpx deprecation, Vite future native
  config-loader compatibility and bundle chunk over 500 kB. No scope-expanding fixes.
- Browser smoke is not the full four-act/Urdu playback/outage rehearsal. Backend
  recovery uses mocked I/O; frontend saved Urdu uses actual exported text.
  T-018 remains the next ticket, pending T-017 remote/reviewer sign-off and its
  existing real audio/evidence prerequisites. T-019/T-020 unchanged.

Acceptance: local tests and invalid-data rejection verified; offline CI configured
and guarded against external requests. Actual GitHub Actions result and independent
live-preflight review remain unverified, so the acceptance checklist stays open.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
