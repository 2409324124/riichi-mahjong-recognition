"""
和牌验证器模块

验证麻将和牌的合法性，防止诈和。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from ..game_logic.tile import Tile
from ..game_logic.hand import Hand
from ..game_logic.scoring.score import ScoreCalculator, ScoreResult
from ..game_logic.scoring.yaku import Yaku, YakuRecognizer


@dataclass
class WinResult:
    """和牌验证结果"""
    is_valid: bool                    # 是否有效和牌
    error: Optional[str] = None       # 错误信息
    yaku_list: List[Yaku] = field(default_factory=list)  # 役种列表
    score: Optional[ScoreResult] = None  # 分数结果
    han: int = 0                      # 总番数
    fu: int = 0                       # 符数
    points: int = 0                   # 点数


class WinValidator:
    """
    和牌验证器
    
    验证麻将和牌的合法性，防止诈和。
    
    验证流程：
    1. 牌数检查 - 手牌必须是 14 张
    2. 和牌形状检查 - 必须满足和牌形状
    3. 役种检查 - 必须有役
    4. 振听检查 - 不能振听（可选）
    """
    
    def __init__(self):
        """初始化验证器"""
        self.yaku_recognizer = YakuRecognizer()
        self.score_calculator = ScoreCalculator()
    
    def validate(
        self,
        hand: Hand,
        winning_tile: Tile,
        is_tsumo: bool = False,
        is_riichi: bool = False,
        is_ippatsu: bool = False,
        is_dealer: bool = False,
        round_wind: int = 27,
        seat_wind: int = 27,
        game_state: Optional[Dict] = None
    ) -> WinResult:
        """
        验证和牌
        
        Args:
            hand: 手牌（13 张）
            winning_tile: 和的牌
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            is_ippatsu: 是否一发
            is_dealer: 是否庄家
            round_wind: 场风牌
            seat_wind: 自风牌
            game_state: 游戏状态（可选）
        
        Returns:
            WinResult: 验证结果
        """
        # 1. 牌数检查（手牌 + 副露 = 13 张）
        hand_tiles = hand.get_tiles()
        melds = hand.get_melds()
        meld_tiles_count = sum(len(meld) for meld in melds)
        total_tiles = len(hand_tiles) + meld_tiles_count
        
        if total_tiles != 13:
            return WinResult(
                is_valid=False,
                error=f"手牌+副露不是13张（当前手牌{len(hand_tiles)}张 + 副露{meld_tiles_count}张 = {total_tiles}张）"
            )
        
        # 添加和的牌，组成 14 张
        test_hand = hand.copy()
        test_hand.add_tile(winning_tile)
        
        # 2. 检查牌的合法性
        tiles = test_hand.get_tiles()
        tile_counts = {}
        for tile in tiles:
            tile_counts[tile.tile_id] = tile_counts.get(tile.tile_id, 0) + 1
        
        # 检查每种牌的数量不超过 4
        for tile_id, count in tile_counts.items():
            if count > 4:
                return WinResult(
                    is_valid=False,
                    error=f"牌 {Tile(tile_id)} 数量超过4张（当前{count}张）"
                )
        
        # 3. 和牌形状检查
        if not self._is_winning_shape(test_hand):
            return WinResult(
                is_valid=False,
                error="不满足和牌形状（4面子+1雀头 或 七对子 或 国士无双）"
            )
        
        # 4. 役种检查
        yaku_list = self.yaku_recognizer.recognize(
            hand=test_hand,
            is_tsumo=is_tsumo,
            is_riichi=is_riichi,
            is_ippatsu=is_ippatsu,
            is_dealer=is_dealer,
            round_wind=round_wind,
            seat_wind=seat_wind
        )
        
        if not yaku_list:
            return WinResult(
                is_valid=False,
                error="无役"
            )
        
        # 5. 计算分数
        try:
            score = self.score_calculator.calculate(
                hand=test_hand,
                winning_tile=winning_tile,
                is_tsumo=is_tsumo,
                is_riichi=is_riichi,
                is_ippatsu=is_ippatsu,
                is_dealer=is_dealer,
                round_wind=round_wind,
                seat_wind=seat_wind
            )
        except Exception as e:
            return WinResult(
                is_valid=False,
                error=f"分数计算失败: {str(e)}"
            )
        
        # 6. 振听检查（可选）
        if game_state and "discard_pool" in game_state:
            if self._is_furiten(hand, winning_tile, game_state["discard_pool"]):
                return WinResult(
                    is_valid=False,
                    error="振听"
                )
        
        # 验证通过
        return WinResult(
            is_valid=True,
            yaku_list=yaku_list,
            score=score,
            han=score.han,
            fu=score.fu,
            points=score.total_points
        )
    
    def _is_winning_shape(self, hand: Hand) -> bool:
        """
        检查是否满足和牌形状
        
        和牌形状：
        - 普通手：4面子 + 1雀头
        - 七对子：7组对子
        - 国士无双：13种幺九牌 + 1种重复
        """
        # 获取门前清手牌的 34 数组
        tiles_34 = hand.to_34_array()
        
        # 将副露的牌也加入到 34 数组中
        melds = hand.get_melds()
        for meld in melds:
            for tile in meld:
                tiles_34[tile.tile_id] += 1
        
        # 检查七对子
        if self._is_chiitoitsu(tiles_34):
            return True
        
        # 检查国士无双
        if self._is_kokushi(tiles_34):
            return True
        
        # 检查普通手（4面子 + 1雀头）
        return self._is_normal_win(tiles_34)
    
    def _is_chiitoitsu(self, tiles_34: List[int]) -> bool:
        """检查七对子（必须是7种不同的对子）"""
        # 每种牌必须恰好是2张（不能4张牌拆成2对）
        pairs = sum(1 for count in tiles_34 if count == 2)
        total_tiles = sum(tiles_34)
        return pairs == 7 and total_tiles == 14
    
    def _is_kokushi(self, tiles_34: List[int]) -> bool:
        """检查国士无双"""
        terminal_honor = Tile.TERMINAL_AND_HONOR_TILES
        
        # 检查是否包含所有幺九牌
        has_all = all(tiles_34[tile_id] >= 1 for tile_id in terminal_honor)
        if not has_all:
            return False
        
        # 检查是否有对子
        has_pair = any(tiles_34[tile_id] >= 2 for tile_id in terminal_honor)
        
        # 检查总数
        total = sum(tiles_34)
        
        return has_pair and total == 14
    
    def _is_normal_win(self, tiles_34: List[int]) -> bool:
        """检查普通手（4面子 + 1雀头）"""
        # 尝试所有可能的雀头
        for tile_id in range(34):
            if tiles_34[tile_id] >= 2:
                # 移除雀头
                temp = tiles_34.copy()
                temp[tile_id] -= 2
                
                # 检查是否能分解成 4 个面子
                if self._can_form_melds(temp, 4):
                    return True
        
        return False
    
    def _can_form_melds(self, tiles: List[int], num_melds: int) -> bool:
        """检查是否能分解成指定数量的面子"""
        if num_melds == 0:
            return sum(tiles) == 0
        
        # 找到第一个有牌的位置
        for tile_id in range(34):
            if tiles[tile_id] > 0:
                # 尝试刻子
                if tiles[tile_id] >= 3:
                    tiles[tile_id] -= 3
                    if self._can_form_melds(tiles, num_melds - 1):
                        tiles[tile_id] += 3
                        return True
                    tiles[tile_id] += 3
                
                # 尝试顺子（只对数牌有效）
                if tile_id < 27:  # 数牌
                    suit_start = (tile_id // 9) * 9
                    if (tile_id - suit_start) <= 6:  # 不超过 7
                        if (tiles[tile_id] >= 1 and 
                            tiles[tile_id + 1] >= 1 and 
                            tiles[tile_id + 2] >= 1):
                            tiles[tile_id] -= 1
                            tiles[tile_id + 1] -= 1
                            tiles[tile_id + 2] -= 1
                            if self._can_form_melds(tiles, num_melds - 1):
                                tiles[tile_id] += 1
                                tiles[tile_id + 1] += 1
                                tiles[tile_id + 2] += 1
                                return True
                            tiles[tile_id] += 1
                            tiles[tile_id + 1] += 1
                            tiles[tile_id + 2] += 1
                
                # 如果这个牌无法组成面子，返回 False
                return False
        
        return num_melds == 0
    
    def _is_furiten(self, hand: Hand, winning_tile: Tile, discard_pool: List[Tile]) -> bool:
        """
        检查振听
        
        振听条件：
        1. 自己的牌河中有和牌相关的牌
        2. 之前打出过和牌
        """
        # 检查牌河中是否有和牌
        for discard in discard_pool:
            if discard.tile_id == winning_tile.tile_id:
                return True
        
        return False
    
    def validate_hand_only(self, hand: Hand) -> Tuple[bool, str]:
        """
        仅验证手牌形状（不检查役种）
        
        Args:
            hand: 手牌（14 张）
        
        Returns:
            (is_valid, error_message)
        """
        tiles = hand.get_tiles()
        if len(tiles) != 14:
            return False, f"手牌不是14张（当前{len(tiles)}张）"
        
        if self._is_winning_shape(hand):
            return True, ""
        else:
            return False, "不满足和牌形状"
    
    def get_hand_info(self, hand: Hand) -> Dict:
        """
        获取手牌信息
        
        Args:
            hand: 手牌
        
        Returns:
            手牌信息字典
        """
        tiles = hand.get_tiles()
        tiles_34 = hand.to_34_array()
        
        return {
            "tile_count": len(tiles),
            "tiles": [str(t) for t in tiles],
            "is_chiitoitsu": self._is_chiitoitsu(tiles_34),
            "is_kokushi": self._is_kokushi(tiles_34),
            "is_normal": self._is_normal_win(tiles_34)
        }