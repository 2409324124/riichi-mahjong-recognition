"""
数据增强脚本

生成合成场景图片，提高模型泛化能力。
"""

import os
import random
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np


class MahjongDataAugmenter:
    """麻将牌数据增强器"""
    
    def __init__(
        self,
        tile_dir: str,
        output_dir: str,
        img_size: int = 640,
        tiles_per_image: int = 9
    ):
        """
        初始化数据增强器
        
        Args:
            tile_dir: 裁剪图片目录
            output_dir: 输出目录
            img_size: 输出图片大小
            tiles_per_image: 每张合成图片包含的牌数
        """
        self.tile_dir = Path(tile_dir)
        self.output_dir = Path(output_dir)
        self.img_size = img_size
        self.tiles_per_image = tiles_per_image
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'images').mkdir(exist_ok=True)
        (self.output_dir / 'labels').mkdir(exist_ok=True)
        
        # 加载所有裁剪图片
        self.tile_images = self._load_tile_images()
        
    def _load_tile_images(self) -> dict:
        """加载所有裁剪图片，按类别分组"""
        tile_images = {}
        
        for img_file in self.tile_dir.glob('*.jpg'):
            # 从文件名提取类别
            parts = img_file.stem.split('_')
            if parts[0] in ['mahjong', 'riichi']:
                if parts[0] == 'mahjong':
                    class_name = parts[1]
                else:
                    class_name = '_'.join(parts[1:-1])
            else:
                class_name = '_'.join(parts[:-1])
            
            if class_name not in tile_images:
                tile_images[class_name] = []
            
            try:
                img = Image.open(img_file).convert('RGBA')
                tile_images[class_name].append((img_file, img))
            except Exception as e:
                print(f"警告：无法加载图片 {img_file}: {e}")
        
        return tile_images
    
    def _create_random_background(self) -> Image.Image:
        """创建随机背景"""
        # 创建纯色背景
        bg_color = (
            random.randint(200, 255),
            random.randint(200, 255),
            random.randint(200, 255)
        )
        background = Image.new('RGB', (self.img_size, self.img_size), bg_color)
        
        # 添加一些随机噪声
        draw = ImageDraw.Draw(background)
        for _ in range(random.randint(50, 200)):
            x = random.randint(0, self.img_size - 1)
            y = random.randint(0, self.img_size - 1)
            noise_color = (
                random.randint(180, 255),
                random.randint(180, 255),
                random.randint(180, 255)
            )
            draw.point((x, y), fill=noise_color)
        
        # 添加一些随机形状
        for _ in range(random.randint(2, 8)):
            shape_type = random.choice(['rectangle', 'ellipse'])
            x1 = random.randint(0, self.img_size)
            y1 = random.randint(0, self.img_size)
            x2 = x1 + random.randint(20, 100)
            y2 = y1 + random.randint(20, 100)
            shape_color = (
                random.randint(150, 230),
                random.randint(150, 230),
                random.randint(150, 230)
            )
            
            if shape_type == 'rectangle':
                draw.rectangle([x1, y1, x2, y2], fill=shape_color)
            else:
                draw.ellipse([x1, y1, x2, y2], fill=shape_color)
        
        # 模糊背景
        background = background.filter(ImageFilter.GaussianBlur(radius=2))
        
        return background
    
    def _transform_tile(self, tile_img: Image.Image) -> Image.Image:
        """对单张牌进行变换"""
        # 随机缩放（限制最大尺寸，避免超出背景）
        max_scale = min(self.img_size / tile_img.width, self.img_size / tile_img.height) * 0.3
        scale = random.uniform(0.3, min(1.5, max_scale))
        new_size = (int(tile_img.width * scale), int(tile_img.height * scale))
        tile_img = tile_img.resize(new_size, Image.LANCZOS)
        
        # 随机旋转
        angle = random.randint(-30, 30)
        tile_img = tile_img.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
        
        # 随机亮度调整
        if random.random() > 0.5:
            enhancer = ImageEnhance.Brightness(tile_img)
            factor = random.uniform(0.7, 1.3)
            tile_img = enhancer.enhance(factor)
        
        # 随机对比度调整
        if random.random() > 0.5:
            enhancer = ImageEnhance.Contrast(tile_img)
            factor = random.uniform(0.7, 1.3)
            tile_img = enhancer.enhance(factor)
        
        return tile_img
    
    def _place_tile_on_background(
        self,
        background: Image.Image,
        tile_img: Image.Image,
        position: tuple
    ) -> tuple:
        """将牌放到背景上，返回边界框"""
        x, y = position
        
        # 确保牌不会超出边界
        x = max(0, min(x, self.img_size - tile_img.width))
        y = max(0, min(y, self.img_size - tile_img.height))
        
        # 创建透明度掩码
        if tile_img.mode == 'RGBA':
            alpha = tile_img.split()[3]
        else:
            alpha = Image.new('L', tile_img.size, 255)
        
        # 粘贴牌到背景
        background.paste(tile_img, (x, y), alpha)
        
        # 计算边界框
        bbox = {
            'x_min': x,
            'y_min': y,
            'x_max': x + tile_img.width,
            'y_max': y + tile_img.height
        }
        
        return bbox
    
    def generate_synthetic_image(self, image_id: int) -> dict:
        """
        生成一张合成图片
        
        Args:
            image_id: 图片 ID
        
        Returns:
            包含图片路径和标注信息的字典
        """
        # 创建随机背景
        background = self._create_random_background()
        
        # 随机选择要放置的牌
        selected_classes = random.sample(
            list(self.tile_images.keys()),
            min(self.tiles_per_image, len(self.tile_images))
        )
        
        # 放置牌
        bboxes = []
        used_positions = []
        
        for class_name in selected_classes:
            # 随机选择一张该类别的牌
            tile_file, tile_img = random.choice(self.tile_images[class_name])
            
            # 变换牌
            tile_img = self._transform_tile(tile_img)
            
            # 随机选择位置（避免重叠）
            max_attempts = 50
            for _ in range(max_attempts):
                x = random.randint(0, self.img_size - tile_img.width)
                y = random.randint(0, self.img_size - tile_img.height)
                
                # 检查是否与已放置的牌重叠
                overlap = False
                for used_pos in used_positions:
                    if (abs(x - used_pos[0]) < tile_img.width * 0.5 and
                        abs(y - used_pos[1]) < tile_img.height * 0.5):
                        overlap = True
                        break
                
                if not overlap:
                    used_positions.append((x, y))
                    break
            
            # 放置牌
            bbox = self._place_tile_on_background(background, tile_img, (x, y))
            
            # 记录标注信息
            bboxes.append({
                'class_name': class_name,
                'x_center': (bbox['x_min'] + bbox['x_max']) / 2 / self.img_size,
                'y_center': (bbox['y_min'] + bbox['y_max']) / 2 / self.img_size,
                'width': (bbox['x_max'] - bbox['x_min']) / self.img_size,
                'height': (bbox['y_max'] - bbox['y_min']) / self.img_size
            })
        
        # 保存图片
        filename = f"synthetic_{image_id:06d}"
        image_path = self.output_dir / 'images' / f"{filename}.jpg"
        background.save(image_path, 'JPEG', quality=95)
        
        # 保存标注文件
        label_path = self.output_dir / 'labels' / f"{filename}.txt"
        with open(label_path, 'w') as f:
            for bbox in bboxes:
                # 获取类别 ID
                class_id = list(self.tile_images.keys()).index(bbox['class_name'])
                f.write(f"{class_id} {bbox['x_center']:.6f} {bbox['y_center']:.6f} {bbox['width']:.6f} {bbox['height']:.6f}\n")
        
        return {
            'image_path': str(image_path),
            'label_path': str(label_path),
            'bboxes': bboxes
        }
    
    def generate_dataset(self, num_images: int = 5000):
        """
        生成数据集
        
        Args:
            num_images: 要生成的图片数量
        """
        print(f"开始生成 {num_images} 张合成图片...")
        
        # 生成图片
        for i in range(num_images):
            if i % 100 == 0:
                print(f"进度: {i}/{num_images}")
            
            self.generate_synthetic_image(i)
        
        print(f"生成完成！图片保存在: {self.output_dir}")
        
        # 保存类别信息
        classes = list(self.tile_images.keys())
        with open(self.output_dir / 'classes.txt', 'w', encoding='utf-8') as f:
            for cls in classes:
                f.write(f"{cls}\n")
        
        print(f"类别数量: {len(classes)}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='麻将牌数据增强')
    parser.add_argument('--tile-dir', type=str, default='data/merged_dataset/images',
                       help='裁剪图片目录')
    parser.add_argument('--output-dir', type=str, default='data/synthetic_dataset',
                       help='输出目录')
    parser.add_argument('--num-images', type=int, default=5000,
                       help='生成图片数量')
    parser.add_argument('--img-size', type=int, default=640,
                       help='输出图片大小')
    parser.add_argument('--tiles-per-image', type=int, default=9,
                       help='每张图片包含的牌数')
    
    args = parser.parse_args()
    
    # 设置随机种子
    random.seed(42)
    np.random.seed(42)
    
    # 创建数据增强器
    augmenter = MahjongDataAugmenter(
        tile_dir=args.tile_dir,
        output_dir=args.output_dir,
        img_size=args.img_size,
        tiles_per_image=args.tiles_per_image
    )
    
    # 生成数据集
    augmenter.generate_dataset(args.num_images)