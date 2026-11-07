# AGENTS.md — UNHEARD coding-agent operating rules

## Mandatory context order

Before implementing a ticket, read:
1. `docs/DECISIONS.md` (especially amended D-021, D-024, D-025)
2. `docs/REQUIREMENTS.md` and `docs/ARCHITECTURE.md`
3. `docs/DATA_CONTRACTS.md` and `docs/DATA_SOURCES.md`
4. `docs/tickets/INDEX.md` and the **one selected** `T-XXX-*.md` ticket
5. `docs/TEST_PLAN.md` if the ticket adds logic or changes data

## Implementation protocol

1. Work **one ready ticket** at a time; confirm prerequisites exist before coding. Do not skip blocked prerequisites by inventing data or API responses.
2. State intended files and contract impact; keep changes limited to the selected ticket. Prefer small functions, typed interfaces, pure calculations, and explicit errors.
3. Treat every `Implementation sketch` in a ticket as **illustrative pseudocode**, not as proven library syntax. Verify against the installed dependencies, actual dataset headers, and real API responses.
4. Follow accepted decisions; if implementation contradicts one, report the conflict and propose a decision-record amendment before changing scope.
5. Write tests for the listed acceptance criteria; mock external services in unit tests; retain at least one separate live integration preflight.
6. Include input provenance and dataset sample counts in outputs; never display invented metrics or replace missing outcomes with zero.
7. Run required checks and report actual pass/fail evidence. Do not mark a ticket `Done` merely because code was written.
8. Update `docs/tickets/INDEX.md` status/dependencies and document meaningful schema or scope changes in `docs/DECISIONS.md`.
9. Do not add app features, auth, databases, agents, new ML models, public hosting, or additional sponsor integrations without an explicit ticket or scope approval.

## Security and privacy

- Never commit API keys, `.env`, user recordings, personal information, or third-party datasets in bulk. Keep ElevenLabs keys on the FastAPI server.
- Do not send unconsented live microphone recordings; microphone capture is a stretch goal, not MVP.
- Restrict filenames to known dataset entries; do not accept arbitrary user-provided filesystem paths. Validate upload type/size and prevent path traversal if live input is later added.
- Honor `docs/DATA_SOURCES.md` and upstream licenses when placing audio in `frontend/public/audio`.

## Data-science red lines

- Verified numerator: the **eight** no-task-audio languages, **79,940** home-language speakers in the supplied categories; denominator **153,480 across 14 tracked non-official categories**, not city population.
- Use `01_people_census/derived/ward_language_profile_2021_corrected.csv` and `population_language_base` for ward percentages.
- Keep geography and external speech experiments independent; never imply geographic recognition rates.
- Evaluate **English, Urdu, Punjabi, Cantonese, Arabic, Mandarin Chinese** using **8 common FLEURS IDs per language, seed `2026`**, each under automatic and supported guided settings.
- Store failures explicitly. `not_tested`, `unsupported`, `technical_error`, and `incompatible_output` are not numeric CER values.
- CER is the primary exploratory metric; compute per-clip paired differences, retain raw outputs, flag script issues, and avoid unsupported significance claims.

## Definition of done

- Acceptance criteria satisfied on real data/verified fixtures.
- Tests pass and manual proof recorded when appropriate.
- Relevant docs/contracts updated.
- No regression in the Urdu end-to-end demo; cached mode still works if ElevenLabs is unavailable.
- Ticket status accurately reflects current reality.

## Handoff format when completing a ticket

```text
Ticket: T-XXX
Implemented files:
Contract changes:
Tests run and observed results:
Known limitations:
How to manually verify:
Ready/blocked next tickets:
```
