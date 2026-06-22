# Stage4 Result: PhysicalBehaviorContext

## Summary

Added a structured physical behavior event layer for human game understanding. This stage does not add CV, video models, large multimodal models, automatic play, RL, or supervised training.

## New Context Structures

- `PhysicalBehaviorEvent`: one observed behavior signal for a player turn.
  - Supports tsumogiri/hand-cut, discard source area, draw insert area, hand movement count, hesitation time, and confidence.
  - Confidence is clamped to `[0, 1]`.
  - Unknown hand areas are normalized to `unknown`.
- `PhysicalBehaviorContext`: round-level collection of behavior events.
  - Supports latest-event lookup by player and optional turn.
  - Supports player summaries for tsumogiri rate, average hesitation, movement count, low-confidence count, and latest areas.

## OpponentBelief Integration

- `OpponentBeliefEstimator.estimate_all` and `estimate_player` now accept optional `physical_context`.
- No physical context keeps Stage3 behavior unchanged.
- High-confidence physical signals add small rule-based adjustments and explanations:
  - long hesitation,
  - recent hand-cut source area,
  - draw insertion area,
  - hand movement before discard,
  - high observed tsumogiri rate.
- Low-confidence events are explained but ignored for scoring.

## Limits

- Behavior events are assumed to come from structured input or fixtures.
- No video parsing, camera tracking, tile localization, or gesture recognition is implemented.
- Physical behavior rules are heuristic and explainable; they do not claim direct psychological inference.
- Event ordering currently uses list order plus turn filtering, not wall-clock timestamps.

## Verification

- `python -m pytest tests/test_physical_behavior_context.py tests/test_opponent_estimator.py -q`: 14 passed.
- `python -m pytest tests/ -v -k "not gui"`: 162 passed, 9 deselected.
