# UNHEARD — Documentation-first implementation kit

**Sheridan Datathon 2026 · ElevenLabs challenge · two-person team · planning baseline 2026-11-07**

> **Status:** T-001 bootstrap and T-002 source audit implemented and verified. The local React shell, FastAPI health service and read-only source audit work; research modules, export pipelines and ElevenLabs experiments remain pending. Do not present sample responses or hypothetical results as real experiments.

## Mission

UNHEARD is an evidence-based voice accessibility investigation for **municipal language-accessibility and service-design teams**. It identifies underrepresented *task-oriented audio evaluation* languages, tests speech-to-text using authentic FLEURS recordings, and explains where further multilingual service testing should be prioritized. It is **not** a replacement for Mississauga 311.

**Confirmed insight:** The supplied `language_coverage.csv` has **8** non-official home-language categories with **no labelled spoken-request recordings in the supplied MInDS-14 or Speech-MASSIVE sets**, totalling **79,940** Mississauga residents who report those languages spoken most often at home. That is approximately **52.1% of the 153,480 speakers across the 14 tracked non-official categories**, **not** 52.1% of Mississauga, a voice-AI error rate, or a count of people unable to speak English.

## Getting started

1. Read [AGENTS.md](AGENTS.md), [requirements](docs/REQUIREMENTS.md), [decisions](docs/DECISIONS.md), [architecture](docs/ARCHITECTURE.md), and [contracts](docs/DATA_CONTRACTS.md).
2. Follow [ROADMAP.md](docs/ROADMAP.md) and [tickets/INDEX.md](docs/tickets/INDEX.md). T-001 and T-002 are verified; T-003 is next, with later work gated by its dependencies.
3. Do the data/API preflight before assuming any ElevenLabs language-guidance support. Speech endpoints, experiment outputs, and geographic polygons remain **unverified or unimplemented**.
4. Keep original dataset archives **outside the public repository**. Refer to [DATA_SOURCES.md](docs/DATA_SOURCES.md) for paths, source corrections, and licensing. Do not upload the 468 MB supplied data ZIP or raw audio indiscriminately.
5. Use [TEST_PLAN.md](docs/TEST_PLAN.md) to verify implementation and [DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) for the local judging flow.

## System at a glance

- **Frontend:** React + Vite + TypeScript (recommended implementation convention) + Tailwind; Leaflet or MapLibre as one selected map stack; charts via one chosen library.
- **Backend:** Python + FastAPI for *local* Scribe/TTS integration and confirmation/retry state machine.
- **Research:** Python scripts generating validated, reproducible **static JSON** for map and experiments; no database/authentication required for MVP.
- **Deployment:** **Localhost for this hackathon**. Cloudflare Pages for the static frontend *after the hackathon* is a future plan, not a current dependency. A future public FastAPI endpoint needs separate hosting and security controls.
- **Ownership:** Developer 1 owns data / experiment / backend; Developer 2 owns frontend / visualization; both review integration, test results, and demo. ChatGPT can draft code and debugging guidance, but **your team executes and verifies it**. Your team handles Devpost, GitHub publication, judging materials, and submissions independently.

## Key documents

| Document | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Coding-agent guardrails and ticket workflow |
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | Scope, measurable behaviour, non-goals |
| [DECISIONS.md](docs/DECISIONS.md) | Full 25-question decision record, including amendments |
| [ROADMAP.md](docs/ROADMAP.md) | Dependency-aware implementation phases and stop rules |
| [IMPLEMENTATION_PLAYBOOK.md](docs/IMPLEMENTATION_PLAYBOOK.md) | Coding-agent prompts and per-ticket workflow |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Data flows, component boundaries, failure modes |
| [DATA_CONTRACTS.md](docs/DATA_CONTRACTS.md) | Proposed versioned data/API schemas with examples |
| [TEST_PLAN.md](docs/TEST_PLAN.md) | Priority tests and go/no-go checks |
| [DATA_SOURCES.md](docs/DATA_SOURCES.md) | Verified pack inventory, limitations, attribution |
| [RISK_REGISTER.md](docs/RISK_REGISTER.md) | Top risks and mitigations |
| [DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) | Four-act localhost demonstration and fallback |
| [tickets/INDEX.md](docs/tickets/INDEX.md) | Full task tracker, dependencies, status conventions |

## Project folder conventions

```text
UNHEARD/
├── AGENTS.md
├── README.md
├── docs/
│   ├── REQUIREMENTS.md
│   ├── DECISIONS.md
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   ├── DATA_CONTRACTS.md
│   ├── TEST_PLAN.md
│   ├── IMPLEMENTATION_PLAYBOOK.md
│   ├── DATA_SOURCES.md
│   ├── RISK_REGISTER.md
│   ├── DEMO_RUNBOOK.md
│   └── tickets/
│       ├── INDEX.md
│       ├── TEMPLATE.md
│       └── T-001-*.md ... T-020-*.md
├── frontend/                  # Created by T-001
├── backend/                   # Created by T-001
├── scripts/                   # Created by T-001
└── data/                      # Ignored local data; generated safe JSON in frontend/public/data
```

## Important limitations

Do not infer individual residents' English proficiency from home language; assign a FLEURS speaker to a Mississauga ward; equate missing audio in supplied packs with a model's inability to recognize a language; equate CER with intent accuracy; or imply the demo is a real 311 integration. Maintain a distinction between **planned**, **tested**, and **verified** findings.

## Windows / VS Code setup (T-001)

Install Node.js 24 LTS and Python 3.12, then open this repository in VS Code.
Use PowerShell terminals at the repository root. Commands use `npm.cmd` and the
virtual environment executable directly, so changing PowerShell execution policy
or activating a virtual environment is unnecessary.

```powershell
py -3.12 -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend ci
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env
New-Item -ItemType Directory -Force data
```

Copy environment examples only on first setup; preserve existing local values.
If `py` reports no installed Python, install Python 3.12 and reopen the terminal.
In VS Code, select `backend/.venv/Scripts/python.exe` as the Python interpreter.

Terminal 1, from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, from the repository root:

```powershell
npm.cmd --prefix frontend run dev
```

Open <http://127.0.0.1:5173>. Health is at <http://127.0.0.1:8000/health> and returns
`{"status":"ok","mode":"local"}`. Both servers bind only to loopback. Vite fails
explicitly if port 5173 is occupied instead of silently selecting a port that CORS
does not allow. Stop each server with Ctrl+C.

The backend loads root `.env`; `UNHEARD_CORS_ORIGINS` is a comma-separated list of
exact HTTP localhost/127.0.0.1 origins with ports. The frontend loads
`frontend/.env`; `VITE_API_BASE_URL` defaults to `http://127.0.0.1:8000`. Restart
the relevant server after environment edits. Never place secrets in `VITE_`
variables: they are public browser configuration. `ELEVENLABS_API_KEY` and
`UNHEARD_DATA_ROOT` are not needed by the health service and may remain empty.

No key or source archive is needed for bootstrap. Keep the original archive
outside the repository; `data/` is ignored local scratch storage. Only reviewed,
generated JSON belongs in `frontend/public/data/`, currently an empty directory.
Raw audio, source tables, archives, credentials, environments, and caches are
ignored. License review is required before deliberately adding any audio later.

## Tests and local integration preflight

For the T-002 source audit (no extraction, speech API requests or public exports):

```powershell
backend/.venv/Scripts/python.exe scripts/audit_sources.py --source data/raw/Mississauga_Unheard_ElevenLabs_Track.zip
backend/.venv/Scripts/python.exe -m pytest scripts/tests -q
```

Supply the actual local ZIP path or exact extracted pack root; a clone does not
include the archive. See [audit instructions](scripts/README.md) and
[observed source audit](docs/DATA_SOURCES.md). The generated
`data/processed/source_manifest.json` stays ignored and records failure explicitly
when required files or values are missing.

```powershell
Push-Location backend
.venv/Scripts/python.exe -m pytest -q
Pop-Location
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
```

Backend tests verify the health contract, startup without a key and exact CORS
configuration. Frontend unit tests use explicitly mocked health responses for
success, unavailable service, retry, bad responses and timeout. Dependencies are
pinned in `backend/requirements.txt` and `frontend/package-lock.json`.

For the separate real browser preflight, install Chromium once:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright"
frontend/node_modules/.bin/playwright.cmd install chromium
```

Leave FastAPI running, stop any manually started Vite instance, then run:

```powershell
Remove-Item Env:EXPECT_BACKEND -ErrorAction SilentlyContinue
npm.cmd --prefix frontend run test:e2e
```

Playwright starts and stops Vite itself. Stop FastAPI, then verify actual outage:

```powershell
$env:EXPECT_BACKEND="offline"
npm.cmd --prefix frontend run test:e2e
Remove-Item Env:EXPECT_BACKEND
```

Both runs check desktop/mobile layouts, health status, module navigation, no
horizontal overflow and no JavaScript page errors. Screenshots are saved in
ignored `frontend/test-results/`. For manual verification, stop FastAPI, press
**Retry connection**, and confirm the actionable unavailable message while the
shell remains usable; restart FastAPI and retry to reconnect. Research remains
explicitly pending in both modes. The full Urdu/cached-results demo is a later
ticket and cannot yet be rehearsed.

If npm cannot write its default cache in a restricted workspace, set
`$env:npm_config_cache="$PWD/.cache/npm"` before installing from the repository root.
