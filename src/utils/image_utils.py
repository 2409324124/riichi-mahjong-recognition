"""
图像处理工具模块

提供图像处理相关的工具函数。
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional


def load_image(image_path: str) -> np.ndarray:
    """
    加载图像
    
    Args:
        image_path: 图像路径
    
    Returns:
        图像数组
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法加载图像: {image_path}")
    return image


def resize_image(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """
    调整图像大小
    
    Args:
        image: 输入图像
        width: 目标宽度
        height: 目标高度
    
    Returns:
        调整大小后的图像
    """
    return cv2.resize(image, (width, height))


def crop_image(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    裁剪图像
    
    Args:
        image: 输入图像
        x: 起始x坐标
        y: 起始y坐标
        width: 裁剪宽度
        height: 裁剪高度
    
    Returns:
        裁剪后的图像
    """
    return image[y:y+height, x:x+width]


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    转换为灰度图
    
    Args:
        image: 输入图像
    
    Returns:
        灰度图像
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    应用高斯模糊
    
    Args:
        image: 输入图像
        kernel_size: 核大小
    
    Returns:
        模糊后的图像
    """
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def apply_threshold(image: np.ndarray, threshold: int = 128) -> np.ndarray:
    """
    应用阈值处理
    
    Args:
        image: 输入图像
        threshold: 阈值
    
    Returns:
        二值化图像
    """
    _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return binary


def find_contours(image: np.ndarray) -> List[np.ndarray]:
    """
    查找轮廓
    
    Args:
        image: 输入图像
    
    Returns:
        轮廓列表
    """
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def draw_contours(image: np.ndarray, contours: List[np.ndarray]) -> np.ndarray:
    """
    绘制轮廓
    
    Args:
        image: 输入图像
        contours: 轮廓列表
    
    Returns:
        绘制轮廓后的图像
    """
    return cv2.drawContours(image.copy(), contours, -1, (0, 255, 0), 2)


def get_contour_bbox(contour: np.ndarray) -> Tuple[int, int, int, int]:
    """
    获取轮廓的边界框
    
    Args:
        contour: 轮廓
    
    Returns:
        边界框 (x, y, width, height)
    """
    x, y, w, h = cv2.boundingRect(contour)
    return x, y, w, h


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    归一化图像
    
    Args:
        image: 输入图像
    
    Returns:
        归一化后的图像
    """
    return image.astype(np.float32) / 255.0


def augment_image(image: np.ndarray) -> List[np.ndarray]:
    """
    图像增强
    
    Args:
        image: 输入图像
    
    Returns:
        增强后的图像列表
    """
    augmented = []
    
    # 原始图像
    augmented.append(image)
    
    # 水平翻转
    flipped = cv2.flip(image, 1)
    augmented.append(flipped)
    
    # 旋转
    for angle in [90, 180, 270]:
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (width, height))
        augmented.append(rotated)
    
    # 亮度调整
    for alpha in [0.8, 1.2]:
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        augmented.append(adjusted)
    
    return augmented