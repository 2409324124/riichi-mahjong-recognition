from dataclasses import dataclass, field
from typing import Dict, List, Optional


UNKNOWN_AREA = "unknown"
VALID_HAND_AREAS = {
    "left_edge",
    "middle_left",
    "middle",
    "middle_right",
    "right_edge",
    UNKNOWN_AREA,
}


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass
class PhysicalBehaviorEvent:
    """Structured physical behavior signal from observation or fixtures."""

    player_id: int
    turn: int
    is_tsumogiri: Optional[bool] = None
    discard_source_area: Optional[str] = None
    draw_insert_area: Optional[str] = None
    hand_movement_count: int = 0
    hesitation_ms: Optional[int] = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        self.confidence = clamp_confidence(self.confidence)
        if self.discard_source_area is not None and self.discard_source_area not in VALID_HAND_AREAS:
            self.discard_source_area = UNKNOWN_AREA
        if self.draw_insert_area is not None and self.draw_insert_area not in VALID_HAND_AREAS:
            self.draw_insert_area = UNKNOWN_AREA
        self.hand_movement_count = max(0, int(self.hand_movement_count))


@dataclass
class PhysicalBehaviorSummary:
    """Aggregated physical behavior signals for one player."""

    player_id: int
    event_count: int = 0
    tsumogiri_rate: Optional[float] = None
    average_hesitation_ms: Optional[int] = None
    total_hand_movement_count: int = 0
    low_confidence_event_count: int = 0
    latest_discard_source_area: Optional[str] = None
    latest_draw_insert_area: Optional[str] = None


@dataclass
class PhysicalBehaviorContext:
    """Collection of structured physical behavior events for one round."""

    events: List[PhysicalBehaviorEvent] = field(default_factory=list)

    def latest_event_for_player(
        self, player_id: int, at_turn: Optional[int] = None
    ) -> Optional[PhysicalBehaviorEvent]:
        for event in reversed(self.events):
            if event.player_id == player_id and (at_turn is None or event.turn <= at_turn):
                return event
        return None

    def events_for_player(self, player_id: int) -> List[PhysicalBehaviorEvent]:
        return [event for event in self.events if event.player_id == player_id]

    def events_by_player(self) -> Dict[int, List[PhysicalBehaviorEvent]]:
        grouped: Dict[int, List[PhysicalBehaviorEvent]] = {}
        for event in self.events:
            grouped.setdefault(event.player_id, []).append(event)
        return grouped

    def summary_for_player(self, player_id: int) -> PhysicalBehaviorSummary:
        events = self.events_for_player(player_id)
        tsumogiri_events = [event for event in events if event.is_tsumogiri is not None]
        hesitation_events = [event for event in events if event.hesitation_ms is not None]
        latest_discard_source_area = None
        latest_draw_insert_area = None

        for event in reversed(events):
            if latest_discard_source_area is None and event.discard_source_area is not None:
                latest_discard_source_area = event.discard_source_area
            if latest_draw_insert_area is None and event.draw_insert_area is not None:
                latest_draw_insert_area = event.draw_insert_area
            if latest_discard_source_area is not None and latest_draw_insert_area is not None:
                break

        tsumogiri_rate = None
        if tsumogiri_events:
            tsumogiri_rate = sum(1 for event in tsumogiri_events if event.is_tsumogiri) / len(
                tsumogiri_events
            )

        average_hesitation_ms = None
        if hesitation_events:
            average_hesitation_ms = int(
                sum(event.hesitation_ms or 0 for event in hesitation_events) / len(hesitation_events)
            )

        return PhysicalBehaviorSummary(
            player_id=player_id,
            event_count=len(events),
            tsumogiri_rate=tsumogiri_rate,
            average_hesitation_ms=average_hesitation_ms,
            total_hand_movement_count=sum(event.hand_movement_count for event in events),
            low_confidence_event_count=sum(1 for event in events if event.confidence < 0.5),
            latest_discard_source_area=latest_discard_source_area,
            latest_draw_insert_area=latest_draw_insert_area,
        )
