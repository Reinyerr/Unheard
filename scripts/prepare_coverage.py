"""Export supplied task-audio coverage and language-first recruitment priorities."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from prepare_census import prepare_census
from audit_sources import COVERAGE, CROSSWALK, PILOT, REPO, WARDS, Source, csv_rows, integer, require
from app.schemas.research import (
    LANGUAGE_MAP, CoverageStatus, Language, Languages, Recommendation, Recommendations,
    Ward, language_id_for_name, validate_artifact,
)


def top_wards(wards: list[Ward], language_id: str, *, by_share: bool) -> list[tuple[int, float | int]]:
    values: list[tuple[int, float | int]] = []
    for ward in wards:
        count = ward.home_speakers_by_language[language_id]
        require(count is not None, WARDS, f"ward {ward.ward_id}: missing {language_id} count")
        if by_share:
            base = ward.population_language_base
            if base is None or base <= 0:
                continue
            value = 100 * count / base
        else:
            value = count
        values.append((ward.ward_id, value))
    return sorted(values, key=lambda item: (-item[1], item[0]))[:3]


def recommendation(language: Language, rank: int, wards: list[Ward]) -> Recommendation:
    counts = top_wards(wards, language.language_id, by_share=False)
    shares = top_wards(wards, language.language_id, by_share=True)
    count_text = "; ".join(f"Ward {ward_id}: {count:,}" for ward_id, count in counts)
    share_text = "; ".join(f"Ward {ward_id}: {share:.2f}%" for ward_id, share in shares)
    return Recommendation(
        language_id=language.language_id, rank=rank, city_home_speakers=language.city_home_speakers,
        reason="No labelled spoken-request audio in the supplied MInDS-14 and Speech-MASSIVE subsets",
        suggested_action=(
            f"Plan consented, realistic municipal-request evaluation in {language.display_name}. "
            f"Top wards by home-speaker count (recruitment volume): {count_text}. "
            "Independently, top wards by home-language share of population_language_base "
            f"(concentration): {share_text or 'unavailable'}. "
            "Suggested ward IDs follow the count ranking. Work with community partners to recruit "
            "willing participants; evaluate outcomes before claiming improvement."
        ),
        suggested_ward_ids=[ward_id for ward_id, _ in counts],
        limitations=[
            "Missing audio refers only to supplied task-dataset subsets, not all recordings worldwide or provider support.",
            "2021 home-language categories do not establish English ability, service demand or individual need.",
            "Ward counts and shares guide future recruitment; no ward-specific recognition rates were measured.",
            "FLEURS speakers are not identified Mississauga residents; pilot outcomes must remain separate.",
            "Top three wards are descriptive, with ascending ward ID breaking ties; shares with unavailable bases are excluded.",
            "Share text is rounded to two decimals for display; ranking uses unrounded count/base ratios.",
        ],
    )


def prepare_coverage(source_path: Path) -> tuple[Languages, Recommendations]:
    # Reuse T-004 source guards, but never rewrite the census export here.
    current = prepare_census(source_path)
    ward_path = REPO / "frontend/public/data/wards.v1.json"
    ward_bytes = ward_path.read_bytes()
    published = validate_artifact("wards", json.loads(ward_bytes))
    require(published.wards == current.wards
            and published.missing_request_language_ids == current.missing_request_language_ids,
            str(ward_path), "stale or different census export; rerun prepare_census.py first")
    for path in (COVERAGE, CROSSWALK, WARDS):
        key = f"{path}:sha256"
        require(published.source.get(key) == current.source[key], str(ward_path),
                f"{path}: input hash changed; rerun prepare_census.py first")
    with Source(source_path) as source:
        coverage_bytes = source.read(COVERAGE)
    require(hashlib.sha256(coverage_bytes).hexdigest() == current.source[f"{COVERAGE}:sha256"],
            COVERAGE, "input changed during generation")
    _, rows = csv_rows(coverage_bytes, COVERAGE, {
        "language", "city_home_speakers", "minds14_calls", "speech_massive_commands",
    })
    languages: list[Language] = []
    for row in rows:
        identity = language_id_for_name(row["language"])
        counts = {"minds14": integer(row["minds14_calls"], COVERAGE, "minds14_calls"),
                  "speech_massive": integer(row["speech_massive_commands"], COVERAGE, "speech_massive_commands")}
        languages.append(Language(
            language_id=identity, **LANGUAGE_MAP[identity],
            city_home_speakers=(integer(row["city_home_speakers"], COVERAGE, "city_home_speakers")
                                if row["city_home_speakers"] else None),
            coverage_status=(CoverageStatus.has_task_audio if sum(counts.values())
                             else CoverageStatus.no_task_audio),
            request_clip_counts=counts, pilot_selected=row["language"] in PILOT,
        ))
    languages.sort(key=lambda item: item.language_id)
    missing = sorted((item for item in languages if item.coverage_status == CoverageStatus.no_task_audio),
                     key=lambda item: (-item.city_home_speakers, item.language_id))
    require({item.language_id for item in missing} == set(current.missing_request_language_ids),
            COVERAGE, "coverage and ward gap IDs disagree")
    provenance = dict(current.source)
    provenance.update({
        "coverage_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "wards_artifact_sha256": hashlib.sha256(ward_bytes).hexdigest(),
        "recommendation_count": str(len(missing)),
        "pilot_language_count": str(sum(item.pilot_selected for item in languages)),
        "ranking_policy": "Missing supplied task audio only; city_home_speakers descending, language_id ascending for ties",
        "ward_selection_policy": "Top 3 by count; independently top 3 by count/population_language_base; ward_id ascending for ties; null-base shares excluded",
        "ward_export_policy": "suggested_ward_ids follows count ranking; suggested_action labels both independent rankings and values",
        "task_dataset_attribution": "MInDS-14: PolyAI / Gerz et al. (2021); Speech-MASSIVE: FBK; supplied coverage counts only",
        "task_dataset_licenses": "MInDS-14 CC BY 4.0, https://huggingface.co/datasets/PolyAI/minds14; Speech-MASSIVE CC BY-NC-SA 4.0, https://mt.fbk.eu/speech-massive/; no audio/transcripts exported",
        "experiment_status": "not_tested; this pipeline performs no experiments and emits no CER/WER metrics",
    })
    timestamp = datetime.now(timezone.utc).isoformat()
    return (
        Languages(schema_version="1.0", generated_at_utc=timestamp, source=provenance, languages=languages),
        Recommendations(schema_version="1.0", generated_at_utc=timestamp, source=provenance,
                        method="missing_task_audio_then_city_home_speakers_desc",
                        items=[recommendation(item, rank, current.wards)
                               for rank, item in enumerate(missing, start=1)]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=os.environ.get("UNHEARD_DATA_ROOT"),
                        help="Explicit ZIP or exact extracted pack root (or UNHEARD_DATA_ROOT)")
    args = parser.parse_args()
    if not args.source:
        parser.error("supply --source or UNHEARD_DATA_ROOT; .env is not loaded automatically")
    staged: list[tuple[Path, Path]] = []
    try:
        languages, recommendations = prepare_coverage(Path(args.source))
        # Validate and stage both artifacts before replacing either output.
        for kind, artifact in (("languages", languages), ("recommendations", recommendations)):
            output = REPO / f"frontend/public/data/{kind}.v1.json"
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                             suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                staged.append((temporary, output))
                stream.write(artifact.model_dump_json(indent=2) + "\n")
        for temporary, output in staged:
            temporary.replace(output)
        print("Wrote languages.v1.json (15 languages) and recommendations.v1.json "
              "(8 priorities; 79,940 / 153,480 tracked home speakers).")
        for item in recommendations.items:
            print(f"{item.rank}. {item.language_id}: {item.city_home_speakers:,}; "
                  f"top count wards {item.suggested_ward_ids}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Coverage export failed: {exc}", file=sys.stderr)
        return 1
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
