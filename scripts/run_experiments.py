"""Resume the frozen paired pilot; default is offline import/cache/report only.

Use --live for pending auto and already-verified guided requests. No new sampling,
silent guided fallback, automatic replay of interrupted calls, or secrets on CLI.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import math
import os
from pathlib import Path
import time
import uuid

from sample_fleurs import atomic_write, canonical
from calculate_metrics import evaluate, export_metrics
from app.services.elevenlabs_adapter import (
    API, MODEL_ID, ConfigurationError, ElevenLabsAdapter, load_selection, now, request_options,
    REPO,
)
from app.schemas.research import ExperimentStatus

CACHE = REPO / "data/local/experiment_cache"
RAW = REPO / "data/local/raw_scribe_responses"
OUTPUT = REPO / "data/processed/experiment_attempts.json"
LOCK = REPO / "data/local/experiment_run.lock"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def local_json(path: Path) -> tuple[dict, bytes]:
    path = path.resolve()
    if not any(path.is_relative_to(REPO / folder) for folder in ("data/local", "data/processed")):
        raise ValueError("Input evidence must remain under data/local or data/processed")
    raw = path.read_bytes()
    return json.loads(raw), raw


def cache_identity(sample, asset: dict, mode: str) -> dict:
    return {"audio_sha256": asset["sha256"], "endpoint": API + "/speech-to-text",
            "model_id": MODEL_ID, "request_options": request_options(sample.language_id, mode)}


def cache_key(identity: dict) -> str:
    return sha(canonical(identity))


def check_raw(attempt: dict) -> None:
    relative = attempt.get("raw_response_path")
    if relative is None:
        if attempt["status"] == "completed" or attempt.get("provider_status") == "completed":
            raise ValueError("Completed provider result requires retained raw response")
        return
    path = (REPO / relative).resolve()
    if not path.is_relative_to(REPO / "data/local"):
        raise ValueError("Raw response path escapes local evidence")
    raw = path.read_bytes()
    if attempt.get("raw_response_sha256") and sha(raw) != attempt["raw_response_sha256"]:
        raise ValueError("Raw response checksum mismatch; cache cannot be reused")
    if attempt.get("provider_status", attempt["status"]) == "completed":
        if json.loads(raw).get("text") != attempt["transcript_raw"]:
            raise ValueError("Cached transcript disagrees with raw response")


def read_cache(identity: dict) -> dict:
    key = cache_key(identity)
    path = CACHE / f"{key}.json"
    if not path.exists():
        return {"schema_version": "1.0", "identity": identity, "history": [], "in_flight": None}
    record, _ = local_json(path)
    if record.get("identity") != identity:
        raise ValueError("Cache identity mismatch")
    # Verify immutable attempt records and raw evidence before using any success.
    for link in record["history"]:
        attempt, raw = local_json(REPO / link["path"])
        if sha(raw) != link["sha256"] or attempt["cache_key"] != key:
            raise ValueError("Cached attempt evidence checksum mismatch")
        if (attempt["audio_sha256"] != identity["audio_sha256"]
                or attempt["request_options"] != identity["request_options"]
                or attempt["model_id"] != identity["model_id"]):
            raise ValueError("Cached attempt settings mismatch")
        check_raw(attempt)
    return record


def save_cache(record: dict) -> None:
    atomic_write(CACHE / f"{cache_key(record['identity'])}.json", canonical(record) + b"\n")


def terminal(record: dict) -> dict | None:
    if record["in_flight"]:
        raise ConfigurationError("Unresolved in-flight request; inspect cache and provider evidence before clearing it",
                                 "unresolved_in_flight")
    return local_json(REPO / record["history"][-1]["path"])[0] if record["history"] else None


def store(record: dict, attempt: dict, sample, flags: list[str], origin: str) -> dict:
    attempt = dict(attempt)
    attempt["provider_status"] = attempt.get("provider_status", attempt["status"])
    check_raw(attempt)
    outcome, details = evaluate(sample, attempt, flags)
    attempt.update(status=outcome.status.value, review_flags=details["flags"],
                   origin=origin, cache_key=cache_key(record["identity"]))
    # Raw responses are saved separately; terminal attempt envelopes are immutable.
    path = RAW / attempt["cache_key"] / f"{uuid.uuid4().hex}.attempt.json"
    raw = canonical(attempt) + b"\n"
    atomic_write(path, raw)
    record["history"].append({"path": str(path.relative_to(REPO)), "sha256": sha(raw)})
    record["in_flight"] = None
    save_cache(record)
    return attempt


def import_preflight(path: Path, samples, assets: dict, selection_sha: str) -> dict:
    report, report_raw = local_json(path)
    if report.get("selection_sha256") != selection_sha or report.get("model_id") != MODEL_ID:
        raise ValueError("Preflight model/selection disagrees with frozen pilot")
    by_id = {sample.sample_id: sample for sample in samples.samples}
    reviews = {}
    for finding in report.get("response_review", {}).get("findings", []):
        if finding.get("comparability_status") == "incompatible_output":
            for mode in finding.get("modes", [finding.get("mode")]):
                reviews.setdefault((finding["sample_id"], mode), []).append("recorded_manual_script_review_exclusion")
    imported = 0
    for attempt in report["attempts"]:
        sample = by_id.get(attempt["sample_id"])
        mode = attempt["mode"]
        if sample is None or mode not in {"auto", "guided"}:
            raise ValueError("Preflight contains an unknown sample/mode")
        identity = cache_identity(sample, assets[sample.sample_id], mode)
        if (attempt["language_id"] != sample.language_id or attempt["model_id"] != MODEL_ID
                or attempt["audio_sha256"] != identity["audio_sha256"]):
            raise ValueError("Preflight sample/audio identity mismatch")
        # Different settings must never seed a cache for the current experiment.
        if attempt["request_options"] != identity["request_options"]:
            raise ValueError("Preflight options differ from current adapter configuration")
        ExperimentStatus(attempt["status"])
        if attempt["status"] == "completed" and not (200 <= (attempt.get("http_status") or 0) < 300):
            raise ValueError("Preflight completion lacks HTTP evidence")
        check_raw(attempt)
        record = read_cache(identity)
        existing = terminal(record)
        if existing is None or (existing["status"] == "technical_error"
                                and attempt["status"] in {"completed", "incompatible_output", "unsupported"}):
            copy = dict(attempt)
            if copy.get("raw_response_path"):
                response = (REPO / copy["raw_response_path"]).read_bytes()
                response_path = RAW / cache_key(identity) / f"{uuid.uuid4().hex}.response.txt"
                atomic_write(response_path, response)
                copy.update(raw_response_path=str(response_path.relative_to(REPO)), raw_response_sha256=sha(response))
            store(record, copy, sample, reviews.get((sample.sample_id, mode), []), "preflight")
            imported += 1
        elif reviews.get((sample.sample_id, mode)) and not set(reviews[sample.sample_id, mode]) <= set(existing.get("review_flags", [])):
            # A subsequent manual exclusion changes comparability, never re-buys audio.
            store(record, existing, sample, reviews[sample.sample_id, mode], "preflight_review")
    return {"path": str(path.resolve().relative_to(REPO)), "sha256": sha(report_raw), "imported": imported}


def retry_delay(attempt: dict, retry_index: int) -> float:
    value = attempt.get("response_headers", {}).get("retry-after")
    if value:
        try:
            delay = float(value)
            return max(delay, 0) if math.isfinite(delay) else 31
        except ValueError:
            try:
                return max((parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds(), 0)
            except (ValueError, TypeError, OverflowError):
                return 31  # Unknown provider delay: pause instead of retrying too soon.
    return float(2 ** retry_index)


def fatal(attempt: dict) -> bool:
    code = (attempt.get("error_code") or "").lower()
    return attempt.get("http_status") in {401, 402, 403} or any(word in code for word in ("quota", "credit", "invalid_api_key"))


def run(args) -> dict:
    samples, assets, selection_sha = load_selection()
    run_id = uuid.uuid4().hex
    report = {"schema_version": "1.0", "run_id": run_id, "started_at_utc": now(), "status": "running",
              "model_id": MODEL_ID, "api_version": "v1", "selection_sha256": selection_sha,
              "source": {"runner_sha256": sha(Path(__file__).read_bytes()),
                         "adapter_sha256": sha((REPO / "backend/app/services/elevenlabs_adapter.py").read_bytes()),
                         "selected_samples": 48, "planned_modes": 96,
                         "limits": "Exploratory frozen pilot; no geographic inference. Model alias does not pin provider weights.",
                         "retry_policy": f"At most {args.max_attempts} sends per pending mode per invocation; explicit --retry-failed for previous transient failures"},
              "imports": [], "attempts": [], "mode_states": [], "events": [], "remote_request_count": 0,
              "run_config": {"live": args.live, "languages": args.languages,
                             "max_attempts": args.max_attempts, "max_requests": args.max_requests,
                             "retry_failed": args.retry_failed},
              "guidance_by_language": {}, "summary_by_language": {}}
    adapter = None
    stop_reason = None
    selected_languages = set(args.languages) if args.languages else {s.language_id.value for s in samples.samples}

    def refresh() -> None:
        report["attempts"], report["mode_states"] = [], []
        guidance = {language: "not_tested" for language in {s.language_id.value for s in samples.samples}}
        for sample in samples.samples:
            for mode in ("auto", "guided"):
                record = read_cache(cache_identity(sample, assets[sample.sample_id], mode))
                if record["in_flight"]:
                    attempt = None
                    status, reason = "technical_error", "unresolved_in_flight"
                else:
                    attempt = terminal(record)
                    status = attempt["status"] if attempt else "not_tested"
                    reason = attempt.get("error_code") if attempt else "no_recorded_request"
                if attempt:
                    if attempt["sample_id"] != sample.sample_id:
                        raise ValueError("Identical audio cache belongs to another sample; review identity before use")
                    report["attempts"].append(attempt)
                    if mode == "guided":
                        evidence = attempt.get("guidance_acceptance", "not_tested")
                        if evidence == "rejected_by_api" or guidance[sample.language_id] == "not_tested":
                            guidance[sample.language_id] = evidence
                report["mode_states"].append({"sample_id": sample.sample_id, "language_id": sample.language_id.value,
                                               "mode": mode, "status": status, "reason": reason,
                                               "in_flight": bool(record["in_flight"])})
        report["guidance_by_language"] = guidance
        report["summary_by_language"] = {}
        for language in sorted(guidance):
            states = [state for state in report["mode_states"] if state["language_id"] == language]
            observed = [a for a in report["attempts"] if a["language_id"] == language]
            counts = Counter(state["status"] for state in states)
            report["summary_by_language"][language] = {
                "n_selected": 8, "n_planned_modes": 16,
                "n_attempted_modes": len(observed), "n_provider_completed": sum(a.get("provider_status") == "completed" for a in observed),
                "n_unresolved_in_flight": sum(state["in_flight"] for state in states),
                "n_completed": counts["completed"], "n_failed": sum(counts[s] for s in ("technical_error", "unsupported", "incompatible_output")),
                "n_not_tested": counts["not_tested"], "status_counts": dict(counts)}

    def save() -> None:
        refresh()
        raw = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
        atomic_write(REPO / f"data/processed/experiment_runs/{run_id}.json", raw)
        atomic_write(OUTPUT, raw)

    try:
        for path in args.preflight or [REPO / "data/local/preflight_log.json"]:
            report["imports"].append(import_preflight(path, samples, assets, selection_sha))
        save()
        for sample in samples.samples:
            if sample.language_id not in selected_languages:
                continue
            for mode in ("auto", "guided"):
                identity = cache_identity(sample, assets[sample.sample_id], mode)
                record = read_cache(identity)
                previous = terminal(record)
                if previous and (previous["status"] != "technical_error"
                                 or not args.retry_failed or not previous.get("retryable")):
                    report["events"].append({"sample_id": sample.sample_id, "mode": mode, "action": "cache_reused"})
                    continue
                if not args.live:
                    continue
                guidance = report["guidance_by_language"][sample.language_id]
                if mode == "guided" and guidance != "accepted_by_api":
                    report["events"].append({"sample_id": sample.sample_id, "mode": mode,
                                             "action": "skipped_guidance", "evidence": guidance})
                    continue
                if adapter is None:
                    adapter = ElevenLabsAdapter()
                    for candidate in samples.samples:
                        if candidate.language_id in selected_languages:
                            adapter.validate_sample(candidate.sample_id)
                for index in range(args.max_attempts):
                    if args.max_requests is not None and report["remote_request_count"] >= args.max_requests:
                        stop_reason = "request_budget_reached"
                        break
                    if previous and previous.get("retryable"):
                        delay = retry_delay(previous, index)
                        if delay > 30:
                            stop_reason = "provider_retry_after_requires_later_resume"
                            break
                        report["events"].append({"sample_id": sample.sample_id, "mode": mode,
                                                 "action": "backoff", "seconds": delay})
                        save()
                        time.sleep(delay)
                    # Persist intent before POST. A crash here cannot silently replay a paid call.
                    record["in_flight"] = {"run_id": run_id, "started_at_utc": now(), "sample_id": sample.sample_id, "mode": mode}
                    save_cache(record)
                    save()
                    result = adapter.transcribe(sample.sample_id, mode).to_dict()
                    report["remote_request_count"] += 1
                    raw = result.pop("raw_response")
                    if raw is not None:
                        path = RAW / cache_key(identity) / f"{uuid.uuid4().hex}.response.txt"
                        raw_bytes = raw.encode("utf-8")
                        atomic_write(path, raw_bytes)
                        result.update(raw_response_path=str(path.relative_to(REPO)), raw_response_sha256=sha(raw_bytes))
                    else:
                        result["raw_response_path"] = None
                    previous = store(record, result, sample, [], "live")
                    report["events"].append({"sample_id": sample.sample_id, "mode": mode,
                                             "action": "remote_attempt", "status": previous["status"], "retry_index": index})
                    save()
                    print(f"{sample.sample_id} {mode}: {previous['status']} (HTTP {previous['http_status']})")
                    if fatal(previous):
                        stop_reason = "credentials_permissions_or_quota"
                        break
                    if previous["status"] != "technical_error" or not previous.get("retryable"):
                        break
                if previous and previous.get("http_status") == 429:
                    stop_reason = stop_reason or "rate_limit_exhausted"
                if stop_reason:
                    break
            if stop_reason:
                break
        report["status"] = "partial" if any(state["status"] in {"not_tested", "technical_error"}
                                            for state in report["mode_states"]) else "recorded"
        if stop_reason:
            report["status"], report["stop_reason"] = "paused", stop_reason
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report.update(status="blocked", error_code=exc.code if isinstance(exc, ConfigurationError) else "invalid_evidence_or_io")
        print("Experiment run blocked; inspect local evidence/configuration. No secret exception text logged.")
    except KeyboardInterrupt:
        report.update(status="interrupted", error_code="user_interrupt")
    finally:
        if adapter:
            adapter.close()
        report["finished_at_utc"] = now()
        save()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send pending requests (can incur charges)")
    parser.add_argument("--languages", nargs="+", choices=["english", "urdu", "punjabi", "cantonese", "arabic", "mandarin_chinese"])
    parser.add_argument("--preflight", type=Path, action="append", help="Import recorded preflight; can be repeated")
    parser.add_argument("--max-attempts", type=int, choices=[1, 2, 3], default=3)
    parser.add_argument("--max-requests", type=int, default=96,
                        help="Cap new POST attempts including retries (default 96)")
    parser.add_argument("--retry-failed", action="store_true", help="Explicitly retry cached retryable technical failures")
    args = parser.parse_args()
    if args.max_requests is not None and args.max_requests < 1:
        parser.error("--max-requests must be positive")
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        print("Another run or stale lock exists; inspect data/local/experiment_run.lock before resuming")
        return 1
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()) + "\n")
        report = run(args)
        # Unknown/in-flight outcomes must not silently replace public metrics.
        if (report["status"] in {"partial", "recorded", "paused"}
                and not any(state["in_flight"] for state in report["mode_states"])):
            export_metrics(OUTPUT)
        print(f"Run {report['status']}; new POSTs={report['remote_request_count']}; evidence: {OUTPUT}")
        for language, counts in report["summary_by_language"].items():
            print(f"{language}: selected={counts['n_selected']}, attempted modes={counts['n_attempted_modes']}, "
                  f"completed={counts['n_completed']}, failed={counts['n_failed']}, not_tested={counts['n_not_tested']}")
        return 1 if report["status"] in {"blocked", "interrupted"} else 0
    except (OSError, ValueError, KeyError, TypeError):
        print("Runner/export failed; prior saved evidence retained; inspect cache and local report")
        return 1
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
