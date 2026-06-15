"""
系统集成模块

将牌面识别、计分系统、牌效计算集成到一个完整流程。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from .game_logic.tile import Tile
from .game_logic.hand import Hand
from .game_logic.scoring.score import ScoreCalculator, ScoreResult
from .game_logic.scoring.yaku import YakuRecognizer
from .efficiency.shanten import ShantenCalculator, ShantenResult
from .efficiency.ukeire import UkeireCalculator, UkeireResult
from .efficiency.analyzer import EfficiencyAnalyzer, HandAnalysis
from .agent.validator import WinValidator, WinResult


@dataclass
class HandInfo:
    """手牌信息"""
    tiles: List[Tile]              # 手牌列表
    melds: List[List[Tile]]        # 副露列表
    dora_indicators: List[Tile]    # 宝牌指示牌
    round_wind: int                # 场风
    seat_wind: int                 # 自风


@dataclass
class AnalysisResult:
    """分析结果"""
    hand_info: HandInfo            # 手牌信息
    shanten: ShantenResult         # 向听数
    ukeire: Optional[UkeireResult] # 接受牌（听牌时为和牌）
    efficiency: Optional[HandAnalysis]  # 牌效分析
    win_result: Optional[WinResult] = None  # 和牌验证（如果和牌）


@dataclass
class GameState:
    """游戏状态"""
    round_number: int = 0          # 局数
    honba: int = 0                 # 本场
    riichi_sticks: int = 0         # 立直棒
    dora_indicators: List[Tile] = field(default_factory=list)
    players: List[Dict] = field(default_factory=list)


class MahjongSystem:
    """
    麻将系统主控制器
    
    整合牌面识别、计分系统、牌效计算。
    """
    
    def __init__(self):
        """初始化系统"""
        self.score_calculator = ScoreCalculator()
        self.yaku_recognizer = YakuRecognizer()
        self.shanten_calculator = ShantenCalculator()
        self.ukeire_calculator = UkeireCalculator()
        self.efficiency_analyzer = EfficiencyAnalyzer()
        self.win_validator = WinValidator()
    
    def analyze_hand(
        self,
        tile_strings: List[str],
        meld_strings: Optional[List[str]] = None,
        dora_indicators: Optional[List[str]] = None,
        round_wind: int = 27,
        seat_wind: int = 27
    ) -> AnalysisResult:
        """
        分析手牌
        
        Args:
            tile_strings: 手牌字符串列表，如 ["1m", "2m", "3m", ...]
            meld_strings: 副露字符串列表（可选）
            dora_indicators: 宝牌指示牌字符串列表（可选）
            round_wind: 场风（27=东, 28=南, 29=西, 30=北）
            seat_wind: 自风（27=东, 28=南, 29=西, 30=北）
        
        Returns:
            AnalysisResult: 分析结果
        """
        # 解析手牌
        tiles = [Tile.from_string(s) for s in tile_strings]
        hand = Hand.from_tiles(tiles)
        
        # 解析副露
        melds = []
        if meld_strings:
            for meld_str in meld_strings:
                meld_tiles = [Tile.from_string(s) for s in meld_str.split(",")]
                melds.append(meld_tiles)
                hand.add_meld(meld_tiles)
        
        # 解析宝牌指示牌
        dora_tiles = []
        if dora_indicators:
            dora_tiles = [Tile.from_string(s) for s in dora_indicators]
            hand.set_dora_indicators(dora_tiles)
        
        # 创建手牌信息
        hand_info = HandInfo(
            tiles=tiles,
            melds=melds,
            dora_indicators=dora_tiles,
            round_wind=round_wind,
            seat_wind=seat_wind
        )
        
        # 计算向听数
        shanten = self.shanten_calculator.calculate(hand)
        
        # 计算接受牌
        ukeire = None
        if shanten.shanten == 0:
            ukeire = self.ukeire_calculator.calculate(hand)
        
        # 牌效分析
        efficiency = None
        if shanten.shanten >= 0:
            efficiency = self.efficiency_analyzer.analyze(hand)
        
        return AnalysisResult(
            hand_info=hand_info,
            shanten=shanten,
            ukeire=ukeire,
            efficiency=efficiency
        )
    
    def validate_win(
        self,
        tile_strings: List[str],
        winning_tile_str: str,
        meld_strings: Optional[List[str]] = None,
        is_tsumo: bool = False,
        is_riichi: bool = False,
        is_ippatsu: bool = False,
        is_dealer: bool = False,
        round_wind: int = 27,
        seat_wind: int = 27
    ) -> WinResult:
        """
        验证和牌
        
        Args:
            tile_strings: 手牌字符串列表（13张，不含和牌）
            winning_tile_str: 和牌字符串
            meld_strings: 副露字符串列表（可选）
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            is_ippatsu: 是否一发
            is_dealer: 是否庄家
            round_wind: 场风
            seat_wind: 自风
        
        Returns:
            WinResult: 验证结果
        """
        # 解析手牌
        tiles = [Tile.from_string(s) for s in tile_strings]
        hand = Hand.from_tiles(tiles)
        
        # 解析副露
        if meld_strings:
            for meld_str in meld_strings:
                meld_tiles = [Tile.from_string(s) for s in meld_str.split(",")]
                hand.add_meld(meld_tiles)
        
        # 解析和牌
        winning_tile = Tile.from_string(winning_tile_str)
        
        # 验证和牌
        return self.win_validator.validate(
            hand=hand,
            winning_tile=winning_tile,
            is_tsumo=is_tsumo,
            is_riichi=is_riichi,
            is_ippatsu=is_ippatsu,
            is_dealer=is_dealer,
            round_wind=round_wind,
            seat_wind=seat_wind
        )
    
    def calculate_score(
        self,
        tile_strings: List[str],
        winning_tile_str: str,
        meld_strings: Optional[List[str]] = None,
        is_tsumo: bool = False,
        is_riichi: bool = False,
        is_ippatsu: bool = False,
        is_dealer: bool = False,
        round_wind: int = 27,
        seat_wind: int = 27
    ) -> ScoreResult:
        """
        计算点数
        
        Args:
            tile_strings: 手牌字符串列表（13张，不含和牌）
            winning_tile_str: 和牌字符串
            meld_strings: 副露字符串列表（可选）
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            is_ippatsu: 是否一发
            is_dealer: 是否庄家
            round_wind: 场风
            seat_wind: 自风
        
        Returns:
            ScoreResult: 点数计算结果
        """
        # 解析手牌
        tiles = [Tile.from_string(s) for s in tile_strings]
        hand = Hand.from_tiles(tiles)
        
        # 解析副露
        if meld_strings:
            for meld_str in meld_strings:
                meld_tiles = [Tile.from_string(s) for s in meld_str.split(",")]
                hand.add_meld(meld_tiles)
        
        # 解析和牌
        winning_tile = Tile.from_string(winning_tile_str)
        
        # 计算点数
        return self.score_calculator.calculate(
            hand=hand,
            winning_tile=winning_tile,
            is_tsumo=is_tsumo,
            is_riichi=is_riichi,
            is_ippatsu=is_ippatsu,
            is_dealer=is_dealer,
            round_wind=round_wind,
            seat_wind=seat_wind
        )
    
    def get_discard_recommendation(
        self,
        tile_strings: List[str],
        meld_strings: Optional[List[str]] = None
    ) -> Dict:
        """
        获取打牌推荐
        
        Args:
            tile_strings: 手牌字符串列表（14张）
            meld_strings: 副露字符串列表（可选）
        
        Returns:
            推荐结果字典
        """
        # 解析手牌
        tiles = [Tile.from_string(s) for s in tile_strings]
        hand = Hand.from_tiles(tiles)
        
        # 解析副露
        if meld_strings:
            for meld_str in meld_strings:
                meld_tiles = [Tile.from_string(s) for s in meld_str.split(",")]
                hand.add_meld(meld_tiles)
        
        # 分析手牌
        analysis = self.efficiency_analyzer.analyze(hand)
        
        # 获取推荐
        best_discard = analysis.best_discard
        best_analysis = analysis.best_analysis
        
        return {
            "current_shanten": analysis.current_shanten,
            "hand_type": analysis.hand_type,
            "best_discard": str(best_discard),
            "best_discard_reason": best_analysis.description,
            "ukeire_count": best_analysis.ukeire_count,
            "ukeire_tiles": [str(t) for t in best_analysis.ukeire_tiles],
            "all_discards": [
                {
                    "tile": str(a.tile),
                    "shanten": a.shanten,
                    "ukeire_count": a.ukeire_count,
                    "efficiency": a.efficiency,
                    "description": a.description
                }
                for a in analysis.discard_analyses
            ]
        }
    
    def format_analysis(self, result: AnalysisResult) -> str:
        """
        格式化分析结果
        
        Args:
            result: 分析结果
        
        Returns:
            格式化后的字符串
        """
        lines = []
        
        # 手牌
        hand_str = " ".join(str(t) for t in result.hand_info.tiles)
        lines.append(f"手牌: {hand_str}")
        
        # 副露
        if result.hand_info.melds:
            melds_str = " | ".join(
                " ".join(str(t) for t in meld)
                for meld in result.hand_info.melds
            )
            lines.append(f"副露: {melds_str}")
        
        # 向听数
        shanten = result.shanten.shanten
        if shanten == -1:
            lines.append("状态: 和了")
        elif shanten == 0:
            lines.append("状态: 听牌")
        else:
            lines.append(f"状态: {shanten}向听")
        
        # 接受牌
        if result.ukeire:
            ukeire_str = ", ".join(str(t) for t in result.ukeire.ukeire_tiles)
            lines.append(f"接受牌: {ukeire_str} ({result.ukeire.ukeire_count}张)")
        
        # 牌效分析
        if result.efficiency and result.efficiency.current_shanten >= 0:
            lines.append(f"最佳打牌: {result.efficiency.best_discard}")
            lines.append(f"理由: {result.efficiency.best_analysis.description}")
        
        # 和牌信息
        if result.win_result and result.win_result.is_valid:
            lines.append(f"番数: {result.win_result.han}")
            lines.append(f"符数: {result.win_result.fu}")
            lines.append(f"点数: {result.win_result.points}")
            yaku_str = ", ".join(y.name for y in result.win_result.yaku_list)
            lines.append(f"役种: {yaku_str}")
        
        return "\n".join(lines)


# 便捷函数
def analyze_hand(tile_strings: List[str], **kwargs) -> AnalysisResult:
    """分析手牌的便捷函数"""
    system = MahjongSystem()
    return system.analyze_hand(tile_strings, **kwargs)


def validate_win(tile_strings: List[str], winning_tile_str: str, **kwargs) -> WinResult:
    """验证和牌的便捷函数"""
    system = MahjongSystem()
    return system.validate_win(tile_strings, winning_tile_str, **kwargs)


def get_recommendation(tile_strings: List[str], **kwargs) -> Dict:
    """获取打牌推荐的便捷函数"""
    system = MahjongSystem()
    return system.get_discard_recommendation(tile_strings, **kwargs)