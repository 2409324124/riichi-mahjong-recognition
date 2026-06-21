"""
Majsoul strict validation scaffold.

This script does not replace scripts/majsoul_parser.py. The parser remains a
trusted_external_result reader. This script separately attempts local
reconstruction and writes JSONL diff rows for investigation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.majsoul_parser import MajsoulRecordParser
from src.agent.validator import WinValidator
from src.context import PublicState, RoundContext, VerificationInput
from src.game_logic.hand import Hand


FAILURE_TYPES = {
    "ok",
    "hand_reconstruction_error",
    "missing_context",
    "yaku_mismatch",
    "fu_mismatch",
    "point_mismatch",
    "unsupported_event",
    "parser_error",
    "unknown",
}


def _point_sum(hule) -> int:
    if getattr(hule, "point_rong", 0) > 0:
        return hule.point_rong
    return hule.point_zimo_qin + hule.point_zimo_xian * 2


def _fan_names(hule) -> List[str]:
    return [fan.name for fan in hule.fans]


def _fan_sum(hule) -> int:
    return sum(fan.val for fan in hule.fans)


def _majsoul_result(hule) -> Dict:
    return {
        "han": _fan_sum(hule),
        "fu": hule.fu,
        "points": _point_sum(hule),
        "fans": [
            {"name": fan.name, "val": fan.val, "id": fan.id}
            for fan in hule.fans
        ],
    }


def _context_flags(hule) -> Dict:
    fans = set(_fan_names(hule))
    return {
        "riichi": bool(getattr(hule, "liqi", False))
        or any("立直" in name for name in fans),
        "ippatsu": any("一发" in name for name in fans),
        "haitei": any("海底" in name for name in fans),
        "houtei": any("河底" in name for name in fans),
        "rinshan": any("岭上" in name or "嶺上" in name for name in fans),
        "chankan": any("抢杠" in name or "搶槓" in name for name in fans),
        "dora_count": len(getattr(hule, "doras", [])),
        "ura_dora_count": len(getattr(hule, "li_doras", [])),
    }


def _parse_hule_melds(parser: MajsoulRecordParser, hule) -> tuple[List[List[str]], int]:
    melds = []
    unparsed_count = 0
    for ming in getattr(hule, "ming", []):
        meld_tiles = parser.parse_ming(ming)
        if meld_tiles:
            melds.append(meld_tiles)
        else:
            unparsed_count += 1
    return melds, unparsed_count


def _build_verification_input(
    parser: MajsoulRecordParser,
    hule,
    context: RoundContext,
    from_actor: Optional[int],
) -> VerificationInput:
    is_tsumo = bool(hule.zimo)
    seat_wind = context.seat_wind_for(hule.seat)
    flags = _context_flags(hule)
    melds, unparsed_meld_count = _parse_hule_melds(parser, hule)
    return VerificationInput(
        hand_tiles=list(hule.hand),
        melds=melds,
        winning_tile=hule.hu_tile,
        win_actor=hule.seat,
        from_actor=None if is_tsumo else from_actor,
        is_tsumo=is_tsumo,
        is_riichi=flags["riichi"],
        is_ippatsu=flags["ippatsu"],
        is_haitei=flags["haitei"],
        is_houtei=flags["houtei"],
        is_rinshan=flags["rinshan"],
        is_chankan=flags["chankan"],
        dora_indicators=list(getattr(hule, "doras", [])),
        ura_dora_indicators=list(getattr(hule, "li_doras", [])),
        round_wind=context.round_wind,
        seat_wind=seat_wind,
        honba=context.honba,
        riichi_sticks=context.riichi_sticks,
        dealer=context.dealer,
        source="majsoul",
        extra_flags={"unparsed_meld_count": unparsed_meld_count},
    )


def _local_validate(
    parser: MajsoulRecordParser,
    validator: WinValidator,
    verification: VerificationInput,
) -> Dict:
    try:
        if verification.extra_flags.get("unparsed_meld_count", 0):
            return {
                "shape_valid": False,
                "is_valid": False,
                "han": 0,
                "fu": 0,
                "points": 0,
                "yaku": [],
                "error_type": "unsupported_event",
                "error": "one or more Majsoul meld strings could not be parsed",
            }

        hand_tiles = [
            parser.convert_tile(tile)
            for tile in verification.hand_tiles
            if parser.convert_tile(tile) is not None
        ]
        winning_tile = parser.convert_tile(verification.winning_tile)
        if winning_tile is None:
            return {
                "shape_valid": False,
                "is_valid": False,
                "han": 0,
                "fu": 0,
                "points": 0,
                "yaku": [],
                "error_type": "parser_error",
                "error": "winning tile could not be parsed",
            }

        if winning_tile in hand_tiles:
            hand_tiles.remove(winning_tile)

        hand = Hand.from_tiles(hand_tiles)
        for ming in verification.melds:
            meld_tiles = [
                parser.convert_tile(tile)
                for tile in ming
                if parser.convert_tile(tile) is not None
            ]
            if meld_tiles:
                hand.add_meld(meld_tiles)

        result = validator.validate(
            hand=hand,
            winning_tile=winning_tile,
            is_tsumo=verification.is_tsumo,
            is_riichi=verification.is_riichi,
            is_ippatsu=verification.is_ippatsu,
            is_dealer=verification.win_actor == verification.dealer,
            round_wind=verification.round_wind,
            seat_wind=verification.seat_wind,
        )
        shape_valid = not (
            result.error
            and (
                result.error.startswith("不满足和牌形状")
                or result.error.startswith("手牌+副露数量异常")
            )
        )
        return {
            "shape_valid": shape_valid,
            "is_valid": result.is_valid,
            "han": result.han,
            "fu": result.fu,
            "points": result.points,
            "yaku": [yaku.name for yaku in result.yaku_list],
            "error_type": None,
            "error": result.error,
        }
    except Exception as exc:
        return {
            "shape_valid": False,
            "is_valid": False,
            "han": 0,
            "fu": 0,
            "points": 0,
            "yaku": [],
            "error_type": "parser_error",
            "error": str(exc),
        }


def _failure_type(our_result: Dict, majsoul_result: Dict, missing_context: bool) -> str:
    if missing_context:
        return "missing_context"
    if our_result.get("error_type") == "unsupported_event":
        return "unsupported_event"
    if our_result.get("error_type") == "parser_error":
        return "parser_error"
    if not our_result.get("shape_valid", False):
        return "hand_reconstruction_error"
    if not our_result.get("is_valid", False):
        return "yaku_mismatch"
    if our_result["han"] != majsoul_result["han"]:
        return "yaku_mismatch"
    if our_result["fu"] != majsoul_result["fu"]:
        return "fu_mismatch"
    if our_result["points"] != majsoul_result["points"]:
        return "point_mismatch"
    return "ok"


def _round_context_from_new_round(record_data) -> RoundContext:
    dora_indicators = list(record_data.doras) or [record_data.dora]
    return RoundContext(
        chang=record_data.chang,
        ju=record_data.ju,
        honba=record_data.ben,
        round_wind=27 + (record_data.chang % 4),
        dealer=record_data.ju,
        riichi_sticks=record_data.liqibang,
        scores=list(record_data.scores),
        dora_indicators=dora_indicators,
        remaining_tiles_count=getattr(record_data, "left_tile_count", 70),
        current_turn=0,
        current_actor=record_data.ju,
    )


def validate_records(records: List[Dict], uuid: str = "unknown") -> List[Dict]:
    parser = MajsoulRecordParser()
    validator = WinValidator()
    context = None
    public_state = None
    hands = {seat: [] for seat in range(4)}
    last_discard_actor = None
    round_index = -1
    hule_index = 0
    rows = []

    for record in records:
        name = record.get("name")
        data = record.get("data")
        if data is None:
            continue

        if name == "RecordNewRound":
            round_index += 1
            hule_index = 0
            context = _round_context_from_new_round(data)
            public_state = PublicState.from_round_context(context)
            hands = {
                0: list(data.tiles0),
                1: list(data.tiles1),
                2: list(data.tiles2),
                3: list(data.tiles3),
            }
            last_discard_actor = None

        elif name == "RecordDealTile" and context is not None:
            hands[data.seat].append(data.tile)
            context.remaining_tiles_count = data.left_tile_count
            context.current_actor = data.seat
            context.current_turn += 1

        elif name == "RecordDiscardTile" and public_state is not None:
            if data.tile in hands[data.seat]:
                hands[data.seat].remove(data.tile)
            public_state.record_discard(data.seat, data.tile, tsumogiri=data.moqie)
            if data.is_liqi:
                player = public_state.players[data.seat]
                player.riichi_declared = True
                player.riichi_discard_index = len(player.discards) - 1
            last_discard_actor = data.seat

        elif name == "RecordChiPengGang" and public_state is not None:
            public_state.record_meld(data.seat, list(data.tiles))
            for tile, from_seat in zip(data.tiles, data.froms):
                if from_seat == data.seat and tile in hands[data.seat]:
                    hands[data.seat].remove(tile)

        elif name == "RecordAnGangAddGang" and public_state is not None:
            public_state.record_meld(data.seat, list(data.tiles))
            for tile in data.tiles:
                if tile in hands[data.seat]:
                    hands[data.seat].remove(tile)

        elif name in {"RecordLiuJu", "RecordNoTile"}:
            last_discard_actor = None

        elif name == "RecordHule":
            for hule in data.hules:
                missing_context = context is None
                if context is None:
                    our_result = {
                        "shape_valid": False,
                        "is_valid": False,
                        "han": 0,
                        "fu": 0,
                        "points": 0,
                        "yaku": [],
                        "error_type": "missing_context",
                        "error": "RecordHule appeared before RecordNewRound",
                    }
                else:
                    verification = _build_verification_input(
                        parser, hule, context, last_discard_actor
                    )
                    our_result = _local_validate(parser, validator, verification)

                maj_result = _majsoul_result(hule)
                failure_type = _failure_type(
                    our_result, maj_result, missing_context=missing_context
                )
                rows.append(
                    {
                        "uuid": uuid,
                        "round_index": round_index,
                        "hule_index": hule_index,
                        "seat": hule.seat,
                        "validation_mode": "strict_local_validator",
                        "our_result": our_result,
                        "majsoul_result": maj_result,
                        "context_flags": _context_flags(hule),
                        "failure_type": failure_type,
                    }
                )
                hule_index += 1

    return rows


def write_jsonl(rows: List[Dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    arg_parser = argparse.ArgumentParser(
        description="Generate Majsoul strict validator JSONL diff report."
    )
    arg_parser.add_argument("--input", help="Local binary Majsoul record file")
    arg_parser.add_argument("--uuid", help="Majsoul record UUID to fetch")
    arg_parser.add_argument(
        "--output",
        default="reports/majsoul_strict_diff.jsonl",
        help="JSONL diff report path",
    )
    args = arg_parser.parse_args()

    parser = MajsoulRecordParser()
    if args.input:
        records = parser.parse_from_file(args.input)
        uuid = Path(args.input).stem
    elif args.uuid:
        records = parser.parse_by_id(args.uuid)
        uuid = args.uuid
    else:
        arg_parser.error("one of --input or --uuid is required")

    rows = validate_records(records, uuid=uuid)
    write_jsonl(rows, Path(args.output))
    print(f"wrote {len(rows)} diff rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
