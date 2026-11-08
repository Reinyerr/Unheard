# UNHEARD attribution and package review — T-019

Implementation handoff: 2026-11-07, branch `feature/final-integration`.
This ledger covers the existing local MVP. Public distribution is not approved.
See [DATA_SOURCES.md](DATA_SOURCES.md) for source hashes and historical reviews.
No automated tests or audit command were run in this implementation session.

## Sources used

| Source / attribution | Used material and modification | Licence / release position |
|---|---|---|
| City of Mississauga | Corrected 2021 ward census, crosswalk/coverage aggregates and recommendations; derived counts/shares, corrected Ward 10, omitted raw resident/service records. Contains information provided by the City of Mississauga. | Pack declares City open-data terms; applicable dataset-specific terms remain unresolved. Local prototype only pending manual review. |
| City of Mississauga / MississaugaData, Ward Boundaries | 11 official polygons, selected ward IDs/properties, WGS84 query; no shape repair. Current-layer snapshot, not certified 2021 geometry; overlap warnings retained. | [Dataset](https://data.mississauga.ca/datasets/mississauga::ward-boundaries/about), [linked terms](https://smartcity.mississauga.ca/wp-content/uploads/2021/04/CityofMississauga_TermsofUse.pdf). Historical retrieval returned 403; no new clearance inferred from the City's general open-data policy. |
| Google; Conneau et al. (2022), *FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech* | 48 selected supplied FLACs copied byte-for-byte; references preserved verbatim. No resampling, translation or normalization of source assets; pack conversion history unknown. Selection and derived metric policies disclosed separately. | [FLEURS source](https://huggingface.co/datasets/google/fleurs), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Retain attribution, links and modification notice with every distributed selection. Upstream revision unknown; exact supplied metadata/asset hashes identify inputs. |
| PolyAI; Gerz et al. (2021), *Multilingual and Cross-Lingual Intent Detection from Spoken Data* | MInDS-14 aggregate language coverage only; no banking recordings or transcripts included. | [Source](https://huggingface.co/datasets/PolyAI/minds14), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Banking requests are not Mississauga 311 speech. |
| FBK-MT; Speech-MASSIVE | Aggregate language coverage only; no assistant recordings or transcripts included. | [Source](https://huggingface.co/datasets/FBK-MT/Speech-MASSIVE), [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Noncommercial/ShareAlike obligations require separate review for any future reuse; aggregates do not grant permission to publish audio. Assistant requests are not Mississauga 311 speech. |
| Weinberger, S. (2015), Speech Accent Archive, George Mason University | No runtime assets; optional source audit only. | [Source](https://accent.gmu.edu), pack-declared CC BY-NC-SA 4.0. Excluded from MVP packaging; upstream rights remain unresolved. |
| Toronto Open Data / City of Mississauga historical contact-centre tables | No raw 311 extracts packaged. Source inventory/context only; Toronto records must not be presented as Mississauga requests. | [Toronto licence](https://open.toronto.ca/open-data-licence/); City terms remain a separate gate. |
| ElevenLabs; UNHEARD-authored demo instruction | Saved Scribe-derived text/metrics; no approved generated TTS audio currently exists. Six selected voice IDs and draft captions are configuration, not a rights grant or verified synthesis. | [Terms](https://elevenlabs.io/terms-of-use), [billing/licensing guidance](https://elevenlabs.io/docs/overview/administration/billing). Generation-time account plan, voice permission and applicable output/distribution terms require manual review. |

ElevenLabs' official guidance checked for T-019 distinguishes noncommercial,
attributed free-plan use from paid-plan commercial rights; this does not establish
the team's generation-time subscription or permission for any selected voice.
Never infer those facts from `rights_reviewed:true`, GET access, a voice ID or
model language support. Retain account/permission evidence privately. Determine
any required public placement/wording of attribution before distribution.

## Curated FLEURS clip ledger

Every row below is one existing `samples.v1.json` entry and inherits the complete
Google/Conneau attribution, source, CC BY 4.0 link and modification notice above.
The original recording speaker is not the confirmer of this demo. No ward
residence or original-speaker municipal consent is asserted.

| Sample ID | Public-relative FLAC path |
|---|---|
| arabic-1533 | `audio/ar_eg/ar_eg_1533.flac` |
| arabic-1537 | `audio/ar_eg/ar_eg_1537.flac` |
| arabic-1566 | `audio/ar_eg/ar_eg_1566.flac` |
| arabic-1587 | `audio/ar_eg/ar_eg_1587.flac` |
| arabic-1608 | `audio/ar_eg/ar_eg_1608.flac` |
| arabic-1632 | `audio/ar_eg/ar_eg_1632.flac` |
| arabic-1635 | `audio/ar_eg/ar_eg_1635.flac` |
| arabic-1651 | `audio/ar_eg/ar_eg_1651.flac` |
| cantonese-1533 | `audio/yue_hant_hk/yue_hant_hk_1533.flac` |
| cantonese-1537 | `audio/yue_hant_hk/yue_hant_hk_1537.flac` |
| cantonese-1566 | `audio/yue_hant_hk/yue_hant_hk_1566.flac` |
| cantonese-1587 | `audio/yue_hant_hk/yue_hant_hk_1587.flac` |
| cantonese-1608 | `audio/yue_hant_hk/yue_hant_hk_1608.flac` |
| cantonese-1632 | `audio/yue_hant_hk/yue_hant_hk_1632.flac` |
| cantonese-1635 | `audio/yue_hant_hk/yue_hant_hk_1635.flac` |
| cantonese-1651 | `audio/yue_hant_hk/yue_hant_hk_1651.flac` |
| english-1533 | `audio/en_us/en_us_1533.flac` |
| english-1537 | `audio/en_us/en_us_1537.flac` |
| english-1566 | `audio/en_us/en_us_1566.flac` |
| english-1587 | `audio/en_us/en_us_1587.flac` |
| english-1608 | `audio/en_us/en_us_1608.flac` |
| english-1632 | `audio/en_us/en_us_1632.flac` |
| english-1635 | `audio/en_us/en_us_1635.flac` |
| english-1651 | `audio/en_us/en_us_1651.flac` |
| mandarin_chinese-1533 | `audio/cmn_hans_cn/cmn_hans_cn_1533.flac` |
| mandarin_chinese-1537 | `audio/cmn_hans_cn/cmn_hans_cn_1537.flac` |
| mandarin_chinese-1566 | `audio/cmn_hans_cn/cmn_hans_cn_1566.flac` |
| mandarin_chinese-1587 | `audio/cmn_hans_cn/cmn_hans_cn_1587.flac` |
| mandarin_chinese-1608 | `audio/cmn_hans_cn/cmn_hans_cn_1608.flac` |
| mandarin_chinese-1632 | `audio/cmn_hans_cn/cmn_hans_cn_1632.flac` |
| mandarin_chinese-1635 | `audio/cmn_hans_cn/cmn_hans_cn_1635.flac` |
| mandarin_chinese-1651 | `audio/cmn_hans_cn/cmn_hans_cn_1651.flac` |
| punjabi-1533 | `audio/pa_in/pa_in_1533.flac` |
| punjabi-1537 | `audio/pa_in/pa_in_1537.flac` |
| punjabi-1566 | `audio/pa_in/pa_in_1566.flac` |
| punjabi-1587 | `audio/pa_in/pa_in_1587.flac` |
| punjabi-1608 | `audio/pa_in/pa_in_1608.flac` |
| punjabi-1632 | `audio/pa_in/pa_in_1632.flac` |
| punjabi-1635 | `audio/pa_in/pa_in_1635.flac` |
| punjabi-1651 | `audio/pa_in/pa_in_1651.flac` |
| urdu-1533 | `audio/ur_pk/ur_pk_1533.flac` |
| urdu-1537 | `audio/ur_pk/ur_pk_1537.flac` |
| urdu-1566 | `audio/ur_pk/ur_pk_1566.flac` |
| urdu-1587 | `audio/ur_pk/ur_pk_1587.flac` |
| urdu-1608 | `audio/ur_pk/ur_pk_1608.flac` |
| urdu-1632 | `audio/ur_pk/ur_pk_1632.flac` |
| urdu-1635 | `audio/ur_pk/ur_pk_1635.flac` |
| urdu-1651 | `audio/ur_pk/ur_pk_1651.flac` |

Frozen selection SHA-256: `59f8c23640f271eefa5787fdedd3833e0091af14e40e448e1f4c8a58584d886c`.

The ledger is 48 clips: six languages × eight common IDs, seed 2026, selected from
560 supplied metadata rows / 40 shared IDs. Local bytes must match the frozen
`data/processed/sampling_manifest.json`; the ledger is not a hash waiver.
`frontend/public/audio/FLEURS_ATTRIBUTION.txt` accompanies local/restored audio.
Audio remains Git-ignored; do not force-add media merely because it has a ledger row.

## TTS and privacy boundaries

No TTS asset is presently approved or listed for distribution. The preparation
flow stages output privately. Only the existing exact-hash listening/language
approval flow can enable a cache; this audit never updates approval flags.
Approved local playback and public distribution rights are separate checks.
No voice cloning, microphone recording, new request or billable generation is
part of T-019. Prompt captions are drafts until competent-language review.

Only prerecorded curated IDs reach the backend. Confirmation is a simulation;
referral contacts nobody. In-memory sessions expire/restart and contain selected
IDs/transcript/decisions, not resident records. No age, birthplace, speaker identity,
contact details or raw 311 records belong in public artifacts. Contract-permitted
FLEURS gender labels and references remain unchanged; they do not locate residents.
Raw provider responses/request logs, keys and account evidence remain private.
Secret rotation after the earlier key-shaped example incident is not verified by
this ticket; historical Git and remote exposure need the owner's separate review.

## Manual audit and future packaging

From repository root, after dependencies and frozen assets are restored:

```sh
backend/.venv/bin/python scripts/audit_publishable_assets.py --target local
backend/.venv/bin/python scripts/audit_publishable_assets.py --target public
```

Windows: substitute `backend/.venv/Scripts/python.exe`. These commands were
**not executed in this session**. They are read-only operational audits, not test
suites. Exit codes: 0 no findings for the requested target, 1 blocked findings,
2 incomplete audit/invalid inputs. Output contains paths/codes, file counts,
selection provenance and a per-clip inventory; matched secret values are omitted.
Keep reports in ignored `data/local/`, not in the public tree.

The command checks index blob bytes independently of current working files,
including nonignored untracked files. It also inspects `frontend/public` and
`frontend/dist`, including ignored audio; building Vite copies public files, so
`.gitignore` alone does not protect the bundle. Missing/stale builds or audio,
symlinks, unknown public assets and unapproved prompts block the audit. Only frozen
FLEURS media are eligible for index approval; generated TTS staged for distribution
requires a separate explicit review even if approved for local playback.

Before manually running a build/audit, use [the runbook](DEMO_RUNBOOK.md) to restore
assets from the supplied ZIP kept **outside the repository**, then rebuild with
`npm --prefix frontend run build`. Inspect the resulting inventory/findings and
review any discrepancy. The script does not build, copy, stage, delete or zip files.
Never upload the whole checkout, `data/`, `.env`, caches, raw ZIP or bulk datasets.
Review `git diff --cached --name-status` before committing; blank `.env.example`
configuration is permitted, populated credential files are not.

Public target deliberately blocks unresolved municipal terms and provider output
rights; resolve them with documented source/account evidence before changing the
policy. Review Git history/remotes and dependency notices separately: this bounded
heuristic checks the current index/worktree/public/dist, not all possible secrets,
PII, copyright, unreachable Git objects or legal compliance. Inspect output paths
before sharing reports, since filenames themselves can contain personal data.
Publishing, deployment and submission remain team-owned (D-021/D-024); this ticket
creates neither a release package nor a public service.
