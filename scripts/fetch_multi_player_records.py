"""
批量获取多个玩家的雀魂游戏记录
"""

import sys
sys.path.insert(0, '.')

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts.majsoul_parser import MajsoulRecordParser


async def search_player(api, nickname: str):
    """搜索玩家，获取玩家 ID"""
    try:
        players = await api.search_player(nickname, limit=5)
        if players:
            return players[0]
    except Exception as e:
        print(f"  搜索玩家 {nickname} 失败: {e}")
    return None


async def get_player_records(api, player_id: int, limit: int = 50):
    """获取玩家的游戏记录"""
    from majsoul_query.api.models.room_rank import all_four_player_room_rank
    
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=365)  # 最近一年
        records = await api.player_records(
            player_id, start_time, end_time,
            room_rank=all_four_player_room_rank,
            limit=limit
        )
        return records
    except Exception as e:
        print(f"  获取记录失败: {e}")
    return []


async def main():
    """主函数"""
    from majsoul_query.api.models.api import four_player_api
    
    # 玩家昵称列表从环境变量读取，避免把真实昵称提交到公开仓库。
    # 示例: MAJSOUL_NICKNAMES="player_a,player_b" python scripts/fetch_multi_player_records.py
    nicknames = [
        nickname.strip()
        for nickname in os.environ.get("MAJSOUL_NICKNAMES", "").split(",")
        if nickname.strip()
    ]
    if not nicknames:
        print("请通过 MAJSOUL_NICKNAMES 环境变量提供玩家昵称，用逗号分隔。")
        return {}, []
    
    print("搜索玩家并获取 ID...")
    player_info = {}
    
    for nickname in nicknames:
        print(f"  搜索: {nickname}")
        player = await search_player(four_player_api, nickname)
        if player:
            player_info[nickname] = {
                'id': player.id,
                'nickname': player.nickname,
                'level': player.level.id.name if hasattr(player.level.id, 'name') else str(player.level.id),
            }
            print(f"    ID: {player.id}, 段位: {player_info[nickname]['level']}")
        else:
            print(f"    未找到")
    
    print(f"\n找到 {len(player_info)} 个玩家")
    
    # 获取每个玩家的记录
    print("\n获取玩家记录...")
    all_records = []
    
    for nickname, info in player_info.items():
        print(f"  {nickname} (ID: {info['id']})")
        records = await get_player_records(four_player_api, info['id'], limit=50)
        print(f"    获取到 {len(records)} 条记录")
        
        for record in records:
            all_records.append({
                'player': nickname,
                'player_id': info['id'],
                'uuid': record.uuid,
                'start_time': record.start_time.isoformat() if record.start_time else None,
            })
    
    print(f"\n总共获取到 {len(all_records)} 条记录")
    
    # 保存结果
    output_file = Path("data/player_records.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'players': player_info,
            'records': all_records,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到: {output_file}")
    
    return player_info, all_records


if __name__ == '__main__':
    player_info, all_records = asyncio.run(main())
