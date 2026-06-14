"""
麻将牌识别器模块

整合检测和分类，提供完整的识别流程。
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from ..game_logic.tile import Tile
from ..game_logic.hand import Hand
from .detector import MahjongDetector, Detection
from .classifier import TileClassifier, Classification


@dataclass
class RecognitionResult:
    """识别结果"""
    tiles: List[Tile]                # 识别到的牌
    detections: List[Detection]      # 检测结果
    classifications: List[Classification]  # 分类结果
    confidence: float                # 整体置信度


class MahjongRecognizer:
    """
    麻将牌识别器
    
    整合检测和分类，提供完整的识别流程。
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化识别器
        
        Args:
            model_path: 检测模型路径
        """
        self._detector = MahjongDetector(model_path)
        self._classifier = TileClassifier()
    
    def recognize(self, image: np.ndarray) -> RecognitionResult:
        """
        识别图像中的麻将牌
        
        Args:
            image: 输入图像
        
        Returns:
            识别结果
        """
        # 检测麻将牌
        detections = self._detector.detect_tiles(image)
        
        # 提取麻将牌图像
        tile_images = self._detector.extract_tiles(image, detections)
        
        # 分类麻将牌
        classifications = []
        for tile_image in tile_images:
            classification = self._classifier.classify(tile_image)
            classifications.append(classification)
        
        # 提取牌列表
        tiles = [classification.tile for classification in classifications]
        
        # 计算整体置信度
        if classifications:
            confidence = sum(c.confidence for c in classifications) / len(classifications)
        else:
            confidence = 0.0
        
        return RecognitionResult(
            tiles=tiles,
            detections=detections,
            classifications=classifications,
            confidence=confidence
        )
    
    def recognize_from_camera(self, camera_id: int = 0) -> RecognitionResult:
        """
        从摄像头识别麻将牌
        
        Args:
            camera_id: 摄像头ID
        
        Returns:
            识别结果
        """
        # 打开摄像头
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise RuntimeError("无法打开摄像头")
        
        # 读取一帧
        ret, frame = cap.read()
        
        # 释放摄像头
        cap.release()
        
        if not ret:
            raise RuntimeError("无法读取摄像头画面")
        
        # 识别麻将牌
        return self.recognize(frame)
    
    def recognize_hand(self, image: np.ndarray) -> Hand:
        """
        识别手牌
        
        Args:
            image: 输入图像
        
        Returns:
            手牌对象
        """
        result = self.recognize(image)
        return Hand.from_tiles(result.tiles)
    
    def draw_recognition(self, image: np.ndarray, result: RecognitionResult) -> np.ndarray:
        """
        在图像上绘制识别结果
        
        Args:
            image: 输入图像
            result: 识别结果
        
        Returns:
            绘制后的图像
        """
        # 绘制检测结果
        result_image = self._detector.draw_detections(image, result.detections)
        
        # 绘制分类结果
        for i, (detection, classification) in enumerate(zip(result.detections, result.classifications)):
            x, y, w, h = detection.bbox
            
            # 绘制牌名
            tile_name = str(classification.tile)
            cv2.putText(result_image, tile_name, (x, y + h + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return result_image
    
    def save_result(self, result: RecognitionResult, output_path: str):
        """
        保存识别结果
        
        Args:
            result: 识别结果
            output_path: 输出路径
        """
        # 这里应该实现结果保存逻辑
        pass
    
    def load_result(self, input_path: str) -> RecognitionResult:
        """
        加载识别结果
        
        Args:
            input_path: 输入路径
        
        Returns:
            识别结果
        """
        # 这里应该实现结果加载逻辑
        return RecognitionResult(
            tiles=[],
            detections=[],
            classifications=[],
            confidence=0.0
        )