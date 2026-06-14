# AGENT.md - 日本立直麻将识别系统

## 项目概述

本项目旨在构建一个自动识别真实麻将牌的系统，专注于日本立直麻将（Riichi Mahjong）规则。系统将实现三个核心功能：

1. **牌面识别**：通过摄像头识别真实麻将牌
2. **计分系统**：计算番数、符数和点数
3. **牌效计算**：分析向听数和牌效率

## 技术架构

### 技术栈

- **编程语言**：Python 3.8+
- **计算机视觉**：YOLOv8 (ultralytics) + OpenCV
- **深度学习**：PyTorch
- **数据处理**：NumPy, Pandas
- **测试框架**：pytest

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  牌面识别    │  │  计分系统    │  │  牌效计算    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
├─────────┼───────────────┼───────────────┼─────────────────┤
│         └───────────────┼───────────────┘                  │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              核心逻辑层                              │   │
│  │  - 麻将牌定义 (tile.py)                             │   │
│  │  - 手牌管理 (hand.py)                               │   │
│  │  - 役种识别 (yaku.py)                               │   │
│  │  - 向听计算 (shanten.py)                            │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              数据层                                  │   │
│  │  - 图像数据集 (data/raw)                            │   │
│  │  - 训练模型 (data/models)                           │   │
│  │  - 配置文件 (config)                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 开发阶段

### 阶段1：项目初始化（1-2天）

**目标**：建立项目基础结构

**任务**：
- [x] 创建项目目录结构
- [x] 初始化git仓库
- [x] 创建AGENT.md
- [ ] 创建README.md
- [ ] 创建requirements.txt
- [ ] 创建pyproject.toml
- [ ] 创建.gitignore

### 阶段2：计分系统（2-3周）

**目标**：实现完整的日本立直麻将计分逻辑

**任务**：
- [ ] 实现麻将牌定义（34种牌）
- [ ] 实现手牌管理
- [ ] 实现役种识别（50+种役）
- [ ] 实现符数计算
- [ ] 实现点数计算
- [ ] 编写单元测试

**关键模块**：
```python
# src/game_logic/tile.py
class Tile:
    """麻将牌定义"""
    # 万子(MAN): 1-9万
    # 筒子(PIN): 1-9筒
    # 索子(SOU): 1-9索
    # 风牌(WIND): 东南西北
    # 三元牌(DRAGON): 白发中

# src/game_logic/hand.py
class Hand:
    """手牌管理"""
    # 手牌表示（34数组格式）
    # 副露管理
    # 宝牌管理

# src/game_logic/scoring/yaku.py
class Yaku:
    """役种类"""
    # 1番：立断平一杯...
    # 2番：三色一通混全...
    # 3番：混一色纯全...
    # 6番：清一色
    # 役满：国士无双九莲宝灯...

# src/game_logic/scoring/score.py
class ScoreCalculator:
    """点数计算器"""
    # 符数计算
    # 番数计算
    # 点数计算
    # 支付计算
```

### 阶段3：牌面识别（3-4周）

**目标**：实现摄像头图像中的麻将牌识别

**任务**：
- [ ] 收集麻将牌图像数据集
- [ ] 数据标注和预处理
- [ ] 训练YOLO检测模型
- [ ] 实现牌面分类器
- [ ] 集成识别pipeline
- [ ] 优化识别准确率

**技术方案**：
```python
# src/recognition/detector.py
class MahjongDetector:
    """麻将牌检测器"""
    # 使用YOLOv8进行目标检测
    # 检测麻将牌位置
    # 返回边界框和置信度

# src/recognition/classifier.py
class TileClassifier:
    """牌面分类器"""
    # 对检测到的牌进行分类
    # 识别牌的类型（万筒索风元）
    # 识别牌的点数

# src/recognition/recognizer.py
class MahjongRecognizer:
    """麻将牌识别器"""
    # 整合检测和分类
    # 处理摄像头输入
    # 返回识别结果
```

### 阶段4：牌效计算（2-3周）

**目标**：实现向听数和牌效率分析

**任务**：
- [ ] 实现向听数计算
- [ ] 实现接受牌计算
- [ ] 实现牌效率分析
- [ ] 实现打牌推荐
- [ ] 编写单元测试

**关键算法**：
```python
# src/efficiency/shanten.py
class ShantenCalculator:
    """向听数计算器"""
    # 计算向听数（0=听牌，-1=和了）
    # 支持普通手、七对子、国士无双
    # 使用34数组格式

# src/efficiency/ukeire.py
class UkeireCalculator:
    """接受牌计算器"""
    # 计算有效牌数量
    # 分析听牌类型
    # 计算和了概率

# src/efficiency/analyzer.py
class EfficiencyAnalyzer:
    """牌效分析器"""
    # 分析每种打牌的效率
    # 考虑向听前进
    # 考虑好形听牌
    # 生成打牌推荐
```

## 工作流程

### 开发流程

1. **需求分析**：明确功能需求和技术要求
2. **设计**：设计模块接口和数据结构
3. **实现**：编写代码实现功能
4. **测试**：编写和运行单元测试
5. **集成**：集成各模块，进行端到端测试
6. **优化**：优化性能和准确率

### 测试策略

- **单元测试**：每个模块独立测试
- **集成测试**：模块间交互测试
- **端到端测试**：完整流程测试
- **性能测试**：识别速度和准确率测试

### 代码规范

- 遵循PEP 8代码规范
- 使用类型注解
- 编写详细的文档字符串
- 保持函数简洁，单一职责

## 相关资源

### 参考项目

- [MahjongRepository/mahjong](https://github.com/MahjongRepository/mahjong) - Python麻将库，包含完整的计分系统
- [EndlessCheng/mahjong-helper](https://github.com/EndlessCheng/mahjong-helper) - 麻将助手，包含牌效分析
- [share2code99/mahjong_tile_recognition](https://github.com/share2code99/mahjong_tile_recognition) - YOLO麻将牌识别

### 技术文档

- [YOLOv8文档](https://docs.ultralytics.com/)
- [OpenCV文档](https://docs.opencv.org/)
- [PyTorch文档](https://pytorch.org/docs/)

### 麻将规则

- [日本立直麻将规则](https://en.wikipedia.org/wiki/Japanese_Mahjong)
- [役种列表](https://en.wikipedia.org/wiki/Japanese_Mahjong#Yaku)
- [计分规则](https://en.wikipedia.org/wiki/Japanese_Mahjong#Scoring)

## 快速开始

### 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd riichi-mahjong-recognition

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_scoring.py

# 运行带覆盖率的测试
pytest --cov=src
```

### 使用示例

```python
from src.game_logic.tile import Tile
from src.game_logic.hand import Hand
from src.game_logic.scoring.score import ScoreCalculator

# 创建手牌
hand = Hand()
hand.add_tile(Tile("1m"))
hand.add_tile(Tile("2m"))
hand.add_tile(Tile("3m"))
# ...

# 计算点数
calculator = ScoreCalculator()
result = calculator.calculate(hand)
print(f"番数: {result.han}, 符数: {result.fu}, 点数: {result.points}")
```

## 注意事项

1. **数据安全**：不要提交大型数据文件到git仓库
2. **模型版本**：使用git-lfs管理大型模型文件
3. **依赖管理**：使用requirements.txt或pyproject.toml管理依赖
4. **文档更新**：及时更新README和AGENT.md
5. **代码审查**：提交前进行代码审查

## 后续计划

1. **GUI界面**：添加图形用户界面
2. **实时识别**：实现实时摄像头识别
3. **多语言支持**：支持中文、英文、日文
4. **移动端适配**：支持手机摄像头
5. **云端部署**：部署到云端提供API服务

---

**最后更新**：2026年6月15日
**维护者**：AI Assistant
**版本**：v0.1.0