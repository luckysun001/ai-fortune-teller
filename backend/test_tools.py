#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量测试工具 - 一次性测试多个 Prompt 和多个案例，对比效果
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.fortune_teller import FortuneTeller
import json
from datetime import datetime


# 测试案例库 - 不同年龄、不同性别、不同方向
TEST_CASES = [
    {
        "name": "25岁男生，事业",
        "birth_date": "1999-03-15",
        "gender": "男",
        "direction": "事业",
        "age": 25,
    },
    {
        "name": "28岁女生，感情",
        "birth_date": "1996-08-20",
        "gender": "女",
        "direction": "感情",
        "age": 28,
    },
    {
        "name": "35岁男士，综合",
        "birth_date": "1989-01-10",
        "gender": "男",
        "direction": "综合",
        "age": 35,
    },
    {
        "name": "42岁女士，财运",
        "birth_date": "1982-11-05",
        "gender": "女",
        "direction": "财运",
        "age": 42,
    },
]


def batch_test(api_key: str, model: str = "deepseek-chat", prompt_version: str = "v2"):
    """批量测试多个案例"""

    teller = FortuneTeller(model=model, api_key=api_key)

    # 切换 Prompt 版本
    if prompt_version == "v2":
        with open("../prompts/fortune_reading_v2.md", "r", encoding="utf-8") as f:
            teller.prompts["fortune_reading"] = f.read()

    print("=" * 80)
    print(f"🧪 批量测试 - {len(TEST_CASES)} 个案例")
    print(f"📅 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 模型：{model}")
    print(f"📝 Prompt 版本：{prompt_version}")
    print("=" * 80)

    results = []

    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n\n{'=' * 80}")
        print(f"📍 案例 {i}/{len(TEST_CASES)}：{case['name']}")
        print(f"{'=' * 80}")

        # 调用
        result = teller.get_fortune(
            birth_date=case["birth_date"],
            gender=case["gender"],
            direction=case["direction"],
        )

        print(result)

        # 保存结果
        results.append({
            "case": case,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })

    # 保存到文件
    output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n\n{'=' * 80}")
    print(f"✅ 测试完成！结果已保存到：{output_file}")
    print("=" * 80)


def compare_prompts(api_key: str, case_idx: int = 0):
    """对比两个版本的 Prompt 效果"""

    teller = FortuneTeller(model="deepseek-chat", api_key=api_key)
    case = TEST_CASES[case_idx]

    print("=" * 80)
    print(f"🔍 Prompt 对比测试 - 案例：{case['name']}")
    print("=" * 80)

    # 版本 1
    print("\n\n" + "=" * 80)
    print("📗 版本 1 - 基础版")
    print("=" * 80)
    result_v1 = teller.get_fortune(
        birth_date=case["birth_date"],
        gender=case["gender"],
        direction=case["direction"],
    )
    print(result_v1)

    # 版本 2
    print("\n\n" + "=" * 80)
    print("📘 版本 2 - 优化版")
    print("=" * 80)
    with open("../prompts/fortune_reading_v2.md", "r", encoding="utf-8") as f:
        teller.prompts["fortune_reading"] = f.read()

    result_v2 = teller.get_fortune(
        birth_date=case["birth_date"],
        gender=case["gender"],
        direction=case["direction"],
    )
    print(result_v2)

    print("\n\n" + "=" * 80)
    print("💡 对比完成，你觉得哪个版本更好？")
    print("=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运势预测测试工具")
    parser.add_argument("--api-key", required=True, help="API Key")
    parser.add_argument("--mode", default="batch", choices=["batch", "compare"], help="测试模式")
    parser.add_argument("--case", type=int, default=0, help="对比模式下用哪个案例")

    args = parser.parse_args()

    if args.mode == "batch":
        batch_test(args.api_key)
    else:
        compare_prompts(args.api_key, args.case)
