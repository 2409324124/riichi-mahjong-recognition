from dataclasses import dataclass, field
from typing import Dict, List


def clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def clamp_score(value: float) -> float:
    """Clamp a normalized non-probability score to [0, 1]."""
    return max(0.0, min(1.0, float(value)))


@dataclass
class OpponentBelief:
    player_id: int
    tenpai_prob: float = 0.0
    speed_score: float = 0.0
    attack_prob: float = 0.0
    defense_prob: float = 0.0
    suit_intent: Dict[str, float] = field(default_factory=dict)
    danger_by_tile: Dict[str, float] = field(default_factory=dict)
    explanation: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.tenpai_prob = clamp_probability(self.tenpai_prob)
        self.speed_score = clamp_score(self.speed_score)
        self.attack_prob = clamp_probability(self.attack_prob)
        self.defense_prob = clamp_probability(self.defense_prob)
        self.suit_intent = {
            suit: clamp_probability(score)
            for suit, score in self.suit_intent.items()
        }
        self.danger_by_tile = {
            tile: clamp_probability(score)
            for tile, score in self.danger_by_tile.items()
        }
