#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成分享图片 - 把测算结果做成好看的卡片，方便分享到朋友圈
"""

import os
from io import BytesIO
from datetime import datetime


def generate_share_image(content: str, title: str = "AI 运势预测") -> BytesIO:
    """
    生成分享图片

    Args:
        content: 测算内容
        title: 标题

    Returns:
        图片 BytesIO 对象，可以直接保存或者发送

    依赖：pip install pillow
    """

    try:
        from PIL import Image, ImageDraw, ImageFont

        # 图片尺寸 - 手机朋友圈比例
        WIDTH = 1080
        PADDING = 80

        # 粗略估算高度（每行约 40 像素）
        lines = content.split("\n")
        HEIGHT = len(lines) * 40 + PADDING * 3 + 150

        # 创建画布 - 渐变色背景
        img = Image.new("RGB", (WIDTH, HEIGHT), "#f8f5f0")
        draw = ImageDraw.Draw(img)

        # 尝试加载字体，如果找不到就用默认
        try:
            # 常见的中文字体路径
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "C:/Windows/Fonts/msyh.ttc",  # Windows
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            ]

            font_path = None
            for p in font_paths:
                if os.path.exists(p):
                    font_path = p
                    break

            if font_path:
                title_font = ImageFont.truetype(font_path, 48)
                content_font = ImageFont.truetype(font_path, 28)
                footer_font = ImageFont.truetype(font_path, 24)
            else:
                raise FileNotFoundError("找不到中文字体")

        except Exception:
            # 用默认字体，可能中文显示有问题，但是至少不会崩溃
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # 画标题
        draw.text((PADDING, PADDING), title, font=title_font, fill="#2c3e50")

        # 画一条分隔线
        draw.line(
            [(PADDING, PADDING + 80), (WIDTH - PADDING, PADDING + 80)],
            fill="#d4c5b0",
            width=2,
        )

        # 画内容
        y = PADDING + 120
        line_height = 40

        for line in content.split("\n"):
            # 简单的换行处理
            if len(line) > 45:
                # 长句子换行
                for i in range(0, len(line), 45):
                    draw.text((PADDING, y), line[i:i+45], font=content_font, fill="#34495e")
                    y += line_height
            else:
                draw.text((PADDING, y), line, font=content_font, fill="#34495e")
                y += line_height

            # 标题和正文之间多空一点
            if line.startswith("##"):
                y += 10

        # 画底部
        y += 30
        draw.line(
            [(PADDING, y), (WIDTH - PADDING, y)],
            fill="#d4c5b0",
            width=2,
        )

        y += 30
        footer_text = f"🔮 AI 运势预测 · {datetime.now().strftime('%Y-%m-%d')}"
        draw.text((PADDING, y), footer_text, font=footer_font, fill="#7f8c8d")

        y += 40
        slogan = "仅供娱乐 · 命运掌握在自己手中"
        draw.text((PADDING, y), slogan, font=footer_font, fill="#95a5a6")

        # 保存到 BytesIO
        output = BytesIO()
        img.save(output, format="PNG", quality=95)
        output.seek(0)

        return output

    except ImportError:
        print("⚠️ 请先安装 Pillow：pip install pillow")
        return None


def save_share_image(content: str, output_path: str, title: str = "AI 运势预测"):
    """保存分享图片到文件"""
    img_io = generate_share_image(content, title)
    if img_io:
        with open(output_path, "wb") as f:
            f.write(img_io.getvalue())
        print(f"✅ 图片已保存到：{output_path}")


if __name__ == "__main__":
    # 测试
    test_content = """
## 整体基调

你给人的第一印象是一个很踏实、很靠谱的人。
表面上看起来你很冷静，好像什么都不在乎，但其实内心很敏感，很在意别人的看法。

这一年整体能量是向上的，是积累和准备的一年。
不要着急，你现在做的每一件事，未来都会有回报。

## 事业运

今年你的事业运不错，有贵人运。
特别是上半年，容易遇到赏识你的人。
但是要注意，不要太急着表现自己，稳一点，把基础打牢。

下半年会有一些变动的机会，可能是换工作，可能是升职。
到时候不要犹豫，该出手时就出手。

## 给你的建议

1. 今年多跟比你年长的人聊天，他们能给你很多有用的建议
2. 少熬夜，身体是革命的本钱
3. 每个月存一点钱，年底你会有惊喜的

## 最后想对你说

25 岁是最好的年纪，不要着急，不要焦虑。
你想要的，岁月都会给你。
慢慢来，比较快。
    """.strip()

    save_share_image(test_content, "test_share.png", "25岁 · 年度运势")
