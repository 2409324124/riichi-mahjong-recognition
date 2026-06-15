"""
数据集合并脚本

合并 mahjong-dataset 和 riichi_mahjong_tiles 数据集。
"""

import os
import shutil
import pandas as pd
from pathlib import Path
import random


def merge_datasets():
    """合并数据集"""
    
    # 数据集路径
    mahjong_dataset_dir = Path('data/datasets/mahjong-dataset')
    riichi_dataset_dir = Path('data/datasets/riichi_mahjong_tiles')
    output_dir = Path('data/merged_dataset')
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'images').mkdir(exist_ok=True)
    
    # 读取 mahjong-dataset 的标签
    labels_df = pd.read_csv(mahjong_dataset_dir / 'tiles-data' / 'data.csv')
    label_names_df = pd.read_csv(mahjong_dataset_dir / 'tiles-data' / 'label.csv')
    
    # 创建标签映射
    label_mapping = dict(zip(label_names_df['label-index'], label_names_df['label-name']))
    
    # 统计信息
    total_images = 0
    
    # 复制 mahjong-dataset 的图片
    print("复制 mahjong-dataset 图片...")
    for _, row in labels_df.iterrows():
        src_image = mahjong_dataset_dir / 'tiles-resized' / row['image-name']
        if src_image.exists():
            # 生成新的文件名
            label_name = row['label-name']
            new_filename = f"mahjong_{label_name}_{total_images:04d}.jpg"
            
            # 复制图片
            shutil.copy2(src_image, output_dir / 'images' / new_filename)
            total_images += 1
    
    # 复制 riichi_mahjong_tiles 的图片
    print("复制 riichi_mahjong_tiles 图片...")
    riichi_images_dir = riichi_dataset_dir / 'cropped_images'
    for img_file in riichi_images_dir.glob('*.jpg'):
        # 生成新的文件名
        tile_type = '_'.join(img_file.stem.split('_')[:-1])
        new_filename = f"riichi_{tile_type}_{total_images:04d}.jpg"
        
        # 复制图片
        shutil.copy2(img_file, output_dir / 'images' / new_filename)
        total_images += 1
    
    print(f"合并完成！总共 {total_images} 张图片")
    
    # 创建类别映射文件
    create_class_mapping(output_dir, labels_df, label_names_df)
    
    return output_dir


def create_class_mapping(output_dir: Path, labels_df: pd.DataFrame, label_names_df: pd.DataFrame):
    """创建类别映射文件"""
    
    # 获取所有类别
    all_classes = set()
    
    # 从 mahjong-dataset 获取类别
    for _, row in label_names_df.iterrows():
        all_classes.add(row['label-name'])
    
    # 从 riichi_mahjong_tiles 获取类别
    riichi_classes = [
        'chun', 'east', 'haku', 'hatsu', 'north', 'south', 'west',
        'm_0', 'm_1', 'm_2', 'm_3', 'm_4', 'm_5', 'm_6', 'm_7', 'm_8', 'm_9',
        'p_0', 'p_1', 'p_2', 'p_3', 'p_4', 'p_5', 'p_6', 'p_7', 'p_8', 'p_9',
        's_0', 's_1', 's_2', 's_3', 's_4', 's_5', 's_6', 's_7', 's_8', 's_9'
    ]
    all_classes.update(riichi_classes)
    
    # 排序并保存
    sorted_classes = sorted(all_classes)
    with open(output_dir / 'classes.txt', 'w', encoding='utf-8') as f:
        for cls in sorted_classes:
            f.write(f"{cls}\n")
    
    print(f"类别数量: {len(sorted_classes)}")
    print(f"类别列表: {sorted_classes[:10]}...")


if __name__ == '__main__':
    merge_datasets()