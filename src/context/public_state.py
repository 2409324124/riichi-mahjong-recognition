from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .round_context import RoundContext


@dataclass
class PlayerPublicState:
    """Public information known about one player."""

    seat: int
    discards: List[str] = field(default_factory=list)
    melds: List[List[str]] = field(default_factory=list)
    riichi_declared: bool = False
    riichi_discard_index: Optional[int] = None
    is_menzen: bool = True
    genbutsu: Set[str] = field(default_factory=set)
    tsumogiri_flags: List[Optional[bool]] = field(default_factory=list)
    visible_safe_tiles: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.genbutsu.update(self.discards)
        self.visible_safe_tiles.update(self.genbutsu)
        if len(self.tsumogiri_flags) < len(self.discards):
            self.tsumogiri_flags.extend([None] * (len(self.discards) - len(self.tsumogiri_flags)))
        if self.melds:
            self.is_menzen = False

    def record_discard(self, tile: str, tsumogiri: Optional[bool] = None) -> None:
        self.discards.append(tile)
        self.tsumogiri_flags.append(tsumogiri)
        self.genbutsu.add(tile)
        self.visible_safe_tiles.add(tile)

    def record_meld(self, meld_tiles: List[str]) -> None:
        self.melds.append(list(meld_tiles))
        self.is_menzen = False


@dataclass
class PublicState:
    """Table-visible state used for validation scaffolds and risk features."""

    players: Dict[int, PlayerPublicState]
    visible_tile_counts: Dict[str, int] = field(default_factory=dict)
    all_discards: List[Tuple[int, str]] = field(default_factory=list)
    all_melds: List[Tuple[int, List[str]]] = field(default_factory=list)
    round_context: Optional[RoundContext] = None
    honba: int = 0
    riichi_sticks: int = 0

    @classmethod
    def from_round_context(cls, context: RoundContext) -> "PublicState":
        state = cls(
            players={seat: PlayerPublicState(seat=seat) for seat in range(4)},
            round_context=context,
            honba=context.honba,
            riichi_sticks=context.riichi_sticks,
        )
        for tile in context.dora_indicators:
            state.add_visible_tile(tile)
        return state

    def add_visible_tile(self, tile: str) -> None:
        self.visible_tile_counts[tile] = self.visible_tile_counts.get(tile, 0) + 1

    def record_discard(self, seat: int, tile: str, tsumogiri: Optional[bool] = None) -> None:
        self.players[seat].record_discard(tile, tsumogiri=tsumogiri)
        self.add_visible_tile(tile)
        self.all_discards.append((seat, tile))

    def record_meld(self, seat: int, meld_tiles: List[str]) -> None:
        self.players[seat].record_meld(meld_tiles)
        for tile in meld_tiles:
            self.add_visible_tile(tile)
        self.all_melds.append((seat, list(meld_tiles)))
