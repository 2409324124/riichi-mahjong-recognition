from types import SimpleNamespace

from scripts.majsoul_strict_validator import validate_records


def test_strict_validator_classifies_unparsed_melds_as_unsupported_event():
    new_round = SimpleNamespace(
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
    hule = SimpleNamespace(
        seat=0,
        zimo=False,
        hand=["1m", "1m", "1m", "2m", "3m", "4m", "5p", "5p", "5p", "6s", "7s", "8s", "E"],
        ming=["unparsed-meld-format"],
        hu_tile="E",
        fans=[],
        fu=30,
        point_rong=1000,
        point_zimo_qin=0,
        point_zimo_xian=0,
        doras=[],
        li_doras=[],
    )
    records = [
        {"name": "RecordNewRound", "data": new_round},
        {"name": "RecordHule", "data": SimpleNamespace(hules=[hule])},
    ]

    rows = validate_records(records, uuid="unit")

    assert rows[0]["failure_type"] == "unsupported_event"
    assert rows[0]["our_result"]["error_type"] == "unsupported_event"
