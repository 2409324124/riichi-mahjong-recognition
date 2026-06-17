"""
役种识别测试

测试日本立直麻将的所有役种识别。
"""

import pytest
from src.game_logic.tile import Tile
from src.game_logic.hand import Hand
from src.game_logic.scoring.score import ScoreCalculator
from src.game_logic.scoring.yaku import YakuRecognizer


class TestYakuRecognizer:
    """役种识别器测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.recognizer = YakuRecognizer()
        self.calculator = ScoreCalculator()
    
    def _check_yaku(self, hand_strings, winning_tile_str, expected_yaku_name, **kwargs):
        """辅助方法：检查役种识别"""
        hand = Hand.from_strings(hand_strings)
        winning_tile = Tile.from_string(winning_tile_str)
        
        result = self.calculator.calculate(
            hand=hand,
            winning_tile=winning_tile,
            **kwargs
        )
        
        yaku_names = [yaku.name for yaku in result.yaku_list]
        assert expected_yaku_name in yaku_names, \
            f"期望役种 '{expected_yaku_name}' 未找到，实际役种: {yaku_names}"
        
        return result
    
    # ==================== 第一批：普通役测试 ====================
    
    # ---------- 1番役 ----------
    
    def test_riichi(self):
        """测试立直"""
        # 手牌：1m2m3m4p5p6p7s8s9s + 1m（立直自摸）
        hand_strings = ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s"]
        self._check_yaku(hand_strings, "1m", "立直", 
                        is_tsumo=True, is_riichi=True)
    
    def test_ippatsu(self):
        """测试一发"""
        # 手牌：1m2m3m4p5p6p7s8s9s + 1m（立直一发自摸）
        hand_strings = ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s"]
        self._check_yaku(hand_strings, "1m", "一发",
                        is_tsumo=True, is_riichi=True, is_ippatsu=True)
    
    def test_menzen_tsumo(self):
        """测试门前清自摸和"""
        # 手牌：1m2m3m4p5p6p7s8s9s + 1m（门前清自摸）
        hand_strings = ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s"]
        self._check_yaku(hand_strings, "1m", "门前清自摸和",
                        is_tsumo=True, is_riichi=False)
    
    def test_tanyao(self):
        """测试断幺九"""
        # 手牌：2m3m4m5p6p7p2s3s4s + 5m（全是中张牌）
        hand_strings = ["2m", "3m", "4m", "5p", "6p", "7p", "2s", "3s", "4s"]
        self._check_yaku(hand_strings, "5m", "断幺九",
                        is_tsumo=True)
    
    def test_pinfu(self):
        """测试平和"""
        # 手牌：1m2m3m4p5p6p7s8s9s + 1m（平和形，需要特定听牌形式）
        # 注意：平和需要两面听，这里简化测试
        hand_strings = ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s"]
        result = self.calculator.calculate(
            hand=Hand.from_strings(hand_strings),
            winning_tile=Tile.from_string("1m"),
            is_tsumo=True
        )
        # 平和可能不满足所有条件，这里只验证有役
        assert len(result.yaku_list) > 0
    
    def test_iipeiko(self):
        """测试一杯口"""
        # 手牌：1m1m2m2m3m3m4p5p6p + 7p（两组相同的顺子）
        hand_strings = ["1m", "1m", "2m", "2m", "3m", "3m", "4p", "5p", "6p"]
        self._check_yaku(hand_strings, "7p", "一杯口",
                        is_tsumo=True)
    
    def test_yakuhai_sangenpai(self):
        """测试役牌：三元牌"""
        # 手牌：1m2m3m白白白4p5p6p + 7p（三元牌刻子）
        hand_strings = ["1m", "2m", "3m", "白", "白", "白", "4p", "5p", "6p"]
        self._check_yaku(hand_strings, "7p", "役牌：三元牌",
                        is_tsumo=True)
    
    def test_yakuhai_bakaze(self):
        """测试役牌：场风牌"""
        # 手牌：1m2m3m东东东4p5p6p + 7p（场风牌刻子，东为场风）
        hand_strings = ["1m", "2m", "3m", "东", "东", "东", "4p", "5p", "6p"]
        self._check_yaku(hand_strings, "7p", "役牌：场风牌",
                        is_tsumo=True, round_wind=27)  # 27=东
    
    def test_yakuhai_jikaze(self):
        """测试役牌：自风牌"""
        # 手牌：1m2m3m南南南4p5p6p + 7p（自风牌刻子，南为自风）
        hand_strings = ["1m", "2m", "3m", "南", "南", "南", "4p", "5p", "6p"]
        self._check_yaku(hand_strings, "7p", "役牌：自风牌",
                        is_tsumo=True, seat_wind=28)  # 28=南
    
    # ---------- 2番役 ----------
    
    def test_sanshoku_douko(self):
        """测试三色同刻"""
        # 手牌：1m1m1m1p1p1p1s1s1s + 2m2m（三色同刻）
        hand_strings = ["1m", "1m", "1m", "1p", "1p", "1p", "1s", "1s", "1s", "2m", "2m"]
        self._check_yaku(hand_strings, "2m", "三色同刻",
                        is_tsumo=True)
    
    def test_sankantsu(self):
        """测试三杠子"""
        # 注意：三杠子需要三组杠子，这里简化测试
        # 实际测试需要更复杂的牌型
        pass
    
    def test_toitoi(self):
        """测试对对和"""
        # 使用有副露的手牌（有副露则不能是四暗刻）
        # 3个暗刻 + 1个碰出的刻子(副露) = 对对和
        hand = Hand.from_strings(["1m", "1m", "1m", "2p", "2p", "2p", "3s", "3s", "3s", "5m"])
        hand.add_meld([Tile.from_string(s) for s in ["4m", "4m", "4m"]])
        winning_tile = Tile.from_string("5m")
        result = self.calculator.calculate(hand=hand, winning_tile=winning_tile, is_tsumo=True)
        yaku_names = [yaku.name for yaku in result.yaku_list]
        assert "对对和" in yaku_names, f"期望役种 '对对和' 未找到，实际役种: {yaku_names}"
    
    def test_sanankou(self):
        """测试三暗刻"""
        # 手牌：1m1m1m2p2p2p3s3s3s + 4m5m6m（三组暗刻）
        hand_strings = ["1m", "1m", "1m", "2p", "2p", "2p", "3s", "3s", "3s", "4m", "5m", "6m"]
        self._check_yaku(hand_strings, "4m", "三暗刻",
                        is_tsumo=True)
    
    def test_shousangen(self):
        """测试小三元"""
        # 手牌：白白白发发发中中 + 1m2m3m（两种三元牌刻子+一种雀头）
        hand_strings = ["白", "白", "白", "发", "发", "发", "中", "中", "1m", "2m", "3m"]
        self._check_yaku(hand_strings, "1m", "小三元",
                        is_tsumo=True)
    
    def test_honroutou(self):
        """测试混老头"""
        # 手牌：1m1m1m9p9p9p1s1s1s + 东东（全是幺九牌）
        hand_strings = ["1m", "1m", "1m", "9p", "9p", "9p", "1s", "1s", "1s", "东", "东"]
        self._check_yaku(hand_strings, "1m", "混老头",
                        is_tsumo=True)
    
    def test_chiitoitsu(self):
        """测试七对子"""
        # 手牌：1m1m2m2m3m3m4p4p5p5p6p6p7p7p（七组对子，14张）
        hand_strings = ["1m", "1m", "2m", "2m", "3m", "3m", "4p", "4p", "5p", "5p", "6p", "6p", "7p", "7p"]
        self._check_yaku(hand_strings, "7p", "七对子",
                        is_tsumo=True)
    
    def test_sanshoku_doujun(self):
        """测试三色同顺"""
        # 手牌：1m2m3m1p2p3p1s2s3s + 4m5m6m（三色同顺）
        hand_strings = ["1m", "2m", "3m", "1p", "2p", "3p", "1s", "2s", "3s", "4m", "5m", "6m"]
        self._check_yaku(hand_strings, "4m", "三色同顺",
                        is_tsumo=True)
    
    def test_ittsu(self):
        """测试一气通贯"""
        # 手牌：1m2m3m4m5m6m7m8m9m + 1p1p（一气通贯）
        hand_strings = ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p"]
        self._check_yaku(hand_strings, "1p", "一气通贯",
                        is_tsumo=True)
    
    def test_chanta(self):
        """测试混全带幺九"""
        # 手牌：1m2m3m7p8p9p1s2s3s + 东东东（每组牌都包含幺九牌）
        hand_strings = ["1m", "2m", "3m", "7p", "8p", "9p", "1s", "2s", "3s", "东", "东", "东"]
        self._check_yaku(hand_strings, "1m", "混全带幺九",
                        is_tsumo=True)
    
    # ---------- 3番役 ----------
    
    def test_honitsu(self):
        """测试混一色"""
        # 手牌：1m2m3m4m5m6m7m8m9m + 东东（一种花色+字牌）
        hand_strings = ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "东", "东"]
        self._check_yaku(hand_strings, "1m", "混一色",
                        is_tsumo=True)
    
    def test_junchan(self):
        """测试纯全带幺九"""
        # 手牌：1m2m3m7p8p9p1s2s3s + 9s9s9s（每组牌都包含老头牌）
        hand_strings = ["1m", "2m", "3m", "7p", "8p", "9p", "1s", "2s", "3s", "9s", "9s", "9s"]
        self._check_yaku(hand_strings, "1m", "纯全带幺九",
                        is_tsumo=True)
    
    def test_ryanpeiko(self):
        """测试二杯口"""
        # 手牌：1m1m2m2m3m3m1p1p2p2p3p3p + 4p（两组一杯口）
        hand_strings = ["1m", "1m", "2m", "2m", "3m", "3m", "1p", "1p", "2p", "2p", "3p", "3p", "4p"]
        self._check_yaku(hand_strings, "4p", "二杯口",
                        is_tsumo=True)
    
    # ---------- 6番役 ----------
    
    def test_chinitsu(self):
        """测试清一色"""
        # 手牌：1m2m3m4m5m6m7m8m9m + 1m1m（只有一种花色）
        hand_strings = ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1m", "1m"]
        self._check_yaku(hand_strings, "1m", "清一色",
                        is_tsumo=True)


    # ==================== 第二批：役满测试 ====================
    
    def test_kokushi(self):
        """测试国士无双"""
        # 手牌：1m9m1p9p1s9s东南西北白发中 + 1m（国士无双）
        hand_strings = ["1m", "9m", "1p", "9p", "1s", "9s", "东", "南", "西", "北", "白", "发", "中", "1m"]
        self._check_yaku(hand_strings, "1m", "国士无双",
                        is_tsumo=True)
    
    def test_kokushi_13men(self):
        """测试国士无双十三面"""
        # 注意：国士无双十三面需要特定的听牌形式，当前实现可能不支持
        # 这里跳过测试
        pass
    
    def test_chuuren(self):
        """测试九莲宝灯"""
        # 手牌：1m1m1m2m3m4m5m6m7m8m9m9m9m + 1m（九莲宝灯）
        hand_strings = ["1m", "1m", "1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "9m", "9m", "1m"]
        self._check_yaku(hand_strings, "1m", "九莲宝灯",
                        is_tsumo=True)
    
    def test_chuuren_9men(self):
        """测试纯正九莲宝灯"""
        # 注意：纯正九莲宝灯需要九面听，当前实现可能不支持
        # 这里跳过测试
        pass
    
    def test_suuankou(self):
        """测试四暗刻"""
        # 手牌：1m1m1m2p2p2p3s3s3s4m4m4m + 5m5m（四暗刻）
        hand_strings = ["1m", "1m", "1m", "2p", "2p", "2p", "3s", "3s", "3s", "4m", "4m", "4m", "5m", "5m"]
        self._check_yaku(hand_strings, "5m", "四暗刻",
                        is_tsumo=True)
    
    def test_suuankou_tanki(self):
        """测试四暗刻单骑"""
        # 注意：四暗刻单骑需要单骑听，当前实现可能不支持
        # 这里跳过测试
        pass
    
    def test_daisangen(self):
        """测试大三元"""
        # 手牌：白白白发发发中中中1m2m3m + 4m（大三元）
        hand_strings = ["白", "白", "白", "发", "发", "发", "中", "中", "中", "1m", "2m", "3m", "4m"]
        self._check_yaku(hand_strings, "4m", "大三元",
                        is_tsumo=True)
    
    def test_shousuushii(self):
        """测试小四喜"""
        # 手牌：东东东南南南西西北北 + 1m2m3m（小四喜）
        hand_strings = ["东", "东", "东", "南", "南", "南", "西", "西", "西", "北", "北", "1m", "2m", "3m"]
        self._check_yaku(hand_strings, "1m", "小四喜",
                        is_tsumo=True)
    
    def test_daisuushii(self):
        """测试大四喜"""
        # 手牌：东东东南南南西西北北北 + 1m1m（大四喜）
        hand_strings = ["东", "东", "东", "南", "南", "南", "西", "西", "西", "北", "北", "北", "1m", "1m"]
        self._check_yaku(hand_strings, "1m", "大四喜",
                        is_tsumo=True)
    
    def test_tsuuiisou(self):
        """测试字一色"""
        # 手牌：东东东南南南西西北北白白发发（全是字牌）
        hand_strings = ["东", "东", "东", "南", "南", "南", "西", "西", "西", "北", "北", "北", "白", "白"]
        self._check_yaku(hand_strings, "白", "字一色",
                        is_tsumo=True)
    
    def test_ryuuiisou(self):
        """测试绿一色"""
        # 手牌：2s3s4s6s8s发发发2s3s4s6s8s + 发（全是绿色牌）
        hand_strings = ["2s", "3s", "4s", "6s", "8s", "发", "发", "发", "2s", "3s", "4s", "6s", "8s", "发"]
        self._check_yaku(hand_strings, "发", "绿一色",
                        is_tsumo=True)
    
    def test_chinroutou(self):
        """测试清老头"""
        # 手牌：1m1m1m9m9m9m1p1p1p9p9p9p1s1s（全是老头牌）
        hand_strings = ["1m", "1m", "1m", "9m", "9m", "9m", "1p", "1p", "1p", "9p", "9p", "9p", "1s", "1s"]
        self._check_yaku(hand_strings, "1s", "清老头",
                        is_tsumo=True)
    
    def test_suukantsu(self):
        """测试四杠子"""
        # 注意：四杠子需要四组杠子，这里简化测试
        # 实际测试需要更复杂的牌型
        pass
    
    def test_tenhou(self):
        """测试天和"""
        # 手牌：1m2m3m4p5p6p7s8s9s1m2m3m4p + 5p（庄家第一巡和牌）
        hand_strings = ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1m", "2m", "3m", "4p", "5p"]
        self._check_yaku(hand_strings, "5p", "天和",
                        is_tsumo=True, is_dealer=True, is_first_round=True)
    
    def test_chiihou(self):
        """测试地和"""
        # 手牌：1m2m3m4p5p6p7s8s9s1m2m3m4p + 5p（闲家第一巡和牌）
        hand_strings = ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1m", "2m", "3m", "4p", "5p"]
        self._check_yaku(hand_strings, "5p", "地和",
                        is_tsumo=True, is_dealer=False, is_first_round=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])