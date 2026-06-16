"""
主窗口模块

提供 GUI 主窗口。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import threading

from ..system import MahjongSystem
from .hand_panel import HandPanel
from .result_panel import ResultPanel
from .camera_panel import CameraPanel


class MainWindow:
    """主窗口"""
    
    def __init__(self):
        """初始化主窗口"""
        self.system = MahjongSystem()
        self.root = tk.Tk()
        self.root.title("日本立直麻将识别系统")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        
        self._create_menu()
        self._create_widgets()
        self._create_status_bar()
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="清空所有", command=self._on_clear_all)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._on_about)
    
    def _create_widgets(self):
        """创建组件"""
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板（手牌输入）
        left_frame = tk.Frame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        self.hand_panel = HandPanel(left_frame, on_analyze=self._on_analyze)
        self.hand_panel.pack(fill=tk.BOTH, expand=True)
        
        # 右侧面板（结果显示 + 摄像头）
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 使用 Notebook（标签页）
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 结果显示标签页
        result_frame = tk.Frame(self.notebook)
        self.notebook.add(result_frame, text="分析结果")
        self.result_panel = ResultPanel(result_frame)
        self.result_panel.pack(fill=tk.BOTH, expand=True)
        
        # 摄像头标签页
        camera_frame = tk.Frame(self.notebook)
        self.notebook.add(camera_frame, text="摄像头识别")
        self.camera_panel = CameraPanel(camera_frame, on_recognize=self._on_camera_recognize)
        self.camera_panel.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Label(
            self.root, text="就绪", anchor=tk.W, relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _on_analyze(self, tiles: List[str]):
        """
        分析手牌回调
        
        Args:
            tiles: 手牌列表
        """
        self.status_bar.config(text="正在分析...")
        
        # 在后台线程执行分析
        def analyze_thread():
            try:
                # 获取副露和宝牌
                melds = self.hand_panel.get_melds()
                dora = self.hand_panel.get_dora_indicators()
                round_wind = self.hand_panel.get_round_wind()
                seat_wind = self.hand_panel.get_seat_wind()
                
                # 判断是分析还是打牌推荐
                if len(tiles) == 14:
                    # 打牌推荐
                    result = self.system.get_discard_recommendation(
                        tiles, meld_strings=melds
                    )
                    self.root.after(0, self._show_recommendation, result)
                elif len(tiles) == 13:
                    # 分析手牌
                    result = self.system.analyze_hand(
                        tiles, meld_strings=melds,
                        dora_indicators=dora,
                        round_wind=round_wind,
                        seat_wind=seat_wind
                    )
                    self.root.after(0, self._show_analysis, result)
                else:
                    self.root.after(0, self._show_error, f"手牌数量错误: {len(tiles)}张")
                    
            except Exception as e:
                self.root.after(0, self._show_error, str(e))
        
        thread = threading.Thread(target=analyze_thread, daemon=True)
        thread.start()
    
    def _on_camera_recognize(self, image_path: str):
        """
        摄像头识别回调
        
        Args:
            image_path: 图片路径
        """
        self.status_bar.config(text=f"正在识别: {image_path}")
        
        # 在后台线程执行识别
        def recognize_thread():
            try:
                # TODO: 调用识别模块
                # result = self.system.recognize_image(image_path)
                # self.root.after(0, self._show_recognition, result)
                self.root.after(0, self._show_error, "摄像头识别功能待实现")
            except Exception as e:
                self.root.after(0, self._show_error, str(e))
        
        thread = threading.Thread(target=recognize_thread, daemon=True)
        thread.start()
    
    def _show_analysis(self, result):
        """显示分析结果"""
        self.result_panel.show_analysis(result)
        self.status_bar.config(text="分析完成")
    
    def _show_recommendation(self, result):
        """显示打牌推荐"""
        self.result_panel.show_recommendation(result)
        self.status_bar.config(text="推荐完成")
    
    def _show_error(self, error_msg: str):
        """显示错误"""
        self.result_panel.show_error(error_msg)
        self.status_bar.config(text=f"错误: {error_msg}")
    
    def _on_clear_all(self):
        """清空所有"""
        self.hand_panel.hand_display.clear()
        self.hand_panel.meld_entry.delete(0, tk.END)
        self.hand_panel.dora_entry.delete(0, tk.END)
        self.result_panel.clear()
        self.status_bar.config(text="已清空")
    
    def _on_about(self):
        """关于对话框"""
        messagebox.showinfo(
            "关于",
            "日本立直麻将识别系统\n\n"
            "功能：\n"
            "- 牌面识别（YOLOv8）\n"
            "- 计分系统（38种役）\n"
            "- 牌效计算（向听/接受牌）\n"
            "- 和牌验证\n\n"
            "版本：v0.3.0"
        )
    
    def run(self):
        """运行主循环"""
        self.root.mainloop()
    
    def cleanup(self):
        """清理资源"""
        self.camera_panel.cleanup()


def launch_gui():
    """启动 GUI"""
    app = MainWindow()
    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == "__main__":
    launch_gui()