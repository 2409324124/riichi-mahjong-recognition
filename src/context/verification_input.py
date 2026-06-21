from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VerificationInput:
    """Unified local-validator input reconstructed from a game log."""

    hand_tiles: List[str]
    melds: List[List[str]]
    winning_tile: str
    win_actor: int
    from_actor: Optional[int]
    is_tsumo: bool
    dora_indicators: List[str]
    ura_dora_indicators: List[str]
    round_wind: int
    seat_wind: int
    honba: int
    riichi_sticks: int
    dealer: int
    source: str
    is_riichi: bool = False
    is_double_riichi: bool = False
    is_ippatsu: bool = False
    is_haitei: bool = False
    is_houtei: bool = False
    is_rinshan: bool = False
    is_chankan: bool = False
    extra_flags: dict = field(default_factory=dict)
