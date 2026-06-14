"""
麻将牌定义模块

定义日本立直麻将中的所有牌类型。
"""

from enum import Enum
from typing import List, Optional


class TileType(Enum):
    """牌类型枚举"""
    MAN = "万子"      # 万子
    PIN = "筒子"      # 筒子
    SOU = "索子"      # 索子
    WIND = "风牌"     # 风牌
    DRAGON = "三元牌"  # 三元牌


class Tile:
    """
    麻将牌类
    
    表示一张麻将牌，包含牌的类型和点数。
    
    编码规则：
    - 万子: 0-8 (1-9万)
    - 筒子: 9-17 (1-9筒)
    - 索子: 18-26 (1-9索)
    - 风牌: 27-30 (东南西北)
    - 三元牌: 31-33 (白发中)
    """
    
    # 牌的总数
    TOTAL_TILES = 34
    
    # 万子定义
    MAN_TILES = list(range(0, 9))      # 0-8: 1-9万
    # 筒子定义
    PIN_TILES = list(range(9, 18))     # 9-17: 1-9筒
    # 索子定义
    SOU_TILES = list(range(18, 27))    # 18-26: 1-9索
    # 风牌定义
    WIND_TILES = list(range(27, 31))   # 27-30: 东南西北
    # 三元牌定义
    DRAGON_TILES = list(range(31, 34)) # 31-33: 白发中
    
    # 字牌（风牌+三元牌）
    HONOR_TILES = WIND_TILES + DRAGON_TILES
    
    # 老头牌（1和9的数牌）
    TERMINAL_TILES = [0, 8, 9, 17, 18, 26]
    
    # 幺九牌（老头牌+字牌）
    TERMINAL_AND_HONOR_TILES = TERMINAL_TILES + HONOR_TILES
    
    # 数牌（万子+筒子+索子）
    NUMBER_TILES = MAN_TILES + PIN_TILES + SOU_TILES
    
    def __init__(self, tile_id: int):
        """
        初始化麻将牌
        
        Args:
            tile_id: 牌的ID (0-33)
        """
        if not (0 <= tile_id < self.TOTAL_TILES):
            raise ValueError(f"无效的牌ID: {tile_id}，必须在0-33之间")
        
        self._tile_id = tile_id
    
    @classmethod
    def from_string(cls, tile_str: str) -> 'Tile':
        """
        从字符串创建麻将牌
        
        Args:
            tile_str: 牌的字符串表示，如"1m", "2p", "3s", "E", "W", "N", "S", "白", "发", "中"
        
        Returns:
            Tile对象
        
        Raises:
            ValueError: 无效的牌字符串
        """
        tile_str = tile_str.strip().upper()
        
        # 解析风牌
        wind_map = {
            'E': 27,  # 东
            'S': 28,  # 南
            'W': 29,  # 西
            'N': 30,  # 北
            '东': 27,
            '南': 28,
            '西': 29,
            '北': 30,
        }
        
        if tile_str in wind_map:
            return cls(wind_map[tile_str])
        
        # 解析三元牌
        dragon_map = {
            '白': 31,
            '发': 32,
            '中': 33,
            'HAKU': 31,
            'HATSU': 32,
            'CHUN': 33,
        }
        
        if tile_str in dragon_map:
            return cls(dragon_map[tile_str])
        
        # 解析数牌
        if len(tile_str) >= 2:
            try:
                number = int(tile_str[0])
                suit = tile_str[1:].lower()
                
                if not (1 <= number <= 9):
                    raise ValueError(f"无效的牌数字: {number}")
                
                if suit == 'm':  # 万子
                    return cls(number - 1)
                elif suit == 'p':  # 筒子
                    return cls(9 + number - 1)
                elif suit == 's':  # 索子
                    return cls(18 + number - 1)
                else:
                    raise ValueError(f"无效的牌花色: {suit}")
            except ValueError as e:
                raise ValueError(f"无效的牌字符串: {tile_str}") from e
        
        raise ValueError(f"无效的牌字符串: {tile_str}")
    
    @property
    def tile_id(self) -> int:
        """获取牌ID"""
        return self._tile_id
    
    @property
    def tile_type(self) -> TileType:
        """获取牌类型"""
        if self._tile_id in self.MAN_TILES:
            return TileType.MAN
        elif self._tile_id in self.PIN_TILES:
            return TileType.PIN
        elif self._tile_id in self.SOU_TILES:
            return TileType.SOU
        elif self._tile_id in self.WIND_TILES:
            return TileType.WIND
        elif self._tile_id in self.DRAGON_TILES:
            return TileType.DRAGON
        else:
            raise ValueError(f"无效的牌ID: {self._tile_id}")
    
    @property
    def number(self) -> int:
        """
        获取牌的点数
        
        Returns:
            数牌: 1-9
            风牌: 1-4 (东南西北)
            三元牌: 1-3 (白发中)
        """
        if self._tile_id in self.NUMBER_TILES:
            return (self._tile_id % 9) + 1
        elif self._tile_id in self.WIND_TILES:
            return self._tile_id - 26  # 东=1, 南=2, 西=3, 北=4
        elif self._tile_id in self.DRAGON_TILES:
            return self._tile_id - 30  # 白=1, 发=2, 中=3
        else:
            raise ValueError(f"无效的牌ID: {self._tile_id}")
    
    @property
    def is_number_tile(self) -> bool:
        """是否为数牌"""
        return self._tile_id in self.NUMBER_TILES
    
    @property
    def is_honor_tile(self) -> bool:
        """是否为字牌"""
        return self._tile_id in self.HONOR_TILES
    
    @property
    def is_wind_tile(self) -> bool:
        """是否为风牌"""
        return self._tile_id in self.WIND_TILES
    
    @property
    def is_dragon_tile(self) -> bool:
        """是否为三元牌"""
        return self._tile_id in self.DRAGON_TILES
    
    @property
    def is_terminal(self) -> bool:
        """是否为老头牌（1或9的数牌）"""
        return self._tile_id in self.TERMINAL_TILES
    
    @property
    def is_terminal_or_honor(self) -> bool:
        """是否为幺九牌（老头牌或字牌）"""
        return self._tile_id in self.TERMINAL_AND_HONOR_TILES
    
    @property
    def is_simple(self) -> bool:
        """是否为中张牌（2-8的数牌）"""
        return self.is_number_tile and not self.is_terminal
    
    def to_string(self) -> str:
        """
        转换为字符串表示
        
        Returns:
            牌的字符串表示
        """
        if self._tile_id in self.MAN_TILES:
            return f"{self.number}m"
        elif self._tile_id in self.PIN_TILES:
            return f"{self.number}p"
        elif self._tile_id in self.SOU_TILES:
            return f"{self.number}s"
        elif self._tile_id in self.WIND_TILES:
            wind_names = ['E', 'S', 'W', 'N']
            return wind_names[self.number - 1]
        elif self._tile_id in self.DRAGON_TILES:
            dragon_names = ['白', '发', '中']
            return dragon_names[self.number - 1]
        else:
            raise ValueError(f"无效的牌ID: {self._tile_id}")
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Tile):
            return self._tile_id == other._tile_id
        return False
    
    def __hash__(self) -> int:
        return hash(self._tile_id)
    
    def __repr__(self) -> str:
        return f"Tile({self.to_string()})"
    
    def __str__(self) -> str:
        return self.to_string()


def create_tile_set() -> List[Tile]:
    """
    创建完整的牌组（每种牌4张）
    
    Returns:
        包含136张牌的列表
    """
    tiles = []
    for tile_id in range(Tile.TOTAL_TILES):
        tile = Tile(tile_id)
        tiles.extend([tile] * 4)
    return tiles


def create_hand_tiles(tile_strings: List[str]) -> List[Tile]:
    """
    从字符串列表创建手牌
    
    Args:
        tile_strings: 牌的字符串列表，如["1m", "2m", "3m"]
    
    Returns:
        Tile对象列表
    """
    return [Tile.from_string(s) for s in tile_strings]