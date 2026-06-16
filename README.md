# 日本立直麻将识别系统

一个基于计算机视觉的真实麻将牌识别系统，专注于日本立直麻将（Riichi Mahjong）规则。

**GitHub**: https://github.com/2409324124/riichi-mahjong-recognition

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                            │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  牌面识别    │  │  计分系统    │  │  牌效计算    │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
├─────────┼───────────────┼───────────────┼─────────────┤
│         └───────────────┼───────────────┘              │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │              主控制器 (system.py)               │   │
│  │  - analyze_hand()                               │   │
│  │  - validate_win()                               │   │
│  │  - calculate_score()                            │   │
│  │  - get_discard_recommendation()                 │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 功能特性

### 1. 牌面识别
- 使用 YOLOv8 进行麻将牌检测
- 支持真实麻将牌识别
- 实时摄像头识别
- mAP50: 99.5%

### 2. 计分系统
- 完整的日本立直麻将规则实现
- 支持 38 种役种识别（含役满）
- 自动计算番数、符数和点数
- 支持各种特殊规则（役满、宝牌等）

### 3. 牌效计算
- 向听数计算
- 接受牌分析
- 牌效率评估
- 打牌推荐

### 4. 和牌验证
- 防止诈和
- 支持副露手牌验证
- 振听检查

### 5. 雀魂记录解析
- 从玩家 ID 获取游戏记录
- 解析 protobuf 格式记录
- 验证和牌事件

---

## 技术栈

- **Python** 3.8+
- **YOLOv8** (ultralytics) - 目标检测
- **OpenCV** - 图像处理
- **PyTorch** - 深度学习后端
- **NumPy** - 数值计算
- **pytest** - 测试框架

---

## 项目结构

```
riichi-mahjong-recognition/
├── README.md                     # 本文件
├── AGENT.md                      # AI 助手指南
├── pyproject.toml                # 项目配置
├── requirements.txt              # Python 依赖
├── Dockerfile                    # Docker 配置
├── docker-compose.yml            # Docker Compose
│
├── src/                          # 源代码
│   ├── system.py                 # 系统集成主控制器
│   ├── cli.py                    # 命令行界面
│   ├── game_logic/               # 麻将逻辑
│   │   ├── tile.py               # 麻将牌定义
│   │   ├── hand.py               # 手牌管理
│   │   └── scoring/              # 计分系统
│   │       ├── yaku.py           # 役种识别
│   │       ├── fu.py             # 符数计算
│   │       └── score.py          # 点数计算
│   ├── efficiency/               # 牌效计算
│   │   ├── shanten.py            # 向听数
│   │   ├── ukeire.py             # 接受牌
│   │   └── analyzer.py           # 牌效分析
│   ├── recognition/              # 牌面识别
│   │   ├── detector.py           # YOLO 检测
│   │   ├── classifier.py         # 分类器
│   │   └── recognizer.py         # 识别器
│   ├── agent/                    # Agent 模块
│   │   └── validator.py          # 和牌验证器
│   ├── gui/                      # GUI 模块
│   │   ├── main_window.py        # 主窗口
│   │   ├── hand_panel.py         # 手牌输入
│   │   ├── result_panel.py       # 结果显示
│   │   ├── camera_panel.py       # 摄像头
│   │   └── widgets.py            # 自定义组件
│   └── utils/                    # 工具函数
│
├── scripts/                      # 脚本
│   ├── train_yolo.py             # YOLO 训练
│   ├── augment_dataset.py        # 数据增强
│   ├── majsoul_parser.py         # 雀魂记录解析
│   └── batch_test.py             # 批量测试
│
├── tests/                        # 测试
│   ├── test_scoring.py           # 计分测试
│   ├── test_yaku.py              # 役种测试
│   ├── test_validator.py         # 验证器测试
│   ├── test_system.py            # 系统集成测试
│   ├── test_gui.py               # GUI 测试
│   └── test_boundary.py          # 边界条件测试
│
└── docs/                         # 文档
    └── MAJSOUL_PARSER.md         # 雀魂记录解析文档
```

---

## 快速开始

### 环境准备

```bash
# 克隆项目
git clone https://github.com/2409324124/riichi-mahjong-recognition.git
cd riichi-mahjong-recognition

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_scoring.py -v

# 运行带覆盖率的测试
pytest --cov=src
```

### 使用示例

#### Python API

```python
from src.system import MahjongSystem

system = MahjongSystem()

# 分析手牌
result = system.analyze_hand(
    ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"]
)
print(f"向听数: {result.shanten.shanten}")

# 验证和牌
result = system.validate_win(
    tile_strings=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s"],
    winning_tile_str="3s",
    is_tsumo=True
)
print(f"有效: {result.is_valid}, 番数: {result.han}")

# 打牌推荐
result = system.get_discard_recommendation(
    ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1s", "1s", "1s", "2s", "3s"]
)
print(f"推荐打牌: {result['best_discard']}")
```

#### 命令行界面

```bash
# 分析手牌
python -m src.cli analyze 1m 2m 3m 4p 5p 6p 7s 8s 9s 1s 1s 1s 2s

# 验证和牌
python -m src.cli win 1m 2m 3m 4p 5p 6p 7s 8s 9s 1s 1s 1s 2s --win 3s --tsumo

# 打牌推荐
python -m src.cli recommend 1m 2m 3m 4p 5p 6p 7s 8s 9s 1s 1s 1s 2s 3s

# 启动 GUI
python -m src.gui
```

#### 雀魂记录解析

```bash
# 查询玩家记录
majsoul-query records "玩家名"

# 解析游戏记录
python scripts/majsoul_parser.py <uuid>

# 批量测试
python scripts/batch_test.py --player-id 68292379 --max-records 100
```

---

## 测试状态

**总计：120+ 个测试全部通过**

| 测试文件 | 测试数 | 说明 |
|----------|--------|------|
| test_scoring.py | 6 | 计分系统 |
| test_yaku.py | 38 | 役种识别 |
| test_validator.py | 16 | 和牌验证 |
| test_cross_validation.py | 15 | 交叉验证 |
| test_system.py | 13 | 系统集成 |
| test_gui.py | 9 | GUI |
| test_boundary.py | 23 | 边界条件 |

---

## 开发阶段

### ✅ 阶段1：项目初始化
- [x] 创建项目目录结构
- [x] 初始化 git 仓库
- [x] 创建 AGENT.md

### ✅ 阶段2：计分系统
- [x] 实现麻将牌定义（34种牌）
- [x] 实现手牌管理
- [x] 实现役种识别（38种役）
- [x] 实现符数计算
- [x] 实现点数计算
- [x] 编写单元测试

### ✅ 阶段3：牌面识别
- [x] 收集麻将牌图像数据集
- [x] 数据标注和预处理
- [x] 训练 YOLO 检测模型
- [x] 实现牌面分类器
- [x] 集成识别 pipeline

### ✅ 阶段4：牌效计算
- [x] 实现向听数计算
- [x] 实现接受牌计算
- [x] 实现牌效分析
- [x] 实现打牌推荐

### ✅ 阶段5：系统集成
- [x] 实现系统集成模块
- [x] 实现命令行界面
- [x] 实现 GUI 界面
- [x] 实现和牌验证器
- [x] 实现雀魂记录解析

---

## 已知问题

1. **honitsu（混一色）测试**：mahjong 包的 API 格式与我们不同，暂未交叉验证
2. **副露手牌验证**：需要将副露的牌加入 34 数组才能正确验证和牌形状
3. **雀魂记录解析**：hand 字段包含和牌，需要移除后才能验证
4. **手牌数量不匹配**：雀魂记录中 hand 字段可能不包含所有牌，导致验证失败

---

## 验收标准

### 计分系统
- ✅ 38 种役种全部实现
- ✅ 120 个测试全部通过

### 牌面识别
- ✅ YOLOv8 模型训练完成
- ✅ mAP50: 99.5%

### 雀魂记录解析
- ✅ 支持从玩家 ID 获取 UUID 列表
- ✅ 支持解析 protobuf 格式记录
- ✅ 支持红宝牌、副露格式
- 🔄 验证通过率 >= 95%（当前 81.2%）

---

## 参考资源

| 资源 | 链接 | 说明 |
|------|------|------|
| MahjongRepository/mahjong | https://github.com/MahjongRepository/mahjong | Python 麻将库 |
| EndlessCheng/mahjong-helper | https://github.com/EndlessCheng/mahjong-helper | 麻将助手 |
| shinkuan/Akagi | https://github.com/shinkuan/Akagi | 雀魂 AI 助手 |
| latorc/MahjongCopilot | https://github.com/latorc/MahjongCopilot | 麻将 Copilot |
| Ultralytics YOLOv8 | https://github.com/ultralytics/ultralytics | 目标检测框架 |

---

**最后更新**: 2026年6月16日
**版本**: v0.6.0
**测试状态**: 120+ passed