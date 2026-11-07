# UNHEARD — Documentation-first implementation kit

**Sheridan Datathon 2026 · ElevenLabs challenge · two-person team · planning baseline 2026-11-07**

> **Status:** Approved design, **not yet implemented**. This package contains *specifications, implementation hints, example code snippets, tickets, and testing instructions*—not a functioning app or completed ElevenLabs study. Do not present sample responses or hypothetical results as real experiments.

## Mission

UNHEARD is an evidence-based voice accessibility investigation for **municipal language-accessibility and service-design teams**. It identifies underrepresented *task-oriented audio evaluation* languages, tests speech-to-text using authentic FLEURS recordings, and explains where further multilingual service testing should be prioritized. It is **not** a replacement for Mississauga 311.

**Confirmed insight:** The supplied `language_coverage.csv` has **8** non-official home-language categories with **no labelled spoken-request recordings in the supplied MInDS-14 or Speech-MASSIVE sets**, totalling **79,940** Mississauga residents who report those languages spoken most often at home. That is approximately **52.1% of the 153,480 speakers across the 14 tracked non-official categories**, **not** 52.1% of Mississauga, a voice-AI error rate, or a count of people unable to speak English.

## Getting started

1. Read [AGENTS.md](AGENTS.md), [requirements](docs/REQUIREMENTS.md), [decisions](docs/DECISIONS.md), [architecture](docs/ARCHITECTURE.md), and [contracts](docs/DATA_CONTRACTS.md).
2. Follow [ROADMAP.md](docs/ROADMAP.md) and [tickets/INDEX.md](docs/tickets/INDEX.md). Start with `T-001`, then unblock dependencies as indicated.
3. Do the data/API preflight before assuming any ElevenLabs language-guidance support. The backend, experiment outputs, and geographic polygons are **unverified or unimplemented** as of this package.
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

## Project folder conventions (target; not generated application code)

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
