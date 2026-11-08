"""Freeze eight common FLEURS IDs and export 48 attributed, unmodified clips."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import random
import sys
import tempfile

from audit_sources import (
    CROSSWALK, FLEURS, PILOT, REPO, Source, csv_rows, flac_info, integer, require, safe_relative,
)

sys.path.insert(0, str(REPO / "backend"))
from app.schemas.research import LANGUAGE_MAP, Sample, Samples, language_id_for_name

DATASET_DIR = str(PurePosixPath(FLEURS).parent)
MANIFEST = REPO / "data/processed/sampling_manifest.json"
PUBLIC = REPO / "frontend/public"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def sample_fleurs(source_path: Path) -> Samples:
    with Source(source_path) as source:
        metadata = source.read(FLEURS)
        crosswalk = source.read(CROSSWALK)
        licenses = source.read("LICENSES.md")
        mapping_bytes = (REPO / "shared/language_map.json").read_bytes()
        mapping = json.loads(mapping_bytes)
        require(hashlib.sha256(crosswalk).hexdigest() == mapping["source_sha256"], CROSSWALK,
                "crosswalk differs from shared identities; review T-003 mapping first")
        require(hashlib.sha256(metadata).hexdigest()
                == "af9e839657ff16029fde74cf131e46dc46461b26e7f1b6a10e435f341d4926c7",
                FLEURS, "metadata differs from T-002 audited snapshot; review source before sampling")
        require(hashlib.sha256(licenses).hexdigest()
                == "6e6c79efdb5f2710e8570d30054745a6b3c19585efcea4e83348e0bb8981eea5",
                "LICENSES.md", "pack license declaration changed; review before exporting")
        _, rows = csv_rows(metadata, FLEURS, {
            "file", "language", "lang_config", "iso639_1", "fleurs_id", "gender",
            "duration_sec", "transcription", "raw_transcription",
        })
        # Preserve references verbatim rather than csv_rows' whitespace-stripped values.
        original_rows = list(csv.DictReader(io.StringIO(metadata.decode("utf-8-sig"), newline="")))
        require(len(rows) == 560, FLEURS, "expected all 560 metadata rows")
        by_language: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
        paths: set[str] = set()
        for row, original in zip(rows, original_rows, strict=True):
            identity = language_id_for_name(row["language"]).value
            expected = LANGUAGE_MAP[identity]
            require(row["lang_config"] == expected["fleurs_config"]
                    and row["iso639_1"] == expected["dataset_language_code"], FLEURS,
                    f"{identity}: config/code mismatch")
            sentence_id = integer(row["fleurs_id"], FLEURS, "fleurs_id")
            require(sentence_id not in by_language[identity], FLEURS,
                    f"{identity}-{sentence_id}: duplicate language/ID")
            relative = safe_relative(row["file"])
            require(relative == f"audio/{row['lang_config']}/{row['lang_config']}_{sentence_id}.flac",
                    FLEURS, f"{identity}-{sentence_id}: unexpected audio path")
            require(relative not in paths, FLEURS, "duplicate audio reference")
            paths.add(relative)
            for key in ("transcription", "raw_transcription"):
                require(bool(original[key].strip()), FLEURS, f"{identity}-{sentence_id}: empty {key}")
                row[key] = original[key]
            require(row["gender"] in {"female", "male", "other"}, FLEURS, "unknown gender label")
            duration = float(row["duration_sec"])
            audio_path = f"{DATASET_DIR}/{relative}"
            with source.open(audio_path) as stream:
                info = flac_info(stream.read(42), audio_path)
            require(math.isfinite(duration) and duration > 0
                    and abs(duration - info["duration_sec"]) <= 0.02,
                    audio_path, "invalid duration or mismatch with FLAC header")
            by_language[identity][sentence_id] = row
        require(len(by_language) == 14 and all(len(group) == 40 for group in by_language.values()),
                FLEURS, "expected 14 languages with 40 unique IDs each")
        pilots = sorted(language_id_for_name(name).value for name in PILOT)
        require(set(pilots) <= set(by_language), FLEURS, "required pilot language absent")
        common = sorted(set.intersection(*(set(by_language[key]) for key in pilots)))
        require(len(common) >= 8, FLEURS, "fewer than eight shared pilot IDs")
        selected = sorted(random.Random(2026).sample(common, 8))
        samples: list[Sample] = []
        assets: list[dict] = []
        for identity in pilots:
            for sentence_id in selected:
                row = by_language[identity][sentence_id]
                source_path_relative = f"{DATASET_DIR}/{row['file']}"
                audio = source.read(source_path_relative)
                samples.append(Sample(
                    sample_id=f"{identity}-{sentence_id}", language_id=identity, fleurs_id=sentence_id,
                    audio_path=row["file"], reference_transcript=row["transcription"],
                    raw_reference_transcript=row["raw_transcription"], gender=row["gender"],
                    duration_sec=float(row["duration_sec"]),
                ))
                assets.append({"sample_id": samples[-1].sample_id, "source_path": source_path_relative,
                               "audio_path": row["file"], "size_bytes": len(audio),
                               "sha256": hashlib.sha256(audio).hexdigest()})
        provenance = {
            "dataset": "FLEURS, supplied UNHEARD challenge subset",
            "attribution": "Google; Conneau et al. (2022), FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech",
            "source_url": "https://huggingface.co/datasets/google/fleurs",
            "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "modifications": "Selected 48 supplied FLAC files copied byte-for-byte; references preserved verbatim; no resampling, translation or normalization. Pack conversion history unknown.",
            "asset_review": "Curated FLEURS only; pack declaration and T-002 upstream review support CC BY 4.0; source/license/attribution/modification notice included",
            "metadata_file": FLEURS, "metadata_sha256": hashlib.sha256(metadata).hexdigest(),
            "crosswalk_sha256": hashlib.sha256(crosswalk).hexdigest(),
            "pack_license_sha256": hashlib.sha256(licenses).hexdigest(),
            "language_map_sha256": hashlib.sha256(mapping_bytes).hexdigest(),
            "metadata_row_count": str(len(rows)), "pilot_language_count": str(len(pilots)),
            "common_id_count": str(len(common)), "selected_id_count": "8", "selected_sample_count": "48",
            "sampling_algorithm": "sorted(random.Random(2026).sample(sorted(common_integer_ids), 8)); language_id then numeric fleurs_id order",
            "gender_counts": json.dumps({key: dict(Counter(s.gender for s in samples if s.language_id == key)) for key in pilots}, sort_keys=True),
            "limitations": "Exploratory n=8 per language; scripts and gender distributions differ; Urdu/Punjabi/Arabic are female-labelled only in this pack; no ward residence or recognition-performance inference",
            "experiment_status": "not_tested; no provider requests or outcome-dependent resampling",
        }
        selection = {"seed": 2026, "strategy": "common_fleurs_ids_random_sample", "ids": selected}
        frozen_content = {"schema_version": "1.0", "source": provenance, "selection": selection,
                          "samples": [sample.model_dump(mode="json") for sample in samples], "assets": assets}
        selection_sha = hashlib.sha256(canonical(frozen_content)).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()
        if MANIFEST.exists():
            frozen = json.loads(MANIFEST.read_bytes())
            require(frozen.get("selection_sha256") == selection_sha
                    and {key: frozen.get(key) for key in frozen_content} == frozen_content,
                    str(MANIFEST), "frozen selection/source/audio differs; refusing replacement or resampling")
            timestamp = frozen.get("generated_at_utc")
        artifact = Samples(schema_version="1.0", generated_at_utc=timestamp,
                           source={**provenance, "selection_sha256": selection_sha},
                           selection=selection, samples=samples)
        manifest = {**frozen_content, "generated_at_utc": timestamp, "selection_sha256": selection_sha}
        # Freeze before exporting any assets or running future experiments.
        if not MANIFEST.exists():
            MANIFEST.parent.mkdir(parents=True, exist_ok=True)
            with MANIFEST.open("xb") as stream:
                stream.write(json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
        for asset in assets:
            audio = source.read(asset["source_path"])
            require(hashlib.sha256(audio).hexdigest() == asset["sha256"], asset["source_path"],
                    "audio changed during export")
            target = PUBLIC / asset["audio_path"]
            require(not target.is_symlink() and target.resolve().is_relative_to(PUBLIC.resolve()),
                    str(target), "public audio path escapes public directory")
            atomic_write(target, audio)
        attribution = (f"{provenance['attribution']}\nSource: {provenance['source_url']}\n"
                       f"License: CC BY 4.0 — {provenance['license_url']}\n"
                       f"Modifications: {provenance['modifications']}\n"
                       f"Selection SHA-256: {selection_sha}\n"
                       "Only the 48 sample paths listed in data/samples.v1.json are part of this selection.\n")
        atomic_write(PUBLIC / "audio/FLEURS_ATTRIBUTION.txt", attribution.encode("utf-8"))
        atomic_write(PUBLIC / "data/samples.v1.json", (artifact.model_dump_json(indent=2) + "\n").encode("utf-8"))
        return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=os.environ.get("UNHEARD_DATA_ROOT"),
                        help="Explicit ZIP or exact extracted pack root (or UNHEARD_DATA_ROOT)")
    args = parser.parse_args()
    if not args.source:
        parser.error("supply --source or UNHEARD_DATA_ROOT; .env is not loaded automatically")
    try:
        artifact = sample_fleurs(Path(args.source))
        print(f"Frozen 48 samples; IDs {artifact.selection.ids}; SHA-256 {artifact.source['selection_sha256']}")
        print("Exported samples.v1.json, 48 curated FLACs and FLEURS_ATTRIBUTION.txt; no API requests.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"FLEURS sampling failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
