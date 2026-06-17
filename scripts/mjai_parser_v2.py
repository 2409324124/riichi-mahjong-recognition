"""
mjai 格式游戏记录解析器

解析 mjai 格式的游戏记录，重建手牌，提取和牌事件并验证。
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_logic.tile import Tile
from src.game_logic.hand import Hand
from src.agent.validator import WinValidator


class MjaiParser:
    """mjai 格式解析器"""

    WIND_TO_TILE_ID = {'E': 27, 'S': 28, 'W': 29, 'N': 30}
    
    def __init__(self):
        """初始化解析器"""
        self.validator = WinValidator()
    
    def parse_file(self, filepath: str) -> List[Dict]:
        """
        解析 mjai 文件
        
        Args:
            filepath: 文件路径
        
        Returns:
            事件列表
        """
        events = []
        pending_start_kyoku = None

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和分隔线
                if not line or line.startswith('#') or line.startswith('-'):
                    continue
                # 尝试解析 JSON
                try:
                    event = json.loads(line)
                    events.append(event)
                    if event.get('type') == 'start_kyoku':
                        pending_start_kyoku = event
                    else:
                        pending_start_kyoku = None
                except json.JSONDecodeError:
                    if pending_start_kyoku:
                        round_match = re.match(r'^([ESWN])-([1-4])\s+kyoku', line)
                        if round_match:
                            wind, kyoku = round_match.groups()
                            pending_start_kyoku['_round_wind'] = self.WIND_TO_TILE_ID[wind]
                            pending_start_kyoku['_round_label'] = f'{wind}-{kyoku}'
                            pending_start_kyoku['_kyoku_number'] = int(kyoku)
                            pending_start_kyoku = None
                    continue
        return events
    
    def convert_tile(self, mjai_tile: str) -> Optional[Tile]:
        """
        转换 mjai 牌格式到内部格式
        
        Args:
            mjai_tile: mjai 格式的牌 (如 "1m", "5p", "9s", "E", "S", "W", "N", "P", "F", "C")
        
        Returns:
            Tile 对象
        """
        if not mjai_tile or mjai_tile == '?':
            return None
        
        # 风牌
        wind_map = {'E': '东', 'S': '南', 'W': '西', 'N': '北'}
        if mjai_tile in wind_map:
            return Tile.from_string(wind_map[mjai_tile])
        
        # 三元牌
        dragon_map = {'P': '白', 'F': '发', 'C': '中'}
        if mjai_tile in dragon_map:
            return Tile.from_string(dragon_map[mjai_tile])
        
        # 数牌
        if len(mjai_tile) >= 2:
            # 处理红宝牌 (5mr, 5pr, 5sr)
            if mjai_tile.lower() in ['5mr', '5pr', '5sr']:
                suit = mjai_tile[1].lower()
                return Tile.from_string(f'5{suit}')
            
            number = mjai_tile[:-1]
            suit = mjai_tile[-1]
            
            # 处理红宝牌
            if number == '5' and suit in ['m', 'p', 's'] and len(mjai_tile) > 2:
                return Tile.from_string(f'5{suit}')
            
            return Tile.from_string(f'{number}{suit}')
        
        return None

    def _copy_hands(self, hands: Dict[int, List[Tile]]) -> Dict[int, List[Tile]]:
        """复制手牌状态，避免后续事件污染历史快照。"""
        return {seat: tiles.copy() for seat, tiles in hands.items()}

    def _copy_melds(self, melds: Dict[int, List[List[Tile]]]) -> Dict[int, List[List[Tile]]]:
        """复制副露状态，避免后续事件污染历史快照。"""
        return {seat: [meld.copy() for meld in player_melds] for seat, player_melds in melds.items()}

    def _remove_tiles_from_hand(self, hand_tiles: List[Tile], tile_strings: List[str]) -> None:
        """从手牌中移除事件消耗的牌。"""
        for tile_str in tile_strings:
            tile = self.convert_tile(tile_str)
            if tile and tile in hand_tiles:
                hand_tiles.remove(tile)

    def _meld_from_event(self, event: Dict) -> List[Tile]:
        """从吃碰杠事件构建副露牌列表。"""
        meld_tiles = []
        for tile_str in event.get('consumed', []):
            tile = self.convert_tile(tile_str)
            if tile:
                meld_tiles.append(tile)

        pai_tile = self.convert_tile(event.get('pai', ''))
        if pai_tile:
            meld_tiles.append(pai_tile)

        return meld_tiles

    def apply_event(
        self,
        event: Dict,
        hands: Dict[int, List[Tile]],
        melds: Dict[int, List[List[Tile]]]
    ) -> Tuple[Dict[int, List[Tile]], Dict[int, List[List[Tile]]]]:
        """
        将单个 mjai 事件应用到当前手牌/副露状态。
        
        start_kyoku 会返回新的空状态，其余事件原地更新并返回同一状态对象。
        """
        event_type = event.get('type')

        if event_type == 'start_kyoku':
            return {0: [], 1: [], 2: [], 3: []}, {0: [], 1: [], 2: [], 3: []}

        if event_type == 'haipai':
            actor = event.get('actor', 0)
            pais = event.get('pais', [])
            hands[actor] = [tile for tile in (self.convert_tile(p) for p in pais) if tile]

        elif event_type == 'tsumo':
            actor = event.get('actor', 0)
            tile = self.convert_tile(event.get('pai', ''))
            if tile:
                hands[actor].append(tile)

        elif event_type == 'dahai':
            actor = event.get('actor', 0)
            tile = self.convert_tile(event.get('pai', ''))
            if tile and tile in hands[actor]:
                hands[actor].remove(tile)

        elif event_type in ('chi', 'pon', 'daiminkan'):
            actor = event.get('actor', 0)
            meld_tiles = self._meld_from_event(event)
            if meld_tiles:
                melds[actor].append(meld_tiles)
            self._remove_tiles_from_hand(hands[actor], event.get('consumed', []))

        elif event_type == 'ankan':
            actor = event.get('actor', 0)
            consumed = event.get('consumed', [])
            meld_tiles = []
            for tile_str in consumed:
                tile = self.convert_tile(tile_str)
                if tile:
                    meld_tiles.append(tile)
            if meld_tiles:
                melds[actor].append(meld_tiles)
            self._remove_tiles_from_hand(hands[actor], consumed)

        elif event_type == 'kakan':
            actor = event.get('actor', 0)
            tile = self.convert_tile(event.get('pai', ''))
            if tile and tile in hands[actor]:
                hands[actor].remove(tile)
            for i, meld in enumerate(melds[actor]):
                if len(meld) == 3 and tile and tile in meld:
                    melds[actor][i].append(tile)
                    break

        return hands, melds
    
    def reconstruct_hands(self, events: List[Dict]) -> Tuple[Dict[int, List[Tile]], Dict[int, List[List[Tile]]], List[Dict[int, List[Tile]]], List[Dict[int, List[List[Tile]]]]]:
        """
        从事件流重建每个玩家的手牌和副露
        
        Args:
            events: 事件列表
        
        Returns:
            (最终玩家手牌字典, 最终玩家副露字典, 所有局手牌列表, 所有局副露列表)
        """
        hands = {0: [], 1: [], 2: [], 3: []}
        melds = {0: [], 1: [], 2: [], 3: []}
        all_hands = []
        all_melds = []
        
        for event in events:
            event_type = event.get('type')
            
            if event_type == 'start_kyoku':
                # 新局开始，重置手牌和副露
                hands = {0: [], 1: [], 2: [], 3: []}
                melds = {0: [], 1: [], 2: [], 3: []}
            
            elif event_type == 'haipai':
                # 初始手牌
                actor = event.get('actor', 0)
                pais = event.get('pais', [])
                hands[actor] = [self.convert_tile(p) for p in pais if self.convert_tile(p)]
            
            elif event_type == 'tsumo':
                # 摸牌
                actor = event.get('actor', 0)
                pai = event.get('pai', '')
                tile = self.convert_tile(pai)
                if tile:
                    hands[actor].append(tile)
            
            elif event_type == 'dahai':
                # 打牌
                actor = event.get('actor', 0)
                pai = event.get('pai', '')
                tile = self.convert_tile(pai)
                if tile and tile in hands[actor]:
                    hands[actor].remove(tile)
            
            elif event_type == 'chi':
                # 吃 - 记录副露
                actor = event.get('actor', 0)
                pai = event.get('pai', '')
                consumed = event.get('consumed', [])
                
                # 构建副露
                meld_tiles = []
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile:
                        meld_tiles.append(tile)
                pai_tile = self.convert_tile(pai)
                if pai_tile:
                    meld_tiles.append(pai_tile)
                melds[actor].append(meld_tiles)
                
                # 从手牌中移除吃的牌
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile and tile in hands[actor]:
                        hands[actor].remove(tile)
            
            elif event_type == 'pon':
                # 碰 - 记录副露
                actor = event.get('actor', 0)
                pai = event.get('pai', '')
                consumed = event.get('consumed', [])
                
                # 构建副露
                meld_tiles = []
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile:
                        meld_tiles.append(tile)
                pai_tile = self.convert_tile(pai)
                if pai_tile:
                    meld_tiles.append(pai_tile)
                melds[actor].append(meld_tiles)
                
                # 从手牌中移除碰的牌
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile and tile in hands[actor]:
                        hands[actor].remove(tile)
            
            elif event_type == 'daiminkan':
                # 大明杠 - 记录副露
                actor = event.get('actor', 0)
                pai = event.get('pai', '')
                consumed = event.get('consumed', [])
                
                # 构建副露
                meld_tiles = []
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile:
                        meld_tiles.append(tile)
                pai_tile = self.convert_tile(pai)
                if pai_tile:
                    meld_tiles.append(pai_tile)
                melds[actor].append(meld_tiles)
                
                # 从手牌中移除杠的牌
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile and tile in hands[actor]:
                        hands[actor].remove(tile)
            
            elif event_type == 'ankan':
                # 暗杠 - 记录副露
                actor = event.get('actor', 0)
                consumed = event.get('consumed', [])
                
                # 构建副露
                meld_tiles = []
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile:
                        meld_tiles.append(tile)
                melds[actor].append(meld_tiles)
                
                # 从手牌中移除暗杠的牌
                for c in consumed:
                    tile = self.convert_tile(c)
                    if tile and tile in hands[actor]:
                        hands[actor].remove(tile)
            
            elif event_type == 'kakan':
                # 加杠 - 更新副露
                actor = event.get('actor', 0)
                pai = event.get('pai', '')
                tile = self.convert_tile(pai)
                
                # 从手牌中移除加杠的牌
                if tile and tile in hands[actor]:
                    hands[actor].remove(tile)
                
                # 找到对应的碰并更新为杠
                for i, meld in enumerate(melds[actor]):
                    if len(meld) == 3 and tile and tile in meld:
                        melds[actor][i].append(tile)
                        break
            
            elif event_type == 'end_kyoku':
                # 局结束，保存当前状态
                all_hands.append(self._copy_hands(hands))
                all_melds.append(self._copy_melds(melds))
        
        return hands, melds, all_hands, all_melds
    
    def validate_hora(
        self,
        hora_event: Dict,
        hands: Dict[int, List[Tile]],
        melds: Dict[int, List[List[Tile]]],
        round_wind: int = 27,
        seat_wind: int = 27
    ) -> Dict:
        """
        验证和牌事件
        
        Args:
            hora_event: hora 事件
            hands: 玩家手牌字典
            melds: 玩家副露字典
        
        Returns:
            验证结果
        """
        actor = hora_event.get('actor', 0)
        target = hora_event.get('target', -1)
        pai = hora_event.get('pai', '')
        
        # 获取手牌和副露
        hand_tiles = hands.get(actor, []).copy()
        player_melds = melds.get(actor, [])
        winning_tile = self.convert_tile(pai)
        
        if not winning_tile:
            return {
                'is_valid': False,
                'error': '无法解析和牌',
                'han': 0,
                'fu': 0,
                'points': 0,
                'yaku_list': []
            }
        
        # 判断是否自摸
        is_tsumo = (actor == target)
        
        # 自摸时，和牌已经在手牌中（因为摸牌事件加入了手牌）
        # 需要从手牌中移除，让验证器重新添加
        if is_tsumo and winning_tile in hand_tiles:
            hand_tiles.remove(winning_tile)
        
        # 创建手牌对象
        hand = Hand.from_tiles(hand_tiles)
        for meld in player_melds:
            hand.add_meld(meld)
        
        # 验证和牌
        result = self.validator.validate(
            hand=hand,
            winning_tile=winning_tile,
            is_tsumo=is_tsumo,
            round_wind=round_wind,
            seat_wind=seat_wind
        )
        
        return {
            'is_valid': result.is_valid,
            'error': result.error,
            'han': result.han,
            'fu': result.fu,
            'points': result.points,
            'yaku_list': [y.name for y in result.yaku_list] if result.yaku_list else [],
            'actor': actor,
            'target': target,
            'is_tsumo': is_tsumo,
            'round_wind': round_wind,
            'seat_wind': seat_wind,
            'hand': [str(t) for t in hand_tiles],
            'melds': [[str(t) for t in meld] for meld in player_melds],
            'winning_tile': str(winning_tile)
        }
    
    def analyze_file(self, filepath: str) -> Dict:
        """
        分析整个文件
        
        Args:
            filepath: 文件路径
        
        Returns:
            分析结果
        """
        events = self.parse_file(filepath)

        hands = {0: [], 1: [], 2: [], 3: []}
        melds = {0: [], 1: [], 2: [], 3: []}
        all_hands = []
        all_melds = []
        results = []
        round_index = -1
        current_oya = 0
        current_round_wind = 27

        for event_index, event in enumerate(events):
            event_type = event.get('type')

            if event_type == 'hora':
                actor = event.get('actor', 0)
                seat_wind = 27 + ((actor - current_oya) % 4)
                result = self.validate_hora(
                    event,
                    self._copy_hands(hands),
                    self._copy_melds(melds),
                    round_wind=current_round_wind,
                    seat_wind=seat_wind
                )
                result['event_index'] = event_index
                result['round_index'] = round_index
                results.append(result)
                continue

            hands, melds = self.apply_event(event, hands, melds)

            if event_type == 'start_kyoku':
                round_index += 1
                current_oya = event.get('oya', 0)
                current_round_wind = event.get('_round_wind', 27)
            elif event_type == 'end_kyoku':
                all_hands.append(self._copy_hands(hands))
                all_melds.append(self._copy_melds(melds))
        
        # 统计结果
        total_hora = len(results)
        valid_hora = sum(1 for r in results if r['is_valid'])
        
        return {
            'filepath': filepath,
            'total_events': len(events),
            'total_hora': total_hora,
            'valid_hora': valid_hora,
            'pass_rate': valid_hora / total_hora * 100 if total_hora > 0 else 0,
            'results': results,
            'all_hands': all_hands,
            'all_melds': all_melds
        }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='mjai 格式解析器')
    parser.add_argument('filepath', type=str, help='mjai 文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 解析文件
    mjai_parser = MjaiParser()
    result = mjai_parser.analyze_file(args.filepath)
    
    # 输出结果
    print(f'文件: {result["filepath"]}')
    print(f'总事件数: {result["total_events"]}')
    print(f'和牌事件数: {result["total_hora"]}')
    print(f'有效和牌数: {result["valid_hora"]}')
    print(f'验证通过率: {result["pass_rate"]:.1f}%')
    
    if args.verbose:
        print('\n详细结果:')
        for i, r in enumerate(result['results']):
            print(f'  [{i+1}] 玩家{r["actor"]} {"自摸" if r["is_tsumo"] else "荣和"} {r["winning_tile"]}')
            print(f'      有效: {r["is_valid"]}, 番数: {r["han"]}, 符数: {r["fu"]}, 点数: {r["points"]}')
            print(f'      手牌: {", ".join(r["hand"])}')
            if r['melds']:
                print(f'      副露: {", ".join([" ".join(m) for m in r["melds"]])}')
            if r['yaku_list']:
                print(f'      役种: {", ".join(r["yaku_list"])}')
            if r['error']:
                print(f'      错误: {r["error"]}')
    
