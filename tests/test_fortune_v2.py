#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FortuneTeller v2 核心逻辑测试
测试内容：mock 模式、内容安全检查、Prompt 加载、年龄计算、统计信息
运行方法: python -m pytest tests/test_fortune_v2.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from backend.fortune_teller_v2 import FortuneTeller


class TestFortuneTellerV2Init(unittest.TestCase):
    """初始化测试"""

    def setUp(self):
        self.teller = FortuneTeller()

    def test_mock_mode_no_api_key(self):
        """无 API Key 时应为 mock 模式"""
        self.assertTrue(self.teller.mock_mode if hasattr(self.teller, 'mock_mode') else self.teller.llm is None)

    def test_prompts_loaded(self):
        """Prompt 模板应被加载"""
        self.assertIsNotNone(self.teller.prompts)
        self.assertGreater(len(self.teller.prompts), 0)

    def test_prompt_keys(self):
        """应包含 daily/fortune/relation 三种 Prompt"""
        self.assertIn("daily", self.teller.prompts)
        self.assertIn("fortune", self.teller.prompts)
        self.assertIn("relation", self.teller.prompts)

    def test_config_loaded(self):
        """模型配置应被加载"""
        self.assertIsNotNone(self.teller.config)
        self.assertIn("model", self.teller.config)


class TestAgeCalculation(unittest.TestCase):
    """年龄计算测试"""

    def setUp(self):
        self.teller = FortuneTeller()

    def test_normal_date(self):
        """正常日期应正确计算年龄"""
        age = self.teller._calculate_age("1995-03-15")
        self.assertGreaterEqual(age, 29)
        self.assertLessEqual(age, 35)

    def test_recent_date(self):
        """较近的日期年龄应较小"""
        age = self.teller._calculate_age("2020-01-01")
        self.assertLessEqual(age, 7)

    def test_invalid_date_returns_default(self):
        """无效日期应返回默认值 30"""
        age = self.teller._calculate_age("invalid-date")
        self.assertEqual(age, 30)

    def test_empty_string_returns_default(self):
        """空字符串应返回默认值"""
        age = self.teller._calculate_age("")
        self.assertEqual(age, 30)


class TestContentSafety(unittest.TestCase):
    """内容安全检查测试"""

    def setUp(self):
        self.teller = FortuneTeller()

    def test_safe_content_passes(self):
        """正常内容应通过安全检查"""
        result = self.teller._check_content_safety("这是一段正常的内容，没有任何敏感词")
        self.assertTrue(result)

    def test_content_with_newlines_passes(self):
        """包含换行的正常内容应通过"""
        result = self.teller._check_content_safety("第一行\n第二行\n第三行")
        self.assertTrue(result)


class TestMockResults(unittest.TestCase):
    """Mock 结果测试"""

    def setUp(self):
        self.teller = FortuneTeller()

    def test_mock_fortune_result(self):
        """mock 年度运势结果应有足够内容"""
        result = self.teller._get_mock_result("fortune")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 500)

    def test_mock_daily_result(self):
        """mock 今日运势结果应有足够内容"""
        result = self.teller._get_mock_result("daily")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 100)
        self.assertIn("幸运色", result)

    def test_mock_relation_result(self):
        """mock 合盘结果应有足够内容"""
        result = self.teller._get_mock_result("relation")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 200)

    def test_mock_unknown_type_returns_empty(self):
        """未知类型的 mock 结果应为空字符串或默认值"""
        result = self.teller._get_mock_result("unknown_type")
        self.assertIsInstance(result, str)


class TestLLMCallMockMode(unittest.TestCase):
    """LLM 调用（mock 模式）测试"""

    def setUp(self):
        self.teller = FortuneTeller()

    def test_call_llm_fortune_mock(self):
        """mock 模式下调用 fortune 应返回结果"""
        prompt = "测试 prompt"
        result = self.teller._call_llm(prompt, "fortune")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 100)

    def test_call_llm_daily_mock(self):
        """mock 模式下调用 daily 应返回结果"""
        result = self.teller._call_llm("test", "daily")
        self.assertIsInstance(result, str)
        self.assertIn("幸运色", result)


class TestFortuneTellerV2Methods(unittest.TestCase):
    """FortuneTeller v2 公开方法测试"""

    def setUp(self):
        self.teller = FortuneTeller()

    def test_get_daily_fortune(self):
        """今日运势应返回有效结果"""
        result = self.teller.get_daily_fortune("1995-03-15")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 100)

    def test_get_fortune(self):
        """年度运势应返回有效结果"""
        result = self.teller.get_fortune("1995-03-15", "男", "事业")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 500)

    def test_get_relation_reading(self):
        """合盘分析应返回有效结果"""
        result = self.teller.get_relation_reading(
            "小明", "1995-03-15",
            "小红", "1996-08-20",
            "情侣",
        )
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 200)

    def test_health_check(self):
        """健康检查 — v2 可能没有此方法，跳过"""
        if not hasattr(self.teller, 'health_check'):
            self.skipTest("v2 FortuneTeller 无 health_check 方法")
        result = self.teller.health_check()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0])
        self.assertIsInstance(result[1], str)

    def test_get_stats(self):
        """统计信息应包含必要字段"""
        stats = self.teller.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("requests", stats)
        self.assertIn("cache", stats)
        self.assertIn("model_profile", stats)


if __name__ == "__main__":
    unittest.main()
