# 日本立直麻将识别系统

一个基于计算机视觉的真实麻将牌识别系统，专注于日本立直麻将（Riichi Mahjong）规则。

## 功能特性

### 1. 牌面识别
- 使用YOLOv8进行麻将牌检测
- 支持真实麻将牌识别
- 实时摄像头识别

### 2. 计分系统
- 完整的日本立直麻将规则实现
- 支持50+种役种识别
- 自动计算番数、符数和点数
- 支持各种特殊规则（役满、宝牌等）

### 3. 牌效计算
- 向听数计算
- 接受牌分析
- 牌效率评估
- 打牌推荐

## 技术栈

- **Python** 3.8+
- **YOLOv8** (ultralytics) - 目标检测
- **OpenCV** - 图像处理
- **PyTorch** - 深度学习后端
- **NumPy** - 数值计算
- **pytest** - 测试框架

## 项目结构

```
riichi-mahjong-recognition/
├── README.md                    # 项目说明
├── AGENT.md                     # AI助手指南
├── requirements.txt             # Python依赖
├── pyproject.toml               # 项目配置
├── .gitignore                   # Git忽略文件
├── data/                        # 数据目录
│   ├── raw/                     # 原始图像数据
│   ├── processed/               # 处理后的数据
│   └── models/                  # 训练好的模型
├── src/                         # 源代码
│   ├── recognition/             # 牌面识别模块
│   │   ├── detector.py          # YOLO检测器
│   │   ├── classifier.py        # 牌面分类器
│   │   └── recognizer.py        # 识别主逻辑
│   ├── game_logic/              # 麻将逻辑模块
│   │   ├── tile.py              # 麻将牌定义
│   │   ├── hand.py              # 手牌管理
│   │   └── scoring/             # 计分系统
│   │       ├── yaku.py          # 役种识别
│   │       ├── fu.py            # 符数计算
│   │       └── score.py         # 点数计算
│   ├── efficiency/              # 牌效计算模块
│   │   ├── shanten.py           # 向听数计算
│   │   ├── ukeire.py            # 接受牌计算
│   │   └── analyzer.py          # 牌效分析
│   └── utils/                   # 工具函数
│       ├── image_utils.py       # 图像处理工具
│       └── mahjong_utils.py     # 麻将工具函数
├── tests/                       # 测试文件
│   ├── test_recognition.py      # 识别测试
│   ├── test_scoring.py          # 计分测试
│   └── test_efficiency.py       # 牌效测试
├── notebooks/                   # Jupyter notebooks
│   └── exploration.ipynb        # 探索性分析
└── scripts/                     # 脚本文件
    ├── train.py                 # 模型训练脚本
    └── evaluate.py              # 模型评估脚本
```

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

## 开发阶段

### 阶段1：项目初始化（1-2天）
- [x] 创建项目目录结构
- [x] 初始化git仓库
- [x] 创建AGENT.md
- [ ] 创建README.md
- [ ] 创建requirements.txt
- [ ] 创建pyproject.toml
- [ ] 创建.gitignore

### 阶段2：计分系统（2-3周）
- [ ] 实现麻将牌定义（34种牌）
- [ ] 实现手牌管理
- [ ] 实现役种识别（50+种役）
- [ ] 实现符数计算
- [ ] 实现点数计算
- [ ] 编写单元测试

### 阶段3：牌面识别（3-4周）
- [ ] 收集麻将牌图像数据集
- [ ] 数据标注和预处理
- [ ] 训练YOLO检测模型
- [ ] 实现牌面分类器
- [ ] 集成识别pipeline
- [ ] 优化识别准确率

### 阶段4：牌效计算（2-3周）
- [ ] 实现向听数计算
- [ ] 实现接受牌计算
- [ ] 实现牌效率分析
- [ ] 实现打牌推荐
- [ ] 编写单元测试

### 阶段5：集成测试（1-2周）
- [ ] 集成所有模块
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档完善

## 麻将规则参考

### 牌的种类
- **万子** (Man): 1-9万
- **筒子** (Pin): 1-9筒
- **索子** (Sou): 1-9索
- **风牌** (Wind): 东、南、西、北
- **三元牌** (Dragon): 白、发、中

### 役种示例
- **1番**: 立直、断幺九、平和、一杯口
- **2番**: 三色同顺、一气通贯、混全带幺九
- **3番**: 混一色、纯全带幺九、二杯口
- **6番**: 清一色
- **役满**: 国士无双、九莲宝灯、大三元

### 计分规则
- 点数 = 基本点 × 支付倍数
- 基本点 = 符 × 2^(番+2)
- 满贯以上固定点数：满贯8000、跳满12000、倍满16000、三倍满24000、役满32000

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 致谢

- [MahjongRepository/mahjong](https://github.com/MahjongRepository/mahjong) - Python麻将库参考
- [EndlessCheng/mahjong-helper](https://github.com/EndlessCheng/mahjong-helper) - 牌效分析参考
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - 目标检测框架

## 联系方式

- 项目链接: [https://github.com/yourusername/riichi-mahjong-recognition](https://github.com/yourusername/riichi-mahjong-recognition)
- 问题反馈: [Issues](https://github.com/yourusername/riichi-mahjong-recognition/issues)

---

**最后更新**: 2026年6月15日
**版本**: v0.1.0