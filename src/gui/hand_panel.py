"""
手牌输入面板

提供手牌输入和管理功能。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List

from .widgets import TileSelector, TileDisplay


class HandPanel(tk.Frame):
    """手牌输入面板"""
    
    def __init__(self, master, on_analyze: Callable[[List[str]], None], **kwargs):
        """
        初始化手牌输入面板
        
        Args:
            master: 父组件
            on_analyze: 分析回调函数
        """
        super().__init__(master, **kwargs)
        self.on_analyze = on_analyze
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 标题
        title = tk.Label(self, text="手牌输入", font=('Arial', 14, 'bold'))
        title.pack(anchor=tk.W, padx=5, pady=5)
        
        # 手牌显示区域
        self.hand_display = TileDisplay(self, max_tiles=14)
        self.hand_display.pack(fill=tk.X, padx=5, pady=5)
        
        # 牌选择器
        self.tile_selector = TileSelector(self, on_select=self._on_tile_select)
        self.tile_selector.pack(fill=tk.X, padx=5, pady=5)
        
        # 按钮区域
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.analyze_btn = tk.Button(
            btn_frame, text="分析手牌", command=self._on_analyze,
            font=('Arial', 11), bg='#4CAF50', fg='white'
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            btn_frame, text="清空", command=self._on_clear,
            font=('Arial', 11), bg='#f44336', fg='white'
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.recommend_btn = tk.Button(
            btn_frame, text="打牌推荐", command=self._on_recommend,
            font=('Arial', 11), bg='#2196F3', fg='white'
        )
        self.recommend_btn.pack(side=tk.LEFT, padx=5)
        
        # 副露输入区域
        meld_frame = tk.LabelFrame(self, text="副露（可选）", padx=5, pady=5)
        meld_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(meld_frame, text="副露牌（逗号分隔，如: 1m,2m,3m）:").pack(anchor=tk.W)
        self.meld_entry = tk.Entry(meld_frame, width=40)
        self.meld_entry.pack(fill=tk.X, pady=2)
        
        # 宝牌指示牌
        dora_frame = tk.LabelFrame(self, text="宝牌指示牌（可选）", padx=5, pady=5)
        dora_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(dora_frame, text="宝牌指示牌（空格分隔，如: 1m 2p）:").pack(anchor=tk.W)
        self.dora_entry = tk.Entry(dora_frame, width=40)
        self.dora_entry.pack(fill=tk.X, pady=2)
        
        # 场风和自风
        wind_frame = tk.LabelFrame(self, text="风位", padx=5, pady=5)
        wind_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(wind_frame, text="场风:").grid(row=0, column=0, sticky=tk.W)
        self.round_wind = ttk.Combobox(wind_frame, values=["东", "南", "西", "北"], width=5)
        self.round_wind.set("东")
        self.round_wind.grid(row=0, column=1, padx=5)
        
        tk.Label(wind_frame, text="自风:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.seat_wind = ttk.Combobox(wind_frame, values=["东", "南", "西", "北"], width=5)
        self.seat_wind.set("东")
        self.seat_wind.grid(row=0, column=3, padx=5)
    
    def _on_tile_select(self, tile_id: str):
        """牌选择回调"""
        self.hand_display.add_tile(tile_id)
    
    def _on_analyze(self):
        """分析按钮回调"""
        tiles = self.hand_display.get_tiles()
        if len(tiles) < 13:
            messagebox.showwarning("警告", f"手牌不足13张（当前{len(tiles)}张）")
            return
        
        # 获取副露
        meld_str = self.meld_entry.get().strip()
        melds = None
        if meld_str:
            melds = [m.strip() for m in meld_str.split(";") if m.strip()]
        
        # 调用分析回调
        self.on_analyze(tiles)
    
    def _on_clear(self):
        """清空按钮回调"""
        self.hand_display.clear()
        self.meld_entry.delete(0, tk.END)
        self.dora_entry.delete(0, tk.END)
    
    def _on_recommend(self):
        """打牌推荐回调"""
        tiles = self.hand_display.get_tiles()
        if len(tiles) != 14:
            messagebox.showwarning("警告", f"打牌推荐需要14张牌（当前{len(tiles)}张）")
            return
        
        # 调用分析回调（传入14张牌）
        self.on_analyze(tiles)
    
    def get_hand_tiles(self) -> List[str]:
        """获取手牌"""
        return self.hand_display.get_tiles()
    
    def get_melds(self) -> Optional[List[str]]:
        """获取副露"""
        meld_str = self.meld_entry.get().strip()
        if meld_str:
            return [m.strip() for m in meld_str.split(";") if m.strip()]
        return None
    
    def get_dora_indicators(self) -> Optional[List[str]]:
        """获取宝牌指示牌"""
        dora_str = self.dora_entry.get().strip()
        if dora_str:
            return [d.strip() for d in dora_str.split() if d.strip()]
        return None
    
    def get_round_wind(self) -> int:
        """获取场风"""
        wind_map = {"东": 27, "南": 28, "西": 29, "北": 30}
        return wind_map.get(self.round_wind.get(), 27)
    
    def get_seat_wind(self) -> int:
        """获取自风"""
        wind_map = {"东": 27, "南": 28, "西": 29, "北": 30}
        return wind_map.get(self.seat_wind.get(), 27)