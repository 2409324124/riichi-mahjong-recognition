"""
数据预处理脚本

将RaesakAce/riichi_mahjong_tiles数据集转换为YOLO格式。
"""

import os
import shutil
import random
from pathlib import Path
from PIL import Image
import numpy as np


def create_yolo_dataset(
    source_dir: str,
    output_dir: str,
    train_ratio: float = 0.8,
    val_ratio: float = 0.15,
    test_ratio: float = 0.05,
    img_size: int = 640
):
    """
    创建YOLO格式的数据集
    
    Args:
        source_dir: 源数据目录
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
    
    # 获取所有图片文件
    image_files = list(source_path.glob('*.jpg'))
    
    # 按牌类型分组
    tile_groups = {}
    for img_file in image_files:
        # 从文件名提取牌类型 (例如: m_1_0.jpg -> m_1)
        tile_type = '_'.join(img_file.stem.split('_')[:-1])
        if tile_type not in tile_groups:
            tile_groups[tile_type] = []
        tile_groups[tile_type].append(img_file)
    
    # 创建类别映射
    tile_types = sorted(tile_groups.keys())
    class_mapping = {tile_type: idx for idx, tile_type in enumerate(tile_types)}
    
    # 保存类别映射
    with open(output_path / 'classes.txt', 'w', encoding='utf-8') as f:
        for tile_type in tile_types:
            f.write(f"{tile_type}\n")
    
    # 处理每个牌类型
    all_images = []
    for tile_type, images in tile_groups.items():
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
        all_images.extend([(img, tile_type, 'train') for img in train_images])
        all_images.extend([(img, tile_type, 'val') for img in val_images])
        all_images.extend([(img, tile_type, 'test') for img in test_images])
    
    # 处理每张图片
    for img_file, tile_type, split in all_images:
        # 读取图片
        img = Image.open(img_file)
        
        # 调整图片大小
        img = img.resize((img_size, img_size), Image.LANCZOS)
        
        # 生成新的文件名
        new_filename = f"{tile_type}_{img_file.stem}.jpg"
        
        # 保存图片
        img.save(output_path / split / 'images' / new_filename)
        
        # 生成YOLO格式的标注文件
        # 由于是裁剪的单张牌图片，整个图片就是一张牌
        class_id = class_mapping[tile_type]
        
        # YOLO格式: class_id x_center y_center width height
        # 对于裁剪图片，牌在图片中心，占满整个图片
        label_content = f"{class_id} 0.5 0.5 1.0 1.0"
        
        # 保存标注文件
        label_filename = new_filename.replace('.jpg', '.txt')
        with open(output_path / split / 'labels' / label_filename, 'w') as f:
            f.write(label_content)
    
    # 创建YOLO配置文件
    create_yolo_config(output_path, tile_types, img_size)
    
    print(f"数据集创建完成！")
    print(f"类别数量: {len(tile_types)}")
    print(f"训练集: {len([x for x in all_images if x[2] == 'train'])} 张")
    print(f"验证集: {len([x for x in all_images if x[2] == 'val'])} 张")
    print(f"测试集: {len([x for x in all_images if x[2] == 'test'])} 张")
    
    return class_mapping


def create_yolo_config(output_path: Path, tile_types: list, img_size: int):
    """
    创建YOLO配置文件
    
    Args:
        output_path: 输出路径
        tile_types: 牌类型列表
        img_size: 图片大小
    """
    config_content = f"""# YOLO配置文件 - 日本立直麻将牌识别

path: {output_path.absolute()}
train: train/images
val: val/images
test: test/images

# 类别数量
nc: {len(tile_types)}

# 类别名称
names:
"""
    
    for tile_type in tile_types:
        config_content += f"  - {tile_type}\n"
    
    with open(output_path / 'mahjong.yaml', 'w', encoding='utf-8') as f:
        f.write(config_content)


def augment_dataset(
    source_dir: str,
    output_dir: str,
    augmentations_per_image: int = 5
):
    """
    数据增强
    
    Args:
        source_dir: 源数据目录
        output_dir: 输出目录
        augmentations_per_image: 每张图片的增强数量
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 获取所有图片
    image_files = list(source_path.glob('*.jpg'))
    
    for img_file in image_files:
        # 读取图片
        img = Image.open(img_file)
        
        # 保存原始图片
        img.save(output_path / img_file.name)
        
        # 生成增强图片
        for i in range(augmentations_per_image):
            augmented = augment_image(img)
            augmented_filename = f"{img_file.stem}_aug_{i}.jpg"
            augmented.save(output_path / augmented_filename)
    
    print(f"数据增强完成！")
    print(f"原始图片: {len(image_files)} 张")
    print(f"增强后图片: {len(image_files) * (1 + augmentations_per_image)} 张")


def augment_image(img: Image.Image) -> Image.Image:
    """
    对单张图片进行增强
    
    Args:
        img: 输入图片
    
    Returns:
        增强后的图片
    """
    # 随机旋转
    if random.random() > 0.5:
        angle = random.randint(-15, 15)
        img = img.rotate(angle, expand=True, fillcolor=(255, 255, 255))
    
    # 随机缩放
    if random.random() > 0.5:
        scale = random.uniform(0.8, 1.2)
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)
        # 裁剪或填充到原始大小
        if scale > 1:
            # 裁剪中心区域
            left = (img.width - 640) // 2
            top = (img.height - 640) // 2
            img = img.crop((left, top, left + 640, top + 640))
        else:
            # 填充到原始大小
            new_img = Image.new('RGB', (640, 640), (255, 255, 255))
            left = (640 - img.width) // 2
            top = (640 - img.height) // 2
            new_img.paste(img, (left, top))
            img = new_img
    
    # 随机亮度调整
    if random.random() > 0.5:
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(img)
        factor = random.uniform(0.8, 1.2)
        img = enhancer.enhance(factor)
    
    # 随机对比度调整
    if random.random() > 0.5:
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        factor = random.uniform(0.8, 1.2)
        img = enhancer.enhance(factor)
    
    return img


if __name__ == '__main__':
    # 设置随机种子
    random.seed(42)
    
    # 创建YOLO格式的数据集
    source_dir = 'data/datasets/riichi_mahjong_tiles/cropped_images'
    output_dir = 'data/yolo_dataset'
    
    class_mapping = create_yolo_dataset(
        source_dir=source_dir,
        output_dir=output_dir,
        train_ratio=0.8,
        val_ratio=0.15,
        test_ratio=0.05,
        img_size=640
    )
    
    # 保存类别映射
    import json
    with open('data/class_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(class_mapping, f, ensure_ascii=False, indent=2)
    
    print(f"\n类别映射已保存到 data/class_mapping.json")