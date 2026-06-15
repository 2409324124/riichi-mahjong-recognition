# AGENT.md - 日本立直麻将识别系统

## 项目概述

自动识别真实麻将牌的系统，专注于日本立直麻将（Riichi Mahjong）规则。

**GitHub**: https://github.com/2409324124/riichi-mahjong-recognition

---

## 已完成的功能

### 1. 计分系统 ✅

| 模块 | 文件 | 说明 |
|------|------|------|
| 麻将牌定义 | `src/game_logic/tile.py` | 34种牌，34数组格式 |
| 手牌管理 | `src/game_logic/hand.py` | 手牌表示、副露管理、宝牌管理 |
| 役种识别 | `src/game_logic/scoring/yaku.py` | 38种役（含役满），500+行 |
| 符数计算 | `src/game_logic/scoring/fu.py` | 完整符数计算 |
| 点数计算 | `src/game_logic/scoring/score.py` | 番数→符数→点数→支付 |

**支持的役种**（38种）：
- 1番：立直、一发、门前清自摸和、断幺九、平和、一杯口、役牌
- 2番：三色同刻、三杠子、对对和、三暗刻、小三元、混老头、七对子、三色同顺、一气通贯、混全带幺九
- 3番：混一色、纯全带幺九、二杯口
- 6番：清一色
- 役满：国士无双、九莲宝灯、四暗刻、大三元、小四喜、大四喜、字一色、绿一色、清老头、四杠子、天和、地和
- 双倍役满：国士无双十三面、纯正九莲宝灯、四暗刻单骑

### 2. 牌效计算 ✅

| 模块 | 文件 | 说明 |
|------|------|------|
| 向听数计算 | `src/efficiency/shanten.py` | 支持普通手、七对子、国士无双 |
| 接受牌计算 | `src/efficiency/ukeire.py` | 有效牌数量、听牌类型 |
| 牌效分析 | `src/efficiency/analyzer.py` | 打牌推荐、牌效率评估 |

### 3. 牌面识别 ✅ (YOLO模型)

| 模块 | 文件 | 说明 |
|------|------|------|
| 检测器 | `src/recognition/detector.py` | YOLOv8 目标检测 |
| 分类器 | `src/recognition/classifier.py` | 牌面分类 |
| 识别器 | `src/recognition/recognizer.py` | 整合检测和分类 |

**训练结果**：
- 模型：YOLOv8n
- 数据集：5000张合成图片（数据增强）
- mAP50：99.5%
- 推理速度：~20ms/张
- 模型文件：`runs/detect/runs/train/mahjong_detection-4/weights/best.pt`

### 4. 和牌验证器 ✅

| 模块 | 文件 | 说明 |
|------|------|------|
| 和牌验证 | `src/agent/validator.py` | 验证和牌合法性，防止诈和 |

**验证内容**：
- 牌数检查（手牌+副露=13张）
- 和牌形状检查（4面子+1雀头、七对子、国士无双）
- 役种检查（至少1个役）
- 振听检查

### 5. 雀魂游戏记录解析器 ✅

| 模块 | 文件 | 说明 |
|------|------|------|
| 解析器 | `scripts/majsoul_parser.py` | 解析雀魂 protobuf 格式记录 |

**使用方式**：
```python
python scripts/majsoul_parser.py 0000034c-a2a9-4dfa-ae63-bd81aa25ebad
```

**已验证**：使用 UUID `0000034c-a2a9-4dfa-ae63-bd81aa25ebad` 验证 4 个和牌事件全部成功。

---

## 测试状态

**总计：75 个测试全部通过**

| 测试文件 | 测试数 | 说明 |
|----------|--------|------|
| `tests/test_scoring.py` | 6 | 计分系统基础测试 |
| `tests/test_yaku.py` | 38 | 所有役种测试 |
| `tests/test_validator.py` | 16 | 和牌验证器测试 |
| `tests/test_cross_validation.py` | 15 | 与 mahjong 包交叉验证 |

---

## 项目结构

```
riichi-mahjong-recognition/
├── AGENT.md                        # 本文件
├── README.md                       # 项目说明
├── pyproject.toml                  # 项目配置
├── requirements.txt                # Python 依赖
├── requirements-train.txt          # 训练依赖
├── Dockerfile                      # Docker 配置
├── docker-compose.yml              # Docker Compose
├── .gitignore
│
├── src/                            # 源代码
│   ├── game_logic/                 # 麻将逻辑
│   │   ├── tile.py                 # 麻将牌定义
│   │   ├── hand.py                 # 手牌管理
│   │   └── scoring/                # 计分系统
│   │       ├── yaku.py             # 役种识别
│   │       ├── fu.py               # 符数计算
│   │       └── score.py            # 点数计算
│   ├── efficiency/                 # 牌效计算
│   │   ├── shanten.py              # 向听数
│   │   ├── ukeire.py               # 接受牌
│   │   └── analyzer.py             # 牌效分析
│   ├── recognition/                # 牌面识别
│   │   ├── detector.py             # YOLO 检测
│   │   ├── classifier.py           # 分类器
│   │   └── recognizer.py           # 识别器
│   ├── agent/                      # Agent 模块
│   │   └── validator.py            # 和牌验证器
│   └── utils/                      # 工具函数
│
├── scripts/                        # 脚本
│   ├── train_yolo.py               # YOLO 训练
│   ├── augment_dataset.py          # 数据增强
│   ├── merge_datasets.py           # 数据集合并
│   ├── majsoul_parser.py           # 雀魂记录解析
│   ├── mjai_parser.py              # mjai 格式解析
│   └── fetch_majsoul_records.py    # 获取雀魂记录
│
├── tests/                          # 测试
│   ├── test_scoring.py             # 计分测试
│   ├── test_yaku.py                # 役种测试
│   ├── test_validator.py           # 验证器测试
│   └── test_cross_validation.py    # 交叉验证
│
├── data/                           # 数据（不提交到 git）
│   ├── merged_dataset/             # 合并数据集
│   ├── synthetic_dataset/          # 合成数据集
│   └── yolo_dataset_final/         # YOLO 训练数据
│
└── runs/                           # 训练输出（不提交到 git）
    └── detect/runs/train/
        └── mahjong_detection-4/    # 最新训练结果
            └── weights/
                ├── best.pt         # 最佳模型
                └── last.pt         # 最后模型
```

---

## 环境配置

```bash
# 克隆项目
git clone https://github.com/2409324124/riichi-mahjong-recognition.git
cd riichi-mahjong-recognition

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 mahjong 包（用于交叉验证）
pip install mahjong

# 运行测试
pytest tests/ -v
```

---

## 关键设计决策

### 牌的表示
- **34数组格式**：长度34的数组，每个位置代表一种牌的数量
  - 索引 0-8：万子 1-9
  - 索引 9-17：筒子 1-9
  - 索引 18-26：索子 1-9
  - 索引 27-30：风牌（东南西北）
  - 索引 31-33：三元牌（白发中）

### 和牌验证
- 手牌 + 副露 = 13 张（不含和牌）
- 和牌后 = 14 张
- 支持副露（吃、碰、杠）

### 雀魂记录解析
- UUID 格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- 记录服务器：`https://record-v2.maj-soul.com:5333/majsoul/game_record/<uuid>`
- 使用 protobuf 解析（`mahjong_soul_api` 包）

---

## 待完成

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 系统集成 | 高 | 将三个模块集成到一个完整流程 |
| 命令行界面 | 中 | 创建 CLI 工具 |
| 摄像头实时识别 | 中 | 实时识别真实麻将牌 |
| GUI 界面 | 低 | 图形用户界面 |

---

## 已知问题

1. **honitsu（混一色）测试**：mahjong 包的 API 格式与我们不同，暂未交叉验证
2. **副露手牌验证**：需要将副露的牌加入 34 数组才能正确验证和牌形状
3. **双倍役满**：国士无双十三面、纯正九莲宝灯、四暗刻单骑的判断逻辑需要进一步验证

---

## 参考资源

| 资源 | 链接 | 说明 |
|------|------|------|
| MahjongRepository/mahjong | https://github.com/MahjongRepository/mahjong | Python 麻将库，26M+ 手牌验证 |
| EndlessCheng/mahjong-helper | https://github.com/EndlessCheng/mahjong-helper | 麻将助手 |
| shinkuan/Akagi | https://github.com/shinkuan/Akagi | 雀魂 AI 助手 |
| latorc/MahjongCopilot | https://github.com/latorc/MahjongCopilot | 麻将 Copilot |

---

**最后更新**：2026年6月15日
**版本**：v0.2.0
**测试状态**：75 passed