# Approved multilingual recovery instructions

Shared non-secret catalog: `shared/tts_prompts.json`. Six exact selected voices,
preferred model eleven_v3, language codes ur/pa/yue/ar/zh/en and authored draft
captions/labels. Configuration is not voice verification. All six currently
remain text-only: no real generated or approved audio is supplied.

Use the per-language opt-in command and manual approval in `backend/README.md`.
Each billed request requires a single selected language plus explicit
`--authorize-billable --rights-reviewed`. Generated files are staged locally as
pending_review, never copied here automatically. Approval requires listening,
review of caption/button meaning and pronunciation by a competent language
speaker, and the exact SHA-256 with `--language-reviewed`.

Approved layout: `{language_id}/manifest.json` and `{language_id}/confirm.mp3`,
where language_id is urdu, punjabi, cantonese, arabic, mandarin_chinese or english.
Manifest schema 2.0 binds exact voice/model/code/text/revision/path and hash,
real synthesis provenance, saved origin, rights review and manual listening /
language approval. Old schema-1.0 English manifests are rejected (none existed).
The instruction does not read the selected transcript or impersonate its speaker.
React checks provenance/hash and only offers audio during confirmation; errors,
unapproved/missing artifacts or configuration mismatch retain text-only fallback.
No synthesis occurs during demo use. MP3s remain Git-ignored, and T-019 audit is
required before public distribution. Do not fabricate manifests or provider data.
