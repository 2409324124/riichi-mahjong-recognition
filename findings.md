# Findings

## Repository State

- Current work is on `feature/human-mahjong-context-engine`.
- Existing `scripts/majsoul_parser.py` still reports `validation_mode == "trusted_external_result"` and should stay a trusted reader.
- Non-GUI test command passed: `python -m pytest tests/ -v -k "not gui"` reported 135 passed and 9 deselected.

## Implementation Notes

- `src/context/` now contains lightweight dataclasses for round context, public state, verification input, and candidate discard-risk features.
- `src/risk/` now contains rule features and mjai risk label generation.
- Majsoul strict validation lives in `scripts/majsoul_strict_validator.py`, separate from the trusted reader.
- The checked-in risk sample is limited to 20 JSONL rows to avoid bloating the repo.
- Diff review found and fixed strict-validator handling for unparsed Majsoul meld strings; those are now classified as `unsupported_event` instead of being silently treated as empty melds.

## Known Limits

- Strict Majsoul validation is a scaffold, not a parity claim.
- Majsoul meld decoding may need more protobuf-specific normalization.
- Dora/ura-dora and several context yaku flags are reported but not fully modeled in local scoring parity.
- Risk labels keep `true_can_ron` and `true_loss_points` nullable until offline truth extraction is reliable.
