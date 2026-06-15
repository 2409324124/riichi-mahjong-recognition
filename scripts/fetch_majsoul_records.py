"""
获取雀魂游戏记录

使用 mahjong_soul_api 获取用户的游戏记录。
"""

import asyncio
import json
import os
from datetime import datetime

# 导入 mahjong_soul_api
from ms.base import MSRPCChannel
from ms.rpc import Lobby
import ms.protocol_pb2 as pb


class MajsoulRecordFetcher:
    """雀魂游戏记录获取器"""
    
    def __init__(self, server: str = "cn"):
        """
        初始化获取器
        
        Args:
            server: 服务器类型 (cn, en, jp)
        """
        self.server = server
        self.lobby = None
        self.channel = None
        
        # 服务器配置
        self.servers = {
            "cn": "wss://gateway-v2.maj-soul.com:5101",
            "en": "wss://mjusgs.mahjongsoul.com:4501",
            "jp": "wss://mjjpgs.mahjongsoul.com:4501"
        }
    
    async def connect(self):
        """连接到雀魂服务器"""
        url = self.servers.get(self.server)
        if not url:
            raise ValueError(f"不支持的服务器: {self.server}")
        
        self.channel = MSRPCChannel(url)
        self.lobby = Lobby(self.channel)
        await self.channel.connect()
        print(f"已连接到 {self.server} 服务器")
    
    async def login(self, username: str, password: str):
        """
        登录
        
        Args:
            username: 用户名
            password: 密码
        """
        if not self.lobby:
            raise RuntimeError("请先连接服务器")
        
        # 登录
        req = pb.ReqLogin()
        req.account = username
        req.password = password
        req.client_version_string = "web-0.11.252"
        
        res = await self.lobby.login(req)
        print(f"登录成功: {res}")
        return res
    
    async def fetch_record_list(self, start: int = 0, count: int = 30):
        """
        获取游戏记录列表
        
        Args:
            start: 起始位置
            count: 数量
        
        Returns:
            游戏记录列表
        """
        if not self.lobby:
            raise RuntimeError("请先登录")
        
        req = pb.ReqGameRecordList()
        req.start = start
        req.count = count
        
        res = await self.lobby.fetch_game_record_list(req)
        return res.record_list
    
    async def fetch_record(self, game_uuid: str):
        """
        获取单个游戏记录
        
        Args:
            game_uuid: 游戏记录 UUID
        
        Returns:
            游戏记录数据
        """
        if not self.lobby:
            raise RuntimeError("请先登录")
        
        req = pb.ReqGameRecord()
        req.game_uuid = game_uuid
        req.client_version_string = "web-0.11.252"
        
        res = await self.lobby.fetch_game_record(req)
        return res
    
    async def get_my_records(self, count: int = 100):
        """
        获取自己的游戏记录
        
        Args:
            count: 获取数量
        
        Returns:
            游戏记录 UUID 列表
        """
        records = []
        start = 0
        
        while len(records) < count:
            batch = await self.fetch_record_list(start=start, count=min(30, count - len(records)))
            if not batch:
                break
            
            for record in batch:
                records.append({
                    "uuid": record.uuid,
                    "start_time": record.start_time,
                    "end_time": record.end_time,
                    "players": [p.nickname for p in record.players]
                })
            
            start += len(batch)
            
            # 避免请求过快
            await asyncio.sleep(0.5)
        
        return records
    
    async def close(self):
        """关闭连接"""
        if self.channel:
            await self.channel.close()
            print("已关闭连接")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="获取雀魂游戏记录")
    parser.add_argument("--server", type=str, default="cn", choices=["cn", "en", "jp"],
                       help="服务器类型")
    parser.add_argument("--username", type=str, help="用户名")
    parser.add_argument("--password", type=str, help="密码")
    parser.add_argument("--count", type=int, default=10, help="获取数量")
    parser.add_argument("--output", type=str, default="data/majsoul_records.json", help="输出文件")
    
    args = parser.parse_args()
    
    # 创建获取器
    fetcher = MajsoulRecordFetcher(server=args.server)
    
    try:
        # 连接服务器
        await fetcher.connect()
        
        # 登录
        if args.username and args.password:
            await fetcher.login(args.username, args.password)
        else:
            print("请提供用户名和密码")
            return
        
        # 获取记录
        print(f"正在获取 {args.count} 条游戏记录...")
        records = await fetcher.get_my_records(count=args.count)
        
        print(f"获取成功，共 {len(records)} 条记录")
        
        # 保存到文件
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"已保存到 {args.output}")
        
        # 显示前 5 条记录
        for i, record in enumerate(records[:5]):
            print(f"  [{i}] UUID: {record['uuid']}")
    
    finally:
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(main())