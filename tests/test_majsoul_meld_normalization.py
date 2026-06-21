from types import SimpleNamespace

from src.majsoul.meld_normalization import (
    StructuredMeld,
    normalize_hule_ming,
    normalize_record_meld,
)


def test_normalize_chipenggang_chi_record():
    record = SimpleNamespace(seat=1, type=0, tiles=["3m", "4m", "5m"], froms=[1, 0, 1])

    meld = normalize_record_meld("RecordChiPengGang", record)

    assert meld == StructuredMeld(
        seat=1,
        meld_type="chi",
        tiles=["3m", "4m", "5m"],
        called_tile="4m",
        from_seat=0,
        is_open=True,
        source="RecordChiPengGang",
    )


def test_normalize_chipenggang_pon_record():
    record = SimpleNamespace(seat=2, type=1, tiles=["E", "E", "E"], froms=[2, 3, 2])

    meld = normalize_record_meld("RecordChiPengGang", record)

    assert meld.meld_type == "pon"
    assert meld.called_tile == "E"
    assert meld.from_seat == 3
    assert meld.is_open is True


def test_normalize_angang_and_kakan_records():
    ankan = normalize_record_meld(
        "RecordAnGangAddGang",
        SimpleNamespace(seat=0, type=0, tiles="7p"),
    )
    kakan = normalize_record_meld(
        "RecordAnGangAddGang",
        SimpleNamespace(seat=0, type=1, tiles="7p"),
    )

    assert ankan.meld_type == "ankan"
    assert ankan.tiles == ["7p", "7p", "7p", "7p"]
    assert ankan.is_open is False
    assert kakan.meld_type == "kakan"
    assert kakan.tiles == ["7p", "7p", "7p", "7p"]
    assert kakan.is_open is True


def test_normalize_hule_ming_strings():
    pon = normalize_hule_ming("kezi(E,E,E)", seat=0)
    chi = normalize_hule_ming("shunzi(3m,5m,4m)", seat=0)
    kan = normalize_hule_ming("gangzi(9s,9s,9s,9s)", seat=0)

    assert pon.meld_type == "pon"
    assert pon.tiles == ["E", "E", "E"]
    assert chi.meld_type == "chi"
    assert chi.tiles == ["3m", "4m", "5m"]
    assert kan.meld_type == "kan"
    assert kan.tiles == ["9s", "9s", "9s", "9s"]


def test_unknown_meld_is_explicit_not_empty():
    meld = normalize_hule_ming("not-a-known-meld", seat=3)

    assert meld.meld_type == "unknown"
    assert meld.tiles == []
    assert meld.error is not None
