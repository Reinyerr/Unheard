"""Read-only audit of the supplied pack; no extraction, API calls or public exports.

Python 3.12 standard library only. Run --help for explicit source configuration.
The generated manifest is local audit evidence, not an application data schema.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import AbstractContextManager
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile

REPO = Path(__file__).resolve().parents[1]
ROOT = "Mississauga_Unheard_ElevenLabs_Track"
COVERAGE = "01_people_census/derived/language_coverage.csv"
WARDS = "01_people_census/derived/ward_language_profile_2021_corrected.csv"
CROSSWALK = "language_crosswalk.csv"
FLEURS = "02_speech_home_languages_FLEURS/metadata.csv"
MISSING = {"Urdu", "Punjabi", "Cantonese", "Tagalog", "Tamil", "Hindi", "Gujarati", "Bengali"}
PILOT = ("English", "Urdu", "Punjabi", "Cantonese", "Arabic", "Mandarin Chinese")
SPEECH = {
    FLEURS: ("fleurs", "fleurs_clips", 560, {"file", "language", "lang_config", "iso639_1", "fleurs_id", "gender", "duration_sec", "transcription", "raw_transcription", "variety_note"}),
    "03_accented_english_SpeechAccentArchive/metadata.csv": ("accent", "accent_archive_speakers", 468, {"file", "language", "duration_sec"}),
    "04_spoken_requests/minds14/metadata.csv": ("minds14", "minds14_calls", 1050, {"file", "language", "locale", "intent", "transcription", "english_transcription"}),
    "04_spoken_requests/speech_massive/metadata.csv": ("speech_massive", "speech_massive_commands", 575, {"file", "language", "locale", "scenario", "intent", "utterance", "annotated_utterance"}),
}


class AuditError(ValueError):
    """A source or repository does not satisfy the audit requirements."""


def require(condition: bool, path: str, message: str) -> None:
    if not condition:
        raise AuditError(f"{path}: {message}")


def safe_relative(name: str) -> str:
    parts = name.split("/")
    require(bool(name) and not any(p in {"", ".", ".."} for p in parts)
            and "\\" not in name and ":" not in name, name, "unsafe relative source path")
    return name


def digest(stream) -> str:
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()


class Source(AbstractContextManager):
    """Explicit ZIP or exact extracted pack root. Never writes to the input."""
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.archive = None
        self.files: dict[str, int] = {}
        require(self.path.exists(), str(path), "source missing; supply --source or UNHEARD_DATA_ROOT")
        if self.path.is_file():
            require(zipfile.is_zipfile(self.path), str(path), "expected ZIP or extracted pack directory")
            self.archive = zipfile.ZipFile(self.path)
            try:
                for info in self.archive.infolist():
                    name = safe_relative(info.filename.rstrip("/"))
                    require(name == ROOT or name.startswith(ROOT + "/"), name, f"expected exact archive root {ROOT}/")
                    require(not stat.S_ISLNK(info.external_attr >> 16), name, "symbolic links are not allowed")
                    if not info.is_dir():
                        rel = name.removeprefix(ROOT + "/")
                        require(rel not in self.files, rel, "duplicate ZIP entry")
                        self.files[rel] = info.file_size
            except Exception:
                self.archive.close()
                raise
        else:
            require(self.path.is_dir() and self.path.name == ROOT, str(path), f"select extracted {ROOT} directory, not its parent")
            for item in self.path.rglob("*"):
                require(not item.is_symlink() and not item.is_junction(), str(item), "links/junctions are not allowed")
                if item.is_file():
                    rel = safe_relative(item.relative_to(self.path).as_posix())
                    self.files[rel] = item.stat().st_size

    def __exit__(self, *args):
        if self.archive:
            self.archive.close()

    def open(self, relative: str):
        safe_relative(relative)
        require(relative in self.files, relative, "required source file missing")
        if self.archive:
            return self.archive.open(ROOT + "/" + relative)
        target = (self.path / relative).resolve()
        require(target.is_relative_to(self.path), relative, "path escapes source root")
        return target.open("rb")

    def read(self, relative: str) -> bytes:
        require(self.files.get(relative, 0) <= 16 * 1024 * 1024, relative, "metadata exceeds 16 MiB limit")
        with self.open(relative) as stream:
            return stream.read()


def csv_rows(raw: bytes, path: str, required: set[str]) -> tuple[list[str], list[dict[str, str]]]:
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
        headers = reader.fieldnames or []
        require(len(headers) == len(set(headers)) and all(headers), path, "duplicate or empty column name")
        require(required <= set(headers), path, f"missing required columns: {', '.join(sorted(required - set(headers)))}")
        rows = []
        for row in reader:
            require(None not in row and all(v is not None for v in row.values()), path, f"row {reader.line_num}: inconsistent field count")
            rows.append({k: v.strip() for k, v in row.items()})
        require(bool(rows), path, "no source rows")
        return headers, rows
    except (UnicodeError, csv.Error) as exc:
        raise AuditError(f"{path}: invalid UTF-8 CSV: {exc}") from exc


def integer(value: str, path: str, field: str) -> int:
    require(bool(re.fullmatch(r"[0-9]+", value)), path, f"{field}: expected nonnegative integer, not blank/missing")
    return int(value)


def boolean(value: str, path: str, field: str) -> bool:
    require(value.lower() in {"true", "false"}, path, f"{field}: expected True/False string")
    return value.lower() == "true"


def unique(rows: list[dict[str, str]], key: str, path: str) -> dict[str, dict[str, str]]:
    result = {row[key]: row for row in rows}
    require("" not in result and len(result) == len(rows), path, f"empty or duplicate {key}")
    return result


def audit_coverage(coverage, crosswalk, wards) -> dict:
    cov = unique(coverage, "language", COVERAGE)
    cross = unique(crosswalk, "language", CROSSWALK)
    require(set(cov) == set(cross) and len(cov) == 15 and "English" in cov, COVERAGE, "expected matching 15-language crosswalk including English")
    require(set(PILOT) <= set(cross), CROSSWALK, "required pilot-language row missing")
    nonofficial = [r for r in coverage if r["language"] != "English"]
    home_columns = [r["census_home_column"] for r in nonofficial]
    require(len(set(home_columns)) == 14 and all(c.startswith("home_") for c in home_columns), COVERAGE, "expected 14 distinct census columns")
    for language, row in cov.items():
        require(row["census_home_column"] == cross[language]["census_home_column"], COVERAGE, f"{language}: crosswalk mismatch")
        counts = [integer(row[col], COVERAGE, col) for col in ("fleurs_clips", "accent_archive_speakers", "minds14_calls", "speech_massive_commands")]
        require(boolean(row["has_service_request_audio"], COVERAGE, "has_service_request_audio") == (counts[2] + counts[3] > 0), COVERAGE, f"{language}: request count/Boolean mismatch")
    require(cov["English"]["city_home_speakers"] == "" and cov["English"]["census_home_column"] == "", COVERAGE, "English must remain outside the tracked non-official denominator")
    missing = [r for r in nonofficial if not boolean(r["has_service_request_audio"], COVERAGE, "has_service_request_audio")]
    numerator = sum(integer(r["city_home_speakers"], COVERAGE, "city_home_speakers") for r in missing)
    denominator = sum(integer(r["city_home_speakers"], COVERAGE, "city_home_speakers") for r in nonofficial)
    require({r["language"] for r in missing} == MISSING and numerator == 79940 and denominator == 153480, COVERAGE, f"coverage mismatch: {len(missing)} missing categories, {numerator}/{denominator}")
    by_ward = unique(wards, "ward", WARDS)
    require(set(by_ward) == {str(n) for n in range(1, 12)}, WARDS, "expected wards 1 through 11 exactly once")
    for row in wards:
        integer(row["population_language_base"], WARDS, "population_language_base")
        require(boolean(row["ward10_corrected"], WARDS, "ward10_corrected") == (row["ward"] == "10"), WARDS, "incorrect Ward 10 correction flag")
        for column in home_columns:
            integer(row[column], WARDS, column)
    require(by_ward["10"]["population_language_base"] == "73830" and by_ward["10"]["home_urdu"] == "4520", WARDS, "corrected Ward 10 baseline differs")
    for row in nonofficial:
        total = sum(int(w[row["census_home_column"]]) for w in wards)
        require(total == int(row["city_home_speakers"]), WARDS, f"{row['language']}: corrected ward sum differs from coverage")
    for lang, code, config in [("Cantonese", "yue", "yue_hant_hk"), ("Mandarin Chinese", "zh", "cmn_hans_cn")]:
        require(cross[lang]["iso639_1"] == code and cross[lang]["fleurs_config"] == config, CROSSWALK, f"{lang}: code/config mismatch")
    return {"tracked_nonofficial_categories": 14, "missing_categories": sorted(MISSING),
            "missing_category_count": len(missing), "missing_home_speakers": numerator,
            "tracked_nonofficial_home_speakers": denominator, "coverage_gap_pct": 100 * numerator / denominator,
            "english_home_speakers": None, "corrected_ward_rows": len(wards)}


def flac_info(header: bytes, path: str) -> dict:
    require(len(header) >= 42 and header[:4] == b"fLaC" and header[4] & 127 == 0
            and int.from_bytes(header[5:8], "big") == 34, path, "invalid FLAC STREAMINFO header")
    packed = int.from_bytes(header[18:26], "big")
    rate, channels, bits, samples = packed >> 44, ((packed >> 41) & 7) + 1, ((packed >> 36) & 31) + 1, packed & ((1 << 36) - 1)
    require(rate > 0 and samples > 0, path, "empty or unspecified FLAC stream")
    return {"format": "FLAC", "sample_rate_hz": rate, "channels": channels, "bits_per_sample": bits, "sample_count": samples, "duration_sec": samples / rate}


def audit_speech(source: Source, tables, crosswalk, coverage) -> tuple[dict, list[dict]]:
    cross = unique(crosswalk, "language", CROSSWALK)
    summary, assets = {}, []
    sentence_ids: dict[str, set[int]] = defaultdict(set)
    genders: dict[str, Counter] = defaultdict(Counter)
    for path, (dataset, count_column, expected_rows, _) in SPEECH.items():
        rows = tables[path]
        require(len(rows) == expected_rows, path, f"expected {expected_rows} rows, got {len(rows)}")
        unique(rows, "file", path)
        counts = Counter(row["language"] for row in rows)
        require(set(counts) <= set(cross), path, "unknown language")
        require(all(counts[row["language"]] == int(row[count_column]) for row in coverage), path, "metadata counts differ from coverage")
        folder = str(PurePosixPath(path).parent)
        formats = Counter()
        references = set()
        for line, row in enumerate(rows, 2):
            relative = safe_relative(row["file"])
            require(relative.startswith("audio/"), path, f"row {line}: audio must be inside dataset audio directory")
            audio_path = folder + "/" + relative
            references.add(audio_path)
            with source.open(audio_path) as stream:
                header = stream.read(42)
            if dataset == "accent":
                require(relative.endswith(".mp3") and (header.startswith(b"ID3") or (len(header) > 1 and header[0] == 255 and header[1] & 224 == 224)), audio_path, "expected MP3 signature")
                info = {"format": "MP3", "verification": "signature only; not decoded"}
            else:
                require(relative.endswith(".flac"), audio_path, "expected .flac extension")
                info = flac_info(header, audio_path)
                # All supplied FLACs are 16 kHz, including MInDS-14. Audit the pack bytes.
                require(info["channels"] == 1 and info["sample_rate_hz"] == 16000, audio_path, "unexpected channels/sample rate")
            formats[info["format"]] += 1
            if dataset == "fleurs":
                language = row["language"]
                require(row["lang_config"] == cross[language]["fleurs_config"] and row["iso639_1"] == cross[language]["iso639_1"], path, f"row {line}: FLEURS crosswalk mismatch")
                require(bool(row["transcription"]) and bool(row["raw_transcription"]), path, f"row {line}: missing reference text")
                sentence = integer(row["fleurs_id"], path, "fleurs_id")
                require(sentence not in sentence_ids[language], path, f"row {line}: duplicate language/fleurs_id")
                sentence_ids[language].add(sentence)
                require(row["gender"] in {"female", "male", "other"}, path, f"row {line}: unknown gender label")
                genders[language][row["gender"]] += 1
                try:
                    duration = float(row["duration_sec"])
                except ValueError as exc:
                    raise AuditError(f"{path}: row {line}: invalid duration_sec") from exc
                require(math.isfinite(duration) and duration > 0 and abs(duration - info["duration_sec"]) <= .02, path, f"row {line}: duration differs from FLAC header")
                with source.open(audio_path) as stream:
                    sha = digest(stream)
                assets.append({"path": audio_path, "size_bytes": source.files[audio_path], "sha256": sha,
                               "dataset": dataset, "license_id": dataset, **info})
            elif dataset in {"minds14", "speech_massive"}:
                require(row["locale"] == cross[row["language"]]["minds14_locale" if dataset == "minds14" else "speech_massive_locale"], path, f"row {line}: locale mismatch")
        actual = {name for name in source.files if name.startswith(folder + "/audio/")}
        require(references == actual, path, "audio inventory and metadata references differ")
        summary[dataset] = {"license_id": dataset, "metadata_rows": len(rows), "counts_by_language": dict(sorted(counts.items())), "audio_files_checked": len(references), "formats": dict(formats), "audio_validation": "signature/STREAMINFO; no full decode"}
    require(len(sentence_ids) == 14 and all(len(ids) == 40 for ids in sentence_ids.values()), FLEURS, "expected 40 distinct IDs in each of 14 languages")
    common = set.intersection(*(sentence_ids[lang] for lang in PILOT))
    require(len(common) == 40 and all(ids == common for ids in sentence_ids.values()), FLEURS, "languages do not share the same 40 IDs")
    summary["fleurs"].update({"pilot_languages": list(PILOT), "pilot_common_id_count": len(common), "pilot_common_ids": sorted(common), "genders_by_language": {k: dict(v) for k, v in sorted(genders.items())}, "selected_experiment_samples": None})
    return summary, assets


def git_audit(repo: Path) -> dict:
    def git(*args):
        try:
            return subprocess.check_output(["git", "-C", str(repo), *args], text=True, encoding="utf-8", stderr=subprocess.PIPE)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise AuditError("Git audit unavailable; cannot assert no committed ZIP files") from exc
    tracked = git("ls-files", "-z").split("\0")
    history = git("log", "--all", "--format=", "--name-only", "-z").split("\0")
    history = [path.strip("\n") for path in history]
    zips = sorted({p for p in history if p.lower().endswith(".zip")})
    unsafe = [p for p in tracked if p.lower().endswith((".zip", ".flac", ".mp3", ".wav")) or p.startswith("data/")]
    require(not zips and not unsafe, "git", f"raw files tracked or ZIPs in reachable history: {sorted(set(zips + unsafe))}")
    return {"tracked_raw_files": unsafe, "committed_zip_paths": zips, "committed_zip_count": len(zips), "scope": "current index and locally reachable --all history; not remote/unreachable objects", "head": git("rev-parse", "HEAD").strip()}


def audit(source_path: Path, repo: Path = REPO) -> dict:
    with Source(source_path) as source:
        file_records = []
        def read_metadata(path: str) -> bytes:
            raw = source.read(path)
            file_records.append({"path": path, "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
            return raw

        documents = {p: read_metadata(p).decode("utf-8-sig") for p in ("README.md", "DATA_DICTIONARY.md", "LICENSES.md")}
        policies_path = Path(__file__).with_name("source_licenses.json")
        policies_raw = policies_path.read_bytes()
        policies = json.loads(policies_raw)
        license_lines = [line for line in documents["LICENSES.md"].splitlines() if line.startswith("|")]
        for policy in policies["datasets"]:
            require(any(policy["pack_match"] in line and policy["declared_license"] in line and policy["source_url"] in line for line in license_lines), "LICENSES.md", f"{policy['id']}: expected license/source row absent or changed; review required")
        tables = {}
        requirements = {
            CROSSWALK: {"language", "census_home_column", "fleurs_config", "iso639_1", "minds14_locale", "speech_massive_locale", "speech_accent_archive_native_language"},
            COVERAGE: {"language", "census_home_column", "city_home_speakers", "has_service_request_audio", "fleurs_clips", "accent_archive_speakers", "minds14_calls", "speech_massive_commands"},
        }
        def table(path: str, required: set[str]):
            headers, rows = csv_rows(read_metadata(path), path, required)
            file_records[-1].update({"format": "CSV", "encoding": "utf-8-sig", "headers": headers, "row_count": len(rows)})
            tables[path] = rows
            return rows
        crosswalk = table(CROSSWALK, requirements[CROSSWALK])
        coverage = table(COVERAGE, requirements[COVERAGE])
        homes = {r["census_home_column"] for r in crosswalk if r["census_home_column"]}
        wards = table(WARDS, {"ward", "population_language_base", "ward10_corrected"} | homes)
        totals = audit_coverage(coverage, crosswalk, wards)
        for path, (_, _, _, headers) in SPEECH.items():
            table(path, headers)
        speech, assets = audit_speech(source, tables, crosswalk, coverage)
        with source.path.open("rb") if source.archive else io.BytesIO() as stream:
            archive_hash = digest(stream) if source.archive else None
        inventory = [{"path": name, "size_bytes": size} for name, size in sorted(source.files.items())]
        return {
            "schema_version": "1.0", "artifact_type": "source_audit", "status": "passed",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": {"name": source.path.name, "kind": "zip" if source.archive else "directory", "archive_root": ROOT,
                       "size_bytes": source.path.stat().st_size if source.archive else None, "sha256": archive_hash,
                       "declared_pack_version": None, "version_note": "No pack release or upstream revision pinned in supplied documentation; checksums identify these exact bytes.",
                       "file_count": len(inventory), "inventory_sha256": hashlib.sha256(json.dumps(inventory, sort_keys=True).encode()).hexdigest()},
            "provenance": {"audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "license_policy_sha256": hashlib.sha256(policies_raw).hexdigest(), "git": git_audit(repo)},
            "checks": totals, "datasets": speech, "metadata_files": file_records,
            "assets": assets, "licenses": policies, "inventory": inventory,
            "limitations": ["No transcripts or speaker identifiers exported; no audio copied or sent to APIs.",
                            "Only FLEURS audio is individually hashed; other audio receives header/signature checks.",
                            "Raw census, 311, neighbourhood and long-form tables are inventory-only in this command.",
                            "Audio was not fully decoded; header checks do not prove all frames are playable.",
                            "No sample selection, experiment metrics, geographic performance, or public redistribution approval."]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=os.environ.get("UNHEARD_DATA_ROOT"), help="ZIP or exact extracted pack root; otherwise UNHEARD_DATA_ROOT (shell environment)")
    parser.add_argument("--output", type=Path, default=REPO / "data/processed/source_manifest.json")
    args = parser.parse_args(argv)
    # This is local evidence; forbid accidental raw-data/public source overwrites.
    output = args.output.resolve()
    if not output.is_relative_to((REPO / "data/processed").resolve()) or output.suffix != ".json":
        parser.error("--output must be a JSON file under this repository's ignored data/processed/")
    try:
        require(bool(args.source), "source", "set --source or UNHEARD_DATA_ROOT; no dataset is assumed")
        report = audit(Path(args.source))
    except (AuditError, OSError, UnicodeError, zipfile.BadZipFile, RuntimeError, json.JSONDecodeError) as exc:
        report = {"schema_version": "1.0", "artifact_type": "source_audit", "status": "failed",
                  "generated_at_utc": datetime.now(timezone.utc).isoformat(), "errors": [str(exc)]}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(json.dumps({"status": report["status"], "manifest": str(output), "checks": report.get("checks"), "errors": report.get("errors", [])}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
