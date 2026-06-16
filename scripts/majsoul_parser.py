"""
雀魂游戏记录解析器

解析雀魂（Majsoul）的游戏记录（paipu），用于验证麻将逻辑。
"""

import urllib.request
from typing import List, Dict, Optional, Tuple
import ms.protocol_pb2 as pb

from src.game_logic.tile import Tile
from src.game_logic.hand import Hand


class MajsoulRecordParser:
    """雀魂游戏记录解析器"""
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    def fetch_record(self, game_uuid: str) -> bytes:
        """
        从雀魂服务器获取游戏记录
        
        Args:
            game_uuid: 游戏记录 UUID（支持纯 UUID 或列表 ID）
        
        Returns:
            原始二进制数据
        """
        url = f"https://record-v2.maj-soul.com:5333/majsoul/game_record/{game_uuid}"
        response = urllib.request.urlopen(url, timeout=30)
        return response.read()
    
    def fetch_uuid_list(self, list_id: str) -> list:
        """
        从文件列表获取 UUID 列表
        
        Args:
            list_id: 列表 ID（如 68292379）
        
        Returns:
            UUID 列表
        """
        import re
        
        data = self.fetch_record(list_id)
        text = data.decode('utf-8')
        
        # 提取 UUID
        pattern = r'game_record/v0/([0-9a-f-]+)'
        uuids = re.findall(pattern, text)
        
        return uuids
    
    def parse(self, data: bytes) -> list:
        """
        解析游戏记录
        
        Args:
            data: 原始二进制数据
        
        Returns:
            解析后的记录列表
        """
        # 解析外层 Wrapper
        wrapper = pb.Wrapper()
        wrapper.ParseFromString(data)
        
        # 解析 GameDetailRecords
        game_details = pb.GameDetailRecords()
        game_details.ParseFromString(wrapper.data)
        
        # 解析每条记录
        records = []
        for record_wrapper_data in game_details.records:
            record_wrapper = pb.Wrapper()
            record_wrapper.ParseFromString(record_wrapper_data)
            
            # 获取消息类型和数据
            name = record_wrapper.name
            if name.startswith(".lq."):
                name = name[4:]  # 去掉 ".lq." 前缀
            
            # 解析具体消息
            try:
                msg_type = getattr(pb, name, None)
                if msg_type:
                    msg = msg_type()
                    msg.ParseFromString(record_wrapper.data)
                    records.append({
                        "name": name,
                        "data": msg
                    })
            except Exception as e:
                print(f"解析记录失败: {name}, 错误: {e}")
                records.append({
                    "name": name,
                    "data": None,
                    "error": str(e)
                })
        
        return records
    
    def parse_by_id(self, game_uuid: str) -> list:
        """
        通过 UUID 获取并解析游戏记录
        
        Args:
            game_uuid: 游戏记录 UUID
        
        Returns:
            解析后的记录列表
        """
        data = self.fetch_record(game_uuid)
        return self.parse(data)
    
    def parse_from_file(self, filepath: str) -> list:
        """
        从文件解析游戏记录
        
        Args:
            filepath: 文件路径
        
        Returns:
            解析后的记录列表
        """
        with open(filepath, "rb") as f:
            data = f.read()
        return self.parse(data)
    
    def extract_game_state(self, records: list) -> dict:
        """
        从记录中提取游戏状态
        
        Args:
            records: 解析后的记录列表
        
        Returns:
            游戏状态字典
        """
        state = {
            "rounds": [],
            "current_round": None
        }
        
        for record in records:
            name = record["name"]
            data = record["data"]
            
            if name == "RecordNewRound":
                # 新局开始
                round_info = {
                    "chang": data.chang,
                    "ju": data.ju,
                    "ben": data.ben,
                    "dora": data.dora,
                    "scores": list(data.scores),
                    "hands": [
                        list(data.tiles0),
                        list(data.tiles1),
                        list(data.tiles2),
                        list(data.tiles3)
                    ],
                    "actions": []
                }
                state["current_round"] = round_info
                state["rounds"].append(round_info)
            
            elif name == "RecordDealTile":
                # 摸牌
                if state["current_round"]:
                    state["current_round"]["actions"].append({
                        "type": "deal_tile",
                        "seat": data.seat,
                        "tile": data.tile
                    })
            
            elif name == "RecordDiscardTile":
                # 打牌
                if state["current_round"]:
                    state["current_round"]["actions"].append({
                        "type": "discard_tile",
                        "seat": data.seat,
                        "tile": data.tile,
                        "is_liqi": data.is_liqi,
                        "moqie": data.moqie
                    })
            
            elif name == "RecordHule":
                # 和牌
                if state["current_round"]:
                    state["current_round"]["actions"].append({
                        "type": "hule",
                        "hules": self._extract_hule_info(data)
                    })
            
            elif name == "RecordNoTile":
                # 流局
                if state["current_round"]:
                    state["current_round"]["actions"].append({
                        "type": "no_tile"
                    })
        
        return state
    
    def _extract_hule_info(self, hule_data) -> list:
        """提取和牌信息"""
        hules = []
        for hule in hule_data.hules:
            info = {
                "seat": hule.seat,
                "zimo": hule.zimo,
                "qinjia": hule.qinjia,
                "hand": list(hule.hand),
                "hu_tile": hule.hu_tile,
                "ming": list(hule.ming),
                "doras": list(hule.doras),
                "li_doras": list(hule.li_doras),
                "fans": [],
                "fu": hule.fu,
                "point_rong": hule.point_rong,
                "point_zimo_qin": hule.point_zimo_qin,
                "point_zimo_xian": hule.point_zimo_xian,
                "count": hule.count
            }
            for fan in hule.fans:
                info["fans"].append({
                    "name": fan.name,
                    "val": fan.val,
                    "id": fan.id
                })
            hules.append(info)
        return hules
    
    def parse_ming(self, ming_str: str) -> List[str]:
        """
        解析副露格式
        
        Args:
            ming_str: 副露字符串，如 "kezi(5z,5z,5z)" 或 "shunzi(1s,3s,2s)"
        
        Returns:
            牌字符串列表
        """
        import re
        
        # 解析 kezi(5z,5z,5z) -> ['5z', '5z', '5z']
        kezi_match = re.match(r'kezi\(([^)]+)\)', ming_str)
        if kezi_match:
            tiles = kezi_match.group(1).split(',')
            return [t.strip() for t in tiles]
        
        # 解析 shunzi(1s,3s,2s) -> ['1s', '2s', '3s']
        shunzi_match = re.match(r'shunzi\(([^)]+)\)', ming_str)
        if shunzi_match:
            tiles = shunzi_match.group(1).split(',')
            # 排序：按照数字顺序
            tiles = [t.strip() for t in tiles]
            tiles.sort(key=lambda t: int(t[0]) if t[0].isdigit() else 0)
            return tiles
        
        # 解析其他格式（如 gangzi）
        gangzi_match = re.match(r'gangzi\(([^)]+)\)', ming_str)
        if gangzi_match:
            tiles = gangzi_match.group(1).split(',')
            return [t.strip() for t in tiles]
        
        return []
    
    def convert_tile(self, tile_str: str) -> Tile:
        """
        转换雀魂牌格式到我们的格式
        
        雀魂格式: "1m", "5p", "9s", "1z", "0M", "0P", "0S" (红宝牌)
        我们的格式: Tile 对象
        """
        if not tile_str:
            return None
        
        # 处理红宝牌 (0M, 0P, 0S -> 5m, 5p, 5s)
        if tile_str.upper() in ['0M', '0P', '0S']:
            suit = tile_str[-1].lower()
            return Tile.from_string(f"5{suit}")
        
        suit = tile_str[-1]
        number = tile_str[:-1]
        
        if suit == "m":
            return Tile.from_string(f"{number}m")
        elif suit == "p":
            return Tile.from_string(f"{number}p")
        elif suit == "s":
            return Tile.from_string(f"{number}s")
        elif suit == "z":
            wind_map = {"1": "东", "2": "南", "3": "西", "4": "北"}
            dragon_map = {"5": "白", "6": "发", "7": "中"}
            if number in wind_map:
                return Tile.from_string(wind_map[number])
            elif number in dragon_map:
                return Tile.from_string(dragon_map[number])
        
        return None
    
    def validate_hora(self, hule_data, is_tsumo: bool = None, is_riichi: bool = False) -> dict:
        """
        验证和牌事件
        
        Args:
            hule_data: HuleInfo 数据
            is_tsumo: 是否自摸（如果为 None，则从数据中读取）
            is_riichi: 是否立直
        
        Returns:
            验证结果字典
        """
        results = []
        
        for hule in hule_data.hules:
            # 1. 获取门前清手牌
            hand_tiles = []
            for tile_str in hule.hand:
                tile = self.convert_tile(tile_str)
                if tile:
                    hand_tiles.append(tile)
            
            # 2. 解析副露
            melds = []
            for ming_str in hule.ming:
                ming_tiles_str = self.parse_ming(ming_str)
                ming_tiles = []
                for tile_str in ming_tiles_str:
                    tile = self.convert_tile(tile_str)
                    if tile:
                        ming_tiles.append(tile)
                if ming_tiles:
                    melds.append(ming_tiles)
            
            # 3. 获取和牌
            winning_tile = self.convert_tile(hule.hu_tile)
            
            # 4. 确定是否自摸
            if is_tsumo is None:
                zimo = hule.zimo
            else:
                zimo = is_tsumo
            
            # 5. 创建手牌对象
            hand = Hand.from_tiles(hand_tiles)
            for meld in melds:
                hand.add_meld(meld)
            
            # 6. 验证和牌
            from src.agent.validator import WinValidator
            validator = WinValidator()
            
            result = validator.validate(
                hand=hand,
                winning_tile=winning_tile,
                is_tsumo=zimo,
                is_riichi=is_riichi
            )
            
            # 7. 构建结果
            result_dict = {
                "seat": hule.seat,
                "zimo": zimo,
                "hand": hand_tiles,
                "melds": melds,
                "winning_tile": winning_tile,
                "is_valid": result.is_valid,
                "error": result.error,
                "han": result.han,
                "fu": result.fu,
                "points": result.points,
                "yaku_list": [y.name for y in result.yaku_list] if result.yaku_list else [],
                "original_fans": [(f.name, f.val) for f in hule.fans],
                "original_fu": hule.fu,
                "original_count": hule.count
            }
            
            results.append(result_dict)
        
        return results


if __name__ == "__main__":
    import sys
    
    parser = MajsoulRecordParser()
    
    if len(sys.argv) > 1:
        game_uuid = sys.argv[1]
        print(f"获取游戏记录: {game_uuid}")
        
        try:
            records = parser.parse_by_id(game_uuid)
            print(f"解析成功，共 {len(records)} 条记录")
            
            # 查找和牌事件
            hora_records = [r for r in records if r['name'] == 'RecordHule']
            print(f"和牌事件: {len(hora_records)} 个")
            
            for i, record in enumerate(hora_records):
                data = record['data']
                results = parser.validate_hora(data)
                for j, result in enumerate(results):
                    print(f"\n[{i}][{j}] 和牌验证:")
                    print(f"  座位: {result['seat']}, 自摸: {result['zimo']}")
                    print(f"  手牌: {[str(t) for t in result['hand']]}")
                    print(f"  副露: {len(result['melds'])} 组")
                    print(f"  和牌: {result['winning_tile']}")
                    print(f"  验证: {'✓' if result['is_valid'] else '✗'}")
                    if result['is_valid']:
                        print(f"  番数: {result['han']}")
                        print(f"  符数: {result['fu']}")
                        print(f"  点数: {result['points']}")
                        print(f"  役种: {result['yaku_list']}")
                    else:
                        print(f"  错误: {result.get('error', '未知')}")
        except Exception as e:
            print(f"获取失败: {e}")
    else:
        print("用法: python majsoul_parser.py <game_uuid_or_paipu>")
        print("")
        print("支持的格式:")
        print("  纯 UUID: 0000034c-a2a9-4dfa-ae63-bd81aa25ebad")
        print("  Paipu:   260523-372a5e0d-8aa9-4af1-bf99-9498d066c896_a40365570")
        print("")
        print("获取方式:")
        print("  majsoul-query records <玩家名>")