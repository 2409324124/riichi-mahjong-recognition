"""
摄像头面板

提供摄像头实时识别功能。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
import threading

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class CameraPanel(tk.Frame):
    """摄像头面板"""
    
    def __init__(self, master, on_recognize: Callable[[str], None], **kwargs):
        """
        初始化摄像头面板
        
        Args:
            master: 父组件
            on_recognize: 识别回调函数
        """
        super().__init__(master, **kwargs)
        self.on_recognize = on_recognize
        self.is_running = False
        self.cap = None
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 标题
        title = tk.Label(self, text="摄像头识别", font=('Arial', 14, 'bold'))
        title.pack(anchor=tk.W, padx=5, pady=5)
        
        # 提示信息
        if not CV2_AVAILABLE:
            tk.Label(
                self, text="需要安装 opencv-python: pip install opencv-python",
                fg='red', wraplength=400
            ).pack(padx=5, pady=5)
            return
        
        # 摄像头选择
        camera_frame = tk.Frame(self)
        camera_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(camera_frame, text="摄像头:").pack(side=tk.LEFT)
        self.camera_var = tk.StringVar(value="0")
        self.camera_entry = tk.Entry(camera_frame, textvariable=self.camera_var, width=10)
        self.camera_entry.pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = tk.Button(
            btn_frame, text="开启摄像头", command=self._on_start,
            font=('Arial', 11), bg='#4CAF50', fg='white'
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            btn_frame, text="停止", command=self._on_stop,
            font=('Arial', 11), bg='#f44336', fg='white', state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.capture_btn = tk.Button(
            btn_frame, text="拍照识别", command=self._on_capture,
            font=('Arial', 11), bg='#2196F3', fg='white', state=tk.DISABLED
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        # 图片选择
        file_frame = tk.Frame(self)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_btn = tk.Button(
            file_frame, text="选择图片", command=self._on_select_file,
            font=('Arial', 11), bg='#FF9800', fg='white'
        )
        self.file_btn.pack(side=tk.LEFT, padx=5)
        
        self.file_label = tk.Label(file_frame, text="未选择文件")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        # 预览区域
        preview_frame = tk.LabelFrame(self, text="预览", padx=5, pady=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(preview_frame, bg='gray', width=320, height=240)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态
        self.status_label = tk.Label(self, text="就绪", anchor=tk.W, relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=5, pady=5)
    
    def _on_start(self):
        """开启摄像头"""
        if not CV2_AVAILABLE:
            messagebox.showerror("错误", "需要安装 opencv-python")
            return
        
        try:
            camera_id = int(self.camera_var.get())
            self.cap = cv2.VideoCapture(camera_id)
            
            if not self.cap.isOpened():
                messagebox.showerror("错误", f"无法打开摄像头 {camera_id}")
                return
            
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.capture_btn.config(state=tk.NORMAL)
            self.status_label.config(text="摄像头已开启")
            
            # 启动预览线程
            self._start_preview()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的摄像头ID")
    
    def _on_stop(self):
        """停止摄像头"""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.capture_btn.config(state=tk.DISABLED)
        self.status_label.config(text="摄像头已关闭")
    
    def _on_capture(self):
        """拍照识别"""
        if not self.cap or not self.is_running:
            messagebox.showwarning("警告", "请先开启摄像头")
            return
        
        ret, frame = self.cap.read()
        if ret:
            # 保存临时文件
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "mahjong_capture.jpg")
            cv2.imwrite(temp_path, frame)
            
            # 调用识别回调
            self.on_recognize(temp_path)
            self.status_label.config(text="已拍照，正在识别...")
    
    def _on_select_file(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.file_label.config(text=file_path)
            self.on_recognize(file_path)
            self.status_label.config(text=f"正在识别: {file_path}")
    
    def _start_preview(self):
        """启动预览"""
        def preview_loop():
            while self.is_running and self.cap:
                ret, frame = self.cap.read()
                if ret:
                    # 转换颜色空间
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # 调整大小
                    h, w = frame_rgb.shape[:2]
                    canvas_w = self.canvas.winfo_width()
                    canvas_h = self.canvas.winfo_height()
                    
                    if canvas_w > 0 and canvas_h > 0:
                        scale = min(canvas_w / w, canvas_h / h)
                        new_w = int(w * scale)
                        new_h = int(h * scale)
                        frame_rgb = cv2.resize(frame_rgb, (new_w, new_h))
                    
                    # 更新画布
                    self.after(0, self._update_canvas, frame_rgb)
                
                # 控制帧率
                import time
                time.sleep(0.03)  # ~30fps
        
        thread = threading.Thread(target=preview_loop, daemon=True)
        thread.start()
    
    def _update_canvas(self, frame_rgb):
        """更新画布显示"""
        try:
            from PIL import Image, ImageTk
            
            # 转换为 PIL Image
            image = Image.fromarray(frame_rgb)
            
            # 转换为 Tkinter PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 更新画布
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # 保持引用
            
        except ImportError:
            # 如果没有 PIL，使用简单显示
            pass
    
    def cleanup(self):
        """清理资源"""
        self._on_stop()