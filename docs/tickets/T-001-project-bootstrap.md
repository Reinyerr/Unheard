# T-001 — Initialize repo, local Vite/FastAPI and safe defaults

**Status:** TODO (not implemented)  
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

- [ ] GET /health returns 200 with expected shape.
- [ ] Frontend starts and shows actionable offline/unavailable state.
- [ ] Git diff and `git status` show no secrets/raw audio.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.
