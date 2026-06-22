from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from src.context import CandidateDiscardRiskFeature, PublicState, RoundContext

from .belief import OpponentBelief, clamp_probability


class OpponentBeliefEstimator:
    """Rule-based, explainable opponent belief baseline."""

    def estimate_all(
        self,
        public_state: PublicState,
        round_context: RoundContext,
        actor: int,
        risk_features: Optional[Iterable[CandidateDiscardRiskFeature]] = None,
    ) -> Dict[int, OpponentBelief]:
        features_by_target = defaultdict(list)
        for feature in risk_features or []:
            features_by_target[feature.target_player].append(feature)

        beliefs = {}
        for seat in sorted(public_state.players):
            if seat == actor:
                continue
            beliefs[seat] = self.estimate_player(
                public_state=public_state,
                round_context=round_context,
                seat=seat,
                risk_features=features_by_target.get(seat, []),
            )
        return beliefs

    def estimate_player(
        self,
        public_state: PublicState,
        round_context: RoundContext,
        seat: int,
        risk_features: Iterable[CandidateDiscardRiskFeature] = (),
    ) -> OpponentBelief:
        player = public_state.players[seat]
        turn = round_context.current_turn
        meld_count = len(player.melds)
        explanation: List[str] = []

        speed_score = 0.12 + min(turn, 18) * 0.015 + meld_count * 0.22
        tenpai_prob = 0.08 + min(turn, 18) * 0.018 + meld_count * 0.14
        attack_prob = 0.18 + meld_count * 0.12
        defense_prob = 0.22

        if player.riichi_declared:
            tenpai_prob = max(tenpai_prob, 0.92)
            attack_prob = max(attack_prob, 0.86)
            speed_score = max(speed_score, 0.78)
            defense_prob = min(defense_prob, 0.08)
            explanation.append("riichi declared: tenpai and attack are high")

        if meld_count:
            explanation.append(f"{meld_count} meld(s): hand is likely faster")
            if meld_count >= 2:
                attack_prob += 0.12
                tenpai_prob += 0.08

        if seat == round_context.dealer:
            attack_prob += 0.06
            explanation.append("dealer seat: attack pressure is higher")

        suit_intent = self._estimate_suit_intent(player.melds, player.discards)
        dominant_suit, dominant_score = max(suit_intent.items(), key=lambda item: item[1])
        if dominant_score >= 0.45 and dominant_suit != "honor":
            explanation.append(f"{dominant_suit}-suit tiles dominate open information")

        danger_by_tile = {}
        for feature in risk_features:
            danger, reasons = self._danger_for_feature(feature)
            danger_by_tile[feature.candidate_tile] = danger
            explanation.extend(reasons)

        return OpponentBelief(
            player_id=seat,
            tenpai_prob=tenpai_prob,
            speed_score=speed_score,
            attack_prob=attack_prob,
            defense_prob=defense_prob,
            suit_intent=suit_intent,
            danger_by_tile=danger_by_tile,
            explanation=explanation,
        )

    def _danger_for_feature(self, feature: CandidateDiscardRiskFeature) -> tuple[float, List[str]]:
        danger = 0.32
        reasons = []

        if feature.target_riichi:
            danger += 0.22
            reasons.append(f"{feature.candidate_tile}: target riichi raises danger")
        if feature.is_genbutsu:
            danger = max(danger - 0.34, 0.04)
            reasons.append(f"{feature.candidate_tile}: genbutsu lowers danger")
        elif feature.is_suji:
            danger -= 0.14
            reasons.append(f"{feature.candidate_tile}: suji lowers danger")
        if feature.is_kabe or feature.is_no_chance:
            danger -= 0.10
            reasons.append(f"{feature.candidate_tile}: wall/no-chance lowers danger")
        if feature.is_dora:
            danger += 0.24
            reasons.append(f"{feature.candidate_tile}: dora raises danger")
        if feature.is_aka_dora:
            danger += 0.16
            reasons.append(f"{feature.candidate_tile}: aka dora raises danger")
        if feature.is_yakuhai:
            danger += 0.08
            reasons.append(f"{feature.candidate_tile}: yakuhai raises value risk")
        if feature.remaining_count <= 1:
            danger -= 0.08
            reasons.append(f"{feature.candidate_tile}: few remaining copies lower wait risk")
        if feature.target_meld_count >= 2:
            danger += 0.08

        return clamp_probability(danger), reasons

    def _estimate_suit_intent(self, melds: List[List[str]], discards: List[str]) -> Dict[str, float]:
        counts = {"m": 0.0, "p": 0.0, "s": 0.0, "honor": 0.0}
        for meld in melds:
            for tile in meld:
                counts[self._tile_group(tile)] += 2.0
        for tile in discards:
            group = self._tile_group(tile)
            if group != "honor":
                counts[group] += 0.3

        total = sum(counts.values())
        if total == 0:
            return {"m": 0.25, "p": 0.25, "s": 0.25, "honor": 0.25}
        return {group: clamp_probability(score / total) for group, score in counts.items()}

    def _tile_group(self, tile: str) -> str:
        if not tile:
            return "honor"
        if tile[-1] in {"m", "p", "s"}:
            return tile[-1]
        return "honor"
