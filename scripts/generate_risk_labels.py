"""
Generate minimum discard-risk label rows.

The first supported source is mjai. Labels keep true_can_ron and
true_loss_points nullable until offline wait/point truth is reliable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.mjai_parser_v2 import MjaiParser
from src.risk import generate_mjai_risk_labels


def write_jsonl(rows, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate discard-risk labels.")
    parser.add_argument(
        "--source",
        choices=["mjai"],
        default="mjai",
        help="Input event source format",
    )
    parser.add_argument("--input", required=True, help="Input mjai log path")
    parser.add_argument(
        "--output",
        default="data/derived/risk_labels.sample.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument("--game-id", default=None, help="Stable public game id")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum rows to write; useful for small checked-in samples",
    )
    args = parser.parse_args()

    if args.source != "mjai":
        parser.error("only --source mjai is supported in this scaffold")

    input_path = Path(args.input)
    events = MjaiParser().parse_file(str(input_path))
    rows = generate_mjai_risk_labels(
        events,
        game_id=args.game_id or input_path.stem,
    )
    if args.limit is not None:
        rows = rows[: args.limit]
    write_jsonl(rows, Path(args.output))
    print(f"wrote {len(rows)} risk label rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
