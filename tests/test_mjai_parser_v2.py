"""
mjai 牌谱解析测试

重点验证事件流重建：每个 hora 必须使用发生当下的手牌/副露快照。
"""

import json

from scripts.mjai_parser_v2 import MjaiParser
from scripts.majsoul_parser import MajsoulRecordParser


def write_mjai(tmp_path, events):
    path = tmp_path / "sample.mjson"
    path.write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in events),
        encoding="utf-8",
    )
    return path


def write_text(tmp_path, content):
    path = tmp_path / "sample.mjlog"
    path.write_text(content, encoding="utf-8")
    return path


def test_hora_uses_snapshot_from_its_own_round(tmp_path):
    events = [
        {"type": "start_kyoku", "oya": 0, "dora_marker": "1m"},
        {
            "type": "haipai",
            "actor": 0,
            "pais": [
                "1m", "2m", "3m",
                "4p", "5p", "6p",
                "7s", "8s", "9s",
                "1s", "1s", "1s",
                "2s",
            ],
        },
        {"type": "dahai", "actor": 1, "pai": "3s"},
        {"type": "hora", "actor": 0, "target": 1, "pai": "3s"},
        {"type": "end_kyoku"},
        {"type": "start_kyoku", "oya": 1, "dora_marker": "1p"},
        {
            "type": "haipai",
            "actor": 2,
            "pais": [
                "2m", "3m", "4m",
                "2p", "3p", "4p",
                "2s", "3s", "4s",
                "6s", "7s", "8s",
                "5m",
            ],
        },
        {"type": "tsumo", "actor": 2, "pai": "5m"},
        {"type": "hora", "actor": 2, "target": 2, "pai": "5m"},
    ]
    parser = MjaiParser()

    result = parser.analyze_file(str(write_mjai(tmp_path, events)))

    assert result["total_hora"] == 2
    assert result["valid_hora"] == 2
    assert result["results"][0]["actor"] == 0
    assert result["results"][0]["is_tsumo"] is False
    assert result["results"][0]["winning_tile"] == "3s"
    assert result["results"][0]["hand"] == [
        "1m", "2m", "3m",
        "4p", "5p", "6p",
        "7s", "8s", "9s",
        "1s", "1s", "1s",
        "2s",
    ]
    assert result["results"][1]["actor"] == 2
    assert result["results"][1]["is_tsumo"] is True
    assert result["results"][1]["winning_tile"] == "5m"
    assert result["results"][1]["hand"].count("5m") == 1


def test_hora_snapshot_includes_melds_and_removes_consumed_tiles(tmp_path):
    events = [
        {"type": "start_kyoku", "oya": 0, "dora_marker": "1m"},
        {
            "type": "haipai",
            "actor": 0,
            "pais": [
                "1m", "2m", "3m",
                "4p", "5p", "6p",
                "7s", "8s", "9s",
                "1s", "P", "P", "4m",
            ],
        },
        {"type": "dahai", "actor": 1, "pai": "P"},
        {"type": "pon", "actor": 0, "target": 1, "pai": "P", "consumed": ["P", "P"]},
        {"type": "dahai", "actor": 0, "pai": "4m"},
        {"type": "dahai", "actor": 2, "pai": "1s"},
        {"type": "hora", "actor": 0, "target": 2, "pai": "1s"},
    ]
    parser = MjaiParser()

    result = parser.analyze_file(str(write_mjai(tmp_path, events)))

    assert result["valid_hora"] == 1
    hora = result["results"][0]
    assert hora["is_valid"] is True
    assert hora["hand"] == [
        "1m", "2m", "3m",
        "4p", "5p", "6p",
        "7s", "8s", "9s",
        "1s",
    ]
    assert hora["melds"] == [["白", "白", "白"]]
    assert "役牌：三元牌" in hora["yaku_list"]


def test_round_wind_from_golden_log_text_is_passed_to_validator(tmp_path):
    content = "\n".join([
        '{"type":"start_kyoku","oya":2,"dora_marker":"E"}',
        'S-3 kyoku 0 honba  dora_marker: E  ',
        '{"type":"haipai","actor":2,"pais":["S","S","3m","4m","5m","2p","2p","3p","4p","4p","5p","5p","1m"]}',
        '{"type":"dahai","actor":0,"pai":"S"}',
        '{"type":"pon","actor":2,"target":0,"pai":"S","consumed":["S","S"]}',
        '{"type":"dahai","actor":2,"pai":"1m"}',
        '{"type":"dahai","actor":0,"pai":"3p"}',
        '{"type":"hora","actor":2,"target":0,"pai":"3p"}',
    ])
    parser = MjaiParser()

    result = parser.analyze_file(str(write_text(tmp_path, content)))

    assert result["valid_hora"] == 1
    assert result["results"][0]["round_wind"] == 28
    assert "役牌：场风牌" in result["results"][0]["yaku_list"]


class FakeFan:
    def __init__(self, name, val, fan_id):
        self.name = name
        self.val = val
        self.id = fan_id


class FakeHule:
    seat = 0
    zimo = False
    qinjia = False
    hand = ["1m", "2m", "3m"]
    hu_tile = "3m"
    ming = []
    doras = []
    li_doras = []
    fans = [FakeFan("立直", 1, 1)]
    fu = 30
    point_rong = 1000
    point_zimo_qin = 0
    point_zimo_xian = 0
    count = 1


class FakeHuleData:
    hules = [FakeHule()]


def test_majsoul_hora_result_marks_trusted_external_validation_mode():
    parser = MajsoulRecordParser()

    result = parser.validate_hora(FakeHuleData())[0]

    assert result["is_valid"] is True
    assert result["validation_mode"] == "trusted_external_result"
