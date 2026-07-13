#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分享图片生成模块测试
运行方法: python -m pytest tests/test_share_image.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from io import BytesIO

# 尝试导入 PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 导入被测模块
from backend.share_image_v2 import (
    THEMES,
    QUOTES,
    create_gradient_background,
    load_font,
    wrap_text,
    generate_share_image,
    PIL_AVAILABLE as MODULE_PIL_AVAILABLE,
)


class TestThemes(unittest.TestCase):
    """主题配置测试"""

    def test_theme_count(self):
        """应有 4 个预设主题"""
        self.assertGreaterEqual(len(THEMES), 4)

    def test_theme_keys(self):
        """应包含 warm/purple/dark/green 主题"""
        for key in ["warm", "purple", "dark", "green"]:
            self.assertIn(key, THEMES)

    def test_theme_structure(self):
        """每个主题应包含必要字段"""
        for key, theme in THEMES.items():
            self.assertIn("name", theme, f"主题 {key} 缺少 name")
            self.assertIn("bg_gradient", theme, f"主题 {key} 缺少 bg_gradient")
            self.assertIn("text_color", theme, f"主题 {key} 缺少 text_color")
            self.assertIn("accent_color", theme, f"主题 {key} 缺少 accent_color")
            self.assertEqual(len(theme["bg_gradient"]), 2, f"主题 {key} 的 bg_gradient 应有 2 个颜色")


class TestQuotes(unittest.TestCase):
    """幸运语录测试"""

    def test_quotes_not_empty(self):
        """语录列表不应为空"""
        self.assertGreater(len(QUOTES), 0)

    def test_quotes_are_strings(self):
        """每条语录应为字符串"""
        for quote in QUOTES:
            self.assertIsInstance(quote, str)
            self.assertGreater(len(quote), 0)


@unittest.skipUnless(PIL_AVAILABLE, "Pillow 未安装，跳过图片生成测试")
class TestGradientBackground(unittest.TestCase):
    """渐变背景生成测试"""

    def test_create_gradient_basic(self):
        """应生成正确尺寸的图片"""
        img = create_gradient_background(400, 600, ["#fff1eb", "#ace0f9"])
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (400, 600))
        self.assertEqual(img.mode, "RGB")

    def test_create_gradient_different_colors(self):
        """不同颜色应生成不同图片"""
        img1 = create_gradient_background(100, 100, ["#000000", "#ffffff"])
        img2 = create_gradient_background(100, 100, ["#ff0000", "#00ff00"])
        # 像素应不同
        pixel1 = img1.getpixel((50, 50))
        pixel2 = img2.getpixel((50, 50))
        self.assertNotEqual(pixel1, pixel2)

    def test_create_gradient_gradient_progression(self):
        """渐变应从上到下变化"""
        img = create_gradient_background(10, 100, ["#000000", "#ffffff"])
        top_pixel = img.getpixel((5, 1))
        bottom_pixel = img.getpixel((5, 99))
        # 底部应比顶部更亮
        self.assertGreater(sum(bottom_pixel), sum(top_pixel))


@unittest.skipUnless(PIL_AVAILABLE, "Pillow 未安装，跳过字体测试")
class TestLoadFont(unittest.TestCase):
    """字体加载测试"""

    def test_load_font_returns_font(self):
        """应返回一个字体对象"""
        font = load_font(32)
        self.assertIsNotNone(font)

    def test_load_font_different_sizes(self):
        """不同大小应返回不同字体"""
        font_small = load_font(16)
        font_large = load_font(64)
        self.assertIsNotNone(font_small)
        self.assertIsNotNone(font_large)


@unittest.skipUnless(PIL_AVAILABLE, "Pillow 未安装，跳过换行测试")
class TestWrapText(unittest.TestCase):
    """文本换行测试"""

    def test_wrap_short_text(self):
        """短文本不需要换行"""
        font = load_font(32)
        lines = wrap_text("hello", font, 1000)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "hello")

    def test_wrap_long_text(self):
        """长文本应被换行"""
        font = load_font(32)
        long_text = "a" * 200
        lines = wrap_text(long_text, font, 100)
        self.assertGreater(len(lines), 1)

    def test_wrap_text_with_newlines(self):
        """包含换行符的文本应保留换行"""
        font = load_font(32)
        lines = wrap_text("line1\nline2", font, 1000)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "line1")
        self.assertEqual(lines[1], "line2")


@unittest.skipUnless(PIL_AVAILABLE, "Pillow 未安装，跳过图片生成测试")
class TestGenerateShareImage(unittest.TestCase):
    """分享图片生成测试"""

    def test_generate_basic_image(self):
        """应生成基本的分享图片"""
        result = generate_share_image(
            title="今日运势",
            content="这是一段测试内容，用于验证图片生成功能是否正常工作。",
            theme="warm",
            size=(400, 800),
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BytesIO)

        # 验证是有效的图片
        result.seek(0)
        img = Image.open(result)
        self.assertEqual(img.size, (400, 800))

    def test_generate_with_different_themes(self):
        """不同主题都应正常生成"""
        for theme in ["warm", "purple", "dark", "green"]:
            result = generate_share_image(
                title="测试标题",
                content="测试内容",
                theme=theme,
                size=(400, 600),
                add_quote=False,
                add_date=False,
            )
            self.assertIsNotNone(result, f"主题 {theme} 生成失败")

    def test_generate_with_quote(self):
        """添加语录应正常"""
        result = generate_share_image(
            title="测试",
            content="内容",
            theme="warm",
            size=(400, 800),
            add_quote=True,
            add_date=False,
        )
        self.assertIsNotNone(result)

    def test_generate_with_date(self):
        """添加日期应正常"""
        result = generate_share_image(
            title="测试",
            content="内容",
            theme="green",
            size=(400, 800),
            add_quote=False,
            add_date=True,
        )
        self.assertIsNotNone(result)

    def test_generate_invalid_theme_falls_back(self):
        """无效主题应回退到 warm"""
        result = generate_share_image(
            title="测试",
            content="内容",
            theme="nonexistent_theme",
            size=(400, 600),
            add_quote=False,
            add_date=False,
        )
        self.assertIsNotNone(result)

    def test_generate_empty_content(self):
        """空内容不应崩溃"""
        result = generate_share_image(
            title="标题",
            content="",
            theme="warm",
            size=(400, 600),
        )
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
