"""
命令行界面

提供 CLI 工具，方便使用麻将系统。
"""

import argparse
import sys
from typing import List, Optional

from .system import MahjongSystem


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="mahjong",
        description="日本立直麻将识别系统"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析手牌")
    analyze_parser.add_argument(
        "tiles",
        nargs="+",
        help="手牌，如: 1m 2m 3m 4p 5p 6p 7s 8s 9s"
    )
    analyze_parser.add_argument(
        "--melds",
        nargs="*",
        help="副露，如: 1m,2m,3m 或 白,白,白"
    )
    analyze_parser.add_argument(
        "--dora",
        nargs="*",
        help="宝牌指示牌"
    )
    analyze_parser.add_argument(
        "--round-wind",
        type=int,
        default=27,
        help="场风 (27=东, 28=南, 29=西, 30=北)"
    )
    analyze_parser.add_argument(
        "--seat-wind",
        type=int,
        default=27,
        help="自风 (27=东, 28=南, 29=西, 30=北)"
    )
    
    # win 命令
    win_parser = subparsers.add_parser("win", help="验证和牌")
    win_parser.add_argument(
        "tiles",
        nargs="+",
        help="手牌（13张，不含和牌）"
    )
    win_parser.add_argument(
        "--win",
        required=True,
        help="和牌"
    )
    win_parser.add_argument(
        "--melds",
        nargs="*",
        help="副露"
    )
    win_parser.add_argument(
        "--tsumo",
        action="store_true",
        help="自摸"
    )
    win_parser.add_argument(
        "--riichi",
        action="store_true",
        help="立直"
    )
    win_parser.add_argument(
        "--ippatsu",
        action="store_true",
        help="一发"
    )
    win_parser.add_argument(
        "--dealer",
        action="store_true",
        help="庄家"
    )
    win_parser.add_argument(
        "--round-wind",
        type=int,
        default=27,
        help="场风"
    )
    win_parser.add_argument(
        "--seat-wind",
        type=int,
        default=27,
        help="自风"
    )
    
    # score 命令
    score_parser = subparsers.add_parser("score", help="计算点数")
    score_parser.add_argument(
        "tiles",
        nargs="+",
        help="手牌（13张，不含和牌）"
    )
    score_parser.add_argument(
        "--win",
        required=True,
        help="和牌"
    )
    score_parser.add_argument(
        "--melds",
        nargs="*",
        help="副露"
    )
    score_parser.add_argument(
        "--tsumo",
        action="store_true",
        help="自摸"
    )
    score_parser.add_argument(
        "--riichi",
        action="store_true",
        help="立直"
    )
    score_parser.add_argument(
        "--ippatsu",
        action="store_true",
        help="一发"
    )
    score_parser.add_argument(
        "--dealer",
        action="store_true",
        help="庄家"
    )
    score_parser.add_argument(
        "--round-wind",
        type=int,
        default=27,
        help="场风"
    )
    score_parser.add_argument(
        "--seat-wind",
        type=int,
        default=27,
        help="自风"
    )
    
    # recommend 命令
    recommend_parser = subparsers.add_parser("recommend", help="获取打牌推荐")
    recommend_parser.add_argument(
        "tiles",
        nargs="+",
        help="手牌（14张）"
    )
    recommend_parser.add_argument(
        "--melds",
        nargs="*",
        help="副露"
    )
    
    # camera 命令
    camera_parser = subparsers.add_parser("camera", help="摄像头实时识别")
    camera_parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="摄像头ID"
    )
    camera_parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="YOLO模型路径"
    )
    
    return parser


def cmd_analyze(args: argparse.Namespace) -> int:
    """执行 analyze 命令"""
    system = MahjongSystem()
    
    try:
        result = system.analyze_hand(
            tile_strings=args.tiles,
            meld_strings=args.melds,
            dora_indicators=args.dora,
            round_wind=args.round_wind,
            seat_wind=args.seat_wind
        )
        
        print(system.format_analysis(result))
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_win(args: argparse.Namespace) -> int:
    """执行 win 命令"""
    system = MahjongSystem()
    
    try:
        result = system.validate_win(
            tile_strings=args.tiles,
            winning_tile_str=args.win,
            meld_strings=args.melds,
            is_tsumo=args.tsumo,
            is_riichi=args.riichi,
            is_ippatsu=args.ippatsu,
            is_dealer=args.dealer,
            round_wind=args.round_wind,
            seat_wind=args.seat_wind
        )
        
        if result.is_valid:
            print("✓ 有效和牌")
            print(f"  番数: {result.han}")
            print(f"  符数: {result.fu}")
            print(f"  点数: {result.points}")
            print(f"  役种: {', '.join(y.name for y in result.yaku_list)}")
            return 0
        else:
            print(f"✗ 无效和牌: {result.error}")
            return 1
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_score(args: argparse.Namespace) -> int:
    """执行 score 命令"""
    system = MahjongSystem()
    
    try:
        result = system.calculate_score(
            tile_strings=args.tiles,
            winning_tile_str=args.win,
            meld_strings=args.melds,
            is_tsumo=args.tsumo,
            is_riichi=args.riichi,
            is_ippatsu=args.ippatsu,
            is_dealer=args.dealer,
            round_wind=args.round_wind,
            seat_wind=args.seat_wind
        )
        
        print(f"番数: {result.han}")
        print(f"符数: {result.fu}")
        print(f"点数类型: {result.score_type.value}")
        print(f"总点数: {result.total_points}")
        print(f"役种: {', '.join(y.name for y in result.yaku_list)}")
        print(f"支付: {result.payment}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_recommend(args: argparse.Namespace) -> int:
    """执行 recommend 命令"""
    system = MahjongSystem()
    
    try:
        result = system.get_discard_recommendation(
            tile_strings=args.tiles,
            meld_strings=args.melds
        )
        
        print(f"当前向听: {result['current_shanten']}")
        print(f"手牌类型: {result['hand_type']}")
        print(f"\n推荐打牌: {result['best_discard']}")
        print(f"理由: {result['best_discard_reason']}")
        print(f"接受牌: {', '.join(result['ukeire_tiles'])} ({result['ukeire_count']}张)")
        
        print("\n所有打牌选项:")
        for i, discard in enumerate(result['all_discards'], 1):
            print(f"  {i}. {discard['tile']} - {discard['description']}")
        
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_camera(args: argparse.Namespace) -> int:
    """执行 camera 命令"""
    try:
        import cv2
    except ImportError:
        print("错误: 需要安装 opencv-python", file=sys.stderr)
        print("运行: pip install opencv-python", file=sys.stderr)
        return 1
    
    try:
        from .recognition.recognizer import MahjongRecognizer
        from .recognition.detector import MahjongDetector
    except ImportError as e:
        print(f"错误: 无法导入识别模块: {e}", file=sys.stderr)
        return 1
    
    # 初始化识别器
    recognizer = MahjongRecognizer(model_path=args.model)
    
    # 打开摄像头
    cap = cv2.VideoCapture(args.camera)
    
    if not cap.isOpened():
        print(f"错误: 无法打开摄像头 {args.camera}", file=sys.stderr)
        return 1
    
    print("摄像头已打开，按 'q' 退出")
    
    system = MahjongSystem()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("错误: 无法读取摄像头画面", file=sys.stderr)
                break
            
            # 识别麻将牌
            try:
                result = recognizer.recognize(frame)
                
                # 绘制检测结果
                frame = recognizer.draw_recognition(frame, result)
                
                # 如果检测到牌，显示信息
                if result.tiles:
                    hand_str = " ".join(str(t) for t in result.tiles)
                    cv2.putText(
                        frame, f"Hand: {hand_str}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2
                    )
                    
                    # 分析手牌
                    if len(result.tiles) == 14:
                        try:
                            tile_strings = [str(t) for t in result.tiles]
                            recommendation = system.get_discard_recommendation(tile_strings)
                            cv2.putText(
                                frame, f"Recommend: {recommendation['best_discard']}",
                                (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2
                            )
                        except:
                            pass
            except Exception as e:
                cv2.putText(
                    frame, f"Error: {e}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 255), 2
                )
            
            # 显示画面
            cv2.imshow("Mahjong Recognition", frame)
            
            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return 0


def main(args: Optional[List[str]] = None) -> int:
    """主函数"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if parsed_args.command is None:
        parser.print_help()
        return 0
    
    commands = {
        "analyze": cmd_analyze,
        "win": cmd_win,
        "score": cmd_score,
        "recommend": cmd_recommend,
        "camera": cmd_camera,
    }
    
    handler = commands.get(parsed_args.command)
    if handler:
        return handler(parsed_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())