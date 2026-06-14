"""
接受牌计算模块

计算麻将手牌的接受牌（有效牌）。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ..game_logic.tile import Tile
from ..game_logic.hand import Hand
from .shanten import ShantenCalculator, ShantenResult


@dataclass
class UkeireResult:
    """接受牌计算结果"""
    ukeire_tiles: List[Tile]  # 接受牌列表
    ukeire_count: int         # 接受牌总数
    shanten: int              # 当前向听数


class UkeireCalculator:
    """
    接受牌计算器
    
    计算手牌的接受牌（有效牌）。
    
    接受牌是指能够使向听数前进的牌。
    - 听牌时：接受牌就是和牌
    - 一向听时：接受牌就是能使手牌听牌的牌
    - ...
    """
    
    def __init__(self):
        """初始化接受牌计算器"""
        self._shanten_calculator = ShantenCalculator()
    
    def calculate(self, hand: Hand) -> UkeireResult:
        """
        计算接受牌
        
        Args:
            hand: 手牌
        
        Returns:
            接受牌计算结果
        """
        # 计算当前向听数
        current_result = self._shanten_calculator.calculate(hand)
        current_shanten = current_result.shanten
        
        # 如果已经和了，没有接受牌
        if current_shanten == -1:
            return UkeireResult(
                ukeire_tiles=[],
                ukeire_count=0,
                shanten=-1
            )
        
        # 计算接受牌
        ukeire_tiles = []
        tiles_34 = hand.to_34_array()
        
        for tile_id in range(Tile.TOTAL_TILES):
            # 尝试添加每种牌
            if tiles_34[tile_id] < 4:  # 最多4张
                # 创建新的手牌
                new_hand = hand.copy()
                new_hand.add_tile(Tile(tile_id))
                
                # 计算新的向听数
                new_result = self._shanten_calculator.calculate(new_hand)
                
                # 如果向听数前进，这是接受牌
                if new_result.shanten < current_shanten:
                    ukeire_tiles.append(Tile(tile_id))
        
        # 计算接受牌总数
        ukeire_count = 0
        for tile in ukeire_tiles:
            # 计算每种接受牌的剩余数量
            remaining = 4 - tiles_34[tile.tile_id]
            ukeire_count += remaining
        
        return UkeireResult(
            ukeire_tiles=ukeire_tiles,
            ukeire_count=ukeire_count,
            shanten=current_shanten
        )
    
    def calculate_for_discard(self, hand: Hand, discard_tile: Tile) -> UkeireResult:
        """
        计算打出某张牌后的接受牌
        
        Args:
            hand: 手牌
            discard_tile: 要打出的牌
        
        Returns:
            接受牌计算结果
        """
        # 创建新的手牌（打出指定牌）
        new_hand = hand.copy()
        new_hand.remove_tile(discard_tile)
        
        return self.calculate(new_hand)
    
    def calculate_all_discards(self, hand: Hand) -> Dict[Tile, UkeireResult]:
        """
        计算所有打牌的接受牌
        
        Args:
            hand: 手牌
        
        Returns:
            打牌到接受牌结果的映射
        """
        results = {}
        tiles_34 = hand.to_34_array()
        
        # 遍历手牌中的每种牌
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                results[tile] = self.calculate_for_discard(hand, tile)
        
        return results
    
    def get_best_discard(self, hand: Hand) -> Tuple[Tile, UkeireResult]:
        """
        获取最佳打牌
        
        Args:
            hand: 手牌
        
        Returns:
            最佳打牌和对应的接受牌结果
        """
        results = self.calculate_all_discards(hand)
        
        # 找出接受牌最多的打牌
        best_tile = None
        best_result = None
        
        for tile, result in results.items():
            if best_result is None or result.ukeire_count > best_result.ukeire_count:
                best_tile = tile
                best_result = result
        
        return best_tile, best_result
    
    def get_winning_tiles(self, hand: Hand) -> List[Tile]:
        """
        获取听牌的和牌
        
        Args:
            hand: 手牌
        
        Returns:
            和牌列表
        """
        # 计算当前向听数
        current_result = self._shanten_calculator.calculate(hand)
        
        # 如果不是听牌，返回空列表
        if current_result.shanten != 0:
            return []
        
        # 计算和牌
        winning_tiles = []
        tiles_34 = hand.to_34_array()
        
        for tile_id in range(Tile.TOTAL_TILES):
            # 尝试添加每种牌
            if tiles_34[tile_id] < 4:  # 最多4张
                # 创建新的手牌
                new_hand = hand.copy()
                new_hand.add_tile(tile_id)
                
                # 计算新的向听数
                new_result = self._shanten_calculator.calculate(new_hand)
                
                # 如果向听数为-1，这是和牌
                if new_result.shanten == -1:
                    winning_tiles.append(Tile(tile_id))
        
        return winning_tiles
    
    def calculate_ukeire_with_melds(self, hand: Hand) -> UkeireResult:
        """
        计算包含副露的手牌接受牌
        
        Args:
            hand: 手牌
        
        Returns:
            接受牌计算结果
        """
        # 对于有副露的手牌，需要特殊处理
        # 这里简化处理，只计算手牌部分
        
        # 获取手牌部分
        hand_tiles = hand.get_tiles()
        
        # 计算手牌部分的接受牌
        hand_hand = Hand.from_tiles(hand_tiles)
        result = self.calculate(hand_hand)
        
        return result