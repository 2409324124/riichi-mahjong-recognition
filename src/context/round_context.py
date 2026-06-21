from dataclasses import dataclass, field
from typing import List, Optional


EAST = 27
SOUTH = 28
WEST = 29
NORTH = 30


@dataclass
class RoundContext:
    """Round-level public context shared by validators and feature builders."""

    chang: int
    ju: int
    honba: int
    dealer: int
    riichi_sticks: int
    scores: List[int]
    dora_indicators: List[str] = field(default_factory=list)
    remaining_tiles_count: int = 70
    current_turn: int = 0
    current_actor: Optional[int] = None
    round_wind: Optional[int] = None

    def __post_init__(self) -> None:
        if self.round_wind is None:
            self.round_wind = EAST + (self.chang % 4)

    def seat_wind_for(self, seat: int) -> int:
        """Return the wind tile id for a seat relative to the dealer."""
        return EAST + ((seat - self.dealer) % 4)
