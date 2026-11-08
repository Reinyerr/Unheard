"""Read-only CI validation of released research exports; no raw ZIP or API needed."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.schemas.research import ARTIFACTS, LANGUAGE_MAP, validate_bundle
from calculate_metrics import summarize


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_exports(directory: Path):
    raw = {}
    for kind in ARTIFACTS:
        path = directory / f"{kind}.v1.json"
        try:
            raw[kind] = json.loads(path.read_bytes())
        except (OSError, ValueError) as exc:
            raise ValueError(f"{path}: {exc}") from exc
    bundle = validate_bundle(raw)
    languages = bundle["languages"].languages
    wards = bundle["wards"]
    require({r.language_id for r in languages} == set(LANGUAGE_MAP), "languages: expected all 15 canonical IDs")
    tracked = [r for r in languages if r.census_home_column is not None]
    missing = [r for r in tracked if r.coverage_status == "no_task_audio"]
    require(len(tracked) == 14 and all(r.city_home_speakers is not None for r in tracked), "languages: expected 14 known census counts")
    require(len(missing) == 8 and sum(r.city_home_speakers for r in missing) == 79940
            and sum(r.city_home_speakers for r in tracked) == 153480, "languages: expected 8 missing categories, 79,940 / 153,480")
    require(next(r for r in languages if r.language_id == "english").city_home_speakers is None, "languages: English census count must remain null")
    require({w.ward_id for w in wards.wards} == set(range(1, 12)), "wards: expected all 11 wards")
    require(set(wards.missing_request_language_ids) == {r.language_id for r in missing}, "wards: coverage categories disagree")
    for w in wards.wards:
        require(set(w.home_speakers_by_language) == {r.language_id for r in tracked}
                and all(v is not None for v in w.home_speakers_by_language.values()), f"wards: Ward {w.ward_id} missing category counts")
        require(w.gap_population == sum(w.home_speakers_by_language[r.language_id] for r in missing), f"wards: Ward {w.ward_id} gap disagrees with categories")
    for r in tracked:
        require(sum(w.home_speakers_by_language[r.language_id] for w in wards.wards) == r.city_home_speakers, f"wards: {r.language_id} city total mismatch")
    ward10 = next(w for w in wards.wards if w.ward_id == 10)
    require(ward10.population_language_base == 73830 and ward10.home_speakers_by_language["urdu"] == 4520, "wards: corrected Ward 10 baseline mismatch")
    ranked = sorted(missing, key=lambda r: (-r.city_home_speakers, r.language_id))
    items = sorted(bundle["recommendations"].items, key=lambda r: r.rank)
    require([(r.rank, r.language_id, r.city_home_speakers) for r in items] ==
            [(i, r.language_id, r.city_home_speakers) for i, r in enumerate(ranked, 1)], "recommendations: coverage/population ranking mismatch")
    samples = bundle["samples"]
    pilots = {"english", "urdu", "punjabi", "cantonese", "arabic", "mandarin_chinese"}
    require(len(samples.selection.ids) == 8 and len(samples.samples) == 48, "samples: expected 8 IDs and 48 clips")
    require({r.language_id for r in samples.samples} == pilots, "samples: incorrect pilot languages")
    for language in pilots:
        require(sorted(r.fleurs_id for r in samples.samples if r.language_id == language) == samples.selection.ids, f"samples: {language} does not share all 8 IDs")
    experiments = bundle["experiments"]
    require({r.sample_id for r in experiments.records} == {r.sample_id for r in samples.samples}, "experiments: all 48 selected samples must retain explicit outcomes")
    require(samples.source.get("selection_sha256") and samples.source["selection_sha256"] == experiments.source.get("selection_sha256"), "experiments: selection provenance mismatch")
    expected = [summarize(language, [r for r in experiments.records if r.language_id == language]) for language in sorted(pilots)]
    require(sorted(experiments.summaries, key=lambda r: r.language_id) == expected, "experiments: summaries disagree with recorded outcomes")
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "frontend/public/data")
    parser.add_argument("--source", type=Path, help="Optional independent real-source preflight; never required in CI")
    args = parser.parse_args()
    try:
        bundle = validate_exports(args.data_dir)
        if args.source:
            from prepare_census import prepare_census
            from prepare_coverage import prepare_coverage
            from audit_sources import Source, FLEURS, csv_rows, PILOT
            import random
            census = prepare_census(args.source)
            languages, recommendations = prepare_coverage(args.source)
            require(census.wards == bundle["wards"].wards, "source: corrected census differs from exports")
            require(languages.languages == bundle["languages"].languages, "source: coverage differs from exports")
            require(recommendations.items == bundle["recommendations"].items, "source: priorities differ from exports")
            with Source(args.source) as source:
                _, rows = csv_rows(source.read(FLEURS), FLEURS, {"language", "fleurs_id"})
            common = sorted(set.intersection(*({int(r["fleurs_id"]) for r in rows if r["language"] == language} for language in PILOT)))
            require(sorted(random.Random(2026).sample(common, 8)) == bundle["samples"].selection.ids,
                    "source: seeded common FLEURS selection mismatch")
            print(f"Real-source preflight passed: {len(rows)} FLEURS metadata rows, {len(common)} common IDs; corrected census/coverage/ranks match. No files changed or API calls made.")
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Export validation failed: {exc}", file=sys.stderr)
        return 1
    print("Validated source-attributed exports: 11 wards, 15 languages (14 census categories), 8 priorities, 48 samples / 96 explicit modes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
