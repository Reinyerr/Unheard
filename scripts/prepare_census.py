"""Export corrected census aggregates; reads only three known pack CSVs.

Run from the repository root with the backend's Python environment.
No audio, raw census tables, experiments or ranking outputs are copied.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from audit_sources import (
    COVERAGE, CROSSWALK, REPO, WARDS, Source,
    boolean, csv_rows, integer, require, unique,
)

sys.path.insert(0, str(REPO / "backend"))
from app.schemas.research import LANGUAGE_MAP, Ward, Wards, language_id_for_name


def gap_share_pct(gap_population: int, population_language_base: int | None) -> float | None:
    if population_language_base is None or population_language_base <= 0:
        return None
    return 100 * gap_population / population_language_base


def population_base(value: str) -> int | None:
    """Preserve unavailable denominators without introducing numeric sentinels."""
    if not value:
        return None
    require(bool(re.fullmatch(r"-?[0-9]+", value)), WARDS,
            "population_language_base: expected integer or blank")
    parsed = int(value)
    return parsed if parsed > 0 else None


def prepare_census(source_path: Path) -> Wards:
    with Source(source_path) as source:
        inputs = {path: source.read(path) for path in (CROSSWALK, COVERAGE, WARDS)}
    crosswalk = unique(csv_rows(inputs[CROSSWALK], CROSSWALK,
                               {"language", "census_home_column"})[1], "language", CROSSWALK)
    coverage = unique(csv_rows(inputs[COVERAGE], COVERAGE, {
        "language", "census_home_column", "city_home_speakers", "minds14_calls",
        "speech_massive_commands", "has_service_request_audio",
    })[1], "language", COVERAGE)
    require(set(coverage) == set(crosswalk) == {r["display_name"] for r in LANGUAGE_MAP.values()},
            COVERAGE, "expected the shared 15-language crosswalk exactly once")
    mapping = json.loads((REPO / "shared/language_map.json").read_text(encoding="utf-8"))
    require(hashlib.sha256(inputs[CROSSWALK]).hexdigest() == mapping["source_sha256"],
            CROSSWALK, "source differs from T-003 shared language map; review mapping first")

    columns: dict[str, str] = {}
    city_counts: dict[str, int] = {}
    missing: list[str] = []
    for name, row in coverage.items():
        identity = language_id_for_name(name).value
        column = LANGUAGE_MAP[identity]["census_home_column"]
        require(row["census_home_column"] == (column or ""), COVERAGE,
                f"{name}: census column disagrees with shared identity")
        has_audio = boolean(row["has_service_request_audio"], COVERAGE, "has_service_request_audio")
        clips = sum(integer(row[key], COVERAGE, key)
                    for key in ("minds14_calls", "speech_massive_commands"))
        require(has_audio == (clips > 0), COVERAGE, f"{name}: request counts disagree with flag")
        if column is None:
            require(row["city_home_speakers"] == "" and has_audio, COVERAGE,
                    "English must stay outside tracked census totals and gap")
            continue
        columns[identity] = column
        city_counts[identity] = integer(row["city_home_speakers"], COVERAGE, "city_home_speakers")
        if not has_audio:
            missing.append(identity)
    missing.sort()
    require(len(set(columns.values())) == 14 and len(missing) == 8
            and sum(city_counts.values()) == 153480
            and sum(city_counts[key] for key in missing) == 79940,
            COVERAGE, "expected 14 tracked categories and 8 missing categories: 79,940 / 153,480")

    headers, rows = csv_rows(inputs[WARDS], WARDS,
                            {"ward", "population_language_base", "ward10_corrected", *columns.values()})
    require({h for h in headers if h.startswith("home_")} == set(columns.values()),
            WARDS, "expected exactly the 14 mapped home-language columns")
    wards: dict[int, Ward] = {}
    for row in rows:
        ward_id = integer(row["ward"], WARDS, "ward")
        require(ward_id not in wards and 1 <= ward_id <= 11, WARDS, "duplicate or invalid ward")
        require(boolean(row["ward10_corrected"], WARDS, "ward10_corrected") == (ward_id == 10),
                WARDS, f"ward {ward_id}: incorrect Ward 10 correction flag")
        counts = {key: integer(row[column], WARDS, column) for key, column in columns.items()}
        base = population_base(row["population_language_base"])
        gap = sum(counts[key] for key in missing)
        wards[ward_id] = Ward(ward_id=ward_id, population_language_base=base,
                              gap_population=gap, gap_share_pct=gap_share_pct(gap, base),
                              home_speakers_by_language=counts)
    require(set(wards) == set(range(1, 12)), WARDS, "expected wards 1–11 exactly once")
    require(wards[10].population_language_base == 73830
            and wards[10].home_speakers_by_language["urdu"] == 4520,
            WARDS, "corrected Ward 10 baseline differs")
    for identity, total in city_counts.items():
        require(sum(ward.home_speakers_by_language[identity] for ward in wards.values()) == total,
                WARDS, f"{identity}: ward counts disagree with city coverage total")
    provenance = {
        "dataset": "Supplied Mississauga UNHEARD challenge pack; 2021 census aggregates",
        "attribution": "City of Mississauga; supplied corrected derived census and coverage tables",
        "license": "Pack declares City open-data terms; dataset-specific redistribution terms unresolved; local use only pending T-019",
        "license_reference": "https://data.mississauga.ca; see docs/DATA_SOURCES.md",
        "ward_row_count": str(len(wards)), "tracked_language_count": str(len(columns)),
        "missing_request_language_count": str(len(missing)),
        "coverage_row_count": str(len(coverage)), "crosswalk_row_count": str(len(crosswalk)),
        "tracked_home_speakers": str(sum(city_counts.values())),
        "gap_home_speakers": str(sum(city_counts[key] for key in missing)),
        "denominator_policy": "population_language_base; blank/zero/negative base becomes null",
        "scope": "Sum of supplied tracked categories; not city population, unique-person inference or geographic ASR performance",
        "ward10_corrected": "True; Urdu=4520; population_language_base=73830",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "language_map_sha256": hashlib.sha256((REPO / "shared/language_map.json").read_bytes()).hexdigest(),
    }
    for path, raw in inputs.items():
        provenance[f"{path}:sha256"] = hashlib.sha256(raw).hexdigest()
    return Wards(schema_version="1.0", generated_at_utc=datetime.now(timezone.utc).isoformat(),
                 source=provenance, source_file=WARDS, missing_request_language_ids=missing,
                 wards=[wards[key] for key in sorted(wards)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=os.environ.get("UNHEARD_DATA_ROOT"),
                        help="Explicit ZIP or exact extracted pack root (or UNHEARD_DATA_ROOT)")
    args = parser.parse_args()
    if not args.source:
        parser.error("supply --source or UNHEARD_DATA_ROOT; .env is not loaded automatically")
    output = REPO / "frontend/public/data/wards.v1.json"
    temporary: Path | None = None
    try:
        artifact = prepare_census(Path(args.source))
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(artifact.model_dump_json(indent=2) + "\n")
        temporary.replace(output)
        print(f"Wrote {output}: 11 wards, 14 tracked languages; gap 79,940 / 153,480")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Census export failed; output not replaced: {exc}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
