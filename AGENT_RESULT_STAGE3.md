# Stage3 Result: OpponentBelief Baseline

## Summary

Added an explainable rule-based opponent belief baseline. This is not RL, not supervised learning, not an auto-play strategy, and not a video-understanding model.

## New Module

- `src/opponent/`
  - `OpponentBelief`: public belief data structure with bounded probabilities.
  - `OpponentBeliefEstimator`: estimates one belief per opponent from `PublicState`, `RoundContext`, and optional `CandidateDiscardRiskFeature` rows.

## Current Estimation Rules

- Riichi strongly raises `tenpai_prob`, `attack_prob`, and `speed_score`.
- Meld count raises `speed_score`; two or more melds also raise attack and tenpai estimates.
- Dealer seat slightly raises attack pressure.
- Candidate tile danger uses visible risk features:
  - genbutsu lowers danger,
  - suji lowers danger,
  - wall/no-chance lowers danger,
  - dora, aka dora, and yakuhai raise danger,
  - very low remaining count lowers wait risk.
- Suit intent is estimated from public meld and discard suit distribution.
- Explanations are plain rule-trigger strings, so downstream tools can inspect why a belief changed.

## Uncertainty and Limits

- No private hand inference beyond public signals.
- No learned calibration; probability values are heuristic baselines.
- No furiten, wait-shape, score-distribution, or hand-value model beyond supplied risk features.
- Suit intent is public-information only and can be wrong for closed hands.
- Physical timing, tsumogiri/tedashi source area, hesitation, and tile movement are not used yet.

## PhysicalBehaviorContext Next Step

Add a separate `PhysicalBehaviorContext` input with structured behavior events such as tsumogiri/tedashi, source area, hesitation time, and tile insertion/movement. The estimator should consume those as additional explainable rule features, not replace the current public-state baseline and not let a video model directly decide safe/dangerous tiles.

## Verification

- `python -m pytest tests/test_opponent_belief.py tests/test_opponent_estimator.py -q`: passed.
- `python -m pytest tests/ -v -k "not gui"`: 152 passed, 9 deselected.
