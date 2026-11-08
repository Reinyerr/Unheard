# One-recording six-language pilot continuation — 2026-11-08

User explicitly authorized one sentence ID (1533) for English, Arabic, Punjabi
and Mandarin Chinese, automatic/guided, up to eight new transcription POSTs.
Urdu/Cantonese retained their previous results. No selection, metric policy,
provider model or API contract changes; no TTS generation authorized or performed.
Existing backend/.env configuration edits were preserved; no key was printed.

## Observed execution

1. `backend/.venv/bin/python scripts/run_experiments.py`: offline import of the
   previous reviewed Urdu/Cantonese report, zero POSTs; preserved manual Cantonese
   exclusion in cache before the new latest preflight report replaced it.
2. Python wrapper loaded backend/.env privately and invoked the existing
   `scripts/preflight_scribe.py --languages english arabic punjabi mandarin_chinese`.
   Existing adapter validated frozen audio hashes before sending; first frozen
   ID=1533, model=scribe_v2, no retries, two modes per language. Exactly **eight
   transcription POSTs** returned **HTTP 200**, all nonempty outputs and accepted
   guided parameters. Two subscription metadata GETs returned **401**; exact
   credit allowance/charges could not be read. No further provider calls occurred.
3. Saved text inspection found matching detected codes eng/ara/pan/zho and
   expected reference scripts. No acoustic, listening or competent-speaker quality
   approval occurred. Original raw responses/run report unchanged; separate
   reviewed report retained locally. No new manual metric exclusions were needed.
4. `backend/.venv/bin/python scripts/run_experiments.py --preflight
   data/local/preflight_before_four_languages_2026-11-08.json --preflight
   data/local/preflight_four_languages_review_2026-11-08.json`: offline cache import
   and metrics export, **zero new POSTs**, status partial (remaining 7 clips per
   language stay untested).
5. `backend/.venv/bin/python scripts/validate_exports.py`: passed the existing
   source-attributed bundle checks for 11 wards, 15 languages, 8 priorities,
   48 samples and 96 explicit mode states. Operational artifact validation, not
   automated unit/browser tests; none were written or run.

## Exported results for 1533

CER shown as percentages, rounded to two decimals; lower is better.

| Language | Automatic CER | Guided CER | Comparable pairs |
|---|---:|---:|---:|
| English | 31.11% | 0.00% | 1 |
| Arabic | 1.06% | 1.06% | 1 |
| Punjabi | 4.88% | 4.88% | 1 |
| Mandarin Chinese | 10.34% | 10.34% | 1 |
| Urdu (retained) | 10.59% | 10.59% | 1 |
| Cantonese (retained) | Excluded pending script/language review | 10.00% | 0 |

English WER is 33.33% automatic / 0.00% guided. Other WERs remain null under
existing tokenizer policy. Exact ratios/raw text remain in artifacts/evidence;
0.00% here is an actual scored result, never a replacement for missing data.
Model-output Latin capitalization in Mandarin is preserved; no silent conversion
or translation introduced. One recording cannot establish language-wide quality,
statistical significance, fairness or geographic performance. Planned selection
remains 8 clips/language (48 total), with 12 attempted modes, 11 scored modes,
1 incompatible mode and 84 not_tested. No cherry-picking or outcome-based resampling.

## Evidence locations and changes

- Original new local run report:
  `data/local/preflight_runs/4dcf048dc53c4859bc3504b8834f9539/report.json`.
- New raw responses live alongside that report; all ignored and key-redacted by
  the existing adapter. Source samples are FLEURS, Google/Conneau et al., CC BY 4.0,
  selection SHA-256 `59f8c23640f271eefa5787fdedd3833e0091af14e40e448e1f4c8a58584d886c`.
- Original previous reviewed report snapshot:
  `data/local/preflight_before_four_languages_2026-11-08.json`.
- New separate text review: `data/local/preflight_four_languages_review_2026-11-08.json`.
- Latest cached outcomes: `data/processed/experiment_attempts.json`; full metric
  details and response/cache histories remain local, not copied wholesale.
- Updated public `frontend/public/data/experiments.v1.json` and added a dynamic
  one-recording warning to SpeechLab.tsx. No invented speaker/resident data.

Manual viewing: refresh the running website, choose each language, then recording
1533 in Investigate. Inspect both transcripts, actual scores and n=1 warning.
In Demonstrate choose browser-only saved results for existing outputs. Refresh
backend availability to load new guidance/cached evidence if using the local route.
No browser interaction or audio listening check was performed by the agent.
This bounded experiment is not sign-off for the full eight-clip pilot or TTS.
