"""Synthetic text only: never exported as research outcomes."""
import pytest
from app.schemas.research import Experiment, Outcome, Sample
from calculate_metrics import error_ratio, evaluate, normalize, summarize


def sample(language="english", text="abc"):
    return Sample(sample_id=f"{language}-1", language_id=language, fleurs_id=1,
                  audio_path="audio/mock.flac", raw_reference_transcript=text,
                  reference_transcript=text, gender="other", duration_sec=None)


@pytest.mark.parametrize("reference,hypothesis,expected", [("abc", "adc", 1/3), ("hello", "", 1), ("a", "aaaa", 3), ("", "a", None)])
def test_cer_edges(reference, hypothesis, expected):
    assert error_ratio(reference, hypothesis) == pytest.approx(expected) if expected is not None else error_ratio(reference, hypothesis) is None


@pytest.mark.parametrize("language,text", [("urdu", "سلام"), ("arabic", "مَرْحَبًا"), ("cantonese", "你好"), ("mandarin_chinese", "你好")])
def test_scripts_preserved_and_wer_unavailable(language, text):
    outcome, _ = evaluate(sample(language, text), {"status": "completed", "transcript_raw": text}, [])
    assert normalize(text, language) == text
    assert outcome.cer == 0 and outcome.wer is None


def test_normalization_empty_and_incompatible_outputs():
    assert normalize("  HE\u0301LLO, WORLD!  ", "english") == "héllo world"
    empty, _ = evaluate(sample(text="hello"), {"status": "completed", "transcript_raw": ""}, [])
    assert empty.cer == empty.wer == 1
    wrong, details = evaluate(sample("urdu", "سلام"), {"status": "completed", "transcript_raw": "hello"}, [])
    assert wrong.status == "incompatible_output" and wrong.cer is None
    assert "unexpected_output_script" in details["flags"]
    blank, _ = evaluate(sample(text="!!!"), {"status": "completed", "transcript_raw": "hello"}, [])
    assert blank.cer is None


def test_pairs_exclude_failures_and_preserve_reasons():
    def outcome(status, cer=None):
        return Outcome(status=status, transcript_raw="mock" if status == "completed" else None, cer=cer, wer=None, request_id=None)
    records = [Experiment(sample_id=f"english-{i}", language_id="english", fleurs_id=i,
        auto=outcome("completed", .2), guided=guided, paired_delta_cer=delta,
        provenance={"source_dataset": "MOCK", "evaluated_at_utc": None})
        for i, (guided, delta) in enumerate([(outcome("completed", .1), .1), (outcome("technical_error"), None), (outcome("unsupported"), None)], 1)]
    result = summarize("english", records)
    assert result.n_selected == 3 and result.n_paired == result.improved_count == 1
    assert result.mean_delta_cer == pytest.approx(.1)
    assert result.unpaired_reasons == {"technical_error": 1, "unsupported": 1}
    with pytest.raises(ValueError, match="null CER/WER"):
        outcome("not_tested", 0)
