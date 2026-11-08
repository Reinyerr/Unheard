"""Read-only real export checks; corruptions live only in temporary directories."""
import json
from pathlib import Path
import subprocess
import sys

import pytest
from prepare_census import gap_share_pct, population_base
from prepare_coverage import top_wards
from validate_exports import ROOT, validate_exports

DATA = ROOT / "frontend/public/data"


def test_generated_bundle_and_independent_ward_ratios():
    bundle = validate_exports(DATA)
    for ward in bundle["wards"].wards:
        assert ward.gap_share_pct == pytest.approx(100 * ward.gap_population / ward.population_language_base)
    assert top_wards(bundle["wards"].wards, "urdu", by_share=False)[0][0] == 10
    mapping = {r.language_id: r.dataset_language_code for r in bundle["languages"].languages}
    assert mapping["cantonese"] == "yue" and mapping["mandarin_chinese"] == "zh"


@pytest.mark.parametrize("base", [None, 0, -1])
def test_unavailable_denominator(base):
    assert gap_share_pct(10, base) is None
    assert population_base("" if base is None else str(base)) is None


def test_independent_rankings_and_stable_ties():
    from app.schemas.research import Ward
    wards = [Ward(ward_id=i, population_language_base=base, gap_population=None,
                  gap_share_pct=None, home_speakers_by_language={"urdu": count})
             for i, base, count in [(3, None, 30), (2, 100, 20), (1, 1000, 20)]]
    assert [i for i, _ in top_wards(wards, "urdu", by_share=False)] == [3, 1, 2]
    assert [i for i, _ in top_wards(wards, "urdu", by_share=True)] == [2, 1]


def test_invalid_export_exits_nonzero_with_actionable_error(tmp_path):
    for path in DATA.glob("*.v1.json"):
        value = json.loads(path.read_bytes())
        if path.name == "wards.v1.json":
            value["wards"] = value["wards"][:-1]
        (tmp_path / path.name).write_text(json.dumps(value), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_exports.py"),
                             "--data-dir", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Recommendation references missing ward" in result.stderr


def test_fixtures_cannot_be_released_as_research():
    from app.schemas.research import validate_artifact
    fixture = json.loads((DATA / "fixtures/samples.v1.json").read_bytes())
    with pytest.raises(ValueError, match="MOCK fixture"):
        validate_artifact("samples", fixture)
    assert validate_artifact("samples", fixture, allow_fixtures=True).is_fixture
