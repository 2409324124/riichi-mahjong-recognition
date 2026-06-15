"""
数据预处理脚本（更新版）

处理合并后的数据集，转换为YOLO格式。
"""

import os
import shutil
import random
from pathlib import Path
from PIL import Image
import numpy as np


def create_yolo_dataset_from_merged(
    source_dir: str,
    output_dir: str,
    train_ratio: float = 0.8,
    val_ratio: float = 0.15,
    test_ratio: float = 0.05,
    img_size: int = 640
):
    """
    从合并后的数据集创建YOLO格式的数据集
    
    Args:
        source_dir: 源数据目录（合并后的数据集）
        output_dir: 输出目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        img_size: 图片大小
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录结构
    for split in ['train', 'val', 'test']:
        (output_path / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_path / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # 读取类别列表
    classes_file = source_path / 'classes.txt'
    if not classes_file.exists():
        print(f"错误：找不到类别文件 {classes_file}")
        return
    
    with open(classes_file, 'r', encoding='utf-8') as f:
        classes = [line.strip() for line in f if line.strip()]
    
    # 创建类别映射
    class_to_id = {cls: idx for idx, cls in enumerate(classes)}
    
    # 获取所有图片文件
    image_files = list((source_path / 'images').glob('*.jpg'))
    
    # 按类别分组
    class_groups = {}
    for img_file in image_files:
        # 从文件名提取类别 (例如: mahjong_bamboo-1_0000.jpg -> bamboo-1)
        parts = img_file.stem.split('_')
        if len(parts) >= 2:
            # 对于 mahjong_dataset 图片：mahjong_bamboo-1_0000
            # 对于 riichi 图片：riichi_m_1_0000
            if parts[0] == 'mahjong':
                class_name = parts[1]
            elif parts[0] == 'riichi':
                class_name = '_'.join(parts[1:-1])
            else:
                class_name = parts[0]
        else:
            class_name = 'unknown'
        
        if class_name not in class_groups:
            class_groups[class_name] = []
        class_groups[class_name].append(img_file)
    
    # 处理每个类别
    all_images = []
    for class_name, images in class_groups.items():
        if class_name not in class_to_id:
            print(f"警告：类别 '{class_name}' 不在类别列表中，跳过")
            continue
        
        # 随机打乱
        random.shuffle(images)
        
        # 分割数据集
        n = len(images)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:]
        
        # 添加到总列表
        all_images.extend([(img, class_name, 'train') for img in train_images])
        all_images.extend([(img, class_name, 'val') for img in val_images])
        all_images.extend([(img, class_name, 'test') for img in test_images])
    
    # 处理每张图片
    for img_file, class_name, split in all_images:
        # 读取图片
        try:
            img = Image.open(img_file)
        except Exception as e:
            print(f"警告：无法读取图片 {img_file}: {e}")
            continue
        
        # 调整图片大小
        img = img.resize((img_size, img_size), Image.LANCZOS)
        
        # 生成新的文件名
        new_filename = f"{class_name}_{img_file.stem}.jpg"
        
        # 保存图片
        img.save(output_path / split / 'images' / new_filename)
        
        # 生成YOLO格式的标注文件
        class_id = class_to_id[class_name]
        
        # YOLO格式: class_id x_center y_center width height
        # 对于裁剪图片，牌在图片中心，占满整个图片
        label_content = f"{class_id} 0.5 0.5 1.0 1.0"
        
        # 保存标注文件
        label_filename = new_filename.replace('.jpg', '.txt')
        with open(output_path / split / 'labels' / label_filename, 'w') as f:
            f.write(label_content)
    
    # 创建YOLO配置文件
    create_yolo_config(output_path, classes, img_size)
    
    print(f"数据集创建完成！")
    print(f"类别数量: {len(classes)}")
    print(f"训练集: {len([x for x in all_images if x[2] == 'train'])} 张")
    print(f"验证集: {len([x for x in all_images if x[2] == 'val'])} 张")
    print(f"测试集: {len([x for x in all_images if x[2] == 'test'])} 张")
    
    return class_to_id


def create_yolo_config(output_path: Path, classes: list, img_size: int):
    """
    创建YOLO配置文件
    
    Args:
        output_path: 输出路径
        classes: 类别列表
        img_size: 图片大小
    """
    config_content = f"""# YOLO配置文件 - 日本立直麻将牌识别（合并数据集）

path: {output_path.absolute()}
train: train/images
val: val/images
test: test/images

# 类别数量
nc: {len(classes)}

# 类别名称
names:
"""
    
    for cls in classes:
        config_content += f"  - {cls}\n"
    
    with open(output_path / 'mahjong.yaml', 'w', encoding='utf-8') as f:
        f.write(config_content)


if __name__ == '__main__':
    # 设置随机种子
    random.seed(42)
    
    # 创建YOLO格式的数据集
    source_dir = 'data/merged_dataset'
    output_dir = 'data/yolo_dataset_merged'
    
    class_mapping = create_yolo_dataset_from_merged(
        source_dir=source_dir,
        output_dir=output_dir,
        train_ratio=0.8,
        val_ratio=0.15,
        test_ratio=0.05,
        img_size=640
    )
    
    # 保存类别映射
    import json
    with open('data/class_mapping_merged.json', 'w', encoding='utf-8') as f:
        json.dump(class_mapping, f, ensure_ascii=False, indent=2)
    
    print(f"\n类别映射已保存到 data/class_mapping_merged.json")