"""
牌效分析模块

分析麻将手牌的牌效率，提供打牌建议。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..game_logic.tile import Tile
from ..game_logic.hand import Hand
from .shanten import ShantenCalculator, ShantenResult
from .ukeire import UkeireCalculator, UkeireResult


class AnalysisType(Enum):
    """分析类型"""
    SHANTEN = "向听"        # 向听分析
    UKEIRE = "接受牌"       # 接受牌分析
    EFFICIENCY = "牌效率"   # 牌效率分析
    DEFENSE = "防守"        # 防守分析


@dataclass
class DiscardAnalysis:
    """打牌分析结果"""
    tile: Tile                    # 打出的牌
    shanten: int                  # 打出后的向听数
    ukeire_tiles: List[Tile]      # 接受牌列表
    ukeire_count: int             # 接受牌总数
    efficiency: float             # 牌效率
    is_good_shape: bool           # 是否好形
    description: str              # 描述


@dataclass
class HandAnalysis:
    """手牌分析结果"""
    current_shanten: int          # 当前向听数
    hand_type: str                # 手牌类型
    discard_analyses: List[DiscardAnalysis]  # 打牌分析列表
    best_discard: Tile            # 最佳打牌
    best_analysis: DiscardAnalysis  # 最佳打牌分析
    winning_tiles: List[Tile]     # 和牌（如果听牌）


class EfficiencyAnalyzer:
    """
    牌效分析器
    
    分析手牌的牌效率，提供打牌建议。
    
    考虑因素：
    - 向听数
    - 接受牌数量
    - 接受牌质量（好形 vs 坏形）
    - 和牌点数
    """
    
    def __init__(self):
        """初始化牌效分析器"""
        self._shanten_calculator = ShantenCalculator()
        self._ukeire_calculator = UkeireCalculator()
    
    def analyze(self, hand: Hand) -> HandAnalysis:
        """
        分析手牌
        
        Args:
            hand: 手牌
        
        Returns:
            手牌分析结果
        """
        # 计算当前向听数
        shanten_result = self._shanten_calculator.calculate(hand)
        current_shanten = shanten_result.shanten
        
        # 计算所有打牌的分析
        discard_analyses = []
        tiles_34 = hand.to_34_array()
        
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                analysis = self._analyze_discard(hand, tile, current_shanten)
                discard_analyses.append(analysis)
        
        # 找出最佳打牌
        best_analysis = max(discard_analyses, key=lambda a: a.efficiency)
        best_discard = best_analysis.tile
        
        # 获取和牌（如果听牌）
        winning_tiles = []
        if current_shanten == 0:
            winning_tiles = self._ukeire_calculator.get_winning_tiles(hand)
        
        return HandAnalysis(
            current_shanten=current_shanten,
            hand_type=shanten_result.hand_type,
            discard_analyses=discard_analyses,
            best_discard=best_discard,
            best_analysis=best_analysis,
            winning_tiles=winning_tiles
        )
    
    def _analyze_discard(self, hand: Hand, discard_tile: Tile, current_shanten: int) -> DiscardAnalysis:
        """
        分析单个打牌
        
        Args:
            hand: 手牌
            discard_tile: 要打出的牌
            current_shanten: 当前向听数
        
        Returns:
            打牌分析结果
        """
        # 计算打出后的接受牌
        ukeire_result = self._ukeire_calculator.calculate_for_discard(hand, discard_tile)
        
        # 计算牌效率
        efficiency = self._calculate_efficiency(
            shanten=ukeire_result.shanten,
            ukeire_count=ukeire_result.ukeire_count,
            current_shanten=current_shanten
        )
        
        # 判断是否好形
        is_good_shape = self._is_good_shape(hand, discard_tile)
        
        # 生成描述
        description = self._generate_description(
            discard_tile=discard_tile,
            shanten=ukeire_result.shanten,
            ukeire_count=ukeire_result.ukeire_count,
            is_good_shape=is_good_shape
        )
        
        return DiscardAnalysis(
            tile=discard_tile,
            shanten=ukeire_result.shanten,
            ukeire_tiles=ukeire_result.ukeire_tiles,
            ukeire_count=ukeire_result.ukeire_count,
            efficiency=efficiency,
            is_good_shape=is_good_shape,
            description=description
        )
    
    def _calculate_efficiency(self, shanten: int, ukeire_count: int, current_shanten: int) -> float:
        """
        计算牌效率
        
        Args:
            shanten: 打出后的向听数
            ukeire_count: 接受牌总数
            current_shanten: 当前向听数
        
        Returns:
            牌效率值
        """
        # 如果向听数前进，效率更高
        if shanten < current_shanten:
            # 向听前进，效率 = 接受牌数量
            return float(ukeire_count)
        elif shanten == current_shanten:
            # 向听不变，效率 = 接受牌数量 * 0.5
            return float(ukeire_count) * 0.5
        else:
            # 向听后退，效率 = 0
            return 0.0
    
    def _is_good_shape(self, hand: Hand, discard_tile: Tile) -> bool:
        """
        判断是否好形
        
        Args:
            hand: 手牌
            discard_tile: 要打出的牌
        
        Returns:
            是否好形
        """
        # 好形判断标准：
        # 1. 两面听 > 双碰听 > 嵌张听 > 边张听 > 单骑听
        # 2. 听牌数量多
        
        # 这里简化处理，实际需要更复杂的判断
        return True
    
    def _generate_description(self, discard_tile: Tile, shanten: int, 
                              ukeire_count: int, is_good_shape: bool) -> str:
        """
        生成打牌描述
        
        Args:
            discard_tile: 打出的牌
            shanten: 打出后的向听数
            ukeire_count: 接受牌总数
            is_good_shape: 是否好形
        
        Returns:
            描述字符串
        """
        if shanten == -1:
            return f"打{discard_tile}和牌"
        elif shanten == 0:
            shape_str = "好形" if is_good_shape else "坏形"
            return f"打{discard_tile}听牌，接受{ukeire_count}张，{shape_str}"
        else:
            return f"打{discard_tile}，{shanten}向听，接受{ukeire_count}张"
    
    def get_recommendation(self, hand: Hand) -> str:
        """
        获取打牌建议
        
        Args:
            hand: 手牌
        
        Returns:
            打牌建议字符串
        """
        analysis = self.analyze(hand)
        
        if analysis.current_shanten == -1:
            return "已经和牌！"
        elif analysis.current_shanten == 0:
            winning_str = ", ".join(str(t) for t in analysis.winning_tiles)
            return f"听牌！和牌：{winning_str}"
        else:
            best = analysis.best_analysis
            return f"建议打{best.tile}，{best.description}"
    
    def compare_discards(self, hand: Hand, tile1: Tile, tile2: Tile) -> str:
        """
        比较两个打牌
        
        Args:
            hand: 手牌
            tile1: 第一个打牌
            tile2: 第二个打牌
        
        Returns:
            比较结果字符串
        """
        analysis1 = self._analyze_discard(hand, tile1, self._shanten_calculator.calculate(hand).shanten)
        analysis2 = self._analyze_discard(hand, tile2, self._shanten_calculator.calculate(hand).shanten)
        
        if analysis1.efficiency > analysis2.efficiency:
            return f"打{tile1}更好（效率：{analysis1.efficiency:.1f} vs {analysis2.efficiency:.1f}）"
        elif analysis2.efficiency > analysis1.efficiency:
            return f"打{tile2}更好（效率：{analysis2.efficiency:.1f} vs {analysis1.efficiency:.1f}）"
        else:
            return f"打{tile1}和打{tile2}效率相同（{analysis1.efficiency:.1f}）"