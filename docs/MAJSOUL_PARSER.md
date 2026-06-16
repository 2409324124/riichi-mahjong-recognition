# 雀魂游戏记录解析器

**文件**: `scripts/majsoul_parser.py`

用于从雀魂服务器获取游戏记录（protobuf 格式），解析为可读的事件流，并验证和牌的合法性。

---

## 架构

```
玩家ID/UUID → 雀魂记录服务器 → Protobuf 二进制 → 解析事件流 → 验证和牌
```

### 核心类

**MajsoulRecordParser** (`scripts/majsoul_parser.py`)

| 方法 | 说明 |
|------|------|
| `fetch_uuid_list(list_id)` | 从文件列表 ID 获取 UUID 列表 |
| `fetch_record(game_uuid)` | 从服务器获取原始 protobuf 数据 |
| `parse(data)` | 解析 protobuf 为事件列表 |
| `parse_by_id(game_uuid)` | 获取并解析（组合方法） |
| `parse_from_file(filepath)` | 从本地文件解析 |
| `validate_hora(hule_data)` | 验证和牌事件 |
| `convert_tile(tile_str)` | 雀魂牌格式转内部格式 |
| `parse_ming(ming_str)` | 解析副露格式 |

---

## 获取游戏记录

### 方式一：通过玩家 ID 获取 UUID 列表

雀魂记录服务器有一个"文件列表"接口，传入玩家 ID 可返回该玩家的所有游戏记录 UUID。

```python
from scripts.majsoul_parser import MajsoulRecordParser

parser = MajsoulRecordParser()

# 玩家 ID（纯数字，如 68292379）
player_id = "68292379"

# 获取该玩家的所有游戏 UUID
uuids = parser.fetch_uuid_list(player_id)
print(f"找到 {len(uuids)} 条记录")
# 输出: 找到 100 条记录
```

**原理**：请求 `https://record-v2.maj-soul.com:5333/majsoul/game_record/{player_id}` 返回 XML 文件列表，从 XML 中提取 UUID。

### 方式二：通过 majsoul-query 工具

```bash
# 安装
pip install git+https://github.com/ssttkkl/majsoul-query-skill.git

# 查询玩家信息
majsoul-query info "玩家昵称"

# 查询玩家游戏记录（返回 paipu 链接）
majsoul-query records "玩家昵称"
```

输出示例：
```
[#1]  [杰1]董728    41700  (+112)
#2  [杰1]五月七日ゆり    31600  (+52)
...
房间：四麻金南
时间：2026/05/23 21:29
https://game.maj-soul.net/1/?paipu=260523-372a5e0d-8aa9-4af1-bf99-9498d066c896_a40365570
```

从链接中提取 paipu UUID（`_` 前面的部分）。

### 方式三：从雀魂游戏客户端

在游戏内查看记录时，分享链接中包含 paipu UUID：
```
https://game.maj-soul.com/1/?paipu=260523-372a5e0d-8aa9-4af1-bf99-9498d066c896_a40365570
```

---

## 解析记录

### Protobuf 格式

雀魂游戏记录使用 protobuf 编码，外层是 `Wrapper`，内层是 `GameDetailRecords`，包含一系列事件：

```
Wrapper (name=".lq.GameDetailRecords")
└── GameDetailRecords
    ├── RecordNewRound    # 新局开始（初始手牌、宝牌、分数）
    ├── RecordDealTile    # 摸牌
    ├── RecordDiscardTile # 打牌
    ├── RecordChiPengGang # 吃/碰/杠
    ├── RecordAnGangAddGang # 暗杠/加杠
    ├── RecordHule        # 和牌（重点）
    ├── RecordNoTile      # 流局
    └── RecordLiuJu       # 途中流局
```

### 使用方法

```python
from scripts.majsoul_parser import MajsoulRecordParser

parser = MajsoulRecordParser()

# 获取并解析
uuid = "0000034c-a2a9-4dfa-ae63-bd81aa25ebad"
records = parser.parse_by_id(uuid)

# 遍历事件
for record in records:
    print(f"{record['name']}")
```

输出示例：
```
RecordNewRound
RecordDiscardTile
RecordDealTile
RecordDiscardTile
...
RecordHule
RecordNoTile
```

---

## 牌格式转换

### 雀魂格式 vs 内部格式

| 雀魂格式 | 含义 | 内部格式 |
|----------|------|----------|
| `1m` - `9m` | 万子 1-9 | `Tile.from_string("1m")` |
| `1p` - `9p` | 筒子 1-9 | `Tile.from_string("1p")` |
| `1s` - `9s` | 索子 1-9 | `Tile.from_string("1s")` |
| `1z` - `4z` | 风牌（东南西北） | `Tile.from_string("东")` |
| `5z` - `7z` | 三元牌（白发中） | `Tile.from_string("白")` |
| `0M` / `0P` / `0S` | 红宝牌（赤5） | `Tile.from_string("5m")` |

### 红宝牌处理

雀魂用 `0` 表示红宝牌（赤ドラ）：

```python
# 红5万
parser.convert_tile("0M")  # → Tile(5m)

# 红5筒
parser.convert_tile("0P")  # → Tile(5p)

# 红5索
parser.convert_tile("0S")  # → Tile(5s)
```

### 副露格式

副露在记录中以字符串格式存储：

| 格式 | 示例 | 说明 |
|------|------|------|
| `kezi(a,b,c)` | `kezi(5z,5z,5z)` | 刻子（碰/暗杠） |
| `shunzi(a,b,c)` | `shunzi(1s,3s,2s)` | 顺子（吃） |
| `gangzi(a,b,c,d)` | `gangzi(5z,5z,5z,5z)` | 杠子 |

```python
tiles = parser.parse_ming("kezi(5z,5z,5z)")
# 返回: ['5z', '5z', '5z']
```

---

## 验证和牌

### HuleInfo 结构

RecordHule 包含 `HuleInfo`，结构如下：

```python
HuleInfo:
    hand: List[str]       # 门前清手牌（不含副露）
    ming: List[str]       # 副露（格式如 "kezi(5z,5z,5z)"）
    hu_tile: str          # 和的牌
    seat: int             # 座位
    zimo: bool            # 是否自摸
    qinjia: bool          # 是否亲家（庄家）
    liqi: bool            # 是否立直
    doras: List[str]      # 宝牌
    li_doras: List[str]   # 里宝牌
    fans: List[FanInfo]   # 役种列表（雀魂原始）
    fu: int               # 符数
    point_rong: int       # 荣和点数
    point_zimo_qin: int   # 自摸庄家支付
    point_zimo_xian: int  # 自摸闲家支付
```

### 验证方法

```python
from scripts.majsoul_parser import MajsoulRecordParser

parser = MajsoulRecordParser()
records = parser.parse_by_id("0000034c-a2a9-4dfa-ae63-bd81aa25ebad")

# 找到和牌事件
for record in records:
    if record['name'] == 'RecordHule':
        hule_data = record['data']
        
        # 验证和牌
        results = parser.validate_hora(hule_data)
        
        for result in results:
            print(f"座位: {result['seat']}")
            print(f"自摸: {result['zimo']}")
            print(f"手牌: {[str(t) for t in result['hand']]}")
            print(f"副露: {len(result['melds'])} 组")
            print(f"和牌: {result['winning_tile']}")
            print(f"验证: {'通过' if result['is_valid'] else '失败'}")
            
            if result['is_valid']:
                print(f"番数: {result['han']}")
                print(f"符数: {result['fu']}")
                print(f"点数: {result['points']}")
                print(f"役种: {result['yaku_list']}")
```

### 验证流程

```
HuleInfo
├── 1. 提取门前清手牌 (hand)
├── 2. 解析副露 (ming)
│   ├── kezi() → 刻子
│   ├── shunzi() → 顺子
│   └── gangzi() → 杠子
├── 3. 合并手牌 + 副露
├── 4. 转换牌格式（处理红宝牌）
├── 5. 调用 WinValidator.validate()
│   ├── 牌数检查 (手牌+副露 = 13张)
│   ├── 和牌形状检查 (4面子+1雀头/七对子/国士无双)
│   ├── 役种检查 (至少1个役)
│   └── 振听检查
└── 6. 返回验证结果
```

### 验证结果

```python
{
    "seat": 3,              # 座位
    "zimo": False,          # 是否自摸
    "hand": [Tile, ...],    # 门前清手牌
    "melds": [[Tile], ...], # 副露
    "winning_tile": Tile,   # 和牌
    "is_valid": True,       # 是否有效
    "han": 4,               # 番数
    "fu": 30,               # 符数
    "points": 1920,         # 点数
    "yaku_list": ["对对和", "混全带幺九"],  # 役种
    "original_fans": [...], # 雀魂原始役种
    "original_fu": 30       # 雀魂原始符数
}
```

---

## 边界条件

### 1. 红宝牌（赤ドラ）

雀魂用 `0M`/`0P`/`0S` 表示红宝牌，需要转换为 `5m`/`5p`/`5s`：

```python
parser.convert_tile("0M")  # → Tile(5m)
parser.convert_tile("0P")  # → Tile(5p)
parser.convert_tile("0S")  # → Tile(5s)
```

### 2. 副露手牌验证

副露后，门前清手牌数量会减少：
- 无副露：门前 13 张
- 1 组副露：门前 10 张
- 2 组副露：门前 7 张
- 3 组副露：门前 4 张
- 4 组副露：门前 1 张

验证时需要将副露牌加入 34 数组才能正确检查和牌形状。

### 3. 振听

振听禁止荣和（只能自摸）。需要检查：
- 自己的牌河中是否有和牌
- 是否放过和牌（临时振听）
- 立直后是否放过和牌（永久振听）

### 4. 无役和牌

即使手牌形状正确，没有役也不能和牌。常见情况：
- 副露后无役（需要至少一个役）
- 断幺九需要所有牌都是中张

### 5. 验证失败的常见原因

| 原因 | 说明 |
|------|------|
| 手牌数量错误 | 门前清 + 副露 != 13 张 |
| 和牌形状错误 | 不满足 4面子+1雀头 |
| 无役 | 没有满足条件的役种 |
| 振听 | 牌河中有和牌 |
| 牌数超过 4 | 同一种牌超过 4 张 |

---

## 实际验证结果

使用玩家 ID `68292379` 测试：

```
测试结果:
  成功: 10/10 记录
  总和牌: 53 个
  有效和牌: 45 个
  验证率: 84.9%
```

验证失败的 8 个和牌主要是因为：
- 副露后的役种识别不完善（三色同顺、一气通贯副露后）
- 部分特殊牌型未覆盖

---

## 使用示例

### 完整示例：查询玩家并验证所有和牌

```python
import sys
sys.path.insert(0, '.')
from scripts.majsoul_parser import MajsoulRecordParser

parser = MajsoulRecordParser()

# 1. 获取玩家的游戏记录 UUID
player_id = "68292379"
uuids = parser.fetch_uuid_list(player_id)
print(f"找到 {len(uuids)} 条记录")

# 2. 遍历每条记录
for i, uuid in enumerate(uuids[:5]):
    print(f"\n[{i+1}] UUID: {uuid}")
    
    try:
        records = parser.parse_by_id(uuid)
        print(f"  解析成功，共 {len(records)} 条记录")
        
        # 3. 找到和牌事件
        hora_records = [r for r in records if r['name'] == 'RecordHule']
        print(f"  和牌事件: {len(hora_records)} 个")
        
        # 4. 验证每个和牌
        for j, record in enumerate(hora_records):
            data = record['data']
            results = parser.validate_hora(data)
            
            for k, result in enumerate(results):
                print(f"    [{j}][{k}] seat={result['seat']}, zimo={result['zimo']}")
                
                if result['is_valid']:
                    print(f"      番数: {result['han']}, 点数: {result['points']}")
                    print(f"      役种: {result['yaku_list']}")
                else:
                    print(f"      失败: {result.get('error', '未知')}")
    
    except Exception as e:
        print(f"  失败: {e}")
```

### 命令行使用

```bash
# 直接解析单条记录
python scripts/majsoul_parser.py 0000034c-a2a9-4dfa-ae63-bd81aa25ebad
```

输出：
```
获取游戏记录: 0000034c-a2a9-4dfa-ae63-bd81aa25ebad
解析成功，共 340 条记录
和牌事件: 4 个

[0][0] 和牌验证:
  座位: 3, 自摸: False
  手牌: [6m, 7m, 8m, 9p, 9p, 6s, 6s, 6s, 9s, 9s]
  副露: 1 组
  和牌: 9s
  验证: True
  番数: 3, 符数: 30, 点数: 960
  役种: ['役牌：三元牌', '混全带幺九']
```

---

## 相关资源

| 资源 | 链接 | 说明 |
|------|------|------|
| mjsoul | https://github.com/takayama-lily/mjsoul | 雀魂通信客户端（JS） |
| mahjong_soul_api | https://github.com/MahjongRepository/mahjong_soul_api | Python protobuf 封装 |
| majsoul-query | https://github.com/ssttkkl/majsoul-query-skill | CLI 查询工具 |
| amae-koromo | https://amae-koromo.sapk.ch | 雀魂牌谱屋 |
| liqi.proto | 雀魂客户端资源 | protobuf 定义文件 |

---

## 已知问题

### 1. hand 字段包含和牌

雀魂记录中 `HuleInfo.hand` 字段**包含和牌**，验证前需要移除：

```python
# 移除和牌
if winning_tile in hand_tiles:
    hand_tiles.remove(winning_tile)
```

### 2. 手牌数量不匹配

移除和牌后，手牌+副露可能不等于 13 张。原因：

| 场景 | 期望 | 实际 | 原因 |
|------|------|------|------|
| 荣和（有副露） | 13 张 | 12 张 | hand 字段可能不包含所有牌 |
| 自摸（有副露） | 13 张 | 12 张 | 同上 |

**当前处理**：记录差异但不阻止验证。

### 3. 副露格式不统一

副露有多种格式：
- `kezi(5z,5z,5z)` - 刻子
- `shunzi(1s,3s,2s)` - 顺子
- `1m|1m|1m|1m` - 杠子（`|` 分隔）

**当前处理**：`parse_ming()` 支持所有格式。

### 4. 红宝牌格式

雀魂用 `0M`/`0P`/`0S` 表示红宝牌，需要转换为 `5m`/`5p`/`5s`。

**当前处理**：`convert_tile()` 自动转换。

---

## 批量测试脚本

**文件**：`scripts/batch_test.py`

**功能**：
- 多线程批量获取和解析游戏记录
- 统计验证通过率
- 分析失败原因
- 输出役种统计和番数分布

**使用方法**：

```bash
# 运行批量测试
python scripts/batch_test.py \
  --player-id 68292379 \
  --max-records 100 \
  --workers 4 \
  --output data/batch_test_results.json
```

**输出示例**：

```
测试结果
============================================================
测试记录数: 100
  成功解析: 100
  解析失败: 0
和牌事件数: 605
有效和牌数: 491
验证通过率: 81.2%

验证失败原因分析
============================================================
  [  99] 手牌+副露不是13张（当前手牌12张 + 副露0张 = 12张）
  [  59] 手牌+副露不是13张（当前手牌9张 + 副露3张 = 12张）
  ...

役种统计 (有效和牌)
============================================================
  [ 187] 平和
  [ 112] 纯全带幺九
  [  83] 混全带幺九
  ...
```

**验收标准**：

| 条件 | 标准 |
|------|------|
| 测试记录数 | >= 100 条 |
| 和牌事件数 | >= 500 个 |
| 验证通过率 | >= 95% |
| 边界条件覆盖 | 红宝牌、副露、振听、无役 |