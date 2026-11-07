# Implementation playbook — working with a coding agent ticket by ticket

**Do not code from the entire project specification at once.** Begin with one unblocked ticket and its dependencies. Work on the user's own repository; this ZIP deliberately does not include source audio, keys or a working app.

## Setup expectations

1. Extract this ZIP into the repository root so `AGENTS.md` is at the top level.
2. Keep the supplied 468 MB challenge archive locally, **outside the public Git repository**; configure an absolute local archive path or extracted source root (e.g. a documented environment variable `UNHEARD_DATA_ROOT`) during T-001/T-002. No assumption that the ZIP is automatically available to another machine.
3. Do not paste or commit an ElevenLabs API key. Use `.env` locally and `.env.example` with placeholder values.
4. Read `docs/DECISIONS.md` first to avoid reverting amendments. The team has chosen **localhost now, Cloudflare later**; the team itself handles submissions.
5. Keep `docs/tickets/INDEX.md` current with the actual state. All tickets start TODO.

## Prompt to start T-001

> Read `AGENTS.md`, `docs/DECISIONS.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md`, and `docs/tickets/T-001-project-bootstrap.md`. Implement only T-001. Explain the file changes, why they are needed, and how to verify them locally. Do not invent dataset outputs or run paid API calls. After implementation, run the ticket's tests and report actual results. Update the ticket tracker only if the acceptance criteria are genuinely satisfied.

## Reusable prompt for any later ticket

> Implement ticket T-XXX from `docs/tickets/`. First read `AGENTS.md`, its dependencies, the relevant contracts, and the accepted decisions. State prerequisites and target files, then produce implementation code, minimal tests, and precise run instructions. Keep actual data separate from fixtures. When done, report observed tests, failures, contract changes, and the next ready tickets. Do not work on an unrelated feature.

## Suggested two-person workflow

- Dev 1: backend/AI/data pipeline branch; Dev 2: frontend/geographic branch. Share schemas before working in parallel.
- A pull request should reference its ticket ID (e.g. `T-004`) and show actual test evidence.
- No late giant merge: first make one real Urdu example work end to end; then expand samples and polish.
- Update a ticket to `Blocked` when evidence (e.g. missing polygons, unsupported Scribe hint) prevents completion; use specified fallback and leave an audit trail.

## Mandatory review before a ticket is done

- [ ] Real source/API inputs verified, or explicit mocked fixtures labelled as fixtures.
- [ ] Critical edge cases implemented; no missing data shown as 0%.
- [ ] Unit/integration tests run and observed outputs recorded.
- [ ] No keys, raw ZIP, unapproved audio, or unnecessary speaker identifiers added to Git.
- [ ] Documentation contract updated if needed; dependent tickets remain consistent.
- [ ] Core demo still runs on localhost in normal and saved-results mode.

## Why code snippets are present in tickets

Snippets communicate **intent and expected logic**, not complete implementations. Actual library APIs, dataset fields and model language-hint support require validation at coding time. Prefer writing straightforward code that meets the acceptance tests over blindly reproducing snippets.
