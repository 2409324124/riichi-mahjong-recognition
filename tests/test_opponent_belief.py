from src.opponent import OpponentBelief


def test_opponent_belief_constructs_with_explanations():
    belief = OpponentBelief(
        player_id=2,
        tenpai_prob=0.8,
        speed_score=0.7,
        attack_prob=0.9,
        defense_prob=0.1,
        suit_intent={"m": 0.1, "p": 0.6, "s": 0.2, "honor": 0.1},
        danger_by_tile={"5p": 0.85},
        explanation=["player declared riichi"],
    )

    assert belief.player_id == 2
    assert belief.danger_by_tile["5p"] == 0.85
    assert belief.explanation == ["player declared riichi"]


def test_opponent_belief_clamps_probabilities_to_unit_range():
    belief = OpponentBelief(
        player_id=1,
        tenpai_prob=1.5,
        speed_score=-0.5,
        attack_prob=2.0,
        defense_prob=-1.0,
        suit_intent={"m": 1.4, "p": -0.2},
        danger_by_tile={"1m": 1.2, "2m": -0.1},
        explanation=[],
    )

    assert belief.tenpai_prob == 1.0
    assert belief.speed_score == 0.0
    assert belief.attack_prob == 1.0
    assert belief.defense_prob == 0.0
    assert belief.suit_intent == {"m": 1.0, "p": 0.0}
    assert belief.danger_by_tile == {"1m": 1.0, "2m": 0.0}
