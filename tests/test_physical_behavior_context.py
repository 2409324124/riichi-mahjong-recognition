from src.context import PhysicalBehaviorContext, PhysicalBehaviorEvent


def test_physical_behavior_event_accepts_structured_discard_signal():
    event = PhysicalBehaviorEvent(
        player_id=2,
        turn=8,
        is_tsumogiri=False,
        discard_source_area="left_edge",
        draw_insert_area="middle_right",
        hesitation_ms=3200,
        confidence=0.82,
    )
    context = PhysicalBehaviorContext(events=[event])

    latest = context.latest_event_for_player(2)

    assert latest == event
    assert event.confidence == 0.82
    assert event.discard_source_area == "left_edge"
    assert event.draw_insert_area == "middle_right"


def test_physical_behavior_summary_uses_player_events():
    context = PhysicalBehaviorContext(
        events=[
            PhysicalBehaviorEvent(
                player_id=2,
                turn=7,
                is_tsumogiri=True,
                hesitation_ms=800,
                confidence=0.9,
            ),
            PhysicalBehaviorEvent(
                player_id=2,
                turn=8,
                is_tsumogiri=False,
                discard_source_area="left_edge",
                draw_insert_area="middle_right",
                hand_movement_count=3,
                hesitation_ms=3200,
                confidence=0.82,
            ),
            PhysicalBehaviorEvent(player_id=2, turn=9, confidence=0.2),
            PhysicalBehaviorEvent(player_id=1, turn=8, is_tsumogiri=True, confidence=0.9),
        ]
    )

    summary = context.summary_for_player(2)

    assert summary.event_count == 3
    assert summary.tsumogiri_rate == 0.5
    assert summary.average_hesitation_ms == 2000
    assert summary.total_hand_movement_count == 3
    assert summary.low_confidence_event_count == 1
    assert summary.latest_discard_source_area == "left_edge"
    assert summary.latest_draw_insert_area == "middle_right"


def test_physical_behavior_event_clamps_confidence_and_supports_turn_lookup():
    context = PhysicalBehaviorContext(
        events=[
            PhysicalBehaviorEvent(
                player_id=2,
                turn=6,
                discard_source_area="bad_area",
                draw_insert_area="middle",
                confidence=1.4,
            ),
            PhysicalBehaviorEvent(player_id=2, turn=9, confidence=-0.1),
        ]
    )

    latest_before_turn_8 = context.latest_event_for_player(2, at_turn=8)

    assert latest_before_turn_8.confidence == 1.0
    assert latest_before_turn_8.discard_source_area == "unknown"
    assert context.latest_event_for_player(2).confidence == 0.0
