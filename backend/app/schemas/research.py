from __future__ import annotations

import json
import math
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator, model_validator

LANGUAGE_MAP = json.loads((Path(__file__).resolve().parents[3] / "shared/language_map.json").read_text(encoding="utf-8"))["languages"]
LanguageId = StrEnum("LanguageId", {name: name for name in LANGUAGE_MAP})


def language_id_for_name(display_name: str) -> LanguageId:
    for identity, row in LANGUAGE_MAP.items():
        if row["display_name"] == display_name:
            return LanguageId(identity)
    raise ValueError(f"Unknown source language: {display_name}")


class CoverageStatus(StrEnum):
    no_task_audio = "no_task_audio"
    has_task_audio = "has_task_audio"


class ExperimentStatus(StrEnum):
    not_tested = "not_tested"
    completed = "completed"
    technical_error = "technical_error"
    unsupported = "unsupported"
    incompatible_output = "incompatible_output"


class RecoveryState(StrEnum):
    select_language = "select_language"
    ready = "ready"
    transcribing = "transcribing"
    confirm = "confirm"
    accepted = "accepted"
    retry_or_refer = "retry_or_refer"
    referral = "referral"


class Origin(StrEnum):
    live = "live"
    saved = "saved"


class MapMetric(StrEnum):
    count = "count"
    share = "share"


Count = Annotated[StrictInt, Field(ge=0)]
WardId = Annotated[StrictInt, Field(ge=1, le=11)]
Ratio = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Percent = Annotated[Ratio, Field(le=100)]


def unique(values: list, label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label}")


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Artifact(Model):
    schema_version: Literal["1.0"]
    generated_at_utc: StrictStr | None
    source: dict[str, StrictStr]
    is_fixture: StrictBool = False
    fixture_label: StrictStr | None = None

    @model_validator(mode="after")
    def provenance(self) -> Self:
        if not self.source:
            raise ValueError("Source provenance is required")
        if self.is_fixture and (not self.fixture_label or not self.fixture_label.startswith("MOCK")):
            raise ValueError("Fixtures require an explicit MOCK label")
        if self.generated_at_utc is None:
            if not self.is_fixture:
                raise ValueError("Only labelled fixtures may omit generation time")
        else:
            value = self.generated_at_utc
            if not value.endswith(("Z", "+00:00")):
                raise ValueError("generated_at_utc must be an ISO UTC timestamp")
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        return self


class RequestCounts(Model):
    minds14: Count
    speech_massive: Count


class Language(Model):
    language_id: LanguageId
    display_name: StrictStr
    census_home_column: StrictStr | None
    city_home_speakers: Count | None
    coverage_status: CoverageStatus
    request_clip_counts: RequestCounts
    fleurs_config: StrictStr | None
    dataset_language_code: StrictStr
    pilot_selected: StrictBool

    @model_validator(mode="after")
    def identity(self) -> Self:
        for key, expected in LANGUAGE_MAP[self.language_id].items():
            if getattr(self, key) != expected:
                raise ValueError(f"{self.language_id}: incorrect {key}")
        has_audio = self.request_clip_counts.minds14 + self.request_clip_counts.speech_massive > 0
        if has_audio != (self.coverage_status == CoverageStatus.has_task_audio):
            raise ValueError("Coverage status disagrees with request counts")
        return self


class Languages(Artifact):
    languages: list[Language]

    @model_validator(mode="after")
    def identifiers(self) -> Self:
        unique([r.language_id for r in self.languages], "language_id")
        return self


class Ward(Model):
    ward_id: WardId
    population_language_base: Count | None
    gap_population: Count | None
    gap_share_pct: Percent | None
    home_speakers_by_language: dict[LanguageId, Count | None]

    @model_validator(mode="after")
    def share(self) -> Self:
        expected = (100 * self.gap_population / self.population_language_base
                    if self.population_language_base and self.gap_population is not None else None)
        if expected is None:
            if self.gap_share_pct is not None:
                raise ValueError("Unavailable denominator/count requires null share")
        elif self.gap_share_pct is None or not math.isclose(expected, self.gap_share_pct, abs_tol=1e-6):
            raise ValueError("Ward share disagrees with denominator")
        return self


class Wards(Artifact):
    source_file: Literal["01_people_census/derived/ward_language_profile_2021_corrected.csv"]
    missing_request_language_ids: list[LanguageId]
    wards: list[Ward]

    @model_validator(mode="after")
    def identifiers(self) -> Self:
        unique(self.missing_request_language_ids, "missing_request_language_id")
        unique([r.ward_id for r in self.wards], "ward_id")
        return self


class SampleIdentity(Model):
    sample_id: StrictStr
    language_id: LanguageId
    fleurs_id: Count

    @model_validator(mode="after")
    def identity(self) -> Self:
        if self.sample_id != f"{self.language_id}-{self.fleurs_id}":
            raise ValueError("sample_id must match language_id and fleurs_id")
        return self


class Sample(SampleIdentity):
    audio_path: StrictStr
    raw_reference_transcript: StrictStr
    reference_transcript: StrictStr
    gender: Literal["female", "male", "other"]
    duration_sec: Annotated[Ratio, Field(gt=0)] | None

    @field_validator("audio_path")
    @classmethod
    def safe_audio(cls, value: str) -> str:
        if (not value.startswith("audio/") or "\\" in value or ":" in value
                or any(p in {"", ".", ".."} for p in value.split("/"))):
            raise ValueError("Expected relative audio/ asset path")
        return value


class Selection(Model):
    seed: Literal[2026]
    strategy: Literal["common_fleurs_ids_random_sample"]
    ids: list[Count]

    @model_validator(mode="after")
    def identifiers(self) -> Self:
        unique(self.ids, "selection ID")
        if self.ids != sorted(self.ids):
            raise ValueError("Selection IDs must be sorted numerically")
        return self


class Samples(Artifact):
    selection: Selection
    samples: list[Sample]

    @model_validator(mode="after")
    def identifiers(self) -> Self:
        unique([r.sample_id for r in self.samples], "sample_id")
        if any(r.fleurs_id not in self.selection.ids for r in self.samples):
            raise ValueError("Sample ID is absent from selection")
        return self


class Outcome(Model):
    status: ExperimentStatus
    transcript_raw: StrictStr | None
    cer: Ratio | None
    wer: Ratio | None
    request_id: StrictStr | None
    language_hint: StrictStr | None = None

    @model_validator(mode="after")
    def missing_metrics(self) -> Self:
        if self.status != ExperimentStatus.completed and (self.cer is not None or self.wer is not None):
            raise ValueError("Non-completed outcomes must have null CER/WER")
        return self


class ExperimentProvenance(Model):
    source_dataset: StrictStr
    evaluated_at_utc: StrictStr | None


class Experiment(SampleIdentity):
    auto: Outcome
    guided: Outcome
    paired_delta_cer: Number | None
    provenance: ExperimentProvenance

    @model_validator(mode="after")
    def pair(self) -> Self:
        expected = (self.auto.cer - self.guided.cer
                    if self.auto.cer is not None and self.guided.cer is not None else None)
        if expected is None:
            if self.paired_delta_cer is not None:
                raise ValueError("Unpaired outcomes require null delta")
        elif self.paired_delta_cer is None or not math.isclose(expected, self.paired_delta_cer, abs_tol=1e-9):
            raise ValueError("Paired delta must equal auto CER minus guided CER")
        return self


class Summary(Model):
    language_id: LanguageId
    n_selected: Count
    n_auto_completed: Count
    n_guided_completed: Count
    n_paired: Count
    mean_auto_cer: Ratio | None
    mean_guided_cer: Ratio | None
    mean_delta_cer: Number | None
    improved_count: Count
    worsened_count: Count
    unchanged_count: Count
    unpaired_reasons: dict[ExperimentStatus, Count]

    @model_validator(mode="after")
    def counts(self) -> Self:
        if not (self.n_paired <= min(self.n_auto_completed, self.n_guided_completed)
                and max(self.n_auto_completed, self.n_guided_completed) <= self.n_selected
                and self.improved_count + self.worsened_count + self.unchanged_count == self.n_paired):
            raise ValueError("Inconsistent summary counts")
        for count, metric in [(self.n_auto_completed, self.mean_auto_cer), (self.n_guided_completed, self.mean_guided_cer), (self.n_paired, self.mean_delta_cer)]:
            if count == 0 and metric is not None:
                raise ValueError("Empty summary requires null metric")
        return self


class ModelInfo(Model):
    provider: Literal["elevenlabs"]
    model_id: StrictStr | None
    api_version: StrictStr | None


class Experiments(Artifact):
    model: ModelInfo
    records: list[Experiment]
    summaries: list[Summary]

    @model_validator(mode="after")
    def identifiers(self) -> Self:
        unique([r.sample_id for r in self.records], "experiment sample_id")
        unique([r.language_id for r in self.summaries], "summary language_id")
        return self


class Recommendation(Model):
    language_id: LanguageId
    reason: StrictStr
    city_home_speakers: Count
    rank: Annotated[Count, Field(ge=1)]
    suggested_action: StrictStr
    suggested_ward_ids: list[WardId]
    limitations: list[StrictStr]

    @model_validator(mode="after")
    def identifiers(self) -> Self:
        unique(self.suggested_ward_ids, "suggested ward_id")
        return self


class Recommendations(Artifact):
    method: Literal["missing_task_audio_then_city_home_speakers_desc"]
    items: list[Recommendation]

    @model_validator(mode="after")
    def identifiers(self) -> Self:
        unique([r.language_id for r in self.items], "recommendation language_id")
        unique([r.rank for r in self.items], "recommendation rank")
        return self


ARTIFACTS = {"languages": Languages, "wards": Wards, "samples": Samples,
             "experiments": Experiments, "recommendations": Recommendations}


def validate_artifact(kind: str, data: object, *, allow_fixtures: bool = False) -> Artifact:
    if kind not in ARTIFACTS:
        raise ValueError(f"Unknown artifact: {kind}")
    result = ARTIFACTS[kind].model_validate(data)
    if result.is_fixture and not allow_fixtures:
        raise ValueError("MOCK fixture cannot be loaded as research data")
    return result


def validate_bundle(data: dict, *, allow_fixtures: bool = False) -> dict[str, Artifact]:
    if set(data) != set(ARTIFACTS):
        raise ValueError("Bundle requires all five research artifacts")
    result = {k: validate_artifact(k, v, allow_fixtures=allow_fixtures) for k, v in data.items()}
    languages = {r.language_id for r in result["languages"].languages}
    wards = {r.ward_id for r in result["wards"].wards}
    samples = {r.sample_id for r in result["samples"].samples}
    referenced = set(result["wards"].missing_request_language_ids)
    for ward in result["wards"].wards:
        referenced.update(ward.home_speakers_by_language)
    for collection in (result["samples"].samples, result["experiments"].records,
                       result["experiments"].summaries, result["recommendations"].items):
        referenced.update(r.language_id for r in collection)
    if not referenced <= languages:
        raise ValueError("Language reference absent from languages artifact")
    if any(r.sample_id not in samples for r in result["experiments"].records):
        raise ValueError("Experiment references missing sample")
    if any(not set(r.suggested_ward_ids) <= wards for r in result["recommendations"].items):
        raise ValueError("Recommendation references missing ward")
    return result
