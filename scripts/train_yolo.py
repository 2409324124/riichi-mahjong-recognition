"""
YOLO训练脚本

使用YOLOv8训练麻将牌识别模型。
"""

import os
from pathlib import Path
from ultralytics import YOLO
import yaml


def train_model(
    data_yaml: str,
    model_size: str = 'n',
    img_size: int = 640,
    batch_size: int = 16,
    epochs: int = 100,
    device: str = '0',
    project: str = 'runs/train',
    name: str = 'mahjong_detection'
):
    """
    训练YOLO模型
    
    Args:
        data_yaml: 数据配置文件路径
        model_size: 模型大小 (n, s, m, l, x)
        img_size: 图片大小
        batch_size: 批次大小
        epochs: 训练轮数
        device: 设备 (0 表示第一个GPU)
        project: 项目目录
        name: 实验名称
    """
    # 加载预训练模型
    model_name = f'yolov8{model_size}.pt'
    print(f"加载预训练模型: {model_name}")
    model = YOLO(model_name)
    
    # 训练模型
    print(f"开始训练...")
    print(f"数据配置: {data_yaml}")
    print(f"模型大小: {model_size}")
    print(f"图片大小: {img_size}")
    print(f"批次大小: {batch_size}")
    print(f"训练轮数: {epochs}")
    print(f"设备: {device}")
    
    results = model.train(
        data=data_yaml,
        imgsz=img_size,
        batch=batch_size,
        epochs=epochs,
        device=device,
        project=project,
        name=name,
        patience=20,  # 早停耐心值
        save=True,  # 保存检查点
        save_period=10,  # 每10轮保存一次
        plots=True,  # 生成训练图表
        verbose=True,  # 详细输出
    )
    
    print(f"\n训练完成！")
    print(f"最佳模型保存在: {results.save_dir}/weights/best.pt")
    print(f"最后模型保存在: {results.save_dir}/weights/last.pt")
    
    return results


def evaluate_model(
    model_path: str,
    data_yaml: str,
    img_size: int = 640,
    device: str = '0'
):
    """
    评估模型
    
    Args:
        model_path: 模型路径
        data_yaml: 数据配置文件路径
        img_size: 图片大小
        device: 设备
    """
    # 加载模型
    print(f"加载模型: {model_path}")
    model = YOLO(model_path)
    
    # 评估模型
    print(f"开始评估...")
    results = model.val(
        data=data_yaml,
        imgsz=img_size,
        device=device,
        verbose=True,
    )
    
    # 打印评估结果
    print(f"\n评估结果:")
    print(f"mAP@0.5: {results.box.map50:.4f}")
    print(f"mAP@0.5:0.95: {results.box.map:.4f}")
    print(f"精度: {results.box.mp:.4f}")
    print(f"召回率: {results.box.mr:.4f}")
    
    return results


def predict_image(
    model_path: str,
    image_path: str,
    conf_threshold: float = 0.5,
    img_size: int = 640,
    device: str = '0'
):
    """
    使用模型预测图片
    
    Args:
        model_path: 模型路径
        image_path: 图片路径
        conf_threshold: 置信度阈值
        img_size: 图片大小
        device: 设备
    """
    # 加载模型
    model = YOLO(model_path)
    
    # 预测图片
    results = model.predict(
        source=image_path,
        conf=conf_threshold,
        imgsz=img_size,
        device=device,
        save=True,  # 保存预测结果
        show_labels=True,  # 显示标签
        show_conf=True,  # 显示置信度
    )
    
    # 打印预测结果
    for result in results:
        boxes = result.boxes
        print(f"\n检测到 {len(boxes)} 个目标:")
        for box in boxes:
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])
            print(f"  {class_name}: {confidence:.2%}")
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='YOLO训练脚本')
    parser.add_argument('--mode', type=str, default='train', 
                       choices=['train', 'eval', 'predict'],
                       help='运行模式: train, eval, predict')
    parser.add_argument('--data', type=str, default='data/yolo_dataset/mahjong.yaml',
                       help='数据配置文件路径')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='模型路径或预训练模型名称')
    parser.add_argument('--model-size', type=str, default='n',
                       choices=['n', 's', 'm', 'l', 'x'],
                       help='模型大小')
    parser.add_argument('--img-size', type=int, default=640,
                       help='图片大小')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='批次大小')
    parser.add_argument('--epochs', type=int, default=100,
                       help='训练轮数')
    parser.add_argument('--device', type=str, default='0',
                       help='设备')
    parser.add_argument('--image', type=str, default=None,
                       help='预测模式下的图片路径')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='置信度阈值')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        # 训练模式
        train_model(
            data_yaml=args.data,
            model_size=args.model_size,
            img_size=args.img_size,
            batch_size=args.batch_size,
            epochs=args.epochs,
            device=args.device,
        )
    
    elif args.mode == 'eval':
        # 评估模式
        evaluate_model(
            model_path=args.model,
            data_yaml=args.data,
            img_size=args.img_size,
            device=args.device,
        )
    
    elif args.mode == 'predict':
        # 预测模式
        if args.image is None:
            print("预测模式需要指定图片路径 (--image)")
        else:
            predict_image(
                model_path=args.model,
                image_path=args.image,
                conf_threshold=args.conf,
                img_size=args.img_size,
                device=args.device,
            )