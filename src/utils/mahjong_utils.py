"""
麻将工具函数模块

提供麻将相关的工具函数。
"""

from typing import List, Dict, Optional, Tuple
from ..game_logic.tile import Tile


def tiles_to_string(tiles: List[Tile]) -> str:
    """
    将牌列表转换为字符串
    
    Args:
        tiles: 牌列表
    
    Returns:
        牌的字符串表示
    """
    return "".join(str(tile) for tile in tiles)


def string_to_tiles(tile_string: str) -> List[Tile]:
    """
    将字符串转换为牌列表
    
    Args:
        tile_string: 牌的字符串表示
    
    Returns:
        牌列表
    """
    tiles = []
    i = 0
    while i < len(tile_string):
        # 尝试解析数牌
        if i + 1 < len(tile_string) and tile_string[i].isdigit():
            number = int(tile_string[i])
            suit = tile_string[i + 1].lower()
            
            if suit in ['m', 'p', 's']:
                tile_str = f"{number}{suit}"
                tiles.append(Tile.from_string(tile_str))
                i += 2
                continue
        
        # 尝试解析字牌
        char = tile_string[i]
        if char in ['E', 'S', 'W', 'N', '东', '南', '西', '北']:
            tiles.append(Tile.from_string(char))
            i += 1
        elif char in ['白', '发', '中']:
            tiles.append(Tile.from_string(char))
            i += 1
        else:
            raise ValueError(f"无法解析字符: {char}")
    
    return tiles


def sort_tiles(tiles: List[Tile]) -> List[Tile]:
    """
    对牌进行排序
    
    Args:
        tiles: 牌列表
    
    Returns:
        排序后的牌列表
    """
    return sorted(tiles, key=lambda t: t.tile_id)


def count_tiles(tiles: List[Tile]) -> Dict[int, int]:
    """
    统计每种牌的数量
    
    Args:
        tiles: 牌列表
    
    Returns:
        牌ID到数量的映射
    """
    counts = {}
    for tile in tiles:
        counts[tile.tile_id] = counts.get(tile.tile_id, 0) + 1
    return counts


def get_tile_type_name(tile_type: int) -> str:
    """
    获取牌类型名称
    
    Args:
        tile_type: 牌类型ID
    
    Returns:
        牌类型名称
    """
    type_names = {
        0: "万子",
        1: "筒子",
        2: "索子",
        3: "风牌",
        4: "三元牌"
    }
    return type_names.get(tile_type, "未知")


def get_wind_name(wind_id: int) -> str:
    """
    获取风牌名称
    
    Args:
        wind_id: 风牌ID (27-30)
    
    Returns:
        风牌名称
    """
    wind_names = {
        27: "东",
        28: "南",
        29: "西",
        30: "北"
    }
    return wind_names.get(wind_id, "未知")


def get_dragon_name(dragon_id: int) -> str:
    """
    获取三元牌名称
    
    Args:
        dragon_id: 三元牌ID (31-33)
    
    Returns:
        三元牌名称
    """
    dragon_names = {
        31: "白",
        32: "发",
        33: "中"
    }
    return dragon_names.get(dragon_id, "未知")


def is_valid_hand(tiles: List[Tile]) -> bool:
    """
    检查手牌是否有效
    
    Args:
        tiles: 牌列表
    
    Returns:
        是否有效
    """
    # 检查牌数量
    if len(tiles) not in [13, 14]:
        return False
    
    # 检查每种牌的数量
    counts = count_tiles(tiles)
    for tile_id, count in counts.items():
        if count > 4:
            return False
    
    return True


def get_tile_display_name(tile: Tile) -> str:
    """
    获取牌的显示名称
    
    Args:
        tile: 牌对象
    
    Returns:
        牌的显示名称
    """
    if tile.is_number_tile:
        type_names = {0: "万", 1: "筒", 2: "索"}
        type_name = type_names[tile.tile_type.value]
        return f"{tile.number}{type_name}"
    elif tile.is_wind_tile:
        return get_wind_name(tile.tile_id)
    elif tile.is_dragon_tile:
        return get_dragon_name(tile.tile_id)
    else:
        return str(tile)


def format_hand(tiles: List[Tile]) -> str:
    """
    格式化手牌显示
    
    Args:
        tiles: 牌列表
    
    Returns:
        格式化后的手牌字符串
    """
    sorted_tiles = sort_tiles(tiles)
    return " ".join(get_tile_display_name(tile) for tile in sorted_tiles)