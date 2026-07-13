#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命令行版本的运势预测
直接在终端里用，不用开浏览器

用法：
    python cli.py --birth 1995-03-15 --gender 男 --direction 事业
    python cli.py --daily --birth 1995-03-15
    python cli.py --relation --name-a 小明 --birth-a 1995-03-15 --name-b 小红 --birth-b 1996-08-20
"""

import sys
import os
import argparse
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.fortune_teller_v2 import FortuneTeller
from backend.logger import logger


def print_banner():
    """打印漂亮的 banner"""
    banner = """
╔══════════════════════════════════════════════════╗
║   🔮 AI 运势预测 - 命令行版                    ║
║   温暖 · 有智慧 · 给你方向                        ║
╚══════════════════════════════════════════════════╝
    """
    print(banner)


def print_result(title: str, content: str):
    """漂亮地打印结果"""
    print("\n" + "=" * 70)
    print(f"✨ {title}")
    print("=" * 70)
    print()
    print(content)
    print()
    print("=" * 70)
    print("💡 结果仅供娱乐，命运掌握在自己手中")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="AI 运势预测 - 命令行版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  年度运势： python cli.py --birth 1995-03-15 --gender 男 --direction 事业
  今日运势： python cli.py --daily --birth 1995-03-15
  两人合盘： python cli.py --relation --name-a 小明 --birth-a 1995-03-15 --name-b 小红 --birth-b 1996-08-20
  模拟模式： 不传 API Key 自动进入模拟模式
        """,
    )

    # 通用参数
    parser.add_argument(
        "--api-key",
        help="DeepSeek / OpenAI API Key，也可以用环境变量 DEEPSEEK_API_KEY",
    )
    parser.add_argument(
        "--model",
        default="default",
        help="模型配置：default / gpt-3.5 / creative",
    )
    parser.add_argument(
        "--prompt-version",
        default="latest",
        help="Prompt 版本：v1 / v2 / latest",
    )

    # 功能选择
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fortune", action="store_true", help="年度运势")
    group.add_argument("--daily", action="store_true", help="今日运势")
    group.add_argument("--relation", action="store_true", help="两人合盘")
    group.add_argument("--stats", action="store_true", help="查看统计信息")

    # 年度运势参数
    parser.add_argument("--birth", help="出生日期：YYYY-MM-DD")
    parser.add_argument("--gender", choices=["男", "女"], help="性别")
    parser.add_argument(
        "--direction",
        choices=["综合", "事业", "感情", "财运", "健康"],
        default="综合",
        help="测算方向",
    )

    # 合盘参数
    parser.add_argument("--name-a", help="第一个人的称呼")
    parser.add_argument("--birth-a", help="第一个人的出生日期")
    parser.add_argument("--name-b", help="第二个人的称呼")
    parser.add_argument("--birth-b", help="第二个人的出生日期")
    parser.add_argument(
        "--relation-type",
        choices=["情侣", "夫妻", "合伙人", "朋友"],
        default="情侣",
        help="关系类型",
    )

    # 输出参数
    parser.add_argument("--save", help="保存结果到文件")
    parser.add_argument("--no-banner", action="store_true", help="不打印 banner")
    parser.add_argument("--quiet", action="store_true", help="安静模式，只打印结果")

    args = parser.parse_args()

    if not args.quiet and not args.no_banner:
        print_banner()

    # 初始化
    teller = FortuneTeller(
        api_key=args.api_key,
        model_profile=args.model,
        prompt_version=args.prompt_version,
    )

    # ========== 查看统计 ==========
    if args.stats:
        import json
        print("\n📊 运行统计")
        print("=" * 70)
        print(json.dumps(teller.get_stats(), ensure_ascii=False, indent=2))
        return

    result = ""

    # ========== 今日运势 ==========
    if args.daily:
        if not args.birth:
            print("❌ 请用 --birth 指定出生日期")
            sys.exit(1)

        if not args.quiet:
            print(f"🔮 正在为你测算今日运势...")

        result = teller.get_daily_fortune(args.birth)

        if not args.quiet:
            print_result("今日运势", result)
        else:
            print(result)

    # ========== 年度运势 ==========
    elif args.fortune:
        if not args.birth or not args.gender:
            print("❌ 请用 --birth 和 --gender 指定出生日期和性别")
            sys.exit(1)

        if not args.quiet:
            print(f"🔮 正在为你详细解读... 约 10 秒")

        result = teller.get_fortune(args.birth, args.gender, args.direction)

        if not args.quiet:
            print_result(f"{args.direction}运势解读", result)
        else:
            print(result)

    # ========== 两人合盘 ==========
    elif args.relation:
        if not all([args.name_a, args.birth_a, args.name_b, args.birth_b]):
            print("❌ 请指定两个人的信息：--name-a, --birth-a, --name-b, --birth-b")
            sys.exit(1)

        if not args.quiet:
            print(f"🔮 正在分析你们的关系... 约 10 秒")

        result = teller.get_relation_reading(
            args.name_a,
            args.birth_a,
            args.name_b,
            args.birth_b,
            args.relation_type,
        )

        if not args.quiet:
            print_result(f"{args.relation_type}合盘分析", result)
        else:
            print(result)

    # 保存到文件
    if args.save and result:
        with open(args.save, "w", encoding="utf-8") as f:
            f.write(result)
        if not args.quiet:
            print(f"\n✅ 结果已保存到：{args.save}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见，祝你好运！")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 出错了: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
