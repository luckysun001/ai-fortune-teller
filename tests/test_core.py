#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单元测试
运行方法: python -m pytest tests/test_core.py -v
或者直接运行: python tests/test_core.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from backend.config import validate_config, get_current_config
from backend.utils import calculate_age, LRUCache, retry, ContentModerator
from backend.fortune_teller import FortuneTeller
from backend.logger import logger


class TestConfig(unittest.TestCase):
    """配置测试"""
    
    def test_validate_config(self):
        """测试配置校验"""
        self.assertTrue(validate_config())
    
    def test_get_config(self):
        """测试获取配置"""
        config = get_current_config()
        self.assertIn("version", config)
        self.assertIn("model_config", config)
        self.assertIn("feature_flags", config)


class TestUtils(unittest.TestCase):
    """工具函数测试"""
    
    def test_calculate_age(self):
        """测试年龄计算"""
        # 测试正常情况
        age = calculate_age("1995-03-15")
        self.assertGreaterEqual(age, 30)
        self.assertLessEqual(age, 35)  # 2026 年是 31 岁，留一点余地
        
        # 测试无效日期
        age = calculate_age("invalid-date")
        self.assertEqual(age, 30)  # 默认值
    
    def test_lru_cache(self):
        """测试 LRU 缓存"""
        cache = LRUCache(max_size=3, ttl_seconds=3600)
        
        # 测试基本功能
        cache.set("test", (1, 2), {"a": "b"}, "value1")
        self.assertEqual(cache.get("test", (1, 2), {"a": "b"}), "value1")
        
        # 测试容量限制
        cache.set("test", (2,), {}, "value2")
        cache.set("test", (3,), {}, "value3")
        cache.set("test", (4,), {}, "value4")
        
        self.assertEqual(len(cache.cache), 3)
        
        # 测试统计
        self.assertGreaterEqual(cache.hits, 0)
        self.assertGreaterEqual(cache.misses, 0)
        self.assertIsInstance(cache.hit_rate, float)
        
        # 测试清空
        cache.clear()
        self.assertEqual(len(cache.cache), 0)
    
    def test_content_moderator(self):
        """测试内容安全检查"""
        moderator = ContentModerator(["敏感词1", "敏感词2"])
        
        # 正常内容
        ok, reason = moderator.check_output("这是正常的内容")
        self.assertTrue(ok)
        self.assertIsNone(reason)
        
        # 包含敏感词
        ok, reason = moderator.check_output("这句话包含敏感词1哦")
        self.assertFalse(ok)
        self.assertIsNotNone(reason)
        self.assertIn("敏感词1", reason)
    
    def test_retry_decorator(self):
        """测试重试装饰器"""
        call_count = [0]
        
        @retry(max_attempts=3, delay_seconds=0.01)
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("又失败了")
            return "success"
        
        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 3)


class TestFortuneTeller(unittest.TestCase):
    """核心类测试"""
    
    def setUp(self):
        self.teller = FortuneTeller()  # 不传入 API Key，使用模拟模式
    
    def test_initialization(self):
        """测试初始化"""
        self.assertTrue(self.teller.mock_mode)  # 应该是模拟模式
        self.assertIsNotNone(self.teller.prompts)
        self.assertIn("daily", self.teller.prompts)
        self.assertIn("fortune", self.teller.prompts)
    
    def test_health_check(self):
        """测试健康检查"""
        healthy, message = self.teller.health_check()
        self.assertTrue(healthy)
        self.assertIsInstance(message, str)
    
    def test_daily_fortune(self):
        """测试今日运势（模拟模式）"""
        result = self.teller.get_daily_fortune("1995-03-15")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 100)  # 至少 100 字
        self.assertIn("今日运势", result)
        self.assertIn("幸运色", result)
    
    def test_fortune(self):
        """测试年度运势（模拟模式）"""
        result = self.teller.get_fortune("1995-03-15", "男", "事业")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 500)  # 至少 500 字
        self.assertIn("事业", result)
    
    def test_relation_reading(self):
        """测试两人合盘（模拟模式）"""
        result = self.teller.get_relation_reading(
            "小明", "1995-03-15",
            "小红", "1996-08-20",
            "情侣",
        )
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 300)
        self.assertIn("关系", result)
    
    def test_stats(self):
        """测试统计信息"""
        stats = self.teller.get_stats()
        self.assertIn("version", stats)
        self.assertIn("requests", stats)
        self.assertIn("cache", stats)
        self.assertIn("mock_mode", stats)


def run_tests():
    """运行所有测试"""
    print("=" * 70)
    print("🧪 运行单元测试")
    print("=" * 70)
    
    # 加载测试用例
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestFortuneTeller))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print(f"❌ 有 {len(result.failures) + len(result.errors)} 个测试失败")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
