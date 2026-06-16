"""
GUI 模块

提供图形用户界面，方便使用麻将系统。
"""

from .main_window import MainWindow


def launch_gui():
    """启动 GUI"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    launch_gui()