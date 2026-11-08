"""Small live preflight; defaults to Urdu/Cantonese auto + guided (4 POSTs).

Reads ELEVENLABS_API_KEY from server environment; never accepts a key on the CLI.
No tests, batch runner, automatic retries or experimental metrics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

from sample_fleurs import atomic_write

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "backend"))
from app.services.elevenlabs_adapter import (
    ConfigurationError, ElevenLabsAdapter, GUIDANCE_CANDIDATES, MODEL_ID, load_selection, now,
)

LOG = REPO / "data/local/preflight_log.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--languages", nargs="+", choices=sorted(GUIDANCE_CANDIDATES),
                        default=["urdu", "cantonese"], help="One frozen clip per language, both modes")
    args = parser.parse_args()
    languages = list(dict.fromkeys(args.languages))
    run_id = uuid.uuid4().hex
    run_dir = REPO / "data/local/preflight_runs" / run_id
    report = {
        "schema_version": "1.0", "run_id": run_id, "started_at_utc": now(),
        "status": "running", "model_id": MODEL_ID, "api_version": "v1",
        "selection_sha256": None, "selected_sample_ids": [], "planned_post_count": 2 * len(languages),
        "attempts": [], "guidance_by_language": {key: "not_tested" for key in GUIDANCE_CANDIDATES},
        "subscription_before": None, "subscription_after": None,
        "docs": ["https://elevenlabs.io/docs/api-reference/speech-to-text/convert",
                 "https://elevenlabs.io/docs/overview/capabilities/speech-to-text/",
                 "https://elevenlabs.io/docs/api-reference/user/subscription/get"],
        "limitations": "HTTP acceptance is not output/script quality or verified improvement; T-010 review required. Allowance snapshots do not establish affordability of 96 requests.",
    }

    def save() -> None:
        raw = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
        atomic_write(run_dir / "report.json", raw)
        atomic_write(LOG, raw)

    adapter = None
    try:
        save()  # Replace stale success before checking configuration or making requests.
        samples, _, digest = load_selection()
        first_id = samples.selection.ids[0]
        selected = [f"{language}-{first_id}" for language in languages]
        report.update(selection_sha256=digest, selected_sample_ids=selected,
                      adapter_sha256=hashlib.sha256((REPO / "backend/app/services/elevenlabs_adapter.py").read_bytes()).hexdigest())
        adapter = ElevenLabsAdapter()
        # Validate all planned local assets before any remote request.
        for sample_id in selected:
            adapter.validate_sample(sample_id)
        report["subscription_before"] = adapter.subscription_snapshot()
        save()
        for sample_id in selected:
            for mode in ("auto", "guided"):
                attempt = adapter.transcribe(sample_id, mode)
                entry = attempt.to_dict()
                raw = entry.pop("raw_response")
                if raw is not None:
                    raw_path = run_dir / f"{sample_id}-{mode}.response.txt"
                    atomic_write(raw_path, raw.encode("utf-8"))
                    entry["raw_response_path"] = str(raw_path.relative_to(REPO))
                else:
                    entry["raw_response_path"] = None
                report["attempts"].append(entry)
                if mode == "guided":
                    report["guidance_by_language"][attempt.language_id] = attempt.guidance_acceptance
                save()
                print(f"{sample_id} {mode}: {attempt.status} (HTTP {attempt.http_status}, {attempt.error_code})")
                if attempt.http_status in {401, 403, 429} or (attempt.error_code and any(
                        word in attempt.error_code for word in ("quota", "credit", "invalid_api_key"))):
                    raise ConfigurationError("Preflight stopped on credentials, permissions, rate or quota failure; remaining modes are not tested")
        report["subscription_after"] = adapter.subscription_snapshot()
        auto_ok = any(a["mode"] == "auto" and a["status"] == "completed" for a in report["attempts"])
        guidance_evidenced = all(report["guidance_by_language"][key] in {
            "accepted_by_api", "rejected_by_api"} for key in languages)
        # Incompatible response shapes remain incomplete even when the parameter was accepted.
        usable = all(a["status"] in {"completed", "unsupported"} for a in report["attempts"])
        report["status"] = "recorded" if auto_ok and guidance_evidenced and usable else "incomplete"
    except (OSError, ValueError, KeyError) as exc:
        report.update(status="blocked", error_code=(exc.code if isinstance(exc, ConfigurationError)
                                                    else "configuration_or_preflight_error"))
        # Do not serialize exception text: transport errors may contain credentials.
        print("Preflight blocked: check server key, frozen manifest/audio, and logged statuses.", file=sys.stderr)
        if isinstance(exc, ConfigurationError):
            # ConfigurationError messages are authored locally and contain no user secret.
            print(str(exc), file=sys.stderr)
    finally:
        if adapter is not None:
            adapter.close()
        report["finished_at_utc"] = now()
        save()
    print(f"Preflight {report['status']}; local evidence: {LOG}")
    return 0 if report["status"] == "recorded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
