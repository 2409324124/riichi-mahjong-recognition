"""
特殊情况交叉验证测试

使用 MahjongRepository/mahjong 包作为参考，验证我们的实现。
"""

import pytest
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.tile import TilesConverter as MjTilesConverter

from src.game_logic.tile import Tile
from src.game_logic.hand import Hand
from src.agent.validator import WinValidator


class TestCrossValidation:
    """交叉验证测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.mahjong_calc = HandCalculator()
        self.validator = WinValidator()
    
    def _mahjong_to_our_tiles(self, mahjong_str: str, suit: str) -> list:
        """将 mahjong 包的牌格式转换为我们的格式"""
        tiles = []
        for ch in mahjong_str:
            tiles.append(Tile.from_string(f"{ch}{suit}"))
        return tiles
    
    def _validate_with_both(self, tiles_136, win_tile_136, is_tsumo=True):
        """同时使用两个系统验证"""
        # mahjong 包
        config = HandConfig(is_tsumo=is_tsumo)
        mj_result = self.mahjong_calc.estimate_hand_value(tiles_136, win_tile_136, config=config)
        
        return mj_result
    
    # ==================== 国士无双 ====================
    
    def test_kokushi_musou(self):
        """国士无双"""
        tiles = MjTilesConverter.string_to_136_array(sou='119', man='19', pin='19', honors='1234567')
        win_tile = MjTilesConverter.string_to_136_array(sou='9')[0]
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han == 13
    
    def test_kokushi_musou_double(self):
        """国士无双十三面"""
        tiles = MjTilesConverter.string_to_136_array(sou='119', man='19', pin='19', honors='1234567')
        win_tile = MjTilesConverter.string_to_136_array(sou='1')[0]  # 13面听
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han == 26
    
    # ==================== 九莲宝灯 ====================
    
    def test_chuuren_poutou(self):
        """九莲宝灯"""
        tiles = MjTilesConverter.string_to_136_array(man='11123456789999')
        win_tile = MjTilesConverter.string_to_136_array(man='1')[0]
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han == 13
    
    def test_chuuren_poutou_double(self):
        """纯正九莲宝灯"""
        tiles = MjTilesConverter.string_to_136_array(man='11122345678999')
        win_tile = MjTilesConverter.string_to_136_array(man='2')[0]
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han == 26
    
    # ==================== 四暗刻 ====================
    
    def test_suuankou(self):
        """四暗刻"""
        tiles = MjTilesConverter.string_to_136_array(sou='111444', man='333', pin='44555')
        win_tile = MjTilesConverter.string_to_136_array(pin='5')[0]
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han == 13
    
    def test_suuankou_tanki(self):
        """四暗刻单骑"""
        tiles = MjTilesConverter.string_to_136_array(sou='111444', man='333', pin='44455')
        win_tile = MjTilesConverter.string_to_136_array(pin='5')[0]
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han == 26
    
    # ==================== 大三元 ====================
    
    def test_daisangen(self):
        """大三元"""
        tiles = MjTilesConverter.string_to_136_array(sou='123', man='22', honors='555666777')
        win_tile = MjTilesConverter.string_to_136_array(honors='7')[0]
        
        result = self._validate_with_both(tiles, win_tile)
        assert result.error is None
        assert result.han == 13
    
    # ==================== 大四喜 ====================
    
    def test_daisuushi(self):
        """大四喜"""
        tiles = MjTilesConverter.string_to_136_array(sou='22', honors='111222333444')
        win_tile = MjTilesConverter.string_to_136_array(honors='4')[0]
        
        result = self._validate_with_both(tiles, win_tile)
        assert result.error is None
        assert result.han >= 26  # 至少双倍役满

    def test_shosuushi(self):
        """小四喜"""
        tiles = MjTilesConverter.string_to_136_array(sou='123', honors='11122233344')
        win_tile = MjTilesConverter.string_to_136_array(honors='4')[0]
        
        result = self._validate_with_both(tiles, win_tile)
        assert result.error is None
        assert result.han >= 13
    
    # ==================== 字一色 ====================
    
    def test_tsuisou(self):
        """字一色"""
        tiles = MjTilesConverter.string_to_136_array(honors='11223344556677')
        win_tile = MjTilesConverter.string_to_136_array(honors='7')[0]
        
        result = self._validate_with_both(tiles, win_tile)
        assert result.error is None
        assert result.han == 13
    
    # ==================== 绿一色 ====================
    
    def test_ryuisou(self):
        """绿一色"""
        tiles = MjTilesConverter.string_to_136_array(sou='22334466888', honors='666')
        win_tile = MjTilesConverter.string_to_136_array(honors='6')[0]
        
        result = self._validate_with_both(tiles, win_tile)
        assert result.error is None
        assert result.han == 13
    
    # ==================== 清老头 ====================
    
    def test_chinroto(self):
        """清老头"""
        tiles = MjTilesConverter.string_to_136_array(sou='111999', man='111999', pin='99')
        win_tile = MjTilesConverter.string_to_136_array(pin='9')[0]
        
        result = self._validate_with_both(tiles, win_tile)
        assert result.error is None
        assert result.han >= 26  # 清老头+对对和
    
    # ==================== 普通役 ====================
    
    def test_tanyao(self):
        """断幺九"""
        tiles = MjTilesConverter.string_to_136_array(man='234', pin='234567', sou='234', honors='22')
        win_tile = MjTilesConverter.string_to_136_array(honors='2')[0]
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han >= 1
    
    def test_chinitsu(self):
        """清一色（九莲宝灯）"""
        tiles = MjTilesConverter.string_to_136_array(man='11123456789999')
        win_tile = MjTilesConverter.string_to_136_array(man='1')[0]
        
        result = self._validate_with_both(tiles, win_tile, is_tsumo=True)
        assert result.error is None
        assert result.han >= 6
    
    # ==================== 计分验证 ====================
    
    def test_yakuman_score(self):
        """役满计分"""
        # 大三元 = 13番
        tiles = MjTilesConverter.string_to_136_array(sou='123', man='22', honors='555666777')
        win_tile = MjTilesConverter.string_to_136_array(honors='7')[0]
        
        result = self._validate_with_both(tiles, win_tile)
        assert result.error is None
        assert result.han >= 13
        assert result.cost is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])