"""
符数计算模块

实现日本立直麻将的符数计算逻辑。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ..tile import Tile
from ..hand import Hand
from .yaku import Yaku


@dataclass
class FuResult:
    """符数计算结果"""
    fu: int             # 符数
    details: Dict[str, int]  # 详细分解


class FuCalculator:
    """
    符数计算器
    
    计算手牌的符数。
    
    符数计算规则：
    - 基本符：20符
    - 自摸：2符（平和除外）
    - 门前清荣和：10符
    - 雀头：役牌2符，其他0符
    - 面子：
      - 明刻：2符（中张）/4符（幺九）
      - 暗刻：4符（中张）/8符（幺九）
      - 明杠：8符（中张）/16符（幺九）
      - 暗杠：16符（中张）/32符（幺九）
    - 听牌形式：
      - 两面听：0符
      - 双碰听：0符
      - 嵌张听：2符
      - 边张听：2符
      - 单骑听：2符
    """
    
    def calculate(self, hand: Hand, 
                  winning_tile: Tile,
                  is_tsumo: bool = False,
                  is_riichi: bool = False,
                  is_ippatsu: bool = False,
                  round_wind: int = 27,
                  seat_wind: int = 27,
                  yaku_list: List[Yaku] = None) -> FuResult:
        """
        计算符数
        
        Args:
            hand: 手牌
            winning_tile: 和牌
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            is_ippatsu: 是否一发
            round_wind: 场风牌ID
            seat_wind: 自风牌ID
            yaku_list: 役种列表
        
        Returns:
            符数计算结果
        """
        if yaku_list is None:
            yaku_list = []
        
        details = {}
        fu = 0
        
        # 检查是否平和
        is_pinfu = any(yaku.name == "平和" for yaku in yaku_list)
        
        # 检查是否七对子
        is_chiitoitsu = any(yaku.name == "七对子" for yaku in yaku_list)
        
        # 七对子固定25符
        if is_chiitoitsu:
            return FuResult(fu=25, details={"七对子": 25})
        
        # 基本符
        fu += 20
        details["基本符"] = 20
        
        # 自摸加符
        if is_tsumo and not is_pinfu:
            fu += 2
            details["自摸"] = 2
        
        # 门前清荣和加符
        if not is_tsumo and not hand.get_melds():
            fu += 10
            details["门前清荣和"] = 10
        
        # 雀头加符
        pair_fu = self._calculate_pair_fu(hand, round_wind, seat_wind)
        if pair_fu > 0:
            fu += pair_fu
            details["雀头"] = pair_fu
        
        # 面子加符
        meld_fu, meld_details = self._calculate_meld_fu(hand)
        fu += meld_fu
        details.update(meld_details)
        
        # 听牌形式加符
        wait_fu = self._calculate_wait_fu(hand, winning_tile)
        if wait_fu > 0:
            fu += wait_fu
            details["听牌形式"] = wait_fu
        
        # 平和自摸固定20符
        if is_pinfu and is_tsumo:
            fu = 20
            details = {"平和自摸": 20}
        
        # 向上取整到10的倍数
        fu = ((fu + 9) // 10) * 10
        
        return FuResult(fu=fu, details=details)
    
    def _calculate_pair_fu(self, hand: Hand, round_wind: int, seat_wind: int) -> int:
        """计算雀头符数"""
        tiles_34 = hand.to_34_array()
        
        # 找到雀头
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] >= 2:
                tile = Tile(tile_id)
                
                # 检查是否为役牌
                if tile.is_dragon_tile:
                    return 2  # 三元牌
                elif tile.is_wind_tile:
                    if tile.tile_id == round_wind:
                        return 2  # 场风牌
                    if tile.tile_id == seat_wind:
                        return 2  # 自风牌
                
                break
        
        return 0
    
    def _calculate_meld_fu(self, hand: Hand) -> Tuple[int, Dict[str, int]]:
        """计算面子符数"""
        fu = 0
        details = {}
        
        # 检查手牌中的刻子
        tiles_34 = hand.to_34_array()
        
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] >= 3:
                tile = Tile(tile_id)
                
                # 计算刻子符数
                if tile.is_terminal_or_honor:
                    # 幺九牌
                    if tiles_34[tile_id] == 3:
                        fu += 4  # 暗刻
                        details[f"暗刻({tile})"] = 4
                    elif tiles_34[tile_id] == 4:
                        fu += 16  # 暗杠
                        details[f"暗杠({tile})"] = 16
                else:
                    # 中张牌
                    if tiles_34[tile_id] == 3:
                        fu += 2  # 暗刻
                        details[f"暗刻({tile})"] = 2
                    elif tiles_34[tile_id] == 4:
                        fu += 8  # 暗杠
                        details[f"暗杠({tile})"] = 8
        
        # 检查副露
        for meld in hand.get_melds():
            if len(meld) >= 3:
                first_tile = meld[0]
                
                # 计算副露面子符数
                if first_tile.is_terminal_or_honor:
                    # 幺九牌
                    if len(meld) == 3:
                        fu += 2  # 明刻
                        details[f"明刻({first_tile})"] = 2
                    elif len(meld) == 4:
                        fu += 8  # 明杠
                        details[f"明杠({first_tile})"] = 8
                else:
                    # 中张牌
                    if len(meld) == 3:
                        fu += 1  # 明刻
                        details[f"明刻({first_tile})"] = 1
                    elif len(meld) == 4:
                        fu += 4  # 明杠
                        details[f"明杠({first_tile})"] = 4
        
        return fu, details
    
    def _calculate_wait_fu(self, hand: Hand, winning_tile: Tile) -> int:
        """计算听牌形式符数"""
        tiles_34 = hand.to_34_array()
        winning_id = winning_tile.tile_id
        
        # 检查单骑听
        if tiles_34[winning_id] == 1:
            return 2
        
        # 检查其他听牌形式
        # 这里简化处理，实际需要分析听牌的具体形式
        
        # 检查嵌张听
        if winning_tile.is_number_tile:
            number = winning_tile.number
            # 计算花色起始索引
            if winning_tile.tile_id < 9:
                suit_start = 0  # 万子
            elif winning_tile.tile_id < 18:
                suit_start = 9  # 筒子
            else:
                suit_start = 18  # 索子
            
            # 检查是否为嵌张
            if 2 <= number <= 8:
                left_id = suit_start + number - 2
                right_id = suit_start + number
                
                if tiles_34[left_id] > 0 and tiles_34[right_id] > 0:
                    return 2
        
        # 检查边张听
        if winning_tile.is_number_tile:
            number = winning_tile.number
            
            # 计算花色起始索引
            if winning_tile.tile_id < 9:
                suit_start = 0  # 万子
            elif winning_tile.tile_id < 18:
                suit_start = 9  # 筒子
            else:
                suit_start = 18  # 索子
            
            # 检查是否为边张
            if number == 3:
                if tiles_34[suit_start] > 0 and tiles_34[suit_start + 1] > 0:
                    return 2
            elif number == 7:
                if tiles_34[suit_start + 6] > 0 and tiles_34[suit_start + 7] > 0:
                    return 2
        
        return 0