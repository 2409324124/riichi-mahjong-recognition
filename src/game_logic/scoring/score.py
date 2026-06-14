"""
点数计算模块

实现日本立直麻将的点数计算逻辑。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..tile import Tile
from ..hand import Hand
from .yaku import Yaku, YakuRecognizer, YakuType
from .fu import FuCalculator, FuResult


class ScoreType(Enum):
    """点数类型"""
    NORMAL = "普通"           # 普通
    MANGAN = "满贯"           # 满贯
    HANEMAN = "跳满"          # 跳满
    BAIMAN = "倍满"           # 倍满
    SANBAIMAN = "三倍满"      # 三倍满
    YAKUMAN = "役满"          # 役满


@dataclass
class ScoreResult:
    """点数计算结果"""
    han: int              # 番数
    fu: int               # 符数
    score_type: ScoreType # 点数类型
    total_points: int     # 总点数
    payment: Dict[str, int]  # 支付详情
    yaku_list: List[Yaku] # 役种列表
    fu_details: Dict[str, int]  # 符数详情


class ScoreCalculator:
    """
    点数计算器
    
    计算日本立直麻将的点数。
    
    点数计算规则：
    - 基本点 = 符 × 2^(番 + 2)
    - 满贯以上固定点数：
      - 满贯：8000点
      - 跳满：12000点
      - 倍满：16000点
      - 三倍满：24000点
      - 役满：32000点
    - 支付方式：
      - 自摸：庄家支付50%，闲家支付50%
      - 荣和：放铳者支付100%
    """
    
    def __init__(self):
        """初始化点数计算器"""
        self._yaku_recognizer = YakuRecognizer()
        self._fu_calculator = FuCalculator()
    
    def calculate(self, hand: Hand,
                  winning_tile: Tile,
                  is_tsumo: bool = False,
                  is_riichi: bool = False,
                  is_ippatsu: bool = False,
                  is_dealer: bool = False,
                  round_wind: int = 27,
                  seat_wind: int = 27,
                  is_first_round: bool = False) -> ScoreResult:
        """
        计算点数
        
        Args:
            hand: 手牌
            winning_tile: 和牌
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            is_ippatsu: 是否一发
            is_dealer: 是否庄家
            round_wind: 场风牌ID
            seat_wind: 自风牌ID
            is_first_round: 是否第一巡（天和/地和）
        
        Returns:
            点数计算结果
        """
        # 识别役种
        yaku_list = self._yaku_recognizer.recognize(
            hand=hand,
            is_riichi=is_riichi,
            is_ippatsu=is_ippatsu,
            is_tsumo=is_tsumo,
            is_dealer=is_dealer,
            round_wind=round_wind,
            seat_wind=seat_wind
        )
        
        # 检查是否有役
        if not yaku_list:
            raise ValueError("无役不能和牌")
        
        # 计算符数
        fu_result = self._fu_calculator.calculate(
            hand=hand,
            winning_tile=winning_tile,
            is_tsumo=is_tsumo,
            is_riichi=is_riichi,
            is_ippatsu=is_ippatsu,
            round_wind=round_wind,
            seat_wind=seat_wind,
            yaku_list=yaku_list
        )
        
        # 计算总番数
        total_han = sum(yaku.han for yaku in yaku_list)
        
        # 检查役满
        yakuman_yaku = [yaku for yaku in yaku_list if yaku.yaku_type in [YakuType.YAKUMAN, YakuType.DOUBLE_YAKUMAN]]
        
        if yakuman_yaku:
            # 役满固定点数
            score_type = ScoreType.YAKUMAN
            total_points = 32000 * len(yakuman_yaku)
        else:
            # 计算点数类型
            score_type = self._get_score_type(total_han)
            
            # 计算基本点
            if score_type == ScoreType.NORMAL:
                base_points = fu_result.fu * (2 ** (total_han + 2))
                total_points = base_points
            elif score_type == ScoreType.MANGAN:
                total_points = 8000
            elif score_type == ScoreType.HANEMAN:
                total_points = 12000
            elif score_type == ScoreType.BAIMAN:
                total_points = 16000
            elif score_type == ScoreType.SANBAIMAN:
                total_points = 24000
        
        # 计算支付
        payment = self._calculate_payment(
            total_points=total_points,
            is_tsumo=is_tsumo,
            is_dealer=is_dealer
        )
        
        return ScoreResult(
            han=total_han,
            fu=fu_result.fu,
            score_type=score_type,
            total_points=total_points,
            payment=payment,
            yaku_list=yaku_list,
            fu_details=fu_result.details
        )
    
    def _get_score_type(self, han: int) -> ScoreType:
        """根据番数获取点数类型"""
        if han >= 13:
            return ScoreType.YAKUMAN
        elif han >= 11:
            return ScoreType.SANBAIMAN
        elif han >= 8:
            return ScoreType.BAIMAN
        elif han >= 6:
            return ScoreType.HANEMAN
        elif han >= 5:
            return ScoreType.MANGAN
        else:
            return ScoreType.NORMAL
    
    def _calculate_payment(self, total_points: int, is_tsumo: bool, is_dealer: bool) -> Dict[str, int]:
        """
        计算支付详情
        
        Args:
            total_points: 总点数
            is_tsumo: 是否自摸
            is_dealer: 是否庄家
        
        Returns:
            支付详情字典
        """
        payment = {}
        
        if is_tsumo:
            if is_dealer:
                # 庄家自摸：闲家每人支付1/3
                per_player = self._round_up_payment(total_points / 3)
                payment["闲家"] = per_player
                payment["总点数"] = per_player * 3
            else:
                # 闲家自摸：庄家支付1/2，闲家支付1/4
                dealer_payment = self._round_up_payment(total_points / 2)
                other_payment = self._round_up_payment(total_points / 4)
                payment["庄家"] = dealer_payment
                payment["闲家"] = other_payment
                payment["总点数"] = dealer_payment + other_payment * 2
        else:
            # 荣和：放铳者支付全部
            payment["放铳者"] = total_points
            payment["总点数"] = total_points
        
        return payment
    
    def _round_up_payment(self, points: float) -> int:
        """向上取整到100的倍数"""
        return ((int(points) + 99) // 100) * 100
    
    def calculate_from_result(self, hand: Hand,
                              winning_tile: Tile,
                              is_tsumo: bool = False,
                              is_dealer: bool = False,
                              round_wind: int = 27,
                              seat_wind: int = 27) -> ScoreResult:
        """
        从结果计算点数（简化版）
        
        Args:
            hand: 手牌
            winning_tile: 和牌
            is_tsumo: 是否自摸
            is_dealer: 是否庄家
            round_wind: 场风牌ID
            seat_wind: 自风牌ID
        
        Returns:
            点数计算结果
        """
        return self.calculate(
            hand=hand,
            winning_tile=winning_tile,
            is_tsumo=is_tsumo,
            is_dealer=is_dealer,
            round_wind=round_wind,
            seat_wind=seat_wind
        )
    
    def get_score_table(self) -> Dict[Tuple[int, int], Dict[str, int]]:
        """
        获取点数表
        
        Returns:
            点数表字典，键为(番数, 符数)，值为支付详情
        """
        score_table = {}
        
        # 普通点数
        for han in range(1, 5):
            for fu in [20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110]:
                base_points = fu * (2 ** (han + 2))
                
                # 自摸支付
                if han >= 5:
                    # 满贯以上
                    if han == 5:
                        total_points = 8000
                    elif han == 6 or han == 7:
                        total_points = 12000
                    elif han == 8 or han == 9 or han == 10:
                        total_points = 16000
                    elif han == 11 or han == 12:
                        total_points = 24000
                    else:
                        total_points = 32000
                else:
                    total_points = base_points
                
                # 计算支付
                dealer_tsumo = self._round_up_payment(total_points / 3)
                non_dealer_tsumo_dealer = self._round_up_payment(total_points / 2)
                non_dealer_tsumo_other = self._round_up_payment(total_points / 4)
                ron = total_points
                
                score_table[(han, fu)] = {
                    "庄家自摸": dealer_tsumo,
                    "闲家自摸_庄家": non_dealer_tsumo_dealer,
                    "闲家自摸_闲家": non_dealer_tsumo_other,
                    "荣和": ron
                }
        
        # 满贯
        score_table[(5, 0)] = {
            "庄家自摸": 2000,
            "闲家自摸_庄家": 4000,
            "闲家自摸_闲家": 2000,
            "荣和": 8000
        }
        
        # 跳满
        score_table[(6, 0)] = {
            "庄家自摸": 3000,
            "闲家自摸_庄家": 6000,
            "闲家自摸_闲家": 3000,
            "荣和": 12000
        }
        score_table[(7, 0)] = score_table[(6, 0)]
        
        # 倍满
        score_table[(8, 0)] = {
            "庄家自摸": 4000,
            "闲家自摸_庄家": 8000,
            "闲家自摸_闲家": 4000,
            "荣和": 16000
        }
        score_table[(9, 0)] = score_table[(8, 0)]
        score_table[(10, 0)] = score_table[(8, 0)]
        
        # 三倍满
        score_table[(11, 0)] = {
            "庄家自摸": 6000,
            "闲家自摸_庄家": 12000,
            "闲家自摸_闲家": 6000,
            "荣和": 24000
        }
        score_table[(12, 0)] = score_table[(11, 0)]
        
        # 役满
        score_table[(13, 0)] = {
            "庄家自摸": 8000,
            "闲家自摸_庄家": 16000,
            "闲家自摸_闲家": 8000,
            "荣和": 32000
        }
        
        return score_table