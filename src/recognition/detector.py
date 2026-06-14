"""
麻将牌检测器模块

使用YOLOv8进行麻将牌检测。
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


@dataclass
class Detection:
    """检测结果"""
    bbox: Tuple[int, int, int, int]  # 边界框 (x, y, width, height)
    confidence: float                  # 置信度
    class_id: int                      # 类别ID
    class_name: str                    # 类别名称


class MahjongDetector:
    """
    麻将牌检测器
    
    使用YOLOv8进行麻将牌检测。
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化检测器
        
        Args:
            model_path: 模型路径，如果为None则使用默认模型
        """
        self._model = None
        self._model_path = model_path
        
        if YOLO_AVAILABLE:
            if model_path:
                self._model = YOLO(model_path)
            else:
                # 使用默认的YOLOv8模型
                self._model = YOLO('yolov8n.pt')
        else:
            print("警告：ultralytics未安装，无法使用YOLO检测器")
    
    def detect(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[Detection]:
        """
        检测图像中的麻将牌
        
        Args:
            image: 输入图像
            confidence_threshold: 置信度阈值
        
        Returns:
            检测结果列表
        """
        if self._model is None:
            return []
        
        # 运行检测
        results = self._model(image, conf=confidence_threshold)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 获取边界框
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                    
                    # 获取置信度和类别
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = result.names[class_id]
                    
                    detections.append(Detection(
                        bbox=(x, y, w, h),
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name
                    ))
        
        return detections
    
    def detect_tiles(self, image: np.ndarray) -> List[Detection]:
        """
        检测麻将牌（简化版）
        
        Args:
            image: 输入图像
        
        Returns:
            检测结果列表
        """
        return self.detect(image, confidence_threshold=0.5)
    
    def draw_detections(self, image: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        在图像上绘制检测结果
        
        Args:
            image: 输入图像
            detections: 检测结果列表
        
        Returns:
            绘制后的图像
        """
        result_image = image.copy()
        
        for detection in detections:
            x, y, w, h = detection.bbox
            
            # 绘制边界框
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            cv2.putText(result_image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return result_image
    
    def extract_tiles(self, image: np.ndarray, detections: List[Detection]) -> List[np.ndarray]:
        """
        从图像中提取麻将牌
        
        Args:
            image: 输入图像
            detections: 检测结果列表
        
        Returns:
            麻将牌图像列表
        """
        tiles = []
        for detection in detections:
            x, y, w, h = detection.bbox
            tile_image = image[y:y+h, x:x+w]
            tiles.append(tile_image)
        
        return tiles
    
    def train(self, dataset_path: str, epochs: int = 100, batch_size: int = 16):
        """
        训练模型
        
        Args:
            dataset_path: 数据集路径
            epochs: 训练轮数
            batch_size: 批次大小
        """
        if not YOLO_AVAILABLE:
            raise RuntimeError("ultralytics未安装，无法训练模型")
        
        # 创建新模型
        model = YOLO('yolov8n.pt')
        
        # 训练模型
        model.train(
            data=dataset_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=640
        )
        
        # 保存模型
        self._model = model
    
    def export_model(self, format: str = 'onnx'):
        """
        导出模型
        
        Args:
            format: 导出格式
        """
        if self._model is None:
            raise RuntimeError("没有训练好的模型")
        
        self._model.export(format=format)