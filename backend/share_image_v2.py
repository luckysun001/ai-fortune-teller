#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成精美的分享图片
支持多种主题风格，一键生成，方便分享朋友圈
"""

import os
import random
from io import BytesIO
from datetime import datetime
from typing import Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ========== 预设主题 ==========
THEMES = {
    "warm": {
        "name": "温暖橙",
        "bg_gradient": ["#fff1eb", "#ace0f9"],
        "text_color": "#2c3e50",
        "accent_color": "#e67e22",
        "card_bg": "#ffffff",
    },
    "purple": {
        "name": "神秘紫",
        "bg_gradient": ["#a8edea", "#fed6e3"],
        "text_color": "#4a4a6a",
        "accent_color": "#9b59b6",
        "card_bg": "#ffffff",
    },
    "dark": {
        "name": "星空黑",
        "bg_gradient": ["#2c3e50", "#4ca1af"],
        "text_color": "#ecf0f1",
        "accent_color": "#f39c12",
        "card_bg": "rgba(255,255,255,0.1)",
    },
    "green": {
        "name": "清新绿",
        "bg_gradient": ["#d4fc79", "#96e6a1"],
        "text_color": "#27ae60",
        "accent_color": "#16a085",
        "card_bg": "#ffffff",
    },
}

# ========== 幸运语录 ==========
QUOTES = [
    "✨ 好运正在向你走来",
    "🌟 相信自己，你比想象中更强大",
    "🍀 今天会有小惊喜等着你",
    "💫 所有的努力都会有回报",
    "🌈 风雨过后一定会有彩虹",
    "🌙 好好休息，明天又是新的一天",
    "☀️ 保持微笑，好运自然来",
]


def create_gradient_background(width: int, height: int, colors: list) -> Image.Image:
    """创建渐变背景"""
    base = Image.new("RGB", (width, height), colors[0])
    draw = ImageDraw.Draw(base)
    
    # 简单的线性渐变
    r1, g1, b1 = tuple(int(colors[0].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    r2, g2, b2 = tuple(int(colors[1].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    
    for y in range(height):
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return base


def load_font(size: int, font_family: str = "default") -> Optional[ImageFont.FreeTypeFont]:
    """加载字体，支持多种操作系统"""
    if not PIL_AVAILABLE:
        return None
    
    # 尝试的字体路径列表
    font_paths = [
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        # Windows
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    
    # 都找不到就用默认字体
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """自动换行"""
    lines = []
    current_line = ""
    
    # 简单的按字符换行
    for char in text:
        if char == "\n":
            lines.append(current_line)
            current_line = ""
            continue
        
        test_line = current_line + char
        try:
            bbox = font.getbbox(test_line)
            line_width = bbox[2] - bbox[0]
        except:
            line_width = len(test_line) * font.size
        
        if line_width > max_width and current_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line)
    
    return lines


def generate_share_image(
    title: str,
    content: str,
    theme: str = "warm",
    size: Tuple[int, int] = (1080, 1920),
    add_quote: bool = True,
    add_date: bool = True,
) -> Optional[BytesIO]:
    """
    生成精美的分享图片
    
    Args:
        title: 标题
        content: 正文内容
        theme: 主题风格：warm / purple / dark / green
        size: 图片尺寸，默认是手机竖屏 1080x1920
        add_quote: 底部加一句幸运语录
        add_date: 加上日期
    
    Returns:
        图片 BytesIO 对象，可以直接保存或者发送
    """
    if not PIL_AVAILABLE:
        print("⚠️  请先安装 Pillow: pip install pillow")
        return None
    
    theme_config = THEMES.get(theme, THEMES["warm"])
    width, height = size
    
    # 1. 创建渐变背景
    img = create_gradient_background(width, height, theme_config["bg_gradient"])
    draw = ImageDraw.Draw(img)
    
    # 2. 加载字体
    title_font = load_font(56)
    content_font = load_font(32)
    quote_font = load_font(28)
    footer_font = load_font(24)
    
    # 3. 边距设置
    padding = 80
    content_width = width - padding * 2
    y = padding + 100
    
    # 4. 绘制标题
    draw.text((padding, y), title, font=title_font, fill=theme_config["accent_color"])
    y += 100
    
    # 5. 绘制分隔线
    line_width = content_width
    draw.line(
        [(padding, y), (padding + line_width, y)],
        fill=theme_config["accent_color"],
        width=3,
    )
    y += 60
    
    # 6. 绘制内容（自动换行）
    for paragraph in content.split("\n\n"):
        for line in wrap_text(paragraph, content_font, content_width):
            draw.text((padding, y), line, font=content_font, fill=theme_config["text_color"])
            y += 48
        y += 20  # 段落之间的间距
    
    # 7. 防止内容太长，加个安全机制
    if y > height - 300:
        y = height - 300
    
    # 8. 底部语录
    if add_quote:
        y += 40
        quote = random.choice(QUOTES)
        draw.text((padding, y), quote, font=quote_font, fill=theme_config["accent_color"])
        y += 60
    
    # 9. 底部日期和水印
    y += 40
    if add_date:
        date_text = datetime.now().strftime("%Y 年 %m 月 %d 日")
        draw.text((padding, y), date_text, font=footer_font, fill=theme_config["text_color"])
    
    # 10. 右下角水印
    watermark = "🔮 AI 运势预测"
    try:
        bbox = footer_font.getbbox(watermark)
        text_width = bbox[2] - bbox[0]
    except:
        text_width = len(watermark) * footer_font.size
    draw.text(
        (width - padding - text_width, y),
        watermark,
        font=footer_font,
        fill=theme_config["text_color"],
    )
    
    # 11. 保存到 BytesIO
    output = BytesIO()
    img.save(output, format="PNG", quality=95)
    output.seek(0)
    
    return output


def save_share_image(
    output_path: str,
    title: str,
    content: str,
    theme: str = "warm",
    **kwargs,
):
    """保存分享图片到文件"""
    img_io = generate_share_image(title, content, theme, **kwargs)
    if img_io:
        with open(output_path, "wb") as f:
            f.write(img_io.getvalue())
        print(f"✅ 图片已保存到: {output_path}")


# ========== 简单测试 ==========
if __name__ == "__main__":
    test_content = """
今年你的事业运整体向上，特别是上半年，会有不错的机会出现。

这一年是「积累和准备」的一年，不要着急爆发。你现在做的每一件小事，未来都会成倍地回报你。

适合稳扎稳打，不适合冒进。如果有换工作或者创业的想法，建议下半年再考虑。

记住：你不需要一开始就很厉害，但是你需要开始，才能变得很厉害。
    """.strip()
    
    # 测试所有主题
    for theme_name in THEMES.keys():
        save_share_image(
            f"test_share_{theme_name}.png",
            "✨ 年度运势 · 中吉",
            test_content,
            theme=theme_name,
        )
    
    print("\n✅ 所有测试图片生成完成！")
