"""
向听数计算模块

计算麻将手牌的向听数。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ..game_logic.tile import Tile
from ..game_logic.hand import Hand


@dataclass
class ShantenResult:
    """向听数计算结果"""
    shanten: int  # 向听数（0=听牌，-1=和了）
    hand_type: str  # 手牌类型（普通、七对子、国士无双）


class ShantenCalculator:
    """
    向听计算器
    
    计算手牌的向听数。
    
    向听数表示手牌距离听牌还需要多少张牌。
    - -1: 和了
    - 0: 听牌
    - 1: 一向听
    - 2: 二向听
    - ...
    
    支持三种手牌类型：
    - 普通手：4组面子+1对雀头
    - 七对子：7组对子
    - 国士无双：13种幺九牌+1种重复
    """
    
    def calculate(self, hand: Hand) -> ShantenResult:
        """
        计算向听数
        
        Args:
            hand: 手牌
        
        Returns:
            向听数计算结果
        """
        tiles_34 = hand.to_34_array()
        
        # 计算三种手牌类型的向听数
        normal_shanten = self._calculate_normal_shanten(tiles_34)
        chiitoitsu_shanten = self._calculate_chiitoitsu_shanten(tiles_34)
        kokushi_shanten = self._calculate_kokushi_shanten(tiles_34)
        
        # 取最小值
        min_shanten = min(normal_shanten, chiitoitsu_shanten, kokushi_shanten)
        
        # 确定手牌类型
        if min_shanten == normal_shanten:
            hand_type = "普通"
        elif min_shanten == chiitoitsu_shanten:
            hand_type = "七对子"
        else:
            hand_type = "国士无双"
        
        return ShantenResult(shanten=min_shanten, hand_type=hand_type)
    
    def _calculate_normal_shanten(self, tiles_34: List[int]) -> int:
        """
        计算普通手的向听数
        
        Args:
            tiles_34: 34数组表示的手牌
        
        Returns:
            向听数
        """
        # 使用递归算法计算向听数
        # 这里使用简化的算法，实际可以使用更高效的算法
        
        total_tiles = sum(tiles_34)
        if total_tiles == 0:
            return 8  # 空手牌
        
        # 计算面子和雀头
        max_sets = 0
        max_pairs = 0
        
        # 尝试所有可能的雀头
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] >= 2:
                # 尝试这个雀头
                tiles_34[tile_id] -= 2
                
                # 计算面子
                sets = self._count_sets(tiles_34)
                
                # 恢复雀头
                tiles_34[tile_id] += 2
                
                if sets > max_sets:
                    max_sets = sets
                    max_pairs = 1
        
        # 如果没有雀头，计算没有雀头的情况
        if max_pairs == 0:
            max_sets = self._count_sets(tiles_34)
        
        # 计算向听数
        # 向听数 = 8 - 2*面子数 - 雀头数
        shanten = 8 - 2 * max_sets - max_pairs
        
        return shanten
    
    def _count_sets(self, tiles_34: List[int]) -> int:
        """
        计算面子数
        
        Args:
            tiles_34: 34数组表示的手牌
        
        Returns:
            面子数
        """
        # 使用贪心算法计算面子数
        # 优先刻子，其次顺子
        
        sets = 0
        
        # 计算刻子
        for tile_id in range(Tile.TOTAL_TILES):
            while tiles_34[tile_id] >= 3:
                tiles_34[tile_id] -= 3
                sets += 1
        
        # 计算顺子
        for suit_start in [0, 9, 18]:
            for i in range(7):
                idx = suit_start + i
                while (tiles_34[idx] >= 1 and 
                       tiles_34[idx + 1] >= 1 and 
                       tiles_34[idx + 2] >= 1):
                    tiles_34[idx] -= 1
                    tiles_34[idx + 1] -= 1
                    tiles_34[idx + 2] -= 1
                    sets += 1
        
        return sets
    
    def _calculate_chiitoitsu_shanten(self, tiles_34: List[int]) -> int:
        """
        计算七对子的向听数
        
        Args:
            tiles_34: 34数组表示的手牌
        
        Returns:
            向听数
        """
        pairs = 0
        unique_tiles = 0
        
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] >= 2:
                pairs += 1
                unique_tiles += 1
            elif tiles_34[tile_id] == 1:
                unique_tiles += 1
        
        # 七对子向听数 = 6 - 对子数 + max(0, 7 - 不同牌数)
        shanten = 6 - pairs + max(0, 7 - unique_tiles)
        
        return shanten
    
    def _calculate_kokushi_shanten(self, tiles_34: List[int]) -> int:
        """
        计算国士无双的向听数
        
        Args:
            tiles_34: 34数组表示的手牌
        
        Returns:
            向听数
        """
        terminal_honor_tiles = Tile.TERMINAL_AND_HONOR_TILES
        
        # 计算幺九牌的种类数
        unique_terminal_honor = 0
        has_pair = False
        
        for tile_id in terminal_honor_tiles:
            if tiles_34[tile_id] >= 1:
                unique_terminal_honor += 1
                if tiles_34[tile_id] >= 2:
                    has_pair = True
        
        # 国士无双向听数 = 13 - 幺九牌种类数 - (1 if 有对子 else 0)
        shanten = 13 - unique_terminal_honor - (1 if has_pair else 0)
        
        return shanten
    
    def calculate_with_melds(self, hand: Hand) -> ShantenResult:
        """
        计算包含副露的手牌向听数
        
        Args:
            hand: 手牌
        
        Returns:
            向听数计算结果
        """
        # 对于有副露的手牌，需要特殊处理
        # 这里简化处理，只计算手牌部分
        
        # 获取手牌部分
        hand_tiles = hand.get_tiles()
        
        # 计算副露的面子数
        meld_sets = len(hand.get_melds())
        
        # 计算手牌部分的向听数
        hand_hand = Hand.from_tiles(hand_tiles)
        result = self.calculate(hand_hand)
        
        # 调整向听数（考虑副露的面子）
        # 向听数 = 手牌向听数 - 2*副露面子数
        adjusted_shanten = result.shanten - 2 * meld_sets
        
        return ShantenResult(shanten=adjusted_shanten, hand_type=result.hand_type)
    
    def is_tenpai(self, hand: Hand) -> bool:
        """
        检查是否听牌
        
        Args:
            hand: 手牌
        
        Returns:
            是否听牌
        """
        result = self.calculate(hand)
        return result.shanten == 0
    
    def is_agari(self, hand: Hand) -> bool:
        """
        检查是否和了
        
        Args:
            hand: 手牌
        
        Returns:
            是否和了
        """
        result = self.calculate(hand)
        return result.shanten == -1