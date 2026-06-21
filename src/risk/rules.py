from typing import Iterable, Mapping, Optional

from src.context import EAST, SOUTH, WEST


def normalize_tile(tile: str) -> str:
    if not tile:
        return tile
    tile = tile.strip()
    if tile in {"0m", "0p", "0s", "0M", "0P", "0S"}:
        return f"5{tile[-1].lower()}"
    if tile.lower() in {"5mr", "5pr", "5sr"}:
        return tile[:2].lower()
    return tile


def _tile_number_and_suit(tile: str) -> tuple[Optional[int], Optional[str]]:
    tile = normalize_tile(tile)
    if len(tile) != 2:
        return None, None
    try:
        number = int(tile[0])
    except ValueError:
        return None, None
    suit = tile[1]
    if suit not in {"m", "p", "s"} or not 1 <= number <= 9:
        return None, None
    return number, suit


def visible_count(tile: str, visible_tile_counts: Mapping[str, int]) -> int:
    return int(visible_tile_counts.get(normalize_tile(tile), 0))


def remaining_count(tile: str, visible_tile_counts: Mapping[str, int]) -> int:
    return max(0, 4 - visible_count(tile, visible_tile_counts))


def is_suji(tile: str, safe_tiles: Iterable[str]) -> bool:
    number, suit = _tile_number_and_suit(tile)
    if number is None or suit is None:
        return False

    normalized_safe_tiles = {normalize_tile(safe) for safe in safe_tiles}
    suji_anchors = []
    if number - 3 >= 1:
        suji_anchors.append(f"{number - 3}{suit}")
    if number + 3 <= 9:
        suji_anchors.append(f"{number + 3}{suit}")
    return any(anchor in normalized_safe_tiles for anchor in suji_anchors)


def is_kabe(tile: str, visible_tile_counts: Mapping[str, int]) -> bool:
    number, suit = _tile_number_and_suit(tile)
    if number is None or suit is None:
        return False
    neighbors = [n for n in (number - 1, number + 1) if 1 <= n <= 9]
    return any(visible_tile_counts.get(f"{neighbor}{suit}", 0) >= 4 for neighbor in neighbors)


def is_no_chance(tile: str, visible_tile_counts: Mapping[str, int]) -> bool:
    return is_kabe(tile, visible_tile_counts)


def is_double_no_chance(tile: str, visible_tile_counts: Mapping[str, int]) -> bool:
    number, suit = _tile_number_and_suit(tile)
    if number is None or suit is None:
        return False
    neighbors = [n for n in (number - 1, number + 1) if 1 <= n <= 9]
    return len(neighbors) == 2 and all(
        visible_tile_counts.get(f"{neighbor}{suit}", 0) >= 4 for neighbor in neighbors
    )


def is_aka_dora(tile: str) -> bool:
    lowered = tile.lower()
    return lowered in {"0m", "0p", "0s", "5mr", "5pr", "5sr"}


def is_yakuhai(tile: str, round_wind: int = EAST, seat_wind: int = EAST) -> bool:
    normalized = normalize_tile(tile)
    if normalized in {"白", "发", "中", "P", "F", "C"}:
        return True
    wind_to_tile = {"E": EAST, "S": SOUTH, "W": WEST, "N": 30}
    tile_id = wind_to_tile.get(normalized)
    return tile_id in {round_wind, seat_wind}
