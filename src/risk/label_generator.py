from dataclasses import asdict
from typing import Dict, Iterable, List

from src.context import CandidateDiscardRiskFeature, PublicState

from .rules import (
    is_aka_dora,
    is_double_no_chance,
    is_kabe,
    is_no_chance,
    is_suji,
    is_yakuhai,
    normalize_tile,
    remaining_count,
    visible_count,
)


def build_candidate_risk_feature(
    public_state: PublicState,
    actor: int,
    candidate_tile: str,
    target_player: int,
    turn: int,
    true_can_ron: bool | None = None,
    true_loss_points: int | None = None,
) -> CandidateDiscardRiskFeature:
    target = public_state.players[target_player]
    context = public_state.round_context
    normalized_tile = normalize_tile(candidate_tile)
    round_wind = context.round_wind if context else 27
    seat_wind = context.seat_wind_for(target_player) if context else 27

    return CandidateDiscardRiskFeature(
        actor=actor,
        candidate_tile=normalized_tile,
        target_player=target_player,
        turn=turn,
        is_genbutsu=normalized_tile in target.genbutsu,
        is_suji=is_suji(normalized_tile, target.genbutsu),
        is_kabe=is_kabe(normalized_tile, public_state.visible_tile_counts),
        is_no_chance=is_no_chance(normalized_tile, public_state.visible_tile_counts),
        is_double_no_chance=is_double_no_chance(
            normalized_tile, public_state.visible_tile_counts
        ),
        visible_count=visible_count(normalized_tile, public_state.visible_tile_counts),
        remaining_count=remaining_count(normalized_tile, public_state.visible_tile_counts),
        is_dora=normalized_tile in (context.dora_indicators if context else []),
        is_aka_dora=is_aka_dora(candidate_tile),
        is_yakuhai=is_yakuhai(normalized_tile, round_wind=round_wind, seat_wind=seat_wind),
        target_riichi=target.riichi_declared,
        target_meld_count=len(target.melds),
        target_is_dealer=bool(context and target_player == context.dealer),
        target_discards_before=len(target.discards),
        true_can_ron=true_can_ron,
        true_loss_points=true_loss_points,
    )


def feature_to_json_record(
    source: str,
    game_id: str,
    round_index: int,
    turn: int,
    actor: int,
    candidate_tile: str,
    chosen_by_human: bool,
    target_player: int,
    feature: CandidateDiscardRiskFeature,
) -> Dict:
    feature_dict = asdict(feature)
    true_can_ron = feature_dict.pop("true_can_ron")
    true_loss_points = feature_dict.pop("true_loss_points")

    return {
        "source": source,
        "game_id": game_id,
        "round_index": round_index,
        "turn": turn,
        "actor": actor,
        "candidate_tile": candidate_tile,
        "chosen_by_human": chosen_by_human,
        "target_player": target_player,
        "features": feature_dict,
        "label": {
            "true_can_ron": true_can_ron,
            "true_loss_points": true_loss_points,
        },
    }


def unique_tiles(tiles: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for tile in tiles:
        normalized = normalize_tile(tile)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _chang_from_event(event: Dict) -> int:
    bakaze = event.get("bakaze")
    if bakaze in {"S", "南"}:
        return 1
    if bakaze in {"W", "西"}:
        return 2
    if bakaze in {"N", "北"}:
        return 3
    return 0


def _dora_indicators_from_event(event: Dict) -> List[str]:
    dora_marker = event.get("dora_marker", [])
    if isinstance(dora_marker, str):
        return [normalize_tile(dora_marker)]
    return [normalize_tile(tile) for tile in dora_marker]


def _meld_tiles_from_mjai_event(event: Dict) -> List[str]:
    if event.get("type") in {"chi", "pon", "daiminkan"}:
        return [
            normalize_tile(tile)
            for tile in [*event.get("consumed", []), event.get("pai", "")]
            if tile
        ]
    if event.get("type") in {"ankan", "kakan"}:
        tiles = event.get("consumed", []) or [event.get("pai", "")]
        return [normalize_tile(tile) for tile in tiles if tile]
    return []


def generate_mjai_risk_labels(events: List[Dict], game_id: str = "unknown") -> List[Dict]:
    """Generate minimum risk-label rows from mjai events with known actor hands."""
    from scripts.mjai_parser_v2 import MjaiParser
    from src.context import PublicState, RoundContext

    parser = MjaiParser()
    hands = {0: [], 1: [], 2: [], 3: []}
    melds = {0: [], 1: [], 2: [], 3: []}
    public_state = None
    round_index = -1
    turn = 0
    labels = []

    for event in events:
        event_type = event.get("type")

        if event_type == "start_kyoku":
            round_index += 1
            turn = 0
            context = RoundContext(
                chang=_chang_from_event(event),
                ju=event.get("_kyoku_number", round_index + 1) - 1,
                honba=event.get("honba", 0),
                dealer=event.get("oya", 0),
                riichi_sticks=event.get("kyotaku", 0),
                scores=event.get("scores", [25000, 25000, 25000, 25000]),
                dora_indicators=_dora_indicators_from_event(event),
                remaining_tiles_count=70,
                current_turn=turn,
                current_actor=event.get("oya", 0),
                round_wind=event.get("_round_wind"),
            )
            public_state = PublicState.from_round_context(context)

        if public_state is not None and event_type in {"chi", "pon", "daiminkan", "ankan", "kakan"}:
            meld_tiles = _meld_tiles_from_mjai_event(event)
            if meld_tiles:
                public_state.record_meld(event.get("actor", 0), meld_tiles)

        if public_state is not None and event_type == "reach":
            actor = event.get("actor", 0)
            public_state.players[actor].riichi_declared = True

        if event_type == "dahai" and public_state is not None:
            actor = event.get("actor", 0)
            chosen_tile = normalize_tile(event.get("pai", ""))
            hand_candidates = unique_tiles(str(tile) for tile in hands.get(actor, []))
            if chosen_tile and chosen_tile not in hand_candidates:
                hand_candidates.append(chosen_tile)

            for candidate in hand_candidates:
                for target_player in range(4):
                    if target_player == actor:
                        continue
                    feature = build_candidate_risk_feature(
                        public_state=public_state,
                        actor=actor,
                        candidate_tile=candidate,
                        target_player=target_player,
                        turn=turn,
                    )
                    labels.append(
                        feature_to_json_record(
                            source="mjai",
                            game_id=game_id,
                            round_index=round_index,
                            turn=turn,
                            actor=actor,
                            candidate_tile=candidate,
                            chosen_by_human=candidate == chosen_tile,
                            target_player=target_player,
                            feature=feature,
                        )
                    )
            public_state.record_discard(
                actor, chosen_tile, tsumogiri=event.get("tsumogiri")
            )
            turn += 1

        hands, melds = parser.apply_event(event, hands, melds)

    return labels
