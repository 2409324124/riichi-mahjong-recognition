from src.context import CandidateDiscardRiskFeature
from src.risk.label_generator import feature_to_json_record
from src.risk.truth_labels import evaluate_ron_truth


def test_ron_truth_fills_true_label_and_loss_points():
    result = evaluate_ron_truth(
        target_hand_tiles=[
            "1m", "2m", "3m",
            "4p", "5p", "6p",
            "7s", "8s", "9s",
            "E", "E", "E",
            "2s",
        ],
        target_melds=[],
        candidate_tile="2s",
        target_player=0,
        dealer=0,
        round_wind=27,
        seat_wind=27,
    )

    assert result.true_can_ron is True
    assert result.true_loss_points is not None
    assert result.missing_reason is None


def test_ron_truth_false_when_candidate_does_not_win():
    result = evaluate_ron_truth(
        target_hand_tiles=[
            "1m", "2m", "3m",
            "4p", "5p", "6p",
            "7s", "8s", "9s",
            "1s", "1s", "1s",
            "2s",
        ],
        target_melds=[],
        candidate_tile="9m",
        target_player=0,
        dealer=0,
        round_wind=27,
        seat_wind=27,
    )

    assert result.true_can_ron is False
    assert result.true_loss_points is None
    assert result.missing_reason is None


def test_ron_truth_missing_when_full_hand_truth_absent():
    result = evaluate_ron_truth(
        target_hand_tiles=[],
        target_melds=[],
        candidate_tile="3s",
        target_player=0,
        dealer=0,
        round_wind=27,
        seat_wind=27,
    )

    assert result.true_can_ron is None
    assert result.true_loss_points is None
    assert result.missing_reason == "missing_target_hand_truth"


def test_json_label_includes_missing_reason():
    row = feature_to_json_record(
        source="mjai",
        game_id="unit",
        round_index=0,
        turn=1,
        actor=1,
        candidate_tile="3s",
        chosen_by_human=True,
        target_player=0,
        feature=CandidateDiscardRiskFeature(
            actor=1,
            candidate_tile="3s",
            target_player=0,
            turn=1,
            is_genbutsu=False,
            is_suji=False,
            is_kabe=False,
            is_no_chance=False,
            is_double_no_chance=False,
            visible_count=0,
            remaining_count=4,
            is_dora=False,
            is_aka_dora=False,
            is_yakuhai=False,
            target_riichi=False,
            target_meld_count=0,
            target_is_dealer=True,
            target_discards_before=0,
        ),
        missing_reason="missing_target_hand_truth",
    )

    assert row["label"] == {
        "true_can_ron": None,
        "true_loss_points": None,
        "missing_reason": "missing_target_hand_truth",
    }
