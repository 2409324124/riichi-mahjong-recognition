from dataclasses import dataclass
from typing import Optional


@dataclass
class CandidateDiscardRiskFeature:
    """Rule features for one candidate discard against one target player."""

    actor: int
    candidate_tile: str
    target_player: int
    turn: int
    is_genbutsu: bool
    is_suji: bool
    is_kabe: bool
    is_no_chance: bool
    is_double_no_chance: bool
    visible_count: int
    remaining_count: int
    is_dora: bool
    is_aka_dora: bool
    is_yakuhai: bool
    target_riichi: bool
    target_meld_count: int
    target_is_dealer: bool
    target_discards_before: int
    true_can_ron: Optional[bool] = None
    true_loss_points: Optional[int] = None
