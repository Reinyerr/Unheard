# T-009 — Run cached paired ElevenLabs pilot and track failures

**Status:** In review — runner implemented; offline real-cache export observed; full live pilot/tests not run.
**Priority:** P0  
**Owner:** Dev 1  
**Depends on:** `T-007`, `T-008`, `T-010`  
**Relevant decisions:** See [`DECISIONS.md`](../DECISIONS.md) and [`REQUIREMENTS.md`](../REQUIREMENTS.md); contracts in [`DATA_CONTRACTS.md`](../DATA_CONTRACTS.md).

## Objective / why this matters

Produce authentic results for both conditions on each selected sample when supported.

## Required prerequisites and inputs

- Read the exact ticket dependencies and `AGENTS.md` before changing code.
- Treat user-supplied `Mississauga_Unheard_ElevenLabs_Track.zip` and the outline as original sources; source data may need to be mounted or locally extracted. Do **not** assume attached ZIP exists on another machine.
- Check the contract/schema conventions and distinguish already verified source facts from implementation assumptions.

## Expected files and deliverables

- `scripts/run_experiments.py`
- `data/local/raw_scribe_responses/ (ignored)`
- `data/processed/experiment_attempts.json`

## Step-by-step implementation plan

1. Iterate deterministic frozen manifest, call the adapter for auto and verified guided modes.
2. Cache by sample hash + model ID + normalized config; resume safely without re-paying for identical completed requests.
3. Retry only transient failures, with bounded backoff and attempt log.
4. Persist `completed`, `technical_error`, `unsupported`, `incompatible_output` and raw responses.
5. Track selected, attempted, completed, failed counts per language; export immutable provenance.

## Implementation guidance (illustrative, not built yet)

```python
for sample in samples:
    for mode in ("auto", "guided"):
        if cache.has_success(sample, mode, model_id):
            continue
        result = attempt_with_bounded_retry(sample, mode)  # mock in CI
        save_status_and_raw_response(sample, mode, result)
```

**Coding-agent instruction:** Verify the actual dataset headers, installed library signatures and real API response; the snippet illustrates logic only, and **must not** be mistaken for implemented or tested code.

## Edge cases and failure states

- Quota exhausted mid-run should leave valid partial results.
- Guidance unsupported must not silently fall back to auto.
- An API success with empty speech content is distinguishable from HTTP failure.

## Acceptance tests

- [ ] No duplicate remote request when cache already valid.
- [ ] Repeated execution produces same selection and honors completed statuses.
- [ ] Failed modes remain visible and cannot produce fabricated paired deltas.

## Definition of done / sign-off

- [ ] Actual code/files exist and satisfy the accepted v1 contracts.
- [ ] Each acceptance test run and **observed** results recorded (not just described).
- [ ] Any source facts, coverage counts and spoken clips attributed as required.
- [ ] Known failures and incomplete experimental results reported instead of filled with demo fiction.
- [ ] `INDEX.md` status changed only after reviewer verifies it; next dependency unblocked.

**Evidence to record:** local command, date, short result/log, relevant commit, any contract amendment, demonstration steps and blocked tickets.

## Prerequisite check — 2026-11-07

Checked on `feature/data-backend`. T-007's sampler and frozen local manifest
exist; its review/acceptance gate remains open. T-008 and T-010 are still TODO:

- Missing `backend/app/services/elevenlabs_adapter.py`,
  `scripts/preflight_scribe.py` and `data/local/preflight_log.json`; no verified
  model/options, guided-language support or real response/error evidence exists.
- Missing `scripts/calculate_metrics.py` and the real
  `frontend/public/data/experiments.v1.json` exporter/output required by T-010.

The ticket/index statuses and source inventory confirm these missing prerequisites.
Per AGENTS.md's one-ready-ticket rule, no runner, guessed adapter interface,
provider responses or metrics were invented. No tests were written/run, no API
requests made, and no UI/shared-contract or unrelated ticket changes made.
Only this blocker record and `INDEX.md` were updated.

Unblock sequence: implement T-008 and record actual preflight evidence, then
implement T-010 using that verified sample/interface, then resume T-009.
Next ready Dev 1 implementation ticket is T-008, subject to existing T-003/T-007
review gates. There is no T-009 run command yet because its implementation cannot
start under the current prerequisites; do not mark this ticket implemented/verified.


Dependency update after T-010 implementation: the missing-prerequisite notes
above are historical. T-008 real small-preflight evidence and T-010 metrics/export
now exist; T-009 is ready for implementation subject to their review gates and
remaining guidance/credit/script validation for a full pilot. No runner was added.


## Implementation evidence — 2026-11-07

On `feature/data-backend`, T-007 frozen selection, T-008 real preflight/adapter,
and T-010 metrics/export implementation exist. Their review gates remain open.
The earlier missing-prerequisite notes above are historical. Prior uncommitted
work was preserved; no commit created.

Created `scripts/run_experiments.py`, ignored local
`data/local/experiment_cache/`, `data/local/raw_scribe_responses/`,
`data/processed/experiment_attempts.json` and per-run snapshots in
`data/processed/experiment_runs/`. Regenerated the public experiments artifact
through T-010, with all unattempted modes explicit. Adapter change extracts its
unchanged request settings into a shared pure function so cache keys exactly
match uploads. T-010 integration preserves cached review_flags and removes its
preflight-only limitation wording for future full runs. No public schema/enums,
React components, new dependencies, new samples or unrelated features changed.

Observed production command:

```sh
python3 scripts/run_experiments.py
```

Exit 0, status partial, zero new POSTs. Imported the four actual T-008 modes,
then subsequent production invocations reused cached evidence while integrating
final report/export changes. Final report lists 96 planned modes, four terminal
outcomes (three completed, one incompatible_output), 92 not_tested, and selected
n=8 per language. Urdu has two completed modes; Cantonese has one completed
and one script-excluded mode. Original provider completions are recorded
separately (four); no failed outcome becomes a metric. T-010 full-bundle production
validation succeeded; raw response copies, immutable attempt envelopes and
checksum-bound cache histories were generated. No automated tests/test files or
new remote requests were run. This is not acceptance-test sign-off.

Runner behavior:

- Frozen language/ID order, content-hash/model/endpoint/canonical-options cache;
  preflight model/audio/settings/raw evidence verified before import. Completed,
  incompatible and unsupported cached results are reused, not re-purchased.
- Guided sends require actual accepted preflight/cache evidence for that
  language/model/hint. Urdu/Cantonese currently have it; other guidance remains
  not_tested and is skipped without automatic-mode fallback. API acceptance does
  not certify output quality or script comparability.
- Live sends require --live and a server environment key. Default new-POST cap is
  96 including retries; --max-requests allows a smaller budget. Max three sends
  per pending mode per invocation, transient errors only, bounded exponential
  backoff/Retry-After. Delays over 30 seconds pause for later resume. Permanent,
  unsupported and incompatible results are not retried. Prior technical failures
  require explicit --retry-failed and must be marked retryable.
- Credential/permission/quota failures stop the run; exhausted 429 stops further
  sends. Each response is retained before incremental terminal reporting. Partial
  results remain valid. There is no provider idempotency guarantee: timeout retries
  can bill again even when no successful response was received.
- Exclusive local process lock prevents competing runners. Before a POST, persist
  an in-flight journal. An interrupted/unknown call blocks replay and metrics
  replacement until the user inspects provider/local evidence; no automatic lock
  clearing or forced replay. Known completed cache entries remain reusable.
- Final input report contains exactly one terminal entry per observed sample/mode,
  a separate complete 96-mode state list, per-language counts, guidance evidence,
  run config, import hashes/events, script hashes and immutable history links.
  Missing outcomes are not_tested, not fabricated technical errors or zero CER.
  Per-run reports stop changing after completion; the latest report is replaceable.

Manual offline command is above. For an explicitly budgeted live continuation,
configure the exported key and run:

```sh
python3 scripts/run_experiments.py --live --max-requests 12
```

Use --languages for a language subset (all eight frozen IDs remain fixed). For
full guided coverage first use the existing T-008 preflight for the four missing
languages and import its report; commands and resume/recovery guidance are in
scripts/README.md. Runner automatically invokes the existing T-010 exporter for
valid complete/partial/paused evidence; no key is needed for offline export.

Known limits: the full live pilot, paid cache-hit replay, crash/retry/quota paths,
independent metrics and Urdu/cached-demo regression are unverified. No tests or
frontend build were run. Subscription credit allowance remains unavailable from
the earlier HTTP 401 response. Additional guidance is not verified; there is no
claim of 96 successful requests or significance. T-009 stays In review, not Done.
Next ready Dev 1 implementation: T-014 (T-001/T-003/T-008 interfaces/evidence exist),
subject to their review gates. No later ticket was implemented.

## Six-language pilot continuation — 2026-11-09

The Windows checkout had all 48 attributed FLEURS FLACs, the frozen manifest
and the published one-recording results. All 48 audio files matched the
manifest's size and SHA-256 checks. The ignored raw responses and cache for the
earlier run were absent. Rebuilding the local saved demo cache would require
up to 96 Scribe v2 requests, including 12 for the previously tested recording
ID. The sampling seed is 2026 and the selection hash is
`59f8c23640f271eefa5787fdedd3833e0091af14e40e448e1f4c8a58584d886c`.

The six-language preflight recorded 12 transport errors with no HTTP response
under the network sandbox. Automatic approval review rejected escalation
pending explicit authorization to send the recordings to ElevenLabs and use
account credits. No new provider outcomes were verified. The public export
continues to show 11 scored modes, one incompatible mode and 84 untested modes.

The export validator passed for 48 samples and 96 explicit mode states.
The frontend build, all 12 frontend unit tests and all 10 Python metric tests
passed. The wider Python suite did not finish in the sandbox. A Chromium check of
the built application served workspace assets via Playwright request routing
with FastAPI unreachable. It selected each of the eight recordings per language
and verified that playback advanced for all 48. A separate check selected Urdu
recording 1533 in Demonstrate using Browser-only saved results and reached
acceptance after confirming the transcript. To reproduce playback manually,
open Investigate, select one of the six pilot languages, and use Recording and
Play recording. For the Urdu check, continue to Demonstrate and choose the
browser-only route and recording 1533.

No schema or pilot scope change. T-009 remains in review, with live completion
blocked pending explicit authorization for the bounded upload.
