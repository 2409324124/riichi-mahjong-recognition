"""
牌面分类器模块

对检测到的麻将牌进行分类。
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from ..game_logic.tile import Tile, TileType


@dataclass
class Classification:
    """分类结果"""
    tile: Tile                      # 麻将牌
    confidence: float                # 置信度
    features: Dict[str, float]      # 特征


class TileClassifier:
    """
    牌面分类器
    
    对检测到的麻将牌进行分类，识别牌的类型和点数。
    """
    
    def __init__(self):
        """初始化分类器"""
        # 牌的特征模板
        self._templates = self._load_templates()
    
    def _load_templates(self) -> Dict[int, np.ndarray]:
        """
        加载特征模板
        
        Returns:
            牌ID到模板的映射
        """
        # 这里应该加载预训练的特征模板
        # 简化处理，返回空字典
        return {}
    
    def classify(self, tile_image: np.ndarray) -> Classification:
        """
        分类麻将牌
        
        Args:
            tile_image: 麻将牌图像
        
        Returns:
            分类结果
        """
        # 提取特征
        features = self._extract_features(tile_image)
        
        # 进行分类
        tile_id, confidence = self._match_template(features)
        
        tile = Tile(tile_id)
        
        return Classification(
            tile=tile,
            confidence=confidence,
            features=features
        )
    
    def _extract_features(self, tile_image: np.ndarray) -> Dict[str, float]:
        """
        提取图像特征
        
        Args:
            tile_image: 麻将牌图像
        
        Returns:
            特征字典
        """
        features = {}
        
        # 转换为灰度图
        if len(tile_image.shape) == 3:
            gray = cv2.cvtColor(tile_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = tile_image
        
        # 调整大小
        resized = cv2.resize(gray, (64, 64))
        
        # 计算直方图
        hist = cv2.calcHist([resized], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        
        # 添加直方图特征
        for i in range(256):
            features[f"hist_{i}"] = float(hist[i])
        
        # 计算HOG特征
        hog_features = self._calculate_hog(resized)
        features.update(hog_features)
        
        # 计算颜色特征
        if len(tile_image.shape) == 3:
            color_features = self._calculate_color_features(tile_image)
            features.update(color_features)
        
        return features
    
    def _calculate_hog(self, image: np.ndarray) -> Dict[str, float]:
        """
        计算HOG特征
        
        Args:
            image: 灰度图像
        
        Returns:
            HOG特征字典
        """
        # 简化的HOG计算
        features = {}
        
        # 计算梯度
        gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        
        # 计算梯度幅值和方向
        magnitude = np.sqrt(gx**2 + gy**2)
        direction = np.arctan2(gy, gx)
        
        # 统计梯度幅值
        features["hog_mean"] = float(np.mean(magnitude))
        features["hog_std"] = float(np.std(magnitude))
        
        return features
    
    def _calculate_color_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        计算颜色特征
        
        Args:
            image: 彩色图像
        
        Returns:
            颜色特征字典
        """
        features = {}
        
        # 转换为HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 计算各通道的均值和标准差
        for i, channel in enumerate(['h', 's', 'v']):
            features[f"{channel}_mean"] = float(np.mean(hsv[:, :, i]))
            features[f"{channel}_std"] = float(np.std(hsv[:, :, i]))
        
        return features
    
    def _match_template(self, features: Dict[str, float]) -> Tuple[int, float]:
        """
        匹配模板
        
        Args:
            features: 特征字典
        
        Returns:
            (牌ID, 置信度)
        """
        # 如果没有模板，返回随机结果
        if not self._templates:
            # 返回一个随机的牌ID
            import random
            tile_id = random.randint(0, 33)
            return tile_id, 0.5
        
        # 计算与每个模板的相似度
        best_score = -1
        best_tile_id = 0
        
        for tile_id, template in self._templates.items():
            score = self._calculate_similarity(features, template)
            if score > best_score:
                best_score = score
                best_tile_id = tile_id
        
        return best_tile_id, best_score
    
    def _calculate_similarity(self, features: Dict[str, float], template: np.ndarray) -> float:
        """
        计算相似度
        
        Args:
            features: 特征字典
            template: 模板特征
        
        Returns:
            相似度分数
        """
        # 简化的相似度计算
        return 0.5
    
    def train(self, dataset_path: str):
        """
        训练分类器
        
        Args:
            dataset_path: 数据集路径
        """
        # 这里应该实现训练逻辑
        pass
    
    def save_model(self, model_path: str):
        """
        保存模型
        
        Args:
            model_path: 模型路径
        """
        # 这里应该实现模型保存逻辑
        pass
    
    def load_model(self, model_path: str):
        """
        加载模型
        
        Args:
            model_path: 模型路径
        """
        # 这里应该实现模型加载逻辑
        pass