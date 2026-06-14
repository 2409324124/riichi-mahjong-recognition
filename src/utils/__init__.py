"""
工具函数模块

提供通用的工具函数。
"""

# 延迟导入，避免在没有cv2时导入失败
try:
    from .image_utils import *
except ImportError:
    pass

from .mahjong_utils import *