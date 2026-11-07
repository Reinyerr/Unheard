# T-001 — Initialize repo, local Vite/FastAPI and safe defaults

**Status:** Done (verified 2026-11-07)
**Priority:** P0  
**Owner:** Shared  
**Depends on:** None  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Create a reproducible empty-but-running two-process local app and safe repository baseline.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `frontend/`
- `backend/`
- `scripts/`
- `data/`
- `frontend/public/data/`
- `.gitignore`
- `.env.example`
- `local run instructions in README`

## Step-by-step implementation plan

1. Initialize React/Vite + TypeScript project under frontend and FastAPI in backend, pin dependencies.
2. Create `GET /health` and minimal shell that displays health and research data loading state.
3. Define `.env.example` without secrets and `.gitignore` for archives, recordings, real `.env`, caches and 311 files.
4. Configure dev CORS for exact localhost frontend origin (do not use wildcard in production).
5. Write local setup/start commands for both developers and verify from a clean checkout.

## Implementation guidance (illustrative, not built yet)

```python
# Backend route sketch (replace with real FastAPI setup)
@app.get("/health")
def health():
    return {"status": "ok", "mode": "local"}
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Missing ElevenLabs key must not prevent static frontend startup.
- Incorrect Vite base path must not be hard-coded for Cloudflare or GitHub Pages.
- No actual dataset ZIP committed.

## Acceptance tests

- [x] GET /health returns 200 with expected shape.
- [x] Frontend starts and shows actionable offline/unavailable state.
- [x] Git diff and `git status` show no secrets/raw audio.

## Definition of done / sign-off

- [x] Actual code/files exist and satisfy the accepted v1 contracts.
- [x] Each acceptance test run and **observed** results recorded (not just described).
- [x] Any source facts, coverage counts and spoken clips attributed as required (none added).
- [x] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [x] `INDEX.md` status changed after implementation evidence review; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Observed implementation evidence — 2026-11-07

Environment: Windows PowerShell, Node 24.21.0, isolated Python 3.12.16.
Working-tree implementation; no commit created. Existing deletion of
`docs/README.md` predates this work and was preserved. Existing local `data/`
contents were not modified and are now ignored.

Implemented: `backend/app/main.py`, backend tests/config/pinned requirements;
React/Vite/TypeScript/Tailwind frontend source, configuration, pinned package
manifest/lockfile, Vitest and Playwright tests; empty `frontend/public/data/`;
`scripts/README.md`; root/frontend environment examples; `.gitignore`; README
Windows setup and verification commands. Only `/health` is implemented; its
existing response contract is unchanged. No decision/schema amendment needed.

| Executed command / check | Observed result |
|---|---|
| `uv python install 3.12`, `uv venv backend/.venv --python 3.12`, `uv pip install --python backend/.venv/Scripts/python.exe fastapi uvicorn python-dotenv pytest httpx` | Local Python runtime/environment and dependencies installed; resolved versions frozen in `backend/requirements.txt` |
| `npm.cmd --prefix frontend install --save-exact react react-dom` and dev dependency installation | Installed pinned frontend dependencies; npm audit reported 0 vulnerabilities |
| `backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000` | Started actual local FastAPI server without ElevenLabs credentials |
| Python `urllib.request.urlopen('http://127.0.0.1:8000/health')` | HTTP 200, exactly `{"status":"ok","mode":"local"}` |
| `.venv/Scripts/python.exe -m pytest -q` from backend | 8 passed; health, no-key startup, allowed/disallowed CORS and invalid config |
| `npm.cmd --prefix frontend test` | 6 passed; mocked success, network failure/retry, HTTP error, malformed contract/JSON and five-second timeout |
| `npm.cmd --prefix frontend run build` | TypeScript check and Vite production build passed |
| `playwright.cmd install chromium`, then `npm.cmd run test:e2e` from frontend with FastAPI running | 2 passed: desktop 1280px and mobile 375px; actual browser health fetch, navigation, no page errors or horizontal overflow |
| Stop actual FastAPI process; set `EXPECT_BACKEND=offline`; `npm.cmd run test:e2e` | 2 passed: actionable unavailable message/retry and usable shell at both widths |
| Inspect desktop/mobile screenshots in ignored `frontend/test-results/` | Legible shell, pending research, no clipped content |
| Copy only tracked and non-ignored source files to `.cache/clean-bootstrap`; `npm.cmd --prefix .cache/clean-bootstrap/frontend ci`, build and test; new isolated Python venv installed from `backend/requirements.txt`, then pytest | Clean source-copy dependency installation succeeded; build passed, 6 frontend and 8 backend tests passed; no `.env` or dataset needed |
| `git diff --check`, `git status --short`, `git ls-files`, `git check-ignore` probes | No whitespace errors; no data/audio/credentials tracked; environment, source, audio, archive and cache probes ignored |
| Filename/size and secret-pattern scan of 58 existing tracked/non-ignored files | No risky paths, files over 1 MB or secret-pattern matches; public data marker intentionally permitted |

Failures resolved during verification: used `npm.cmd` for restricted PowerShell
execution policy and workspace npm cache for filesystem permissions; installed
Python locally because none was present. PowerShell/curl downloads failed with
Windows TLS errors; Node fetch downloaded uv successfully. Browser tests first
exposed missing whitespace in navigation accessible names; fixed and rerun.
Tailwind source scanning is scoped to `src/` so clean-copy and original builds
produce the same asset hashes, independent of surrounding cached files.

Limitations: Starlette emits one non-failing deprecation warning for its httpx
TestClient adapter. This restricted Windows environment required manually stopping
the test-owned Vite processes after browser assertions to finish runner cleanup;
both final browser runs exited 0. Python's optional global PATH/registry setup
was denied; the isolated runtime works via its explicit path. No paid API calls,
dataset processing, research findings or Urdu/cached speech demo exist yet.
Full demo/outage requirements remain assigned to their later tickets.

Manual verification: follow README's two-terminal start commands, open
`http://127.0.0.1:5173`, observe connected status, stop FastAPI and retry, then
restart FastAPI and retry. The four planned modules and pending research notice
remain visible throughout. T-002 is ready; T-003 still requires T-002, and all
other tickets retain their documented prerequisites.
