#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
backend/share_image.py（v1 版）补充测试。
该模块依赖 Pillow，无 Pillow 时 generate_share_image 返回 None。
"""

import os
import sys
import tempfile
import unittest
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from backend import share_image


class TestShareImageV1(unittest.TestCase):
    @unittest.skipUnless(PIL_AVAILABLE, "Pillow 未安装，跳过图片生成测试")
    def test_generate_returns_bytesio(self):
        buf = share_image.generate_share_image("第一行\n第二行内容", title="测试标题")
        self.assertIsNotNone(buf)
        self.assertIsInstance(buf, BytesIO)
        buf.seek(0)
        img = Image.open(buf)
        self.assertEqual(img.mode, "RGB")
        self.assertGreater(img.size[0], 0)
        self.assertGreater(img.size[1], 0)

    @unittest.skipUnless(PIL_AVAILABLE, "Pillow 未安装，跳过保存测试")
    def test_save_to_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "share.png")
            share_image.save_share_image("内容文字", path, "标题")
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)

    def test_generate_no_pil_returns_none(self):
        # 无论是否安装 Pillow，行为都应有确定结果
        result = share_image.generate_share_image("x")
        if not PIL_AVAILABLE:
            self.assertIsNone(result)
        else:
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
