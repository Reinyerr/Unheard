# T-019 — Audit licenses, secrets and publishable assets

**Status:** In review — implementation only; manual audit execution, rights review and sign-off pending.
**Priority:** P0  
**Owner:** Shared  
**Depends on:** `T-002`, `T-007`, `T-013`, `T-015`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Ensure demos and future git publishing do not leak data or breach source constraints.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `docs/DATA_SOURCES.md (final)`
- `docs/attributions.md`
- `scripts/audit_publishable_assets.py`

## Step-by-step implementation plan

1. Audit every used FLAC/audio file license and include original source attribution and modifications.
2. Review generated TTS clips licensing/usage requirements and store only approved ones.
3. Search repository for .env keys, bulk ZIPs, 311 extracts, birth-city metadata or non-commercial audio.
4. Document why bank/assistant task audio was coverage evidence, not actual Mississauga 311.
5. Provide instructions to keep raw ZIP outside repository and prompt manual review before public deployment.

## Implementation guidance (illustrative, not built yet)

```python
# Guard concept: fail packaging if a private key or raw ZIP is staged
for path in staged_paths:
    assert not path.endswith(('.env','.zip'))
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Real `.env.example` is allowed, populated `.env` forbidden.
- Non-commercial/ShareAlike status may affect future use even if event is noncommercial.
- External polygon boundaries also need provenance and reuse check.

## Acceptance tests

- [ ] No unapproved raw audio/data or secrets staged.
- [ ] Every public clip has dataset attribution/licensing entry.
- [ ] Local data source files remain referenced and not copied wholesale.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Implementation handoff — 2026-11-07

Continued `feature/final-integration` at `b7759d3`, preserving uncommitted T-018
work. Dependencies T-002/T-007/T-013/T-015 exist in code and artifacts; T-015's
approved audio and historical reviewer gates remain incomplete. No prerequisites
were replaced with invented audio, provider results or licence approvals.

Implemented `scripts/audit_publishable_assets.py`, [attributions](../attributions.md)
with all 48 FLEURS paths, final package-scope notes in DATA_SOURCES.md and a
local report clarification in DECISIONS.md. No runtime or public contract change.
The audit inspects index bytes, current tracked/nonignored files and public/dist
including ignored media; flags private/bulk inputs, suspected credentials,
selected personal fields, unknown assets, hash mismatches and unapproved TTS.
It reuses the existing frozen selection/TTS approval validators. Public mode
blocks unresolved applicable City terms and provider-account output rights.

No automated tests were written/run, and no build or new audit command ran,
per the implementation-only request. Read-only Git inventory observed 136
indexed paths with zero indexed ZIP/FLAC/MP3/WAV files before these changes;
that count is not a secret scan or acceptance pass. No new audio or API requests.
Official ElevenLabs terms/billing guidance was consulted; account/voice rights
were not inferred. Existing source licence records were retained, not reapproved.

Manual commands from repository root (not run):

```sh
backend/.venv/bin/python scripts/audit_publishable_assets.py --target local
backend/.venv/bin/python scripts/audit_publishable_assets.py --target public
git diff --cached --name-status
```

See attributions.md for preparation, build/restoration commands, exit codes and
scope limits. Review current and historic secrets separately; owner rotation of
the earlier exposed key-shaped example is unverified. Public distribution,
municipal terms, generation-time account/output permissions and any future TTS
listening/rights review remain blockers. Acceptance boxes intentionally remain
open; implementation is not evidence of a passed audit.

Next implementation candidate is T-020 for Developer 2: its UI prerequisites
exist but T-015 voice/reviewer gates remain. Do not start it under this ticket.
