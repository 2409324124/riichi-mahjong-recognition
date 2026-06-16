"""
自定义组件模块

提供 GUI 中使用的自定义组件。
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List


class TileButton(tk.Button):
    """麻将牌按钮"""
    
    # 牌的显示文本
    TILE_DISPLAY = {
        '1m': '一万', '2m': '二万', '3m': '三万', '4m': '四万', '5m': '五万',
        '6m': '六万', '7m': '七万', '8m': '八万', '9m': '九万',
        '1p': '一筒', '2p': '二筒', '3p': '三筒', '4p': '四筒', '5p': '五筒',
        '6p': '六筒', '7p': '七筒', '8p': '八筒', '9p': '九筒',
        '1s': '一索', '2s': '二索', '3s': '三索', '4s': '四索', '5s': '五索',
        '6s': '六索', '7s': '七索', '8s': '八索', '9s': '九索',
        'E': '东', 'S': '南', 'W': '西', 'N': '北',
        'P': '白', 'F': '发', 'C': '中'
    }
    
    def __init__(self, master, tile_id: str, **kwargs):
        """
        初始化牌按钮
        
        Args:
            master: 父组件
            tile_id: 牌ID（如 '1m', 'E', 'P'）
        """
        self.tile_id = tile_id
        display_text = self.TILE_DISPLAY.get(tile_id, tile_id)
        
        super().__init__(
            master,
            text=display_text,
            width=4,
            height=2,
            font=('Arial', 10, 'bold'),
            **kwargs
        )


class TileSelector(tk.Frame):
    """牌选择器"""
    
    def __init__(self, master, on_select: Callable[[str], None], **kwargs):
        """
        初始化牌选择器
        
        Args:
            master: 父组件
            on_select: 选择回调函数
        """
        super().__init__(master, **kwargs)
        self.on_select = on_select
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 万子
        man_frame = tk.LabelFrame(self, text="万子", padx=5, pady=5)
        man_frame.pack(fill=tk.X, padx=5, pady=2)
        for i in range(1, 10):
            btn = TileButton(man_frame, f"{i}m", command=lambda t=f"{i}m": self.on_select(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # 筒子
        pin_frame = tk.LabelFrame(self, text="筒子", padx=5, pady=5)
        pin_frame.pack(fill=tk.X, padx=5, pady=2)
        for i in range(1, 10):
            btn = TileButton(pin_frame, f"{i}p", command=lambda t=f"{i}p": self.on_select(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # 索子
        sou_frame = tk.LabelFrame(self, text="索子", padx=5, pady=5)
        sou_frame.pack(fill=tk.X, padx=5, pady=2)
        for i in range(1, 10):
            btn = TileButton(sou_frame, f"{i}s", command=lambda t=f"{i}s": self.on_select(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # 风牌
        wind_frame = tk.LabelFrame(self, text="风牌", padx=5, pady=5)
        wind_frame.pack(fill=tk.X, padx=5, pady=2)
        for wind in ['E', 'S', 'W', 'N']:
            btn = TileButton(wind_frame, wind, command=lambda t=wind: self.on_select(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # 三元牌
        dragon_frame = tk.LabelFrame(self, text="三元牌", padx=5, pady=5)
        dragon_frame.pack(fill=tk.X, padx=5, pady=2)
        for dragon in ['P', 'F', 'C']:
            btn = TileButton(dragon_frame, dragon, command=lambda t=dragon: self.on_select(t))
            btn.pack(side=tk.LEFT, padx=2)


class TileDisplay(tk.Frame):
    """牌显示区域"""
    
    def __init__(self, master, max_tiles: int = 14, **kwargs):
        """
        初始化牌显示区域
        
        Args:
            master: 父组件
            max_tiles: 最大牌数
        """
        super().__init__(master, **kwargs)
        self.max_tiles = max_tiles
        self.tiles: List[str] = []
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        self.label = tk.Label(self, text="手牌", font=('Arial', 12, 'bold'))
        self.label.pack(anchor=tk.W)
        
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.X)
        
        self.buttons: List[TileButton] = []
    
    def add_tile(self, tile_id: str) -> bool:
        """
        添加牌
        
        Args:
            tile_id: 牌ID
        
        Returns:
            是否添加成功
        """
        if len(self.tiles) >= self.max_tiles:
            return False
        
        self.tiles.append(tile_id)
        self._update_display()
        return True
    
    def remove_tile(self, index: int) -> bool:
        """
        移除牌
        
        Args:
            index: 牌索引
        
        Returns:
            是否移除成功
        """
        if 0 <= index < len(self.tiles):
            self.tiles.pop(index)
            self._update_display()
            return True
        return False
    
    def clear(self):
        """清空手牌"""
        self.tiles.clear()
        self._update_display()
    
    def get_tiles(self) -> List[str]:
        """获取手牌"""
        return self.tiles.copy()
    
    def _update_display(self):
        """更新显示"""
        # 清除旧按钮
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
        
        # 创建新按钮
        for i, tile_id in enumerate(self.tiles):
            btn = TileButton(self.frame, tile_id, command=lambda idx=i: self.remove_tile(idx))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.buttons.append(btn)


class ResultDisplay(tk.Frame):
    """结果显示区域"""
    
    def __init__(self, master, **kwargs):
        """
        初始化结果显示区域
        
        Args:
            master: 父组件
        """
        super().__init__(master, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        self.label = tk.Label(self, text="分析结果", font=('Arial', 12, 'bold'))
        self.label.pack(anchor=tk.W)
        
        self.text = tk.Text(self, height=15, width=50, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)
    
    def clear(self):
        """清空结果"""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
    
    def set_text(self, text: str):
        """设置结果文本"""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, text)
        self.text.config(state=tk.DISABLED)
    
    def append_text(self, text: str):
        """追加结果文本"""
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, text + "\n")
        self.text.config(state=tk.DISABLED)


class StatusBar(tk.Frame):
    """状态栏"""
    
    def __init__(self, master, **kwargs):
        """
        初始化状态栏
        
        Args:
            master: 父组件
        """
        super().__init__(master, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        self.label = tk.Label(self, text="就绪", anchor=tk.W, relief=tk.SUNKEN)
        self.label.pack(fill=tk.X)
    
    def set_status(self, text: str):
        """设置状态文本"""
        self.label.config(text=text)