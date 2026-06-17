"""
批量测试脚本（多线程版）

从雀魂服务器批量获取游戏记录，解析并验证和牌。
"""

import sys
import json
from pathlib import Path
from collections import Counter
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.majsoul_parser import MajsoulRecordParser

# 线程安全的计数器
lock = threading.Lock()


def parse_single_record(parser: MajsoulRecordParser, uuid: str) -> Dict:
    """
    解析单条记录
    
    Args:
        parser: 解析器
        uuid: 游戏 UUID
    
    Returns:
        解析结果
    """
    try:
        records = parser.parse_by_id(uuid)
        
        hora_records = [r for r in records if r['name'] == 'RecordHule']
        results = []
        
        for record in hora_records:
            data = record['data']
            validation_results = parser.validate_hora(data)
            
            for result in validation_results:
                results.append({
                    'uuid': uuid,
                    'seat': result['seat'],
                    'zimo': result['zimo'],
                    'is_valid': result['is_valid'],
                    'han': result.get('han', 0),
                    'fu': result.get('fu', 0),
                    'points': result.get('points', 0),
                    'yaku_list': result.get('yaku_list', []),
                    'error': result.get('error', None),
                    'hand': [str(t) for t in result.get('hand', [])],
                    'melds': len(result.get('melds', [])),
                    'winning_tile': str(result.get('winning_tile', '')),
                })
        
        return {'uuid': uuid, 'success': True, 'results': results}
    
    except Exception as e:
        return {'uuid': uuid, 'success': False, 'error': str(e), 'results': []}


def batch_test(
    player_id: str,
    max_records: int = 100,
    num_workers: int = 4,
    output_file: str = None
):
    """
    批量测试（多线程版）
    
    Args:
        player_id: 玩家 ID
        max_records: 最大记录数
        num_workers: 线程数
        output_file: 输出文件路径
    """
    parser = MajsoulRecordParser()
    
    # 1. 获取 UUID 列表
    print(f"获取玩家 {player_id} 的游戏记录...")
    uuids = parser.fetch_uuid_list(player_id)
    print(f"找到 {len(uuids)} 条记录")
    
    uuids = uuids[:max_records]
    print(f"测试前 {len(uuids)} 条记录，使用 {num_workers} 个线程")
    
    # 2. 多线程解析
    all_results = []
    error_counter = Counter()
    success_count = 0
    fail_count = 0
    
    print("\n开始解析...")
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # 提交所有任务
        futures = {
            executor.submit(parse_single_record, parser, uuid): uuid
            for uuid in uuids
        }
        
        # 收集结果
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            uuid = result['uuid']
            
            if result['success']:
                success_count += 1
                all_results.extend(result['results'])
            else:
                fail_count += 1
                error_counter[result['error']] += 1
            
            # 进度显示
            print(f"\r[{i+1}/{len(uuids)}] 成功: {success_count}, 失败: {fail_count}", end="", flush=True)
    
    print()  # 换行
    
    # 3. 统计结果
    total_hora = len(all_results)
    valid_hora = sum(1 for r in all_results if r['is_valid'])
    invalid_hora = total_hora - valid_hora
    
    # 错误分析
    for r in all_results:
        if not r['is_valid']:
            error_counter[r['error'] or '未知'] += 1
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"测试记录数: {len(uuids)}")
    print(f"  成功解析: {success_count}")
    print(f"  解析失败: {fail_count}")
    print(f"和牌事件数: {total_hora}")
    print(f"有效和牌数: {valid_hora}")
    print(f"验证通过率: {valid_hora/total_hora*100:.1f}%" if total_hora > 0 else "验证通过率: N/A")
    
    # 4. 错误分析
    if error_counter:
        print("\n" + "=" * 60)
        print("验证失败原因分析")
        print("=" * 60)
        for error, count in error_counter.most_common(20):
            print(f"  [{count:4d}] {error}")
    
    # 5. 役种统计
    yaku_counter = Counter()
    for r in all_results:
        if r['is_valid']:
            for yaku in r['yaku_list']:
                yaku_counter[yaku] += 1
    
    if yaku_counter:
        print("\n" + "=" * 60)
        print("役种统计 (有效和牌)")
        print("=" * 60)
        for yaku, count in yaku_counter.most_common(20):
            print(f"  [{count:4d}] {yaku}")
    
    # 6. 番数分布
    han_counter = Counter()
    for r in all_results:
        if r['is_valid']:
            han_counter[r['han']] += 1
    
    if han_counter:
        print("\n" + "=" * 60)
        print("番数分布")
        print("=" * 60)
        for han in sorted(han_counter.keys()):
            count = han_counter[han]
            print(f"  {han:2d}番: {count:4d} ({count/valid_hora*100:.1f}%)")
    
    # 7. 保存结果
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'player_id': player_id,
                'total_records': len(uuids),
                'success_count': success_count,
                'fail_count': fail_count,
                'total_hora': total_hora,
                'valid_hora': valid_hora,
                'pass_rate': valid_hora/total_hora*100 if total_hora > 0 else 0,
                'errors': dict(error_counter),
                'yaku_stats': dict(yaku_counter),
                'han_stats': dict(han_counter),
                'results': all_results,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {output_path}")
    
    return all_results, error_counter


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='批量测试雀魂记录（多线程版）')
    parser.add_argument('--player-id', type=str, default='68292379', help='玩家 ID')
    parser.add_argument('--max-records', type=int, default=100, help='最大记录数')
    parser.add_argument('--workers', type=int, default=4, help='线程数')
    parser.add_argument('--output', type=str, default='data/batch_test_results.json', help='输出文件')
    
    args = parser.parse_args()
    
    batch_test(
        player_id=args.player_id,
        max_records=args.max_records,
        num_workers=args.workers,
        output_file=args.output
    )