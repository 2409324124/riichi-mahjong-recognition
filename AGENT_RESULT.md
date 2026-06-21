# Human Mahjong Context Engine Result

## Summary

已建立人类牌局理解所需的上下文与危险度数据生成底座。

本阶段没有做 RL、监督学习、Mortal 接入、视频理解大模型，也没有改动牌面识别模型、GUI、既有计分/役种/WinValidator 核心逻辑。

## Changed Files

- `src/context/`
  - `round_context.py`
  - `public_state.py`
  - `verification_input.py`
  - `risk_features.py`
  - `__init__.py`
- `src/risk/`
  - `rules.py`
  - `label_generator.py`
  - `__init__.py`
- `scripts/majsoul_strict_validator.py`
- `scripts/generate_risk_labels.py`
- `tests/test_context_models.py`
- `tests/test_majsoul_strict_validator.py`
- `tests/test_majsoul_trusted_reader.py`
- `tests/test_risk_features.py`
- `data/derived/risk_labels.sample.jsonl`
- `.gitignore`

## New Data Structures

- `RoundContext`: round number, honba, dealer, winds, scores, dora indicators, wall count, current turn/actor.
- `PlayerPublicState`: ordered discards, melds, riichi flags, menzen state, genbutsu, tsumogiri flags, visible safe tiles.
- `PublicState`: four public player states, visible tile counts, all discards, all melds, round mirror fields.
- `VerificationInput`: unified local validation input for reconstructed wins.
- `CandidateDiscardRiskFeature`: rule features for one candidate discard against one target player, with nullable offline labels.

## Majsoul Strict Validation Scaffold

`scripts/majsoul_strict_validator.py` is separate from `scripts/majsoul_parser.py`.

`majsoul_parser.validate_hora` remains a `trusted_external_result` reader. The strict validator is a new scaffold that:

- reads records from local Majsoul binary input or UUID,
- rebuilds `RoundContext` and `PublicState` across known round events,
- handles `RecordNewRound`, `RecordDealTile`, `RecordDiscardTile`, `RecordChiPengGang`, `RecordAnGangAddGang`, `RecordLiuJu`, `RecordNoTile`, and `RecordHule`,
- builds `VerificationInput` at `RecordHule`,
- calls the existing `WinValidator`,
- writes JSONL diff rows to `reports/majsoul_strict_diff.jsonl`.

Current status: CLI loads and the scaffold can generate diff rows when a Majsoul record is supplied. It is not claimed to have the trusted reader's pass rate.

Failure categories supported by the scaffold:

- `ok`
- `hand_reconstruction_error`
- `missing_context`
- `yaku_mismatch`
- `fu_mismatch`
- `point_mismatch`
- `parser_error`
- `unknown`

## Risk Label Generator

`scripts/generate_risk_labels.py` currently supports `--source mjai`.

It reconstructs actor hands with the existing mjai parser, maintains public state, enumerates unique candidate discards at each discard decision, and emits one row per candidate-target pair. Rule features include genbutsu, suji, kabe/no-chance, visible/remaining count, dora/aka/yakuhai flags, target riichi, target meld count, dealer flag, and target discard count.

Offline truth fields are present but nullable:

- `true_can_ron`
- `true_loss_points`

Generated sample:

- `data/derived/risk_labels.sample.jsonl`
- 20 rows, generated with `--limit 20`

## Missing Context

- Majsoul strict validation still needs broader real-record fixtures to classify event-specific failures accurately.
- Majsoul meld decoding is scaffold-level and may need protobuf-specific normalization for all chi/pon/kan variants.
- Dora and ura-dora currently flow into report context, but the existing validator/scoring core is not extended for full Majsoul parity.
- Ippatsu, haitei/houtei, rinshan, and chankan are inferred from Majsoul fan names/flags when available; this may require stricter event-state derivation later.
- Risk labels do not yet compute true ron waits or loss points; those remain nullable by design.

## Likely Failure Sources

- `missing_context`: `RecordHule` without prior `RecordNewRound`, or incomplete round reconstruction.
- `hand_reconstruction_error`: local hand shape/count mismatch, meld decoding mismatch, or local parser state drift.
- `yaku_mismatch`, `fu_mismatch`, `point_mismatch`: expected early for unsupported context flags, dora parity gaps, or differences between local scoring rules and Majsoul result details.
- Possible parser bugs should be separated from known missing context by inspecting the JSONL diff rows, not by treating trusted Majsoul results as strict local validation.

## Next Steps

1. Add small anonymized Majsoul binary fixtures and assert strict diff JSONL shape.
2. Normalize Majsoul meld representation into structured meld objects before stronger validation.
3. Add offline wait/ron truth extraction for mjai or Majsoul, then fill `true_can_ron` and `true_loss_points`.
4. Extend `PublicState` only as needed for opponent belief features; do not start model training yet.

## Verification

- `python -m pytest tests/test_context_models.py tests/test_majsoul_trusted_reader.py tests/test_risk_features.py -q`: passed.
- `python -m pytest tests/test_majsoul_strict_validator.py -q`: passed.
- `PYTHONPYCACHEPREFIX=<tmp_pycache> python -m py_compile scripts/majsoul_strict_validator.py scripts/generate_risk_labels.py`: passed.
- `python scripts/majsoul_strict_validator.py --help`: passed.
- `python scripts/generate_risk_labels.py --source mjai --input data/mjai/test.mjlog.golden.log --output data/derived/risk_labels.sample.jsonl --game-id mjai_sample --limit 20`: passed.
- `python -m pytest tests/ -v -k "not gui"`: 135 passed, 9 deselected.

Note: pytest reported a cache-write warning because the sandbox sees the underlying cache path as read-only. Test execution itself passed.
