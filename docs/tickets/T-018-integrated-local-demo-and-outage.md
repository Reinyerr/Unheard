# T-018 — Rehearse full four-act localhost and offline scenarios

**Status:** In review — automated four-act/outage rehearsal passed; both developers' independent rehearsal and reviewer sign-off pending.
**Priority:** P0  
**Owner:** Shared  
**Depends on:** `T-011`, `T-013`, `T-015`, `T-016`, `T-017`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Establish reliable, independently operable demo under normal and failure conditions.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `docs/DEMO_RUNBOOK.md (filled actual steps)`
- `docs/test-evidence/local-smoke.md`

## Step-by-step implementation plan

1. Document cold-start npm/Python commands and local ports.
2. Run Urdu act 1->4 with actual recorded clip/result, independent of developer who built each part.
3. Disconnect ElevenLabs/backend and verify saved map/audio/results still usable.
4. Exercise unsupported language, missing results, invalid audio, one-retry exhaustion and no polygons.
5. Record what failed, exact fix and retest; freeze scope when pass criteria met.

## Implementation guidance (illustrative, not built yet)

```python
# Manual smoke path (not executed by documentation itself)
# 1. Select Urdu; verify ward count/share
# 2. Play real sample; inspect both results
# 3. Reject -> retry different clip -> referral
# 4. Open recommendation; disable API and repeat saved path
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Do not promise judge can access localhost from their personal device.
- Do not claim fresh API calls while showing saved results.
- If no verified experiment available, present partial core honestly.

## Acceptance tests

- [ ] Both developers successfully operate four acts without coaching.
- [x] Backend unplugged map/speech/results still usable (10 browser cases passed with FastAPI stopped, 2026-11-07).
- [x] Demo evidence includes run date and observed results.

## Definition of done / sign-off

- [x] Actual code/files exist and satisfy the accepted v1 contracts (production export/source validation and build passed).
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [x] Any source facts, coverage counts and spoken clips attributed as required (existing source metadata/UI and restored FLEURS attribution retained; public packaging review remains T-019).
- [x] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Continuation evidence — 2026-11-07

Starting commit `b7759d3` already contained the integrated UI, T-017 checks,
audio restoration helper and partial T-018 browser suite; no completed feature
was restarted. See [actual command/results evidence](../test-evidence/local-smoke.md)
and [filled runbook](../DEMO_RUNBOOK.md).

Observed this session: 70 Python tests, 13 frontend tests, frontend type/build,
real-source/export validation, compile check, 10 online browser cases and 10
backend-stopped browser cases passed. The browser suite exercises the real Urdu
four acts, saved source FLAC playback, count/share, saved CER/WER-unavailable,
confirmation/retry/referral, selection cleanup and missing-data/audio/geometry.
Fixed only the test's assumption about absent local saved evidence and Chromium's
standalone-shell crash on macOS; application code/data/contracts unchanged.

Approved TTS playback has no asset to verify; text-only fallback passed. No new
provider calls, billable generation, human listening or approval occurred. Only
one usable Urdu saved recording exists: retry to an unavailable second clip
correctly gives referral; two usable-clip rejections remain a real-data limitation
(state transitions are covered with mocked unit tests). Full pilot remains partial.

Both developers' cold-start, uncoached four-act rehearsal and reviewer sign-off
are still unverified. Historical dependency review gates (including T-017 remote
CI/live review and T-015 audio approval) are not changed by this evidence.
**Not Done; no downstream ticket is marked unblocked. T-019/T-020 not started.**
