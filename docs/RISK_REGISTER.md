# Risk register — prioritized and actionable

**Status:** risk planning only. Update owner/mitigation after execution.

| ID | Severity | Risk / trigger | Mitigation | Fallback / stop rule | Owner |
|---|---|---|---|---|---|
| R-01 | Critical | Unsupported Scribe language hints / Cantonese support | one real preflight per configuration; log exact error and model version | show `unsupported`, keep measured auto-only, no fabricated comparison | Dev 1 |
| R-02 | Critical | Bad census denominator/Ward 10 | corrected file, tests for source reconciliation | block map claim; use verified table | Dev 1 |
| R-03 | High | No validated ward polygons | verify external boundary source/ward property | use ward bars/table until validated | Dev 2 |
| R-04 | Critical | API failure/quota exhausted | pilot first, caching, bounded retries | static authentic experiment results, labelled offline | Dev 1 |
| R-05 | High | FLEURS scripts mismatch model output | preserve raw outputs, explicit normalization review | exclude incompatible paired CER with disclosed reason | Dev 1 |
| R-06 | High | n=8 not representative | fixed seed, clip-level transparency, limitations | exploratory conclusions only | Both |
| R-07 | Critical | Wrong geographic inference | explicitly separate language- and ward-level evidence | stop displaying unverified ward risk rankings | Both |
| R-08 | High | Audio redistribution or leaked secrets | licensing checklist + repo audit | omit offending files and use approved clips only | Both |
| R-09 | Critical | Front/back data schema diverges | frozen v1 contracts, fixtures, CI | delay feature merge / present static research | Both |
| R-10 | High | TTS language unavailable | capability preflight, cache actual prompts | clearly labelled text-only prompt, do not claim TTS | Dev 1 |
| R-11 | High | Voice demo traps user or overclaims | deterministic states and two total attempts | referral screen / stop | Dev 1 & Dev 2 |
| R-12 | High | Team runs out of development time | one vertical slice, P0 first, no stretch | protect research, Urdu demo and docs | Both |
| R-13 | Medium | Localhost fails on demo machine | clean-start runbook, dependencies pinned, offline test | prerecorded verified walkthrough + source artifact, subject to event rules | Both |
| R-14 | Medium | Inaccurate language labels/codes | crosswalk review and distinct API hint capability checks | mark unsupported/unknown rather than silently remap | Dev 1 |

## Escalation rule

When a **critical** risk prevents truthful demonstration of a feature, mark the dependent ticket `Blocked`, capture evidence, use the documented fallback, and **never label it completed**. D-025 requires explicit scope/decision updates if mitigation changes accepted product behaviour.
