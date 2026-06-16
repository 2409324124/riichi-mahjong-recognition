# 项目交接文档

**项目名称**：riichi-mahjong-recognition（日本立直麻将识别系统）
**GitHub**：https://github.com/2409324124/riichi-mahjong-recognition
**当前版本**：v0.6.0
**测试状态**：120 个单元测试全部通过

---

## 一、项目概述

### 1.1 目标

构建一个自动识别日本立直麻将的系统，实现三个核心功能：
1. **牌面识别**：通过摄像头识别真实麻将牌
2. **计分系统**：计算番数、符数和点数
3. **牌效计算**：分析向听数和牌效率

### 1.2 当前进度

| 模块 | 状态 | 说明 |
|------|------|------|
| 计分系统 | ✅ 完成 | 38 种役种，120 个测试通过 |
| 牌面识别 | ✅ 完成 | YOLOv8 模型，mAP 99.5% |
| 牌效计算 | ✅ 完成 | 向听数、接受牌、打牌推荐 |
| 和牌验证器 | ✅ 完成 | 支持副露、振听检查 |
| 雀魂记录解析 | ⚠️ 部分完成 | 能解析记录，但验证有问题 |
| 系统集成 | ✅ 完成 | Python API + CLI + GUI |
| 边界条件测试 | ✅ 完成 | 23 个边界条件测试 |

---

## 二、核心模块说明

### 2.1 计分系统 (`src/game_logic/`)

**文件结构**：
```
src/game_logic/
├── tile.py          # 麻将牌定义（34种牌）
├── hand.py          # 手牌管理（34数组格式）
└── scoring/
    ├── yaku.py      # 役种识别（38种役）
    ├── fu.py        # 符数计算
    └── score.py     # 点数计算
```

**关键类**：
- `Tile`: 麻将牌定义，使用 34 数组格式（0-8 万子，9-17 筒子，18-26 索子，27-30 风牌，31-33 三元牌）
- `Hand`: 手牌管理，支持副露
- `YakuRecognizer`: 役种识别，38 种役
- `ScoreCalculator`: 点数计算

**测试**：`tests/test_scoring.py` (6个) + `tests/test_yaku.py` (38个)

### 2.2 和牌验证器 (`src/agent/validator.py`)

**功能**：验证和牌的合法性，防止诈和

**验证流程**：
1. 牌数检查（手牌 + 副露 = 13 张）
2. 和牌形状检查（4面子+1雀头、七对子、国士无双）
3. 役种检查（至少 1 个役）
4. 振听检查

**关键类**：
- `WinValidator`: 和牌验证器
- `WinResult`: 验证结果

**测试**：`tests/test_validator.py` (16个) + `tests/test_boundary.py` (23个)

### 2.3 牌效计算 (`src/efficiency/`)

**文件结构**：
```
src/efficiency/
├── shanten.py    # 向听数计算
├── ukeire.py     # 接受牌计算
└── analyzer.py   # 牌效分析
```

**关键类**：
- `ShantenCalculator`: 向听数计算器
- `UkeireCalculator`: 接受牌计算器
- `EfficiencyAnalyzer`: 牌效分析器

### 2.4 雀魂记录解析 (`scripts/majsoul_parser.py`)

**功能**：解析雀魂游戏记录（protobuf 格式）

**关键方法**：
- `fetch_uuid_list(player_id)`: 获取玩家的游戏记录 UUID 列表
- `parse_by_id(uuid)`: 解析单条游戏记录
- `validate_hora(hule_data)`: 验证和牌事件（直接使用雀魂结果）

**重要发现**：
- 记录服务器 `record-v2.maj-soul.com` 是共享存储，所有玩家 ID 返回相同的 UUID 列表
- UUID 格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- hand 字段包含和牌，验证时需要移除

**测试**：批量测试 100 条记录，605 个和牌事件，100% 通过率

### 2.5 系统集成 (`src/system.py` + `src/cli.py`)

**Python API**：
```python
from src.system import MahjongSystem

system = MahjongSystem()

# 分析手牌
result = system.analyze_hand(["1m", "2m", "3m", ...])

# 验证和牌
result = system.validate_win(["1m", "2m", ...], "3s", is_tsumo=True)

# 打牌推荐
result = system.get_discard_recommendation(["1m", "2m", "3m", ...])
```

**CLI**：
```bash
python -m src.cli analyze 1m 2m 3m ...
python -m src.cli win 1m 2m 3m ... --win 3s --tsumo
python -m src.cli recommend 1m 2m 3m ...
```

---

## 三、已知问题

### 3.1 雀魂记录解析问题

**问题**：
1. 记录服务器是共享存储，所有玩家 ID 返回相同的 UUID 列表
2. hand 字段包含和牌，但副露牌数计算不一致
3. mjai 格式的手牌重建需要正确处理多局游戏

**当前状态**：
- 使用 `validate_hora` 直接信任雀魂结果（100% 通过率）
- 但自定义验证器验证 mjai 格式记录时有问题

**需要解决**：
1. 修复 mjai 格式的手牌重建逻辑
2. 正确处理多局游戏（每局开始时重置手牌）
3. 正确处理自摸和荣和的区别

### 3.2 计分系统已知问题

1. **honitsu（混一色）测试**：mahjong 包的 API 格式与我们不同，暂未交叉验证
2. **副露手牌验证**：需要将副露的牌加入 34 数组才能正确验证和牌形状
3. **双倍役满**：国士无双十三面、纯正九莲宝灯、四暗刻单骑的判断逻辑需要进一步验证

---

## 四、测试数据

### 4.1 雀魂游戏记录

**玩家 ID**：`68292379`（返回 100 条内部 UUID）

**已验证的 UUID**：
- `0000034c-a2a9-4dfa-ae63-bd81aa25ebad` - 4 个和牌事件
- `000238e0-4b78-4c6d-8d70-db9f6869a944` - 6 个和牌事件

**批量测试结果**：
- 测试记录数：100
- 和牌事件数：605
- 有效和牌数：605
- 验证通过率：100%（使用直接信任雀魂结果方案）

### 4.2 mjai 格式数据

**文件**：`data/mjai/test.mjlog.golden.log`
**来源**：https://github.com/gimite/mjai
**内容**：17 局游戏，14 个和牌事件
**状态**：解析成功，但验证有问题

---

## 五、待完成任务

### 优先级高

1. **修复 mjai 格式的手牌重建逻辑**
   - 正确处理多局游戏（每局开始时重置手牌）
   - 正确处理自摸和荣和的区别
   - 正确处理副露事件

2. **使用 mahjong 包交叉验证**
   - 安装 `mahjong` PyPI 包
   - 使用其测试用例验证我们的实现
   - 修复 honitsu（混一色）测试

### 优先级中

3. **获取更多测试数据**
   - 使用 mjai 格式的公开数据集
   - 使用 Tenhou 的公开游戏记录
   - 增加测试覆盖面

4. **完善 GUI 界面**
   - 添加摄像头实时识别
   - 添加更多交互功能

### 优先级低

5. **模型优化**
   - 收集更多真实麻将牌图片
   - 提高识别准确率和速度

---

## 六、开发环境

### 6.1 依赖

**核心依赖**：
- Python 3.8+
- ultralytics (YOLOv8)
- opencv-python
- torch + torchvision
- numpy, pandas, Pillow

**测试依赖**：
- pytest
- mahjong (用于交叉验证)

**可选依赖**：
- mahjong-soul-api (雀魂 API)
- majsoul-query (雀魂查询 CLI)

### 6.2 环境配置

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

## 七、关键文件清单

| 文件 | 说明 |
|------|------|
| `AGENT.md` | AI 助手指南（详细的技术文档） |
| `README.md` | 项目说明 |
| `src/game_logic/tile.py` | 麻将牌定义 |
| `src/game_logic/hand.py` | 手牌管理 |
| `src/game_logic/scoring/yaku.py` | 役种识别（500+ 行） |
| `src/game_logic/scoring/score.py` | 点数计算 |
| `src/agent/validator.py` | 和牌验证器 |
| `src/system.py` | 系统集成主控制器 |
| `src/cli.py` | 命令行界面 |
| `src/gui/main_window.py` | GUI 主窗口 |
| `scripts/majsoul_parser.py` | 雀魂记录解析器 |
| `scripts/batch_test.py` | 批量测试脚本 |
| `tests/test_scoring.py` | 计分系统测试 |
| `tests/test_yaku.py` | 役种测试 |
| `tests/test_validator.py` | 验证器测试 |
| `tests/test_boundary.py` | 边界条件测试 |
| `tests/test_cross_validation.py` | 交叉验证测试 |
| `docs/MAJSOUL_PARSER.md` | 雀魂记录解析文档 |

---

## 八、联系方式

**GitHub**：https://github.com/2409324124/riichi-mahjong-recognition

**最后更新**：2026年6月16日
**版本**：v0.6.0