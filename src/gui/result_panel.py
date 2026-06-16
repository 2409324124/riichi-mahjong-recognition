"""
结果显示面板

提供分析结果的显示功能。
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from .widgets import ResultDisplay


class ResultPanel(tk.Frame):
    """结果显示面板"""
    
    def __init__(self, master, **kwargs):
        """
        初始化结果显示面板
        
        Args:
            master: 父组件
        """
        super().__init__(master, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 标题
        title = tk.Label(self, text="分析结果", font=('Arial', 14, 'bold'))
        title.pack(anchor=tk.W, padx=5, pady=5)
        
        # 结果显示区域
        self.result_display = ResultDisplay(self)
        self.result_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 快捷信息区域
        info_frame = tk.LabelFrame(self, text="快捷信息", padx=5, pady=5)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 向听数
        shanten_frame = tk.Frame(info_frame)
        shanten_frame.pack(fill=tk.X, pady=2)
        tk.Label(shanten_frame, text="向听数:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.shanten_label = tk.Label(shanten_frame, text="--", font=('Arial', 12, 'bold'))
        self.shanten_label.pack(side=tk.LEFT)
        
        # 接受牌
        ukeire_frame = tk.Frame(info_frame)
        ukeire_frame.pack(fill=tk.X, pady=2)
        tk.Label(ukeire_frame, text="接受牌:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.ukeire_label = tk.Label(ukeire_frame, text="--", wraplength=300)
        self.ukeire_label.pack(side=tk.LEFT)
        
        # 推荐打牌
        recommend_frame = tk.Frame(info_frame)
        recommend_frame.pack(fill=tk.X, pady=2)
        tk.Label(recommend_frame, text="推荐打牌:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.recommend_label = tk.Label(recommend_frame, text="--", font=('Arial', 12, 'bold'), fg='green')
        self.recommend_label.pack(side=tk.LEFT)
        
        # 番数/点数
        score_frame = tk.Frame(info_frame)
        score_frame.pack(fill=tk.X, pady=2)
        tk.Label(score_frame, text="番数/点数:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.score_label = tk.Label(score_frame, text="--", font=('Arial', 12, 'bold'), fg='red')
        self.score_label.pack(side=tk.LEFT)
    
    def clear(self):
        """清空结果"""
        self.result_display.clear()
        self.shanten_label.config(text="--")
        self.ukeire_label.config(text="--")
        self.recommend_label.config(text="--")
        self.score_label.config(text="--")
    
    def show_analysis(self, result):
        """
        显示分析结果
        
        Args:
            result: AnalysisResult 对象
        """
        self.clear()
        
        # 更新快捷信息
        if result.shanten:
            shanten = result.shanten.shanten
            if shanten == -1:
                self.shanten_label.config(text="和了", fg='red')
            elif shanten == 0:
                self.shanten_label.config(text="听牌", fg='green')
            else:
                self.shanten_label.config(text=f"{shanten}向听", fg='black')
        
        if result.ukeire:
            ukeire_str = ", ".join(str(t) for t in result.ukeire.ukeire_tiles)
            self.ukeire_label.config(text=f"{ukeire_str} ({result.ukeire.ukeire_count}张)")
        
        if result.efficiency and result.efficiency.current_shanten >= 0:
            self.recommend_label.config(text=str(result.efficiency.best_discard))
        
        # 显示详细结果
        from ..system import MahjongSystem
        system = MahjongSystem()
        result_text = system.format_analysis(result)
        self.result_display.set_text(result_text)
    
    def show_win_result(self, result):
        """
        显示和牌验证结果
        
        Args:
            result: WinResult 对象
        """
        self.clear()
        
        if result.is_valid:
            self.shanten_label.config(text="和了", fg='red')
            self.score_label.config(text=f"{result.han}番 {result.fu}符 {result.points}点")
            
            result_text = "✓ 有效和牌\n\n"
            result_text += f"番数: {result.han}\n"
            result_text += f"符数: {result.fu}\n"
            result_text += f"点数: {result.points}\n"
            result_text += f"\n役种:\n"
            for yaku in result.yaku_list:
                result_text += f"  - {yaku.name} ({yaku.han}番)\n"
        else:
            result_text = f"✗ 无效和牌\n\n原因: {result.error}"
        
        self.result_display.set_text(result_text)
    
    def show_recommendation(self, result: dict):
        """
        显示打牌推荐
        
        Args:
            result: 推荐结果字典
        """
        self.clear()
        
        shanten = result.get('current_shanten', -1)
        if shanten == -1:
            self.shanten_label.config(text="和了", fg='red')
        elif shanten == 0:
            self.shanten_label.config(text="听牌", fg='green')
        else:
            self.shanten_label.config(text=f"{shanten}向听", fg='black')
        
        best_discard = result.get('best_discard', '--')
        self.recommend_label.config(text=best_discard)
        
        ukeire_tiles = result.get('ukeire_tiles', [])
        ukeire_count = result.get('ukeire_count', 0)
        if ukeire_tiles:
            self.ukeire_label.config(text=f"{', '.join(ukeire_tiles)} ({ukeire_count}张)")
        
        # 显示详细结果
        result_text = f"当前向听: {shanten}\n"
        result_text += f"手牌类型: {result.get('hand_type', '--')}\n\n"
        result_text += f"推荐打牌: {best_discard}\n"
        result_text += f"理由: {result.get('best_discard_reason', '--')}\n\n"
        result_text += f"接受牌: {', '.join(ukeire_tiles)} ({ukeire_count}张)\n\n"
        result_text += "所有打牌选项:\n"
        
        for i, discard in enumerate(result.get('all_discards', []), 1):
            result_text += f"  {i}. {discard['tile']} - {discard['description']}\n"
        
        self.result_display.set_text(result_text)
    
    def show_error(self, error_msg: str):
        """
        显示错误信息
        
        Args:
            error_msg: 错误信息
        """
        self.clear()
        self.result_display.set_text(f"错误: {error_msg}")