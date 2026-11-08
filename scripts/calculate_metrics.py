"""Offline CER/WER and paired export from recorded, frozen-sample outcomes.

Input is a T-008-style report, with one terminal attempt per sample/mode.
No provider requests, transcription retries or outcome-dependent sample selection.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
import unicodedata

from sample_fleurs import atomic_write
from app.services.elevenlabs_adapter import GUIDANCE_CANDIDATES, REPO, load_selection
from app.schemas.research import (
    Experiment, Experiments, ExperimentStatus, Outcome, Sample, Summary, validate_bundle,
)

POLICY = "nfc_codepoints_punctuation_space_english_casefold_v1"
SCRIPT = {"english": "LATIN", "urdu": "ARABIC", "arabic": "ARABIC",
          "punjabi": "GURMUKHI", "cantonese": "CJK", "mandarin_chinese": "CJK"}
CODE_ALIASES = {
    "english": {"en", "eng"}, "urdu": {"ur", "urd"}, "arabic": {"ar", "ara"},
    "punjabi": {"pa", "pan"}, "cantonese": {"yue"}, "mandarin_chinese": {"zh", "zho", "cmn"},
}


def normalize(text: str, language_id: str) -> str:
    text = unicodedata.normalize("NFC", text)
    if language_id == "english":
        text = text.casefold()
    return " ".join("".join(" " if unicodedata.category(ch).startswith("P") else ch
                            for ch in text).split())


def levenshtein(reference, hypothesis) -> int:
    """Unit edit costs, linear memory; units can be code points or word tokens."""
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for i, left in enumerate(reference, 1):
        current = [i]
        for j, right in enumerate(hypothesis, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]


def error_ratio(reference, hypothesis) -> float | None:
    return levenshtein(reference, hypothesis) / len(reference) if reference else None


def script_flags(reference: str, hypothesis: str, language_id: str) -> list[str]:
    expected = SCRIPT[language_id]
    ref_letters = [ch for ch in reference if unicodedata.category(ch).startswith("L")]
    hyp_letters = [ch for ch in hypothesis if unicodedata.category(ch).startswith("L")]
    def expected_count(letters):
        return sum(expected in unicodedata.name(ch, "") for ch in letters)
    flags = []
    if not ref_letters or expected_count(ref_letters) / len(ref_letters) < 0.5:
        flags.append("reference_script_requires_review")
    # Empty successful recognition remains comparable, with full-deletion CER.
    if hyp_letters and expected_count(hyp_letters) / len(hyp_letters) < 0.5:
        flags.append("unexpected_output_script")
    return flags


def evaluate(sample: Sample, attempt: dict | None, review_flags: list[str]) -> tuple[Outcome, dict]:
    details = {"sample_id": sample.sample_id, "reference_raw": sample.raw_reference_transcript,
               "reference_transcript": sample.reference_transcript, "flags": list(review_flags),
               "wer_policy": "english_whitespace_tokens" if sample.language_id == "english" else "unavailable_unvalidated_tokenization"}
    if attempt is None:
        return Outcome(status="not_tested", transcript_raw=None, cer=None, wer=None,
                       request_id=None), details
    details["flags"] = sorted(set(details["flags"] + attempt.get("review_flags", [])))
    status = ExperimentStatus(attempt["status"])
    text = attempt.get("transcript_raw")
    if text is not None and not isinstance(text, str):
        raise ValueError(f"{sample.sample_id}: transcript must be string or null")
    reference = normalize(sample.reference_transcript, sample.language_id)
    hypothesis = normalize(text, sample.language_id) if text is not None else None
    ref_chars = "".join(reference.split())
    hyp_chars = "".join(hypothesis.split()) if hypothesis is not None else None
    cer = wer = None
    if status == ExperimentStatus.completed:
        if text is None:
            raise ValueError(f"{sample.sample_id}: completed outcome has no transcript")
        details["flags"].extend(script_flags(reference, hypothesis, sample.language_id))
        detected = attempt.get("detected_language_code")
        if detected and detected not in CODE_ALIASES[sample.language_id]:
            details["flags"].append("detected_language_mismatch_requires_review")
        if not ref_chars:
            details["flags"].append("empty_normalized_reference")
        if details["flags"]:
            status = ExperimentStatus.incompatible_output
        else:
            cer = error_ratio(ref_chars, hyp_chars)
            if sample.language_id == "english":
                wer = error_ratio(reference.split(), hypothesis.split())
    details.update(reference_normalized=reference, hypothesis_normalized=hypothesis,
                   reference_character_count=len(ref_chars),
                   character_edits=levenshtein(ref_chars, hyp_chars) if cer is not None else None,
                   word_edits=levenshtein(reference.split(), hypothesis.split()) if wer is not None else None,
                   provider_status=attempt["status"], status=status.value,
                   cer=cer, wer=wer, transcript_raw=text, request_options=attempt.get("request_options"),
                   raw_response_path=attempt.get("raw_response_path"))
    return Outcome(status=status, transcript_raw=text, cer=cer, wer=wer,
                   request_id=attempt.get("request_id"),
                   language_hint=attempt.get("request_options", {}).get("language_code")), details


def summarize(language_id: str, records: list[Experiment]) -> Summary:
    auto = [r.auto.cer for r in records if r.auto.cer is not None]
    guided = [r.guided.cer for r in records if r.guided.cer is not None]
    paired = [r.paired_delta_cer for r in records if r.paired_delta_cer is not None]
    reasons = Counter()
    for record in records:
        if record.paired_delta_cer is None:
            # Count each exclusion status once per clip; multiple reasons can overlap.
            reasons.update({o.status for o in (record.auto, record.guided)
                            if o.status != ExperimentStatus.completed})
    tied = sum(math.isclose(delta, 0, abs_tol=1e-12) for delta in paired)
    return Summary(language_id=language_id, n_selected=len(records),
                   n_auto_completed=len(auto), n_guided_completed=len(guided), n_paired=len(paired),
                   mean_auto_cer=mean(auto) if auto else None,
                   mean_guided_cer=mean(guided) if guided else None,
                   mean_delta_cer=mean(paired) if paired else None,
                   improved_count=sum(delta > 1e-12 for delta in paired),
                   worsened_count=sum(delta < -1e-12 for delta in paired), unchanged_count=tied,
                   unpaired_reasons=dict(reasons))


def export_metrics(input_path: Path) -> Experiments:
    input_path = input_path.resolve()
    if not any(input_path.is_relative_to(REPO / folder) for folder in ("data/local", "data/processed")):
        raise ValueError("Outcome input must be local JSON under data/local or data/processed")
    raw = input_path.read_bytes()
    report = json.loads(raw)
    samples, assets, selection_sha = load_selection()
    if report.get("selection_sha256") != selection_sha:
        raise ValueError("Outcome selection hash disagrees with frozen samples")
    model_id = report.get("model_id")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError("Outcome report requires actual model_id")
    by_id = {sample.sample_id: sample for sample in samples.samples}
    attempts = {}
    raw_hashes = {}
    for attempt in report["attempts"]:
        identity, mode = attempt["sample_id"], attempt["mode"]
        if identity not in by_id or mode not in {"auto", "guided"} or (identity, mode) in attempts:
            raise ValueError("Unknown sample/mode or duplicate terminal attempt; resolve retries before export")
        if (attempt["language_id"] != by_id[identity].language_id
                or attempt["audio_sha256"] != assets[identity]["sha256"]
                or attempt["model_id"] != model_id
                or attempt["request_options"].get("model_id") != model_id):
            raise ValueError(f"{identity}: mismatched audio, identity or model provenance")
        hint = attempt["request_options"].get("language_code")
        if (mode == "auto" and hint is not None) or (mode == "guided" and not hint):
            raise ValueError(f"{identity}: request options disagree with condition")
        if attempt["status"] == "completed" and not (200 <= (attempt.get("http_status") or 0) < 300):
            raise ValueError(f"{identity}: completed outcome requires successful HTTP evidence")
        relative = attempt.get("raw_response_path")
        if relative:
            path = (REPO / relative).resolve()
            if not path.is_relative_to(REPO / "data/local"):
                raise ValueError("Raw response path must remain under data/local")
            response = path.read_bytes()
            raw_hashes[f"{identity}:{mode}"] = hashlib.sha256(response).hexdigest()
            if attempt["status"] == "completed" and json.loads(response).get("text") != attempt["transcript_raw"]:
                raise ValueError(f"{identity}: transcript disagrees with retained provider response")
        elif attempt["status"] == "completed":
            raise ValueError(f"{identity}: completed outcome requires retained raw response")
        attempts[identity, mode] = attempt
    manual_flags = {}
    for finding in report.get("response_review", {}).get("findings", []):
        if finding.get("comparability_status") == "incompatible_output":
            for mode in finding.get("modes", [finding.get("mode")]):
                manual_flags.setdefault((finding["sample_id"], mode), []).append("recorded_manual_script_review_exclusion")
    records, details = [], []
    for sample in samples.samples:
        auto_attempt, guided_attempt = (attempts.get((sample.sample_id, mode)) for mode in ("auto", "guided"))
        if auto_attempt and guided_attempt:
            auto_options = dict(auto_attempt["request_options"])
            guided_options = dict(guided_attempt["request_options"])
            guided_options.pop("language_code", None)
            if auto_options != guided_options:
                raise ValueError(f"{sample.sample_id}: paired conditions differ beyond language guidance")
        outcomes = {}
        for mode in ("auto", "guided"):
            outcome, detail = evaluate(sample, attempts.get((sample.sample_id, mode)),
                                       manual_flags.get((sample.sample_id, mode), []))
            outcomes[mode] = outcome
            details.append({"mode": mode, **detail})
        delta = (outcomes["auto"].cer - outcomes["guided"].cer
                 if outcomes["auto"].cer is not None and outcomes["guided"].cer is not None else None)
        dates = [a["finished_at_utc"] for a in (auto_attempt, guided_attempt) if a]
        records.append(Experiment(sample_id=sample.sample_id, language_id=sample.language_id,
                                  fleurs_id=sample.fleurs_id, **outcomes, paired_delta_cer=delta,
                                  provenance={"source_dataset": "FLEURS", "evaluated_at_utc": max(dates) if dates else None}))
    flags = {f"{d['sample_id']}:{d['mode']}": d["flags"] for d in details if d["flags"]}
    artifact = Experiments(
        schema_version="1.0", generated_at_utc=datetime.now(timezone.utc).isoformat(),
        source={
            "dataset": "FLEURS; Google / Conneau et al. (2022)",
            "source_url": "https://huggingface.co/datasets/google/fleurs",
            "license": "CC BY 4.0; https://creativecommons.org/licenses/by/4.0/",
            "selection_sha256": selection_sha, "outcome_input_sha256": hashlib.sha256(raw).hexdigest(),
            "metrics_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "policy": POLICY, "unicode_version": unicodedata.unidata_version,
            "normalization": "NFC; punctuation replaced with spaces; whitespace collapsed; English casefold only; CER removes whitespace; no transliteration, translation, diacritic removal or script conversion",
            "cer_units": "Unicode code points, combining marks retained; Levenshtein unit costs / reference length; uncapped ratios",
            "wer_policy": "English whitespace tokens only; other five languages null pending validated tokenization",
            "script_policy": "Expected script must represent >=50% of reference/output letters; detected-language mismatch and recorded manual exclusions block metrics. Empty successful transcript is scored. Same-script translation/Chinese variants require manual review.",
            "review_flags": json.dumps(flags, sort_keys=True),
            "raw_response_sha256": json.dumps(raw_hashes, sort_keys=True),
            "selected_sample_count": str(len(samples.samples)), "recorded_mode_count": str(len(attempts)),
            "summary_policy": "Unweighted per-clip means; completion counts mean comparable scored outcomes, not HTTP successes. Missing statuses counted once per clip/status; exclusions may overlap. Delta=autoCER-guidedCER; positive improves; tie tolerance 1e-12.",
            "limitations": "Exploratory pilot (n_selected=8 per language); inspect recorded/scored/paired counts for completeness. No population, ward or significance inference. Independent mode means may have different clip sets; mean_delta_cer uses paired clips only. No confidence intervals or general improvement claim.",
        },
        model={"provider": "elevenlabs", "model_id": model_id, "api_version": report.get("api_version")},
        records=records, summaries=[summarize(language, [r for r in records if r.language_id == language])
                                 for language in sorted(GUIDANCE_CANDIDATES)],
    )
    bundle = {kind: json.loads((REPO / f"frontend/public/data/{kind}.v1.json").read_bytes())
              for kind in ("languages", "wards", "samples", "recommendations")}
    validate_bundle({**bundle, "experiments": artifact.model_dump(mode="json")})
    audit = {"schema_version": "1.0", "generated_at_utc": artifact.generated_at_utc,
             "source": artifact.source, "input_path": str(input_path.relative_to(REPO)), "details": details}
    atomic_write(REPO / "data/processed/metric_details.json",
                 (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode())
    atomic_write(REPO / "frontend/public/data/experiments.v1.json",
                 (artifact.model_dump_json(indent=2) + "\n").encode())
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=REPO / "data/local/preflight_log.json")
    args = parser.parse_args()
    try:
        artifact = export_metrics(args.input)
        print(f"Exported {len(artifact.records)} frozen samples with explicit missing modes; full bundle schema validation passed.")
        for summary in artifact.summaries:
            print(f"{summary.language_id}: selected={summary.n_selected}, scored auto/guided="
                  f"{summary.n_auto_completed}/{summary.n_guided_completed}, paired={summary.n_paired}, "
                  f"mean delta CER={summary.mean_delta_cer}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Metrics export failed; public output not replaced: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
