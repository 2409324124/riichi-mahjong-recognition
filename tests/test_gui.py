"""
GUI 测试
"""

import pytest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestGUIImports:
    """GUI 导入测试"""
    
    def test_import_gui_module(self):
        """测试导入 GUI 模块"""
        from src.gui import MainWindow
        assert MainWindow is not None
    
    def test_import_widgets(self):
        """测试导入 widgets 模块"""
        from src.gui.widgets import TileButton, TileSelector, TileDisplay, ResultDisplay
        assert TileButton is not None
        assert TileSelector is not None
        assert TileDisplay is not None
        assert ResultDisplay is not None
    
    def test_import_hand_panel(self):
        """测试导入 hand_panel 模块"""
        from src.gui.hand_panel import HandPanel
        assert HandPanel is not None
    
    def test_import_result_panel(self):
        """测试导入 result_panel 模块"""
        from src.gui.result_panel import ResultPanel
        assert ResultPanel is not None
    
    def test_import_camera_panel(self):
        """测试导入 camera_panel 模块"""
        from src.gui.camera_panel import CameraPanel
        assert CameraPanel is not None


class TestWidgets:
    """Widgets 测试"""
    
    def test_tile_button_display(self):
        """测试牌按钮显示"""
        # 需要创建 Tkinter root
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        try:
            from src.gui.widgets import TileButton
            
            # 测试万子
            btn = TileButton(root, "1m")
            assert btn.tile_id == "1m"
            assert btn.cget("text") == "一万"
            
            # 测试风牌
            btn = TileButton(root, "E")
            assert btn.tile_id == "E"
            assert btn.cget("text") == "东"
            
            # 测试三元牌
            btn = TileButton(root, "P")
            assert btn.tile_id == "P"
            assert btn.cget("text") == "白"
            
        finally:
            root.destroy()
    
    def test_tile_display_add_remove(self):
        """测试牌显示区域添加和删除"""
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        try:
            from src.gui.widgets import TileDisplay
            
            display = TileDisplay(root, max_tiles=14)
            
            # 添加牌
            assert display.add_tile("1m") == True
            assert display.add_tile("2m") == True
            assert len(display.get_tiles()) == 2
            
            # 删除牌
            assert display.remove_tile(0) == True
            assert len(display.get_tiles()) == 1
            
            # 清空
            display.clear()
            assert len(display.get_tiles()) == 0
            
        finally:
            root.destroy()


class TestSystemIntegration:
    """系统集成测试"""
    
    def test_system_analyze(self):
        """测试系统分析"""
        from src.system import MahjongSystem
        
        system = MahjongSystem()
        
        # 测试分析手牌
        result = system.analyze_hand(
            ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"]
        )
        
        assert result.hand_info is not None
        assert result.shanten is not None
    
    def test_system_validate_win(self):
        """测试系统验证和牌"""
        from src.system import MahjongSystem
        
        system = MahjongSystem()
        
        # 测试验证和牌
        result = system.validate_win(
            tile_strings=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"],
            winning_tile_str="3s",
            is_tsumo=True
        )
        
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])