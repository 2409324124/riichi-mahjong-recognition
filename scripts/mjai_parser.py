"""
mjai 格式游戏记录解析器

解析 mjai 格式的游戏记录，用于验证麻将逻辑。
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from ..game_logic.tile import Tile
from ..game_logic.hand import Hand
from ..agent.validator import WinValidator, WinResult


class MjaiParser:
    """mjai 格式解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.validator = WinValidator()
    
    def parse_file(self, filepath: str) -> List[Dict]:
        """
        解析 mjai 文件
        
        Args:
            filepath: 文件路径
        
        Returns:
            事件列表
        """
        events = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events
    
    def parse_string(self, content: str) -> List[Dict]:
        """
        解析 mjai 字符串
        
        Args:
            content: mjai 格式字符串
        
        Returns:
            事件列表
        """
        events = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                events.append(json.loads(line))
        return events
    
    def convert_tile(self, mjai_tile: str) -> Tile:
        """
        转换 mjai 牌格式到我们的格式
        
        Args:
            mjai_tile: mjai 格式的牌 (如 "1m", "5p", "9s", "E", "S", "W", "N", "P", "F", "C")
        
        Returns:
            Tile 对象
        """
        if not mjai_tile or mjai_tile == '?':
            return None
        
        # 风牌
        wind_map = {'E': '东', 'S': '南', 'W': '西', 'N': '北'}
        if mjai_tile in wind_map:
            return Tile.from_string(wind_map[mjai_tile])
        
        # 三元牌
        dragon_map = {'P': '白', 'F': '发', 'C': '中'}
        if mjai_tile in dragon_map:
            return Tile.from_string(dragon_map[mjai_tile])
        
        # 数牌
        if len(mjai_tile) >= 2:
            number = mjai_tile[:-1]
            suit = mjai_tile[-1]
            
            # 处理红宝牌
            if number == '5' and suit in ['m', 'p', 's'] and len(mjai_tile) > 2:
                # 红宝牌 (5mr, 5pr, 5sr)
                return Tile.from_string(f'5{suit}')
            
            return Tile.from_string(f'{number}{suit}')
        
        return None
    
    def extract_hands_from_hora(self, event: Dict) -> Tuple[List[str], str]:
        """
        从 hora 事件中提取手牌
        
        Args:
            event: hora 事件
        
        Returns:
            (手牌列表, 和牌)
        """
        hora_tehais = event.get('hora_tehais', [])
        pai = event.get('pai', '')
        
        # 分离手牌和和牌
        hand_tiles = hora_tehais[:-1] if hora_tehais else []
        winning_tile = pai if pai else (hora_tehais[-1] if hora_tehais else '')
        
        return hand_tiles, winning_tile
    
    def validate_hora(self, event: Dict, 
                      is_tsumo: bool = True,
                      is_riichi: bool = False,
                      is_dealer: bool = False) -> WinResult:
        """
        验证 hora 事件
        
        Args:
            event: hora 事件
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            is_dealer: 是否庄家
        
        Returns:
            验证结果
        """
        # 提取手牌和和牌
        hand_tiles, winning_tile = self.extract_hands_from_hora(event)
        
        if not hand_tiles or not winning_tile:
            return WinResult(
                is_valid=False,
                error="无法提取手牌或和牌"
            )
        
        # 转换牌格式
        tiles = []
        for tile_str in hand_tiles:
            tile = self.convert_tile(tile_str)
            if tile:
                tiles.append(tile)
        
        winning = self.convert_tile(winning_tile)
        
        if not tiles or not winning:
            return WinResult(
                is_valid=False,
                error="牌格式转换失败"
            )
        
        # 创建手牌对象
        hand = Hand.from_tiles(tiles)
        
        # 验证和牌
        return self.validator.validate(
            hand=hand,
            winning_tile=winning,
            is_tsumo=is_tsumo,
            is_riichi=is_riichi,
            is_dealer=is_dealer
        )
    
    def analyze_game(self, filepath: str) -> List[Dict]:
        """
        分析整个游戏记录
        
        Args:
            filepath: 文件路径
        
        Returns:
            分析结果列表
        """
        events = self.parse_file(filepath)
        results = []
        
        for i, event in enumerate(events):
            if event.get('type') == 'hora':
                # 验证和牌
                result = self.validate_hora(event)
                results.append({
                    'event_index': i,
                    'event': event,
                    'validation': result
                })
        
        return results


if __name__ == "__main__":
    import sys
    
    parser = MjaiParser()
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        print(f"分析游戏记录: {filepath}")
        
        try:
            results = parser.analyze_game(filepath)
            print(f"分析成功，共 {len(results)} 个和牌事件")
            
            for i, result in enumerate(results):
                validation = result['validation']
                print(f"\n  [{i}] 和牌验证:")
                print(f"    有效: {validation.is_valid}")
                if validation.is_valid:
                    print(f"    番数: {validation.han}")
                    print(f"    符数: {validation.fu}")
                    print(f"    点数: {validation.points}")
                    print(f"    役种: {[y.name for y in validation.yaku_list]}")
                else:
                    print(f"    错误: {validation.error}")
        except Exception as e:
            print(f"分析失败: {e}")
    else:
        print("用法: python mjai_parser.py <mjai_file>")
        print("示例: python mjai_parser.py data/test_mjai.mjson")