"""
手牌管理模块

管理麻将手牌，包括手牌的添加、删除、查询等操作。
"""

from typing import List, Dict, Optional, Tuple
from collections import Counter

from .tile import Tile


class Hand:
    """
    手牌类
    
    管理麻将手牌，支持以下功能：
    - 手牌的添加和删除
    - 手牌的查询和统计
    - 手牌的34数组表示
    - 副露管理
    """
    
    def __init__(self):
        """初始化空手牌"""
        self._tiles: List[Tile] = []
        self._melds: List[List[Tile]] = []  # 副露
        self._dora_indicators: List[Tile] = []  # 宝牌指示牌
    
    @classmethod
    def from_strings(cls, tile_strings: List[str]) -> 'Hand':
        """
        从字符串列表创建手牌
        
        Args:
            tile_strings: 牌的字符串列表
        
        Returns:
            Hand对象
        """
        hand = cls()
        for tile_str in tile_strings:
            hand.add_tile(Tile.from_string(tile_str))
        return hand
    
    @classmethod
    def from_tiles(cls, tiles: List[Tile]) -> 'Hand':
        """
        从Tile列表创建手牌
        
        Args:
            tiles: Tile对象列表
        
        Returns:
            Hand对象
        """
        hand = cls()
        for tile in tiles:
            hand.add_tile(tile)
        return hand
    
    def add_tile(self, tile: Tile) -> None:
        """
        添加一张牌到手牌
        
        Args:
            tile: 要添加的牌
        """
        self._tiles.append(tile)
    
    def remove_tile(self, tile: Tile) -> bool:
        """
        从手牌中删除一张牌
        
        Args:
            tile: 要删除的牌
        
        Returns:
            是否成功删除
        """
        try:
            self._tiles.remove(tile)
            return True
        except ValueError:
            return False
    
    def remove_tile_by_id(self, tile_id: int) -> bool:
        """
        根据牌ID删除一张牌
        
        Args:
            tile_id: 牌的ID
        
        Returns:
            是否成功删除
        """
        for i, tile in enumerate(self._tiles):
            if tile.tile_id == tile_id:
                self._tiles.pop(i)
                return True
        return False
    
    def get_tiles(self) -> List[Tile]:
        """
        获取所有手牌
        
        Returns:
            手牌列表
        """
        return self._tiles.copy()
    
    def get_tile_count(self) -> int:
        """
        获取手牌数量
        
        Returns:
            手牌数量
        """
        return len(self._tiles)
    
    def get_tile_counts(self) -> Dict[int, int]:
        """
        获取每种牌的数量
        
        Returns:
            牌ID到数量的映射
        """
        counts = Counter()
        for tile in self._tiles:
            counts[tile.tile_id] += 1
        return dict(counts)
    
    def to_34_array(self) -> List[int]:
        """
        转换为34数组表示
        
        34数组是一种紧凑的手牌表示方法：
        - 索引0-8: 万子1-9的数量
        - 索引9-17: 筒子1-9的数量
        - 索引18-26: 索子1-9的数量
        - 索引27-30: 风牌(东南西北)的数量
        - 索引31-33: 三元牌(白发中)的数量
        
        Returns:
            长度为34的整数列表
        """
        array = [0] * Tile.TOTAL_TILES
        for tile in self._tiles:
            array[tile.tile_id] += 1
        return array
    
    @classmethod
    def from_34_array(cls, array: List[int]) -> 'Hand':
        """
        从34数组创建手牌
        
        Args:
            array: 长度为34的整数列表
        
        Returns:
            Hand对象
        """
        if len(array) != Tile.TOTAL_TILES:
            raise ValueError(f"数组长度必须为{Tile.TOTAL_TILES}")
        
        hand = cls()
        for tile_id, count in enumerate(array):
            tile = Tile(tile_id)
            for _ in range(count):
                hand.add_tile(tile)
        return hand
    
    def add_meld(self, meld_tiles: List[Tile]) -> None:
        """
        添加副露
        
        Args:
            meld_tiles: 副露的牌列表
        """
        self._melds.append(meld_tiles)
    
    def get_melds(self) -> List[List[Tile]]:
        """
        获取所有副露
        
        Returns:
            副露列表
        """
        return self._melds.copy()
    
    def set_dora_indicators(self, indicators: List[Tile]) -> None:
        """
        设置宝牌指示牌
        
        Args:
            indicators: 宝牌指示牌列表
        """
        self._dora_indicators = indicators
    
    def get_dora_tiles(self) -> List[Tile]:
        """
        获取宝牌列表
        
        Returns:
            宝牌列表
        """
        dora_tiles = []
        for indicator in self._dora_indicators:
            dora_id = (indicator.tile_id + 1) % Tile.TOTAL_TILES
            dora_tiles.append(Tile(dora_id))
        return dora_tiles
    
    def count_dora(self) -> int:
        """
        计算手中的宝牌数量
        
        Returns:
            宝牌数量
        """
        dora_tiles = self.get_dora_tiles()
        count = 0
        for tile in self._tiles:
            if tile in dora_tiles:
                count += 1
        return count
    
    def sort_tiles(self) -> None:
        """对手牌进行排序"""
        self._tiles.sort(key=lambda t: t.tile_id)
    
    def get_sorted_tiles(self) -> List[Tile]:
        """
        获取排序后的手牌
        
        Returns:
            排序后的手牌列表
        """
        return sorted(self._tiles, key=lambda t: t.tile_id)
    
    def clear(self) -> None:
        """清空手牌"""
        self._tiles.clear()
        self._melds.clear()
        self._dora_indicators.clear()
    
    def copy(self) -> 'Hand':
        """
        复制手牌
        
        Returns:
            手牌副本
        """
        new_hand = Hand()
        new_hand._tiles = self._tiles.copy()
        new_hand._melds = [meld.copy() for meld in self._melds]
        new_hand._dora_indicators = self._dora_indicators.copy()
        return new_hand
    
    def __len__(self) -> int:
        return len(self._tiles)
    
    def __contains__(self, tile: Tile) -> bool:
        return tile in self._tiles
    
    def __iter__(self):
        return iter(self._tiles)
    
    def __repr__(self) -> str:
        tiles_str = ', '.join(str(tile) for tile in self.get_sorted_tiles())
        return f"Hand([{tiles_str}])"
    
    def __str__(self) -> str:
        return self.__repr__()


def create_hand_from_string(hand_str: str) -> Hand:
    """
    从字符串创建手牌
    
    Args:
        hand_str: 手牌字符串，如"1m2m3m4p5p6p7s8s9sEWN"
    
    Returns:
        Hand对象
    """
    hand = Hand()
    i = 0
    while i < len(hand_str):
        # 尝试解析数牌
        if i + 1 < len(hand_str) and hand_str[i].isdigit():
            number = int(hand_str[i])
            suit = hand_str[i + 1].lower()
            
            if suit in ['m', 'p', 's']:
                tile_str = f"{number}{suit}"
                hand.add_tile(Tile.from_string(tile_str))
                i += 2
                continue
        
        # 尝试解析字牌
        char = hand_str[i]
        if char in ['E', 'S', 'W', 'N', '东', '南', '西', '北']:
            hand.add_tile(Tile.from_string(char))
            i += 1
        elif char in ['白', '发', '中']:
            hand.add_tile(Tile.from_string(char))
            i += 1
        else:
            raise ValueError(f"无法解析字符: {char}")
    
    return hand