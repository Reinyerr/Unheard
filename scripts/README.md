# Reproducible processing scripts

T-002 supplies the read-only source audit. Schema implementation, sampling and
public data exports belong to later tickets. No experiment results are generated.

From the repository root (Python 3.12, no additional runtime dependencies):

```powershell
backend/.venv/Scripts/python.exe scripts/audit_sources.py --source data/raw/Mississauga_Unheard_ElevenLabs_Track.zip
backend/.venv/Scripts/python.exe -m pytest scripts/tests -q
```

The script does not assume this ZIP exists. Alternatively set a shell environment
variable pointing to the ZIP or the **exact extracted pack directory**:

```powershell
$env:UNHEARD_DATA_ROOT="C:/your-local-source/Mississauga_Unheard_ElevenLabs_Track"
backend/.venv/Scripts/python.exe scripts/audit_sources.py
```

`--source` overrides the environment. The standard-library script does not load
`.env` automatically. No whole-archive extraction or copying audio is needed.
Leave the original archive where it is; never add it to Git.

The default output is ignored `data/processed/source_manifest.json`. Exit code 0
means the required source checks passed; 1 means failed. A failed attempt writes a
new **failed** report instead of leaving stale successful evidence at that path.
Optional `--output` must remain under this repository's `data/processed/` and end
in `.json`. Do not publish the local inventory. Errors name the source path.

The manifest contains archive and selected-file hashes, sizes, CSV headers/row
counts, coverage totals, metadata/audio reference checks, audio header formats,
FLEURS common-ID availability, license/attribution policies and Git ZIP checks.
No transcripts, speaker background or raw audio bytes are exported. FLEURS
audio is hashed individually. Other audio gets format-header checks only; raw
census/311/optional tables are inventory-only. Audio is not decoded for playback.
License review metadata is maintained in `source_licenses.json`; running the audit
does not refresh upstream websites or grant redistribution permission.

Tests generate explicitly synthetic CSV and header-only audio fixtures in temporary
directories. They do not require the real archive or network. The separate command
against the actual archive is the live local integration preflight. See
`docs/DATA_SOURCES.md` for the observed audit and unresolved provenance limits.
