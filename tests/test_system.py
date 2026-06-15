"""
系统集成测试
"""

import pytest
from src.system import MahjongSystem


class TestMahjongSystem:
    """系统集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.system = MahjongSystem()
    
    # ==================== 分析手牌测试 ====================
    
    def test_analyze_hand_basic(self):
        """测试基本手牌分析"""
        result = self.system.analyze_hand(
            ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"]
        )
        
        assert result.hand_info is not None
        assert result.shanten is not None
        assert len(result.hand_info.tiles) == 13
    
    def test_analyze_hand_tenpai(self):
        """测试听牌分析"""
        # 123m 456p 789s 111s + 2s (14张，需要打一张)
        result = self.system.analyze_hand(
            ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"]
        )
        
        # 13张手牌，计算向听数
        assert result.shanten is not None
        assert result.hand_info is not None
    
    def test_analyze_hand_with_melds(self):
        """测试包含副露的手牌分析"""
        result = self.system.analyze_hand(
            tile_strings=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s"],
            meld_strings=["白,白,白"]
        )
        
        assert result.hand_info is not None
        assert len(result.hand_info.melds) == 1
    
    # ==================== 验证和牌测试 ====================
    
    def test_validate_win_basic(self):
        """测试基本和牌验证"""
        result = self.system.validate_win(
            tile_strings=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"],
            winning_tile_str="3s",
            is_tsumo=True
        )
        
        assert result.is_valid == True
        assert result.han >= 1
    
    def test_validate_win_kokushi(self):
        """测试国士无双验证"""
        result = self.system.validate_win(
            tile_strings=["1m", "9m", "1p", "9p", "1s", "9s", "东", "南", "西", "北", "白", "发", "中"],
            winning_tile_str="1m",
            is_tsumo=True
        )
        
        assert result.is_valid == True
        assert any(y.name == "国士无双" for y in result.yaku_list)
    
    def test_validate_win_daisangen(self):
        """测试大三元验证"""
        result = self.system.validate_win(
            tile_strings=["1s", "2s", "3s", "2m", "2m", "白", "白", "白", "发", "发", "发", "中", "中"],
            winning_tile_str="中",
            is_tsumo=True
        )
        
        assert result.is_valid == True
        assert any(y.name == "大三元" for y in result.yaku_list)
    
    def test_validate_win_invalid(self):
        """测试无效和牌"""
        result = self.system.validate_win(
            tile_strings=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"],
            winning_tile_str="3s",
            is_tsumo=False
        )
        
        # 门前清荣和可能无役
        # 这里只验证不崩溃
        assert result is not None
    
    # ==================== 计算点数测试 ====================
    
    def test_calculate_score_basic(self):
        """测试基本点数计算"""
        result = self.system.calculate_score(
            tile_strings=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"],
            winning_tile_str="3s",
            is_tsumo=True
        )
        
        assert result.han >= 1
        assert result.total_points > 0
    
    def test_calculate_score_yakuman(self):
        """测试役满点数计算"""
        result = self.system.calculate_score(
            tile_strings=["1m", "9m", "1p", "9p", "1s", "9s", "东", "南", "西", "北", "白", "发", "中"],
            winning_tile_str="1m",
            is_tsumo=True
        )
        
        assert result.han >= 13
        assert result.total_points >= 32000
    
    # ==================== 打牌推荐测试 ====================
    
    def test_get_recommendation(self):
        """测试打牌推荐"""
        result = self.system.get_discard_recommendation(
            ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s", "3s"]
        )
        
        assert "best_discard" in result
        assert "ukeire_count" in result
        assert "all_discards" in result
    
    def test_get_recommendation_tenpai(self):
        """测试打牌推荐"""
        result = self.system.get_discard_recommendation(
            ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s", "3s"]
        )
        
        assert result["current_shanten"] is not None
        assert "best_discard" in result


class TestCLI:
    """CLI 测试"""
    
    def test_cli_import(self):
        """测试 CLI 导入"""
        from src.cli import main
        assert main is not None
    
    def test_cli_parser(self):
        """测试 CLI 参数解析"""
        from src.cli import create_parser
        
        parser = create_parser()
        
        # 测试 analyze 命令
        args = parser.parse_args(["analyze", "1m", "2m", "3m"])
        assert args.command == "analyze"
        assert args.tiles == ["1m", "2m", "3m"]
        
        # 测试 win 命令
        args = parser.parse_args(["win", "1m", "2m", "3m", "--win", "4m"])
        assert args.command == "win"
        assert args.win == "4m"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])