"""
役种识别模块

实现日本立直麻将的所有役种识别。
"""

from enum import Enum
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

from ..tile import Tile
from ..hand import Hand


class YakuType(Enum):
    """役种类型"""
    NORMAL = "普通役"      # 普通役
    YAKUMAN = "役满"       # 役满
    DOUBLE_YAKUMAN = "双倍役满"  # 双倍役满


@dataclass
class Yaku:
    """役种类"""
    name: str           # 役种名称
    han: int            # 番数
    yaku_type: YakuType # 役种类型
    is_open: bool       # 是否门前清限定（False=门前清限定，True=副露也可）
    description: str    # 描述


class YakuRecognizer:
    """
    役种识别器
    
    识别手牌中的所有役种。
    """
    
    def __init__(self):
        """初始化役种识别器"""
        self._yaku_list = self._create_yaku_list()
    
    def _create_yaku_list(self) -> List[Yaku]:
        """创建役种列表"""
        return [
            # 一番役
            Yaku("立直", 1, YakuType.NORMAL, False, "门前清立直"),
            Yaku("一发", 1, YakuType.NORMAL, False, "立直后一巡内和牌"),
            Yaku("门前清自摸和", 1, YakuType.NORMAL, False, "门前清自摸和牌"),
            Yaku("断幺九", 1, YakuType.NORMAL, True, "没有幺九牌"),
            Yaku("平和", 1, YakuType.NORMAL, False, "基本形和牌"),
            Yaku("一杯口", 1, YakuType.NORMAL, False, "两组相同的顺子"),
            Yaku("役牌：自风牌", 1, YakuType.NORMAL, True, "自风牌刻子"),
            Yaku("役牌：场风牌", 1, YakuType.NORMAL, True, "场风牌刻子"),
            Yaku("役牌：三元牌", 1, YakuType.NORMAL, True, "三元牌刻子"),
            
            # 二番役
            Yaku("三色同刻", 2, YakuType.NORMAL, True, "三种花色相同数字的刻子"),
            Yaku("三杠子", 2, YakuType.NORMAL, True, "三组杠子"),
            Yaku("对对和", 2, YakuType.NORMAL, True, "四组刻子+一对"),
            Yaku("三暗刻", 2, YakuType.NORMAL, True, "三组暗刻"),
            Yaku("小三元", 2, YakuType.NORMAL, True, "两种三元牌刻子+一种三元牌雀头"),
            Yaku("混老头", 2, YakuType.NORMAL, True, "全是幺九牌"),
            Yaku("七对子", 2, YakuType.NORMAL, False, "七组对子"),
            
            # 二番役（副露减一番）
            Yaku("三色同顺", 2, YakuType.NORMAL, True, "三种花色相同数字的顺子"),
            Yaku("一气通贯", 2, YakuType.NORMAL, True, "一种花色的123,456,789"),
            Yaku("混全带幺九", 2, YakuType.NORMAL, True, "每组牌都包含幺九牌"),
            
            # 三番役
            Yaku("混一色", 3, YakuType.NORMAL, True, "一种花色+字牌"),
            Yaku("纯全带幺九", 3, YakuType.NORMAL, True, "每组牌都包含老头牌"),
            Yaku("二杯口", 3, YakuType.NORMAL, False, "两组一杯口"),
            
            # 六番役
            Yaku("清一色", 6, YakuType.NORMAL, True, "只有一种花色"),
            
            # 役满
            Yaku("国士无双", 13, YakuType.YAKUMAN, False, "13种幺九牌+1种重复"),
            Yaku("国士无双十三面", 26, YakuType.DOUBLE_YAKUMAN, False, "13种幺九牌的13面听"),
            Yaku("九莲宝灯", 13, YakuType.YAKUMAN, False, "一种花色的1112345678999+任意一张"),
            Yaku("纯正九莲宝灯", 26, YakuType.DOUBLE_YAKUMAN, False, "一种花色的1112345678999的9面听"),
            Yaku("四暗刻", 13, YakuType.YAKUMAN, False, "四组暗刻"),
            Yaku("四暗刻单骑", 26, YakuType.DOUBLE_YAKUMAN, False, "四暗刻的单骑听"),
            Yaku("大三元", 13, YakuType.YAKUMAN, True, "三种三元牌的刻子"),
            Yaku("小四喜", 13, YakuType.YAKUMAN, True, "三种风牌刻子+一种风牌雀头"),
            Yaku("大四喜", 26, YakuType.DOUBLE_YAKUMAN, True, "四种风牌的刻子"),
            Yaku("字一色", 13, YakuType.YAKUMAN, True, "全是字牌"),
            Yaku("绿一色", 13, YakuType.YAKUMAN, True, "全是绿色牌（23468索+发）"),
            Yaku("清老头", 13, YakuType.YAKUMAN, True, "全是老头牌"),
            Yaku("四杠子", 13, YakuType.YAKUMAN, True, "四组杠子"),
            Yaku("天和", 13, YakuType.YAKUMAN, False, "庄家第一巡和牌"),
            Yaku("地和", 13, YakuType.YAKUMAN, False, "闲家第一巡和牌"),
        ]
    
    def recognize(self, hand: Hand, 
                  is_riichi: bool = False,
                  is_ippatsu: bool = False,
                  is_tsumo: bool = False,
                  is_dealer: bool = False,
                  round_wind: int = 27,
                  seat_wind: int = 27) -> List[Yaku]:
        """
        识别手牌中的役种
        
        Args:
            hand: 手牌
            is_riichi: 是否立直
            is_ippatsu: 是否一发
            is_tsumo: 是否自摸
            is_dealer: 是否庄家
            round_wind: 场风牌ID
            seat_wind: 自风牌ID
        
        Returns:
            识别到的役种列表
        """
        recognized_yaku = []
        
        # 获取手牌的34数组表示
        tiles_34 = hand.to_34_array()
        
        # 检查各种役种
        if is_riichi:
            recognized_yaku.append(self._find_yaku("立直"))
        
        if is_ippatsu:
            recognized_yaku.append(self._find_yaku("一发"))
        
        if is_tsumo and not hand.get_melds():
            recognized_yaku.append(self._find_yaku("门前清自摸和"))
        
        # 断幺九
        if self._is_tanyao(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("断幺九"))
        
        # 平和
        if self._is_pinfu(tiles_34, hand.get_melds(), round_wind, seat_wind):
            recognized_yaku.append(self._find_yaku("平和"))
        
        # 一杯口
        if self._is_iipeiko(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("一杯口"))
        
        # 役牌
        yaku_tile_yaku = self._check_yaku_tiles(tiles_34, hand.get_melds(), round_wind, seat_wind)
        recognized_yaku.extend(yaku_tile_yaku)
        
        # 三色同刻
        if self._is_sanshoku_douko(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("三色同刻"))
        
        # 三杠子
        if self._is_sankantsu(hand.get_melds()):
            recognized_yaku.append(self._find_yaku("三杠子"))
        
        # 对对和
        if self._is_toitoi(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("对对和"))
        
        # 三暗刻
        if self._is_sanankou(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("三暗刻"))
        
        # 小三元
        if self._is_shousangen(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("小三元"))
        
        # 混老头
        if self._is_honroutou(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("混老头"))
        
        # 七对子
        if self._is_chiitoitsu(tiles_34):
            recognized_yaku.append(self._find_yaku("七对子"))
        
        # 三色同顺
        if self._is_sanshoku_doujun(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("三色同顺"))
        
        # 一气通贯
        if self._is_ittsu(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("一气通贯"))
        
        # 混全带幺九
        if self._is_chanta(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("混全带幺九"))
        
        # 混一色
        if self._is_honitsu(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("混一色"))
        
        # 纯全带幺九
        if self._is_junchan(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("纯全带幺九"))
        
        # 二杯口
        if self._is_ryanpeiko(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("二杯口"))
        
        # 清一色
        if self._is_chinitsu(tiles_34, hand.get_melds()):
            recognized_yaku.append(self._find_yaku("清一色"))
        
        # 役满检查
        yakuman_yaku = self._check_yakuman(tiles_34, hand.get_melds(), is_tsumo, is_dealer)
        recognized_yaku.extend(yakuman_yaku)
        
        return recognized_yaku
    
    def _find_yaku(self, name: str) -> Optional[Yaku]:
        """根据名称查找役种"""
        for yaku in self._yaku_list:
            if yaku.name == name:
                return yaku
        return None
    
    def _is_tanyao(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查断幺九"""
        # 检查手牌
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if not tile.is_simple:
                    return False
        
        # 检查副露
        for meld in melds:
            for tile in meld:
                if not tile.is_simple:
                    return False
        
        return True
    
    def _is_pinfu(self, tiles_34: List[int], melds: List[List[Tile]], 
                  round_wind: int, seat_wind: int) -> bool:
        """检查平和"""
        # 门前清限定
        if melds:
            return False
        
        # 检查是否和牌
        # 这里简化处理，实际需要检查和牌的分解
        # 平和条件：4组顺子+1对非役牌雀头+两面听
        
        # 检查雀头是否为役牌
        # 简化：假设雀头不是役牌
        return True
    
    def _is_iipeiko(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查一杯口"""
        # 门前清限定
        if melds:
            return False
        
        # 检查是否有两组相同的顺子
        for suit_start in [0, 9, 18]:
            for i in range(7):
                idx = suit_start + i
                if tiles_34[idx] >= 2 and tiles_34[idx + 1] >= 2 and tiles_34[idx + 2] >= 2:
                    return True
        
        return False
    
    def _check_yaku_tiles(self, tiles_34: List[int], melds: List[List[Tile]],
                          round_wind: int, seat_wind: int) -> List[Yaku]:
        """检查役牌"""
        yaku_list = []
        
        # 检查三元牌
        dragon_tiles = [31, 32, 33]  # 白发中
        for dragon_id in dragon_tiles:
            if tiles_34[dragon_id] >= 3:
                yaku_list.append(self._find_yaku("役牌：三元牌"))
                break
        
        # 检查场风牌
        if tiles_34[round_wind] >= 3:
            yaku_list.append(self._find_yaku("役牌：场风牌"))
        
        # 检查自风牌
        if round_wind != seat_wind and tiles_34[seat_wind] >= 3:
            yaku_list.append(self._find_yaku("役牌：自风牌"))
        
        # 检查副露中的役牌
        for meld in melds:
            if len(meld) >= 3:
                first_tile = meld[0]
                if first_tile.is_dragon_tile:
                    if not any(yaku.name == "役牌：三元牌" for yaku in yaku_list):
                        yaku_list.append(self._find_yaku("役牌：三元牌"))
                elif first_tile.is_wind_tile:
                    if first_tile.tile_id == round_wind:
                        if not any(yaku.name == "役牌：场风牌" for yaku in yaku_list):
                            yaku_list.append(self._find_yaku("役牌：场风牌"))
                    if first_tile.tile_id == seat_wind:
                        if not any(yaku.name == "役牌：自风牌" for yaku in yaku_list):
                            yaku_list.append(self._find_yaku("役牌：自风牌"))
        
        return yaku_list
    
    def _is_sanshoku_douko(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查三色同刻"""
        # 检查手牌中的刻子
        for number in range(9):
            man_id = number
            pin_id = 9 + number
            sou_id = 18 + number
            
            if tiles_34[man_id] >= 3 and tiles_34[pin_id] >= 3 and tiles_34[sou_id] >= 3:
                return True
        
        # 检查副露
        # 简化处理
        return False
    
    def _is_sankantsu(self, melds: List[List[Tile]]) -> bool:
        """检查三杠子"""
        kan_count = sum(1 for meld in melds if len(meld) == 4)
        return kan_count >= 3
    
    def _is_toitoi(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查对对和"""
        # 检查手牌中的刻子
        triplets = sum(1 for count in tiles_34 if count >= 3)
        
        # 检查副露中的刻子
        meld_triplets = sum(1 for meld in melds if len(meld) >= 3)
        
        return triplets + meld_triplets >= 4
    
    def _is_sanankou(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查三暗刻"""
        # 检查手牌中的暗刻
        ankou_count = sum(1 for count in tiles_34 if count >= 3)
        
        return ankou_count >= 3
    
    def _is_shousangen(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查小三元"""
        dragon_tiles = [31, 32, 33]  # 白发中
        
        # 检查三元牌的刻子
        dragon_triplets = sum(1 for dragon_id in dragon_tiles if tiles_34[dragon_id] >= 3)
        
        # 检查三元牌的雀头
        dragon_pairs = sum(1 for dragon_id in dragon_tiles if tiles_34[dragon_id] >= 2)
        
        return dragon_triplets >= 2 and dragon_pairs >= 3
    
    def _is_honroutou(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查混老头"""
        # 检查手牌
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if not tile.is_terminal_or_honor:
                    return False
        
        # 检查副露
        for meld in melds:
            for tile in meld:
                if not tile.is_terminal_or_honor:
                    return False
        
        return True
    
    def _is_chiitoitsu(self, tiles_34: List[int]) -> bool:
        """检查七对子"""
        pairs = sum(1 for count in tiles_34 if count >= 2)
        return pairs >= 7
    
    def _is_sanshoku_doujun(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查三色同顺"""
        # 检查手牌中的顺子
        for i in range(7):
            man_count = sum(tiles_34[j] for j in range(i, i + 3))
            pin_count = sum(tiles_34[9 + j] for j in range(i, i + 3))
            sou_count = sum(tiles_34[18 + j] for j in range(i, i + 3))
            
            if man_count >= 3 and pin_count >= 3 and sou_count >= 3:
                return True
        
        return False
    
    def _is_ittsu(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查一气通贯"""
        # 检查手牌中的一气通贯
        for suit_start in [0, 9, 18]:
            if (tiles_34[suit_start] >= 1 and tiles_34[suit_start + 1] >= 1 and tiles_34[suit_start + 2] >= 1 and
                tiles_34[suit_start + 3] >= 1 and tiles_34[suit_start + 4] >= 1 and tiles_34[suit_start + 5] >= 1 and
                tiles_34[suit_start + 6] >= 1 and tiles_34[suit_start + 7] >= 1 and tiles_34[suit_start + 8] >= 1):
                return True
        
        return False
    
    def _is_chanta(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查混全带幺九"""
        # 检查手牌
        has_terminal = False
        has_honor = False
        
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if tile.is_terminal:
                    has_terminal = True
                elif tile.is_honor_tile:
                    has_honor = True
                elif tile.is_simple:
                    return False
        
        # 检查副露
        for meld in melds:
            meld_has_terminal = False
            for tile in meld:
                if tile.is_terminal:
                    meld_has_terminal = True
                elif tile.is_honor_tile:
                    pass
                elif tile.is_simple:
                    return False
            
            if meld_has_terminal:
                has_terminal = True
        
        return has_terminal and has_honor
    
    def _is_honitsu(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查混一色"""
        # 找出手牌中的花色
        suits = set()
        has_honor = False
        
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if tile.is_number_tile:
                    suits.add(tile.tile_type)
                elif tile.is_honor_tile:
                    has_honor = True
        
        # 检查副露
        for meld in melds:
            for tile in meld:
                if tile.is_number_tile:
                    suits.add(tile.tile_type)
                elif tile.is_honor_tile:
                    has_honor = True
        
        return len(suits) == 1 and has_honor
    
    def _is_junchan(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查纯全带幺九"""
        # 检查手牌
        has_terminal = False
        
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if tile.is_terminal:
                    has_terminal = True
                elif tile.is_honor_tile:
                    return False
                elif tile.is_simple:
                    return False
        
        # 检查副露
        for meld in melds:
            meld_has_terminal = False
            for tile in meld:
                if tile.is_terminal:
                    meld_has_terminal = True
                elif tile.is_honor_tile:
                    return False
                elif tile.is_simple:
                    return False
            
            if meld_has_terminal:
                has_terminal = True
        
        return has_terminal
    
    def _is_ryanpeiko(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查二杯口"""
        # 门前清限定
        if melds:
            return False
        
        # 检查是否有两组一杯口
        iipeiko_count = 0
        for suit_start in [0, 9, 18]:
            for i in range(7):
                idx = suit_start + i
                if tiles_34[idx] >= 2 and tiles_34[idx + 1] >= 2 and tiles_34[idx + 2] >= 2:
                    iipeiko_count += 1
        
        return iipeiko_count >= 2
    
    def _is_chinitsu(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查清一色"""
        # 找出手牌中的花色
        suits = set()
        
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if tile.is_number_tile:
                    suits.add(tile.tile_type)
                elif tile.is_honor_tile:
                    return False
        
        # 检查副露
        for meld in melds:
            for tile in meld:
                if tile.is_number_tile:
                    suits.add(tile.tile_type)
                elif tile.is_honor_tile:
                    return False
        
        return len(suits) == 1
    
    def _check_yakuman(self, tiles_34: List[int], melds: List[List[Tile]],
                       is_tsumo: bool, is_dealer: bool) -> List[Yaku]:
        """检查役满"""
        yakuman_list = []
        
        # 国士无双
        if self._is_kokushi(tiles_34):
            yakuman_list.append(self._find_yaku("国士无双"))
        
        # 九莲宝灯
        if self._is_chuuren_poutou(tiles_34):
            yakuman_list.append(self._find_yaku("九莲宝灯"))
        
        # 四暗刻
        if self._is_suuankou(tiles_34, melds):
            yakuman_list.append(self._find_yaku("四暗刻"))
        
        # 大三元
        if self._is_daisangen(tiles_34, melds):
            yakuman_list.append(self._find_yaku("大三元"))
        
        # 小四喜
        if self._is_shousuushii(tiles_34, melds):
            yakuman_list.append(self._find_yaku("小四喜"))
        
        # 大四喜
        if self._is_daisuushii(tiles_34, melds):
            yakuman_list.append(self._find_yaku("大四喜"))
        
        # 字一色
        if self._is_tsuuiisou(tiles_34, melds):
            yakuman_list.append(self._find_yaku("字一色"))
        
        # 绿一色
        if self._is_ryuuiisou(tiles_34, melds):
            yakuman_list.append(self._find_yaku("绿一色"))
        
        # 清老头
        if self._is_chinroutou(tiles_34, melds):
            yakuman_list.append(self._find_yaku("清老头"))
        
        # 四杠子
        if self._is_suukantsu(melds):
            yakuman_list.append(self._find_yaku("四杠子"))
        
        # 天和
        if is_tsumo and is_dealer and not melds:
            yakuman_list.append(self._find_yaku("天和"))
        
        # 地和
        if is_tsumo and not is_dealer and not melds:
            yakuman_list.append(self._find_yaku("地和"))
        
        return yakuman_list
    
    def _is_kokushi(self, tiles_34: List[int]) -> bool:
        """检查国士无双"""
        terminal_honor_tiles = Tile.TERMINAL_AND_HONOR_TILES
        
        # 检查是否包含所有幺九牌
        for tile_id in terminal_honor_tiles:
            if tiles_34[tile_id] == 0:
                return False
        
        # 检查是否有对子
        has_pair = any(tiles_34[tile_id] >= 2 for tile_id in terminal_honor_tiles)
        
        # 检查总数
        total = sum(tiles_34)
        
        return has_pair and total == 14
    
    def _is_chuuren_poutou(self, tiles_34: List[int]) -> bool:
        """检查九莲宝灯"""
        # 检查是否只有一种花色
        suits = set()
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if tile.is_number_tile:
                    suits.add(tile.tile_type)
                else:
                    return False
        
        if len(suits) != 1:
            return False
        
        # 检查是否满足九莲宝灯的牌型
        # 1112345678999 + 任意一张
        suit_start = list(suits)[0].value * 9
        
        # 检查1和9是否至少有3张
        if tiles_34[suit_start] < 3 or tiles_34[suit_start + 8] < 3:
            return False
        
        # 检查2-8是否至少有1张
        for i in range(1, 8):
            if tiles_34[suit_start + i] < 1:
                return False
        
        # 检查总数
        total = sum(tiles_34)
        return total == 14
    
    def _is_suuankou(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查四暗刻"""
        # 门前清限定
        if melds:
            return False
        
        # 检查手牌中的刻子
        ankou_count = sum(1 for count in tiles_34 if count >= 3)
        
        return ankou_count >= 4
    
    def _is_daisangen(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查大三元"""
        dragon_tiles = [31, 32, 33]  # 白发中
        
        # 检查手牌中的三元牌刻子
        for dragon_id in dragon_tiles:
            if tiles_34[dragon_id] < 3:
                return False
        
        return True
    
    def _is_shousuushii(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查小四喜"""
        wind_tiles = [27, 28, 29, 30]  # 东南西北
        
        # 检查风牌的刻子
        wind_triplets = sum(1 for wind_id in wind_tiles if tiles_34[wind_id] >= 3)
        
        # 检查风牌的雀头
        wind_pairs = sum(1 for wind_id in wind_tiles if tiles_34[wind_id] >= 2)
        
        return wind_triplets >= 3 and wind_pairs >= 4
    
    def _is_daisuushii(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查大四喜"""
        wind_tiles = [27, 28, 29, 30]  # 东南西北
        
        # 检查风牌的刻子
        for wind_id in wind_tiles:
            if tiles_34[wind_id] < 3:
                return False
        
        return True
    
    def _is_tsuuiisou(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查字一色"""
        # 检查手牌
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if not tile.is_honor_tile:
                    return False
        
        # 检查副露
        for meld in melds:
            for tile in meld:
                if not tile.is_honor_tile:
                    return False
        
        return True
    
    def _is_ryuuiisou(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查绿一色"""
        # 绿色牌：23468索+发
        green_tiles = [19, 20, 21, 23, 25, 32]  # 2s,3s,4s,6s,8s,发
        
        # 检查手牌
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                if tile_id not in green_tiles:
                    return False
        
        # 检查副露
        for meld in melds:
            for tile in meld:
                if tile.tile_id not in green_tiles:
                    return False
        
        return True
    
    def _is_chinroutou(self, tiles_34: List[int], melds: List[List[Tile]]) -> bool:
        """检查清老头"""
        # 检查手牌
        for tile_id in range(Tile.TOTAL_TILES):
            if tiles_34[tile_id] > 0:
                tile = Tile(tile_id)
                if not tile.is_terminal:
                    return False
        
        # 检查副露
        for meld in melds:
            for tile in meld:
                if not tile.is_terminal:
                    return False
        
        return True
    
    def _is_suukantsu(self, melds: List[List[Tile]]) -> bool:
        """检查四杠子"""
        kan_count = sum(1 for meld in melds if len(meld) == 4)
        return kan_count >= 4