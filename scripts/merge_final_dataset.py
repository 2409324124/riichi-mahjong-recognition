"""
合并数据集脚本

合并原始数据集和合成数据集，创建 YOLO 格式的训练数据。
"""

import os
import shutil
import random
from pathlib import Path


def merge_datasets(
    original_dir: str,
    synthetic_dir: str,
    output_dir: str,
    train_ratio: float = 0.8,
    val_ratio: float = 0.15,
    test_ratio: float = 0.05
):
    """
    合并数据集
    
    Args:
        original_dir: 原始数据集目录
        synthetic_dir: 合成数据集目录
        output_dir: 输出目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
    """
    original_path = Path(original_dir)
    synthetic_path = Path(synthetic_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    for split in ['train', 'val', 'test']:
        (output_path / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_path / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # 读取类别列表
    classes_file = original_path / 'classes.txt'
    if not classes_file.exists():
        classes_file = synthetic_path / 'classes.txt'
    
    with open(classes_file, 'r', encoding='utf-8') as f:
        classes = [line.strip() for line in f if line.strip()]
    
    # 收集所有图片和标注
    all_images = []
    
    # 收集原始数据集
    if (original_path / 'images').exists():
        for img_file in (original_path / 'images').glob('*.jpg'):
            label_file = original_path / 'labels' / f"{img_file.stem}.txt"
            if label_file.exists():
                all_images.append((img_file, label_file, 'original'))
    
    # 收集合成数据集
    if (synthetic_path / 'images').exists():
        for img_file in (synthetic_path / 'images').glob('*.jpg'):
            label_file = synthetic_path / 'labels' / f"{img_file.stem}.txt"
            if label_file.exists():
                all_images.append((img_file, label_file, 'synthetic'))
    
    # 随机打乱
    random.shuffle(all_images)
    
    # 分割数据集
    n = len(all_images)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    
    train_images = all_images[:n_train]
    val_images = all_images[n_train:n_train + n_val]
    test_images = all_images[n_train + n_val:]
    
    # 复制文件
    for split, images in [('train', train_images), ('val', val_images), ('test', test_images)]:
        for img_file, label_file, source in images:
            # 生成新的文件名
            new_filename = f"{source}_{img_file.stem}"
            
            # 复制图片
            shutil.copy2(img_file, output_path / split / 'images' / f"{new_filename}.jpg")
            
            # 复制标注文件
            shutil.copy2(label_file, output_path / split / 'labels' / f"{new_filename}.txt")
    
    # 创建 YOLO 配置文件
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
    
    # 保存类别列表
    with open(output_path / 'classes.txt', 'w', encoding='utf-8') as f:
        for cls in classes:
            f.write(f"{cls}\n")
    
    print(f"数据集合并完成！")
    print(f"总图片数: {len(all_images)}")
    print(f"训练集: {len(train_images)} 张")
    print(f"验证集: {len(val_images)} 张")
    print(f"测试集: {len(test_images)} 张")
    print(f"类别数量: {len(classes)}")
    
    return output_path


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='合并数据集')
    parser.add_argument('--original-dir', type=str, default='data/merged_dataset',
                       help='原始数据集目录')
    parser.add_argument('--synthetic-dir', type=str, default='data/synthetic_dataset',
                       help='合成数据集目录')
    parser.add_argument('--output-dir', type=str, default='data/yolo_dataset_final',
                       help='输出目录')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                       help='训练集比例')
    parser.add_argument('--val-ratio', type=float, default=0.15,
                       help='验证集比例')
    parser.add_argument('--test-ratio', type=float, default=0.05,
                       help='测试集比例')
    
    args = parser.parse_args()
    
    # 设置随机种子
    random.seed(42)
    
    # 合并数据集
    merge_datasets(
        original_dir=args.original_dir,
        synthetic_dir=args.synthetic_dir,
        output_dir=args.output_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )