# Stage2 Result: Majsoul Strict Diff Enhancement

## Summary

Completed the Stage2 scaffold enhancements for Majsoul strict diff reporting and risk truth labels. This remains a context/data foundation and does not claim full Majsoul scoring parity.

## Implemented

- Added Majsoul meld normalization with `StructuredMeld`.
- Updated strict validator meld handling to use normalized melds.
- Kept unknown/unparsed melds explicit and classified as `unsupported_event`.
- Added strict diff JSONL shape tests with anonymous mock fixtures.
- Added ron truth label evaluation for risk samples when full target hand truth is available.
- Updated risk label JSON output to include `label.missing_reason`.
- Regenerated `data/derived/risk_labels.sample.jsonl` with the Stage2 label shape.

## Reported Metrics

- Strict diff mock distribution: `parser_error=1`, `unsupported_event=1`.
- Risk truth label run on `data/mjai/test.mjlog.golden.log`:
  - rows: `29451`
  - non-null `true_can_ron`: `29451`
  - non-null ratio: `1.0`

## Still Missing

- Real anonymized Majsoul binary fixtures for strict validator parity checks.
- Full Majsoul meld type mapping against real protobuf examples.
- Dora, ura-dora, riichi stick, honba, ippatsu, rinshan, chankan, haitei/houtei parity in local scoring.
- Furiten and complete opponent wait truth for risk labels.

## Verification

- `python -m pytest tests/test_majsoul_meld_normalization.py -q`: passed.
- `python -m pytest tests/test_majsoul_meld_normalization.py tests/test_majsoul_strict_validator.py tests/test_majsoul_strict_diff_report.py -q`: passed.
- `python -m pytest tests/test_risk_features.py tests/test_risk_truth_labels.py -q`: passed.
- `python -m pytest tests/ -v -k "not gui"`: 146 passed, 9 deselected.
- `python -m py_compile scripts/majsoul_strict_validator.py scripts/generate_risk_labels.py`: failed because the environment could not write `scripts/__pycache__`.
- `PYTHONPYCACHEPREFIX=<tmp_pycache> python -m py_compile scripts/majsoul_strict_validator.py scripts/generate_risk_labels.py`: passed.
