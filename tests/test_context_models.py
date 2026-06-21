from src.context import (
    PlayerPublicState,
    PublicState,
    RoundContext,
    VerificationInput,
)


def test_round_context_maps_seat_winds_from_dealer():
    context = RoundContext(
        chang=1,
        ju=2,
        honba=1,
        dealer=2,
        riichi_sticks=0,
        scores=[25000, 25000, 25000, 25000],
        dora_indicators=["4p"],
        remaining_tiles_count=70,
        current_turn=0,
        current_actor=2,
    )

    assert context.round_wind == 28
    assert context.seat_wind_for(2) == 27
    assert context.seat_wind_for(3) == 28
    assert context.seat_wind_for(0) == 29
    assert context.seat_wind_for(1) == 30


def test_public_state_updates_visible_counts_and_genbutsu():
    public_state = PublicState.from_round_context(
        RoundContext(
            chang=0,
            ju=0,
            honba=0,
            dealer=0,
            riichi_sticks=0,
            scores=[25000, 25000, 25000, 25000],
            dora_indicators=["1m"],
            remaining_tiles_count=70,
        )
    )

    public_state.record_discard(1, "5m", tsumogiri=True)
    public_state.record_discard(1, "5m", tsumogiri=False)

    assert public_state.visible_tile_counts["5m"] == 2
    assert public_state.players[1].discards == ["5m", "5m"]
    assert public_state.players[1].tsumogiri_flags == [True, False]
    assert "5m" in public_state.players[1].genbutsu
    assert public_state.all_discards == [(1, "5m"), (1, "5m")]


def test_verification_input_constructs_with_context_flags():
    verification = VerificationInput(
        hand_tiles=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "E", "E", "白", "白"],
        melds=[],
        winning_tile="E",
        win_actor=0,
        from_actor=None,
        is_tsumo=True,
        is_riichi=True,
        dora_indicators=["3m"],
        ura_dora_indicators=["6s"],
        round_wind=27,
        seat_wind=27,
        honba=0,
        riichi_sticks=1,
        dealer=0,
        source="mjai",
    )

    assert verification.is_tsumo is True
    assert verification.is_riichi is True
    assert verification.from_actor is None
    assert verification.source == "mjai"
