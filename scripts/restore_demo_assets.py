"""Restore the existing frozen FLEURS audio from the audited ZIP, without rewriting research JSON.

Windows Git CRLF conversion can change the local language-map byte hash. Only
an exact LF reconstruction of the recorded original hash is accepted; the frozen
selection digest must still match in full. No provider evidence is reconstructed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import sample_fleurs as sampler
from app.schemas.research import validate_artifact


def verify_restoration(published: dict, candidate: dict, mapping: bytes) -> dict:
    source = dict(published["source"])
    expected = source.pop("selection_sha256")
    mapping_hash = source["language_map_sha256"]
    if mapping_hash not in {hashlib.sha256(mapping).hexdigest(),
                           hashlib.sha256(mapping.replace(b"\r\n", b"\n")).hexdigest()}:
        raise ValueError("language_map.json differs beyond Git CRLF conversion; restore original mapping")
    observed_source = dict(candidate["source"])
    observed_source["language_map_sha256"] = mapping_hash
    if observed_source != source:
        raise ValueError("Audited source provenance differs from the published frozen selection")
    if candidate["selection"] != published["selection"] or candidate["samples"] != published["samples"]:
        raise ValueError("Restored sample identities/references differ from the published selection")
    content = {key: candidate[key] for key in ("schema_version", "source", "selection", "samples", "assets")}
    content["source"] = source
    if hashlib.sha256(sampler.canonical(content)).hexdigest() != expected:
        raise ValueError("Restored asset hashes do not match the original frozen selection digest")
    return {**content, "selection_sha256": expected, "generated_at_utc": published["generated_at_utc"]}


def restore(source: Path) -> str:
    public, manifest_path = sampler.PUBLIC, sampler.MANIFEST
    published_bytes = (public / "data/samples.v1.json").read_bytes()
    published = validate_artifact("samples", json.loads(published_bytes)).model_dump(mode="json")
    # Use the existing audited sampler in isolation. Its outputs are compared
    # before any real local assets are installed; published JSON remains untouched.
    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary)
        try:
            sampler.PUBLIC, sampler.MANIFEST = stage / "public", stage / "manifest.json"
            sampler.sample_fleurs(source)
            candidate = json.loads(sampler.MANIFEST.read_bytes())
        finally:
            sampler.PUBLIC, sampler.MANIFEST = public, manifest_path
        restored = verify_restoration(published, candidate, (sampler.REPO / "shared/language_map.json").read_bytes())
        if manifest_path.exists() and json.loads(manifest_path.read_bytes()) != restored:
            raise ValueError("Existing local manifest differs; no replacement allowed")
        for asset in restored["assets"]:
            target = public / asset["audio_path"]
            if target.is_symlink() or not target.resolve().is_relative_to(public.resolve()):
                raise ValueError("Unsafe public asset destination")
        for asset in restored["assets"]:
            sampler.atomic_write(public / asset["audio_path"], (stage / "public" / asset["audio_path"]).read_bytes())
        provenance = restored["source"]
        attribution = (f"{provenance['attribution']}\nSource: {provenance['source_url']}\n"
                       f"License: CC BY 4.0 — {provenance['license_url']}\n"
                       f"Modifications: {provenance['modifications']}\n"
                       f"Selection SHA-256: {restored['selection_sha256']}\n"
                       "Only the 48 sample paths listed in data/samples.v1.json are part of this selection.\n")
        sampler.atomic_write(public / "audio/FLEURS_ATTRIBUTION.txt", attribution.encode("utf-8"))
        sampler.atomic_write(manifest_path, (json.dumps(restored, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return restored["selection_sha256"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    try:
        digest = restore(args.source)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Restoration failed: {exc}\n")
    print(f"Restored 48 verified FLACs, attribution and local manifest; selection {digest}. Research JSON unchanged; no provider requests.")


if __name__ == "__main__":
    main()
