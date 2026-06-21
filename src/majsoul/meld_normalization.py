from dataclasses import dataclass
import re
from typing import Any, List, Optional


@dataclass
class StructuredMeld:
    seat: int
    meld_type: str
    tiles: List[str]
    called_tile: Optional[str] = None
    from_seat: Optional[int] = None
    is_open: bool = True
    source: str = ""
    raw: Optional[str] = None
    error: Optional[str] = None


CHIPENGGANG_TYPE_MAP = {
    0: "chi",
    1: "pon",
    2: "kan",
}

ANGANG_ADDGANG_TYPE_MAP = {
    0: "ankan",
    1: "kakan",
    2: "ankan",
    3: "kakan",
}


def _as_tile_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(tile) for tile in value]


def _called_tile(tiles: List[str], froms: List[int], seat: int) -> tuple[Optional[str], Optional[int]]:
    for tile, from_seat in zip(tiles, froms):
        if from_seat != seat:
            return tile, from_seat
    return None, None


def normalize_record_meld(record_name: str, record_data: Any) -> StructuredMeld:
    seat = int(getattr(record_data, "seat", -1))
    source = record_name

    if record_name == "RecordChiPengGang":
        tiles = _as_tile_list(getattr(record_data, "tiles", []))
        froms = [int(from_seat) for from_seat in getattr(record_data, "froms", [])]
        called_tile, from_seat = _called_tile(tiles, froms, seat)
        meld_type = CHIPENGGANG_TYPE_MAP.get(
            int(getattr(record_data, "type", -1)), "unknown"
        )
        error = None if meld_type != "unknown" else "unknown RecordChiPengGang type"
        return StructuredMeld(
            seat=seat,
            meld_type=meld_type,
            tiles=tiles,
            called_tile=called_tile,
            from_seat=from_seat,
            is_open=True,
            source=source,
            error=error,
        )

    if record_name == "RecordAnGangAddGang":
        raw_tiles = _as_tile_list(getattr(record_data, "tiles", []))
        tiles = raw_tiles * 4 if len(raw_tiles) == 1 else raw_tiles
        meld_type = ANGANG_ADDGANG_TYPE_MAP.get(
            int(getattr(record_data, "type", -1)), "unknown"
        )
        error = None if meld_type != "unknown" else "unknown RecordAnGangAddGang type"
        return StructuredMeld(
            seat=seat,
            meld_type=meld_type,
            tiles=tiles,
            called_tile=tiles[0] if meld_type == "kakan" and tiles else None,
            from_seat=seat,
            is_open=meld_type != "ankan",
            source=source,
            error=error,
        )

    return StructuredMeld(
        seat=seat,
        meld_type="unknown",
        tiles=[],
        is_open=True,
        source=source,
        error=f"unsupported record type: {record_name}",
    )


def normalize_hule_ming(ming: str, seat: int) -> StructuredMeld:
    raw = ming
    ming = ming.strip()
    match = re.match(r"^(kezi|shunzi|gangzi)\(([^)]*)\)$", ming)
    if match:
        kind, body = match.groups()
        tiles = [tile.strip() for tile in body.split(",") if tile.strip()]
        if kind == "shunzi":
            tiles.sort(key=lambda tile: int(tile[0]) if tile and tile[0].isdigit() else 0)
        meld_type = {"kezi": "pon", "shunzi": "chi", "gangzi": "kan"}[kind]
        return StructuredMeld(
            seat=seat,
            meld_type=meld_type,
            tiles=tiles,
            called_tile=None,
            from_seat=None,
            is_open=True,
            source="HuleInfo.ming",
            raw=raw,
        )

    if "|" in ming:
        tiles = [tile.strip() for tile in ming.split("|") if tile.strip()]
        meld_type = "kan" if len(tiles) == 4 else "pon" if len(tiles) == 3 else "unknown"
        return StructuredMeld(
            seat=seat,
            meld_type=meld_type,
            tiles=tiles if meld_type != "unknown" else [],
            called_tile=None,
            from_seat=None,
            is_open=True,
            source="HuleInfo.ming",
            raw=raw,
            error=None if meld_type != "unknown" else "unsupported pipe meld shape",
        )

    return StructuredMeld(
        seat=seat,
        meld_type="unknown",
        tiles=[],
        called_tile=None,
        from_seat=None,
        is_open=True,
        source="HuleInfo.ming",
        raw=raw,
        error="unsupported hule ming format",
    )


def normalize_hule_melds(mings: List[str], seat: int) -> List[StructuredMeld]:
    return [normalize_hule_ming(ming, seat=seat) for ming in mings]
