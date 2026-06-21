import json
from types import SimpleNamespace

from scripts.majsoul_strict_validator import validate_records, write_jsonl


def _new_round():
    return SimpleNamespace(
        chang=0,
        ju=0,
        ben=0,
        doras=[],
        dora="1m",
        liqibang=0,
        scores=[25000, 25000, 25000, 25000],
        left_tile_count=70,
        tiles0=[],
        tiles1=[],
        tiles2=[],
        tiles3=[],
    )


def _hule(ming=None, fans=None):
    return SimpleNamespace(
        seat=0,
        zimo=False,
        hand=["1m", "1m", "1m", "2m", "3m", "4m", "5p", "5p", "5p", "6s", "7s", "8s", "E"],
        ming=ming or [],
        hu_tile="E",
        fans=fans or [],
        fu=30,
        point_rong=1000,
        point_zimo_qin=0,
        point_zimo_xian=0,
        doras=[],
        li_doras=[],
    )


def test_strict_diff_jsonl_shape(tmp_path):
    records = [
        {"name": "RecordNewRound", "data": _new_round()},
        {"name": "RecordHule", "data": SimpleNamespace(hules=[_hule()])},
    ]
    rows = validate_records(records, uuid="anonymous-fixture")
    output = tmp_path / "strict_diff.jsonl"

    write_jsonl(rows, output)
    decoded = json.loads(output.read_text(encoding="utf-8").strip())

    assert set(decoded) >= {
        "uuid",
        "round_index",
        "hule_index",
        "seat",
        "validation_mode",
        "our_result",
        "majsoul_result",
        "context_flags",
        "failure_type",
    }
    assert decoded["validation_mode"] == "strict_local_validator"
    assert set(decoded["our_result"]) >= {
        "shape_valid",
        "is_valid",
        "han",
        "fu",
        "points",
        "yaku",
        "error_type",
        "error",
    }


def test_strict_diff_classifies_unknown_hule_meld_as_unsupported_event():
    records = [
        {"name": "RecordNewRound", "data": _new_round()},
        {"name": "RecordHule", "data": SimpleNamespace(hules=[_hule(ming=["unknown-meld"])])},
    ]

    rows = validate_records(records, uuid="anonymous-fixture")

    assert rows[0]["failure_type"] == "unsupported_event"
    assert rows[0]["our_result"]["error_type"] == "unsupported_event"
