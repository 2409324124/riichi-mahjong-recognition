from dataclasses import dataclass
from typing import Iterable, List, Optional

from src.agent.validator import WinValidator
from src.game_logic.hand import Hand
from src.game_logic.tile import Tile


@dataclass
class RiskTruthLabel:
    true_can_ron: Optional[bool]
    true_loss_points: Optional[int]
    missing_reason: Optional[str] = None


def _tile_from_label(tile) -> Optional[Tile]:
    if isinstance(tile, Tile):
        return tile
    if not tile:
        return None
    tile = str(tile)
    if tile in {"P", "白"}:
        return Tile.from_string("白")
    if tile in {"F", "发"}:
        return Tile.from_string("发")
    if tile in {"C", "中"}:
        return Tile.from_string("中")
    if tile.lower() in {"0m", "0p", "0s", "5mr", "5pr", "5sr"}:
        return Tile.from_string(f"5{tile[-1].lower() if tile[0] == '0' else tile[1].lower()}")
    try:
        return Tile.from_string(tile)
    except ValueError:
        return None


def _to_tiles(tile_labels: Iterable) -> Optional[List[Tile]]:
    tiles = []
    for label in tile_labels:
        tile = _tile_from_label(label)
        if tile is None:
            return None
        tiles.append(tile)
    return tiles


def _meld_tile_count(melds: List[List[Tile]]) -> int:
    return sum(3 if len(meld) == 4 else len(meld) for meld in melds)


def evaluate_ron_truth(
    target_hand_tiles: Iterable,
    target_melds: Iterable[Iterable],
    candidate_tile,
    target_player: int,
    dealer: int,
    round_wind: int,
    seat_wind: int,
    is_riichi: bool = False,
) -> RiskTruthLabel:
    hand_tiles = _to_tiles(target_hand_tiles)
    if not hand_tiles:
        return RiskTruthLabel(None, None, "missing_target_hand_truth")

    melds = []
    for meld in target_melds:
        meld_tiles = _to_tiles(meld)
        if meld_tiles is None:
            return RiskTruthLabel(None, None, "unparseable_target_meld")
        melds.append(meld_tiles)

    if len(hand_tiles) + _meld_tile_count(melds) != 13:
        return RiskTruthLabel(None, None, "incomplete_target_hand_truth")

    winning_tile = _tile_from_label(candidate_tile)
    if winning_tile is None:
        return RiskTruthLabel(None, None, "unparseable_candidate_tile")

    hand = Hand.from_tiles(hand_tiles.copy())
    for meld in melds:
        hand.add_meld(meld)

    result = WinValidator().validate(
        hand=hand,
        winning_tile=winning_tile,
        is_tsumo=False,
        is_riichi=is_riichi,
        is_dealer=target_player == dealer,
        round_wind=round_wind,
        seat_wind=seat_wind,
    )
    if result.is_valid:
        return RiskTruthLabel(True, result.points, None)
    return RiskTruthLabel(False, None, None)
