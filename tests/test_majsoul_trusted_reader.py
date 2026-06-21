from types import SimpleNamespace

from scripts.majsoul_parser import MajsoulRecordParser


def test_validate_hora_reports_trusted_external_result_mode():
    fan = SimpleNamespace(name="立直", val=1, id=1)
    hule = SimpleNamespace(
        seat=0,
        zimo=False,
        qinjia=True,
        hand=["1m", "1m", "1m", "2m", "3m", "4m", "5p", "5p", "5p", "6s", "7s", "8s", "E"],
        ming=[],
        hu_tile="E",
        fans=[fan],
        fu=30,
        point_rong=1000,
        point_zimo_qin=0,
        point_zimo_xian=0,
        count=1,
    )
    hule_data = SimpleNamespace(hules=[hule])

    results = MajsoulRecordParser().validate_hora(hule_data)

    assert results[0]["validation_mode"] == "trusted_external_result"
    assert results[0]["is_valid"] is True
    assert results[0]["points"] == 1000
