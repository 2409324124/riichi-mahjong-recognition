"""
牌面识别模块

使用YOLOv8进行麻将牌检测和识别。
"""

# 延迟导入，避免在没有cv2或ultralytics时导入失败
try:
    from .detector import MahjongDetector
    from .classifier import TileClassifier
    from .recognizer import MahjongRecognizer
except ImportError:
    # 如果依赖未安装，提供占位符
    MahjongDetector = None
    TileClassifier = None
    MahjongRecognizer = None