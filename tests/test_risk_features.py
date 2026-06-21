from src.context import PlayerPublicState, RoundContext, PublicState
from src.risk import (
    build_candidate_risk_feature,
    generate_mjai_risk_labels,
    is_kabe,
    is_no_chance,
    is_suji,
    remaining_count,
)


def test_genbutsu_and_suji_features_use_target_discards():
    target = PlayerPublicState(
        seat=2,
        discards=["3m", "6m"],
        riichi_declared=True,
        riichi_discard_index=1,
    )

    assert "3m" in target.genbutsu
    assert is_suji("9m", target.genbutsu) is True
    assert is_suji("8m", target.genbutsu) is False


def test_kabe_no_chance_and_remaining_counts_use_visible_counts():
    visible_counts = {"7p": 4, "5p": 4, "8p": 1}

    assert is_kabe("8p", visible_counts) is True
    assert is_no_chance("8p", visible_counts) is True
    assert remaining_count("8p", visible_counts) == 3


def test_build_candidate_risk_feature_combines_public_state():
    context = RoundContext(
        chang=0,
        ju=0,
        honba=0,
        dealer=2,
        riichi_sticks=1,
        scores=[25000, 25000, 25000, 25000],
        dora_indicators=["4m"],
        remaining_tiles_count=55,
        current_turn=8,
        current_actor=1,
    )
    public_state = PublicState.from_round_context(context)
    public_state.record_discard(2, "6m", tsumogiri=True)
    public_state.players[2].riichi_declared = True
    public_state.players[2].melds = [["7p", "8p", "9p"]]

    feature = build_candidate_risk_feature(
        public_state=public_state,
        actor=1,
        candidate_tile="9m",
        target_player=2,
        turn=8,
    )

    assert feature.actor == 1
    assert feature.candidate_tile == "9m"
    assert feature.target_player == 2
    assert feature.is_suji is True
    assert feature.target_riichi is True
    assert feature.target_meld_count == 1
    assert feature.target_is_dealer is True
    assert feature.target_discards_before == 1


def test_mjai_risk_labels_reflect_public_melds_and_riichi():
    events = [
        {"type": "start_kyoku", "oya": 0, "dora_marker": "1m"},
        {"type": "haipai", "actor": 0, "pais": ["1m", "1m", "2m"]},
        {"type": "haipai", "actor": 1, "pais": ["3m", "4m", "5m"]},
        {"type": "dahai", "actor": 2, "pai": "1m"},
        {"type": "pon", "actor": 0, "target": 2, "pai": "1m", "consumed": ["1m", "1m"]},
        {"type": "reach", "actor": 0},
        {"type": "dahai", "actor": 1, "pai": "3m"},
    ]

    rows = generate_mjai_risk_labels(events, game_id="unit")
    target_rows = [
        row for row in rows if row["actor"] == 1 and row["target_player"] == 0
    ]

    assert target_rows
    assert target_rows[0]["features"]["target_meld_count"] == 1
    assert target_rows[0]["features"]["target_riichi"] is True
