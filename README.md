# UNHEARD

**Sheridan Datathon 2026 Winner · ElevenLabs Challenge**

UNHEARD is a voice accessibility research app that explores how multilingual
voice interfaces could better serve Mississauga residents. It maps gaps in
supplied speech evaluation datasets, compares real speech-to-text results, and
demonstrates how a voice interface can let someone correct a misunderstood
transcript before accepting it. The project gives municipal language-access and
service-design teams evidence for deciding which languages to evaluate and where
to recruit participants. It aligns with Sustainable Development Goal 10,
Reduced Inequalities.

**79,940 of 153,480 home-language speakers across 14 tracked non-official
language categories (52.1%)** were in eight categories with no labelled
spoken-request audio in the supplied MInDS-14 and Speech-MASSIVE subsets.
The 153,480 denominator covers the tracked categories. The coverage gap describes
what the supplied evaluation material contains. The app reports transcription
error separately, using a small speech pilot.

## What you can do in the app

| Step | What it shows |
| --- | --- |
| **Discover** | Explore corrected 2021 census data across Mississauga's 11 wards. Switch between speaker counts and share of the ward's census language base, select a ward to inspect its figures, or use the ward table. The initial map aggregates the eight coverage-gap categories. |
| **Investigate** | Select a prerecorded FLEURS sample. Listen with native audio controls and a waveform derived from the recording, then compare the reference transcript with saved ElevenLabs Scribe v2 output under automatic detection and language guidance. The lab shows raw transcripts, character error rates, paired differences, and explicit unavailable states. |
| **Demonstrate** | Review a transcript before accepting it. A rejection offers one retry with a different recording. If the retry fails, the flow suggests seeking human assistance through official channels. This simulation uses prerecorded speech and does not contact any service. |

Use **Next**, **Back**, or the numbered steps to navigate. Selections persist
across steps, and playback pauses when you leave the current step.

## Run locally

Run the commands from the repository root. The browser demo requires Node.js
**22.12 or newer** and npm. Use **Python 3.12** for the optional backend, audio
restoration, or data verification.

### 1. Start the browser demo

**Windows PowerShell**

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run dev
```

**macOS or Linux**

```sh
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open <http://127.0.0.1:5173>. The checked-in data powers the ward map,
transcript comparisons and **Browser-only saved results**
without FastAPI, an ElevenLabs key, or the original source pack. In
**Demonstrate**, select **Browser-only saved results** to use that path. Stop
Vite with Ctrl+C.

### 2. Restore audio playback if you have the source pack

A fresh clone includes references and saved results. The FLEURS FLAC files are
restored locally from the original Sheridan challenge pack ZIP or its exact
extracted directory. The restoration script checks the frozen selection,
references, and all 48 file hashes before installing the audio. It leaves the
research exports intact and makes no provider requests.

**Windows PowerShell**

```powershell
py -3.12 -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
backend/.venv/Scripts/python.exe scripts/restore_demo_assets.py --source 'C:/path/to/Mississauga_Unheard_ElevenLabs_Track.zip'
```

**macOS or Linux**

```sh
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python scripts/restore_demo_assets.py --source '/path/to/Mississauga_Unheard_ElevenLabs_Track.zip'
```

Replace the example path with your local source. If the source pack is
unavailable, you can still follow the walkthrough with saved transcripts and
results.

### 3. Start the optional FastAPI server

Use the Python environment from step 2. Keep Vite running and start FastAPI in
a second terminal. The defaults work without creating or copying an environment
file. For a key-free session, make sure no key is set in the shell,
`backend/.env`, or the repository-root `.env`.

**Windows PowerShell**

```powershell
backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

**macOS or Linux**

```sh
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Check [API health](http://127.0.0.1:8000/health) or open the
[interactive API docs](http://127.0.0.1:8000/docs). Choose **Local backend** in
**Demonstrate** to use the server. Backend saved mode requires matching local raw
response evidence, which is separate from the browser exports and audio
restoration. Use **Browser-only saved results** when that evidence is unavailable.

| Setting | Where it is read | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `frontend/.env` | Optional browser API URL. Defaults to `http://127.0.0.1:8000`. |
| `UNHEARD_CORS_ORIGINS` | Server environment | Comma-separated exact HTTP loopback origins. Defaults to localhost and 127.0.0.1 on port 5173. |
| `ELEVENLABS_API_KEY` | Server environment | Optional credential for explicitly selected live transcription, which may incur charges. Keep it out of browser configuration and version control. |
| `UNHEARD_DATA_ROOT` | Shell for data scripts that support it | Optional local source-pack path. An explicit `--source` is used in the commands above. |

FastAPI reads shell variables first, then `backend/.env`, then the root
`.env` for missing values. Restart the relevant server after editing its
configuration. The local recovery API keeps sessions in one worker's memory, so
restarting it clears those sessions. Live guided mode depends on verified
language guidance. The checked-in demo displays confirmation instructions as
text. Spoken instructions require separately approved cached prompt audio.
See the [backend guide](backend/README.md) for recovery endpoints and provider
configuration.

## Walk through the saved Urdu example

1. In **Discover**, choose **Urdu** and select **Ward 10**. Switch between
   speaker count and share. The corrected ward record shows **4,520** Urdu home
   speakers, or **6.12%** of its **73,830** census language base.
2. In **Investigate**, select sample **1533**. Read the reference and the
   automatic and guided transcripts. Both saved modes have **10.6% character
   error rate** on this recording. Play the source clip if audio is restored.
3. In **Demonstrate**, choose **Browser-only saved results**, **Automatic
   detection**, and sample **1533**. Start the simulation and choose **Correct**
   to accept the transcript. In a separate simulation, choose **Incorrect** and
   retry with sample **1537**. That clip has no saved result, so the app shows a
   referral after the second attempt.
4. Choose **Return to ward map** to see the citywide coverage figure and
   revisit your selected ward. The repository also includes research exports
   that rank coverage-gap languages by citywide home-speaker count.

## Data and methods

- **Census and coverage.** The map uses the supplied
  `ward_language_profile_2021_corrected.csv` and calculates ward shares with
  `population_language_base`.
  The eight coverage-gap categories are Urdu, Punjabi, Cantonese, Tagalog,
  Tamil, Hindi, Gujarati, and Bengali. The gap uses coverage counts from the
  supplied MInDS-14 and Speech-MASSIVE subsets. Their examples cover banking
  requests and assistant commands. Home-language counts provide demographic
  context and cannot establish an individual's English proficiency.
- **Speech sample.** The frozen FLEURS selection uses seed `2026` and eight
  common sentence IDs across English, Urdu, Punjabi, Cantonese, Arabic, and
  Mandarin Chinese, for 48 clips. The committed pilot records both modes for
  sentence ID 1533 in all six languages. Eleven of the twelve mode outcomes
  have scores, yielding five comparable pairs. Cantonese automatic output was
  excluded as incompatible. The other seven selected IDs per language have
  explicit untested outcomes in the saved export.
- **Scoring.** Character error rate (CER) is the number of character insertions,
  deletions, and substitutions needed to match the normalized reference,
  divided by the reference length. The project compares modes on the same
  clip by subtracting guided CER from automatic CER. A positive difference
  means fewer character errors with guidance on that clip. Word error rate
  uses English tokenization only. Missing, unsupported, failed, and
  incompatible outcomes remain separate from numeric scores.
- **Interpretation.** FLEURS is a read-speech dataset independent of the ward
  data. Ward rankings describe where future recruitment could focus, while
  the pilot describes transcription on specific recordings. The saved sample
  is too small to generalize the effect of language guidance. CER measures text
  differences and does not measure whether a municipal request was understood
  or resolved.

## Project structure

| Path | Role |
| --- | --- |
| [`frontend/`](frontend/) | React, TypeScript, and Vite interface with a Leaflet ward map, recording playback, and the browser-only simulation. |
| [`frontend/public/data/`](frontend/public/data/) | Versioned census, sample, experiment, and recommendation JSON, plus ward geometry. These files let the research views run independently of the API. |
| [`backend/`](backend/) | FastAPI health, capabilities, and recovery endpoints, with optional ElevenLabs Scribe v2 transcription for the frozen recordings. |
| [`scripts/`](scripts/) | Source audits, census and coverage exports, fixed-seed sampling, audio restoration, experiment execution, and metrics. |
| [`shared/`](shared/) | Canonical language mappings and confirmation prompt definitions. |
| [`docs/`](docs/) | Research sources, data contracts, architecture, and demo verification. |

## Build and verify

With frontend dependencies installed, run the following from the repository
root. On Windows PowerShell, use `npm.cmd` in place of `npm` and
`backend/.venv/Scripts/python.exe` in place of `backend/.venv/bin/python`.

```sh
npm --prefix frontend test
npm --prefix frontend run build
backend/.venv/bin/python -m pytest backend/tests scripts/tests -q
```

The production frontend build is written to `frontend/dist/`. To serve it
locally, stop the development server and run
`npm --prefix frontend run preview`.

To validate the checked-in exports against the source pack, run
`backend/.venv/bin/python scripts/validate_exports.py --source /path/to/Mississauga_Unheard_ElevenLabs_Track.zip`
with your local source path. For the full Playwright walkthrough, restore the
audio, install Chromium with `npm --prefix frontend exec -- playwright install chromium`,
then stop the manually started Vite server before running
`npm --prefix frontend run test:e2e`. The suite starts Vite itself. See the
[demo runbook](docs/DEMO_RUNBOOK.md) for backend and outage configurations and
the [scripts guide](scripts/README.md) for reproducing the data pipeline.

## Sources and attribution

The Mississauga challenge pack supplies the corrected census aggregates,
coverage metadata, and ward geography. The boundary snapshot carries source
and redistribution caveats. FLEURS is attributed to Google and Conneau et al.
(2022) under CC BY 4.0. MInDS-14 and Speech-MASSIVE contribute coverage counts.
See the [source inventory and usage terms](docs/DATA_SOURCES.md), the
[attributions](docs/attributions.md), and the
[FLEURS audio attribution](frontend/public/audio/FLEURS_ATTRIBUTION.txt).
