# Human Mahjong Context Engine Plan

## Goal

Build the context and data foundation for human-game understanding:

- reconstruct public round context,
- prepare strict local validation diff reports,
- generate rule-based discard-risk label rows.

This is a data/context foundation only. It does not claim to model human psychology or train a Mahjong AI.

## Non-Goals

- No RL, supervised learning, Mortal integration, or video-understanding model.
- No changes to tile-recognition models or GUI.
- No rewrite of existing scoring, yaku, or `WinValidator`.
- Do not turn `scripts/majsoul_parser.py` into a strict validator; it remains a `trusted_external_result` reader.

## Current Branch

- `feature/human-mahjong-context-engine`

## Work Items

| Status | Item | Notes |
|---|---|---|
| complete | Context models | Added round, public state, verification input, and risk feature dataclasses. |
| complete | Majsoul strict validation scaffold | Added separate JSONL diff generator script. |
| complete | Risk label generator | First version supports mjai logs and nullable offline truth labels. |
| complete | Tests | Added context, trusted-reader, and risk feature tests. |
| complete | Report | Added concise implementation report in `AGENT_RESULT.md`. |
| in_progress | Mainline preparation | Review tracked files, sensitive strings, and final test status before merge/push. |

## Mainline Checklist

- [x] Keep changes scoped to context/risk/scaffold scripts/tests.
- [x] Preserve `majsoul_parser.validate_hora` trusted-reader semantics.
- [x] Keep risk sample small and derived.
- [x] Run non-GUI tests.
- [x] Check for local paths, private nicknames, and obvious sensitive strings in new files.
- [ ] Decide whether to merge this branch into `master`.
- [ ] Push only after confirming the target branch and intended public exposure.

## Remaining Follow-Up

- Add small anonymized Majsoul fixtures for strict diff tests.
- Normalize Majsoul melds into structured local meld objects.
- Add offline wait/ron truth extraction before filling `true_can_ron` and `true_loss_points`.
