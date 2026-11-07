"""Synthetic fixtures only: fake references/header-only audio, never research data."""
import csv
import io
import json
from pathlib import Path
import subprocess
import zipfile

import pytest

from scripts import audit_sources as a


def csv_bytes(rows):
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return text.getvalue().encode("utf-8-sig")


def fake_flac(rate=16000):
    # STREAMINFO-only synthetic bytes, intentionally not playable audio.
    packed = (rate << 44) | (15 << 36) | rate
    return b"fLaC\x80\x00\x00\x22" + bytes(10) + packed.to_bytes(8, "big") + bytes(16)


@pytest.fixture(scope="module")
def fixture_files():
    # Regression totals from approved documentation; no source transcripts copied.
    population = {"Urdu": 22535, "Arabic": 20570, "Mandarin Chinese": 17730, "Punjabi": 15025,
                  "Polish": 12565, "Cantonese": 10765, "Tagalog": 10695, "Spanish": 9360,
                  "Tamil": 7420, "Vietnamese": 7315, "Hindi": 6640, "Portuguese": 6000,
                  "Gujarati": 4345, "Bengali": 2515}
    accent_counts = [29, 40, 40, 11, 38, 35, 29, 40, 10, 39, 34, 40, 17, 21, 45]
    names = list(population) + ["English"]
    mind = {"English", "Polish", "Portuguese", "Spanish", "Mandarin Chinese"}
    massive = {"Arabic", "Polish", "Portuguese", "Spanish", "Vietnamese"}
    cross, coverage = [], []
    for i, lang in enumerate(names):
        home = "home_" + lang.lower().replace(" ", "_") if lang != "English" else ""
        config = {"Cantonese": "yue_hant_hk", "Mandarin Chinese": "cmn_hans_cn", "Bengali": ""}.get(lang, f"fixture_{i}")
        code = {"Cantonese": "yue", "Mandarin Chinese": "zh"}.get(lang, f"code_{i}")
        cross.append(dict(language=lang, census_home_column=home, fleurs_config=config, iso639_1=code,
                          minds14_locale=f"locale_{i}" if lang in mind else "", speech_massive_locale=f"locale_{i}" if lang in massive else "", speech_accent_archive_native_language=lang.lower()))
        coverage.append(dict(language=lang, census_home_column=home, city_home_speakers=str(population[lang]) if lang != "English" else "",
                             fleurs_clips="40" if config else "0", accent_archive_speakers=str(accent_counts[i]), minds14_calls="210" if lang in mind else "0",
                             speech_massive_commands="115" if lang in massive else "0", has_service_request_audio=str(lang in mind | massive)))
    wards = []
    for n in range(1, 12):
        row = dict(ward=str(n), population_language_base="73830", ward10_corrected=str(n == 10))
        for lang, total in population.items():
            column = next(r["census_home_column"] for r in cross if r["language"] == lang)
            row[column] = str((total - 4520 if lang == "Urdu" else total) if n == 1 else (4520 if n == 10 and lang == "Urdu" else 0))
        wards.append(row)
    files = {a.CROSSWALK: csv_bytes(cross), a.COVERAGE: csv_bytes(coverage), a.WARDS: csv_bytes(wards),
             "README.md": b"Synthetic fixture; no actual source pack version", "DATA_DICTIONARY.md": b"Synthetic fixture dictionary"}
    policies = json.loads(Path(a.__file__).with_name("source_licenses.json").read_text())
    files["LICENSES.md"] = "\n".join(f"| {p['pack_match'].strip('| ')} | {p['source_url']} | {p['declared_license']} |" for p in policies["datasets"]).encode()
    for path, (dataset, column, _, required) in a.SPEECH.items():
        rows = []
        for mapping, cov in zip(cross, coverage):
            for i in range(int(cov[column])):
                row = {k: "fixture" for k in sorted(required)}
                row.update(language=mapping["language"], file=f"audio/fixture_{len(rows)}.{'mp3' if dataset == 'accent' else 'flac'}")
                if dataset == "fleurs":
                    row.update(lang_config=mapping["fleurs_config"], iso639_1=mapping["iso639_1"], fleurs_id=str(i), gender="female", duration_sec="1", transcription="synthetic reference", raw_transcription="Synthetic reference")
                if dataset in {"minds14", "speech_massive"}:
                    row["locale"] = mapping["minds14_locale" if dataset == "minds14" else "speech_massive_locale"]
                rows.append(row)
                files[Path(path).parent.as_posix() + "/" + row["file"]] = b"ID3" + bytes(39) if dataset == "accent" else fake_flac()
        files[path] = csv_bytes(rows)
    return files


def write_zip(tmp_path, files):
    target = tmp_path / "fixture.zip"
    with zipfile.ZipFile(target, "w") as z:
        for path, raw in files.items():
            z.writestr(a.ROOT + "/" + path, raw)
    return target


@pytest.fixture
def mock_git(monkeypatch):
    monkeypatch.setattr(a, "git_audit", lambda repo: {"committed_zip_count": 0, "fixture": True})


def test_complete_synthetic_zip_manifest(tmp_path, fixture_files, mock_git):
    report = a.audit(write_zip(tmp_path, fixture_files))
    assert report["status"] == "passed"
    assert report["checks"]["missing_category_count"] == 8
    assert report["checks"]["missing_home_speakers"] == 79940
    assert report["checks"]["tracked_nonofficial_home_speakers"] == 153480
    assert report["checks"]["english_home_speakers"] is None
    assert report["datasets"]["fleurs"]["pilot_common_id_count"] == 40
    assert len(report["assets"]) == 560
    assert all(p["license_url"].startswith("https://") for p in report["licenses"]["datasets"])
    assert report["provenance"]["git"]["committed_zip_count"] == 0
    assert "synthetic reference" not in json.dumps(report)
    assert report["source"]["declared_pack_version"] is None
    assert all(len(p["sha256"]) == 64 for p in report["assets"])


def test_extracted_directory(tmp_path, fixture_files, mock_git):
    root = tmp_path / a.ROOT
    for name, data in fixture_files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    report = a.audit(root)
    assert report["source"]["kind"] == "directory"
    assert report["source"]["sha256"] is None
    assert not (root / "source_manifest.json").exists()


@pytest.mark.parametrize("raw,required,message", [
    (b"a\n1\n", {"missing"}, "missing required columns: missing"),
    (b"a,a\n1,2\n", {"a"}, "duplicate"),
    (b"a,b\n1\n", {"a"}, "inconsistent field count"),
    (b"a\n", {"a"}, "no source rows"),
    (b"a\n\xff\n", {"a"}, "invalid UTF-8"),
])
def test_csv_errors_include_source_path(raw, required, message):
    with pytest.raises(a.AuditError, match="some/source.csv") as exc:
        a.csv_rows(raw, "some/source.csv", required)
    assert message in str(exc.value)


def test_utf8_bom_and_boolean_case():
    _, rows = a.csv_rows(b"\xef\xbb\xbfflag\n  fAlSe  \n", "fixture.csv", {"flag"})
    assert a.boolean(rows[0]["flag"], "fixture.csv", "flag") is False


@pytest.mark.parametrize("value", ["", "yes", "0", "null"])
def test_unknown_booleans_fail(value):
    with pytest.raises(a.AuditError, match="fixture.csv"):
        a.boolean(value, "fixture.csv", "flag")


@pytest.mark.parametrize("value", ["", "nan", "-1", "1.5"])
def test_missing_or_invalid_counts_fail(value):
    with pytest.raises(a.AuditError):
        a.integer(value, "fixture.csv", "count")


@pytest.mark.parametrize("mutation,expected", [
    ("column", a.COVERAGE), ("missing_file", a.WARDS), ("total", "coverage mismatch"),
    ("empty_reference", "missing reference text"), ("duplicate_id", "duplicate language/fleurs_id"),
    ("traversal", "unsafe relative source path"), ("absent_audio", "required source file missing"),
    ("bad_audio", "invalid FLAC"), ("wrong_rate", "unexpected channels/sample rate"),
    ("license", "LICENSES.md"), ("wrong_code", "code/config mismatch"),
])
def test_source_failures(tmp_path, fixture_files, mock_git, mutation, expected):
    files = dict(fixture_files)
    if mutation in {"column", "total"}:
        _, rows = a.csv_rows(files[a.COVERAGE], a.COVERAGE, set())
        if mutation == "column":
            for row in rows:
                del row["city_home_speakers"]
        else:
            rows[0]["city_home_speakers"] = "1"
        files[a.COVERAGE] = csv_bytes(rows)
    elif mutation == "missing_file":
        del files[a.WARDS]
    elif mutation == "license":
        files["LICENSES.md"] = b"No licenses"
    elif mutation == "wrong_code":
        _, rows = a.csv_rows(files[a.CROSSWALK], a.CROSSWALK, set())
        next(r for r in rows if r["language"] == "Cantonese")["iso639_1"] = "zh"
        files[a.CROSSWALK] = csv_bytes(rows)
    else:
        _, rows = a.csv_rows(files[a.FLEURS], a.FLEURS, set())
        audio = Path(a.FLEURS).parent.as_posix() + "/" + rows[0]["file"]
        if mutation == "empty_reference": rows[0]["transcription"] = ""
        if mutation == "duplicate_id": rows[1]["fleurs_id"] = rows[0]["fleurs_id"]
        if mutation == "traversal": rows[0]["file"] = "../outside.flac"
        if mutation == "absent_audio": del files[audio]
        if mutation == "bad_audio": files[audio] = b"not audio"
        if mutation == "wrong_rate": files[audio] = fake_flac(8000)
        files[a.FLEURS] = csv_bytes(rows)
    with pytest.raises(a.AuditError, match=expected):
        a.audit(write_zip(tmp_path, files))


@pytest.mark.parametrize("name", ["../escape.csv", "wrong_root/file.csv", a.ROOT + "/a/../../escape.csv"])
def test_unsafe_archive_entries(tmp_path, name):
    path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(name, "fixture")
    with pytest.raises(a.AuditError):
        a.Source(path)


def test_duplicate_zip_entries(tmp_path):
    path = tmp_path / "duplicate.zip"
    with pytest.warns(UserWarning), zipfile.ZipFile(path, "w") as z:
        z.writestr(a.ROOT + "/README.md", "one")
        z.writestr(a.ROOT + "/README.md", "two")
    with pytest.raises(a.AuditError, match="duplicate ZIP"):
        a.Source(path)


def test_missing_source(tmp_path):
    with pytest.raises(a.AuditError, match="source missing"):
        a.Source(tmp_path / "missing.zip")


@pytest.mark.parametrize("history,index", [("data/raw/pack.ZIP\n", ""), ("", "data/raw/file.csv\0")])
def test_git_refuses_committed_zip_or_tracked_data(monkeypatch, history, index):
    monkeypatch.setattr(subprocess, "check_output", lambda args, **kwargs: index if "ls-files" in args else history)
    with pytest.raises(a.AuditError, match="raw files tracked or ZIPs"):
        a.git_audit(Path("fixture"))


def test_cli_failed_run_replaces_stale_success(tmp_path, monkeypatch):
    monkeypatch.setattr(a, "REPO", tmp_path)
    output = tmp_path / "data/processed/source_manifest.json"
    output.parent.mkdir(parents=True)
    output.write_text('{"status":"passed"}')
    assert a.main(["--source", str(tmp_path / "missing.zip"), "--output", str(output)]) == 1
    assert json.loads(output.read_text())["status"] == "failed"


def test_cli_rejects_public_output(tmp_path, monkeypatch):
    monkeypatch.setattr(a, "REPO", tmp_path)
    with pytest.raises(SystemExit):
        a.main(["--output", str(tmp_path / "frontend/public/data/audit.json")])
