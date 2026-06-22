from src.context import PublicState, RoundContext
from src.risk import build_candidate_risk_feature
from src.opponent import OpponentBeliefEstimator


def _round_context(turn=8):
    return RoundContext(
        chang=0,
        ju=0,
        honba=0,
        dealer=2,
        riichi_sticks=1,
        scores=[25000, 25000, 25000, 25000],
        dora_indicators=["5m"],
        remaining_tiles_count=55,
        current_turn=turn,
        current_actor=0,
    )


def test_riichi_opponent_has_high_tenpai_and_attack():
    context = _round_context(turn=9)
    public_state = PublicState.from_round_context(context)
    public_state.players[1].riichi_declared = True
    public_state.players[1].riichi_discard_index = 6

    beliefs = OpponentBeliefEstimator().estimate_all(public_state, context, actor=0)
    riichi_belief = beliefs[1]
    quiet_belief = beliefs[3]

    assert riichi_belief.tenpai_prob > quiet_belief.tenpai_prob
    assert riichi_belief.attack_prob > quiet_belief.attack_prob
    assert any("riichi" in reason for reason in riichi_belief.explanation)


def test_meld_count_increases_speed_score():
    context = _round_context(turn=7)
    public_state = PublicState.from_round_context(context)
    public_state.record_meld(1, ["2p", "3p", "4p"])
    public_state.record_meld(1, ["6p", "7p", "8p"])

    belief = OpponentBeliefEstimator().estimate_all(public_state, context, actor=0)[1]

    assert belief.speed_score >= 0.6
    assert any("meld" in reason for reason in belief.explanation)


def test_danger_by_tile_uses_risk_features():
    context = _round_context(turn=10)
    public_state = PublicState.from_round_context(context)
    public_state.players[2].riichi_declared = True
    public_state.record_discard(2, "4m")
    public_state.visible_tile_counts["6m"] = 4

    safe = build_candidate_risk_feature(public_state, 0, "4m", 2, 10)
    suji = build_candidate_risk_feature(public_state, 0, "7m", 2, 10)
    dora = build_candidate_risk_feature(public_state, 0, "5m", 2, 10)

    belief = OpponentBeliefEstimator().estimate_all(
        public_state, context, actor=0, risk_features=[safe, suji, dora]
    )[2]

    assert belief.danger_by_tile["5m"] > belief.danger_by_tile["7m"]
    assert belief.danger_by_tile["7m"] > belief.danger_by_tile["4m"]
    assert any("5m" in reason and "dora" in reason for reason in belief.explanation)


def test_suit_intent_reflects_meld_and_discard_patterns():
    context = _round_context(turn=8)
    public_state = PublicState.from_round_context(context)
    public_state.record_meld(1, ["2p", "3p", "4p"])
    public_state.record_meld(1, ["6p", "7p", "8p"])
    public_state.record_discard(1, "1m")
    public_state.record_discard(1, "9s")

    belief = OpponentBeliefEstimator().estimate_all(public_state, context, actor=0)[1]

    assert belief.suit_intent["p"] > belief.suit_intent["m"]
    assert belief.suit_intent["p"] > belief.suit_intent["s"]
    assert any("p-suit" in reason for reason in belief.explanation)
