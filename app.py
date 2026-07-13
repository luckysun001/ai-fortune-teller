#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI 运势预测 - 完整版 v3.1
✅ 流式输出
✅ 分享图片生成（4 种主题）
✅ 更好的交互体验
✅ 一键复制
✅ 历史记录
"""

import sys
import os
import time
import random

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

import streamlit as st
from datetime import datetime

# 尝试导入新版核心类
try:
    from backend.fortune_teller_v2 import FortuneTeller
except ImportError:
    from backend.fortune_teller import FortuneTeller

# 尝试导入分享图片功能
try:
    from backend.share_image_v2 import generate_share_image, THEMES
    SHARE_IMAGE_AVAILABLE = True
except ImportError:
    SHARE_IMAGE_AVAILABLE = False

st.set_page_config(
    page_title="AI 运势预测",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 自定义 CSS
st.markdown("""
<style>
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .thinking {
        animation: pulse 1.5s ease-in-out infinite;
    }
    .stButton>button {
        border-radius: 20px;
        height: 3em;
        font-weight: 600;
    }
    .result-card {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== 工具函数 ==========
def stream_output(text: str, speed: float = 0.008):
    """打字机效果输出"""
    output_placeholder = st.empty()
    current_text = ""
    
    for char in text:
        current_text += char
        output_placeholder.markdown(current_text)
        time.sleep(speed)
    
    return output_placeholder

# 随机加载文案
LOADING_MESSAGES = [
    "🔮 正在连接宇宙能量...",
    "📅 正在查看你的星盘...",
    "✨ 正在为你解读运势...",
    "🧘 深呼吸，答案马上就来...",
    "🌙 正在询问月亮的意见...",
    "⭐ 正在收集星光...",
    "🍀 正在召唤好运...",
]

# 初始化 session state
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("⚙️ 设置")
    
    api_key = st.text_input("API Key", type="password", help="DeepSeek / OpenAI API Key")
    model = st.text_input("模型名称", value="deepseek-chat")
    
    prompt_version = st.selectbox(
        "Prompt 版本",
        ["v2 (优化版)", "v1 (基础版)"],
    )
    
    st.markdown("---")
    
    st.subheader("🎮 体验设置")
    streaming_enabled = st.checkbox("启用流式输出", value=True, help="打字机效果，体验更好")
    
    if SHARE_IMAGE_AVAILABLE:
        share_theme = st.selectbox(
            "分享图片主题",
            [f"{v['name']} ({k})" for k, v in THEMES.items()],
            help="生成分享图片的配色方案",
        )
        # 提取 key
        share_theme_key = share_theme.split("(")[-1].rstrip(")")
    else:
        share_theme_key = "warm"
        st.info("📷 安装 Pillow 后可以使用分享图片功能")
    
    st.markdown("---")
    
    # 快速体验按钮
    st.subheader("⚡ 快速体验")
    if st.button("🎲 随机算一卦", use_container_width=True):
        # 随机生成一个出生日期
        import random
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        st.session_state.random_birth = f"1995-{month:02d}-{day:02d}"
        st.experimental_rerun()

# ========== 主标题 ==========
st.title("🔮 AI 运势预测")
st.markdown("> 懂你的运势解读，温暖、有智慧、给你方向")

# 演示模式提示
if not api_key:
    st.warning("👋 你现在在 **演示模式**，使用的是预设的高质量模拟数据。输入 API Key 可以获得真实的 AI 解读。")

# 快速填充
if st.session_state.get("random_birth"):
    st.info(f"🎲 随机出生日期：{st.session_state.random_birth}")
    del st.session_state.random_birth

st.markdown("---")

# ========== 功能 Tab ==========
tab1, tab2, tab3, tab4 = st.tabs(
    ["📅 今日运势", "🔮 年度运势", "💑 两人合盘", "📜 历史记录"]
)

# ========== 公共的结果显示函数 ==========
def show_result_actions(result: str, title: str):
    """显示结果后的操作按钮"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 复制结果", use_container_width=True):
            st.code(result, language="markdown")
            st.toast("✅ 已复制到剪贴板")
    
    with col2:
        if SHARE_IMAGE_AVAILABLE and st.button("📷 生成分享图", use_container_width=True):
            with st.spinner("正在生成分享图片..."):
                img_io = generate_share_image(
                    title=f"✨ {title}",
                    content=result[:500] + "..." if len(result) > 500 else result,
                    theme=share_theme_key,
                )
                if img_io:
                    st.image(img_io, caption="长按图片保存分享")
                    st.download_button(
                        label="💾 下载图片",
                        data=img_io,
                        file_name=f"运势_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                else:
                    st.error("生成图片失败")
    
    with col3:
        if st.button("💖 感觉很准", use_container_width=True):
            st.balloons()
            st.toast("谢谢你的认可！祝你好运 🍀")

# ========== 今日运势 ==========
with tab1:
    st.subheader("今日运势卡片")
    
    birth_date = st.date_input("你的出生日期", key="daily_birth")
    
    if st.button("✨ 生成今日运势", use_container_width=True):
        loading_msg = random.choice(LOADING_MESSAGES)
        with st.spinner(loading_msg):
            time.sleep(1)
        
        teller = FortuneTeller(api_key=api_key if api_key else None)
        result = teller.get_daily_fortune(birth_date.strftime("%Y-%m-%d"))
        
        # 显示结果
        st.markdown("---")
        with st.container():
            if streaming_enabled:
                stream_output(result)
            else:
                st.markdown(result)
        
        # 保存到历史
        st.session_state.last_result = result
        st.session_state.history.insert(0, {
            "type": "今日运势",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": result,
        })
        
        # 操作按钮
        show_result_actions(result, "今日运势")

# ========== 年度运势 ==========
with tab2:
    st.subheader("年度详细运势解读")
    
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("出生日期", key="fortune_birth")
    with col2:
        gender = st.selectbox("性别", ["男", "女"], key="fortune_gender")
    
    direction = st.selectbox(
        "测算方向",
        ["综合", "事业", "感情", "财运", "健康"],
        key="fortune_direction",
    )
    
    if st.button("🔮 开始测算", use_container_width=True):
        loading_msg = random.choice(LOADING_MESSAGES)
        with st.spinner(loading_msg):
            time.sleep(1.5)
        
        teller = FortuneTeller(api_key=api_key if api_key else None)
        result = teller.get_fortune(
            birth_date.strftime("%Y-%m-%d"),
            gender,
            direction,
        )
        
        # 显示结果
        st.markdown("---")
        with st.container():
            if streaming_enabled:
                stream_output(result)
            else:
                st.markdown(result)
        
        # 保存到历史
        st.session_state.last_result = result
        st.session_state.history.insert(0, {
            "type": f"{direction}运势",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": result,
        })
        
        # 操作按钮
        show_result_actions(result, f"{direction}运势")

# ========== 两人合盘 ==========
with tab3:
    st.subheader("两人关系合盘分析")
    
    st.markdown("#### 第一个人")
    col1, col2 = st.columns(2)
    with col1:
        name_a = st.text_input("称呼", value="小明", key="rel_name_a")
    with col2:
        birth_a = st.date_input("出生日期", key="rel_birth_a")
    
    st.markdown("#### 第二个人")
    col1, col2 = st.columns(2)
    with col1:
        name_b = st.text_input("称呼", value="小红", key="rel_name_b")
    with col2:
        birth_b = st.date_input("出生日期", key="rel_birth_b")
    
    relation_type = st.selectbox(
        "关系类型",
        ["情侣", "夫妻", "合伙人", "朋友"],
        key="rel_type",
    )
    
    if st.button("💞 开始分析", use_container_width=True):
        loading_msg = random.choice(LOADING_MESSAGES)
        with st.spinner(loading_msg):
            time.sleep(1.5)
        
        teller = FortuneTeller(api_key=api_key if api_key else None)
        result = teller.get_relation_reading(
            name_a,
            birth_a.strftime("%Y-%m-%d"),
            name_b,
            birth_b.strftime("%Y-%m-%d"),
            relation_type,
        )
        
        # 显示结果
        st.markdown("---")
        with st.container():
            if streaming_enabled:
                stream_output(result)
            else:
                st.markdown(result)
        
        # 保存到历史
        st.session_state.last_result = result
        st.session_state.history.insert(0, {
            "type": f"{relation_type}合盘",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": result,
        })
        
        # 操作按钮
        show_result_actions(result, f"{relation_type}合盘")

# ========== 历史记录 ==========
with tab4:
    st.subheader("本地历史记录")
    
    if not st.session_state.history:
        st.info("📜 还没有测算记录，快去试试吧！")
        
        # 加几个引导按钮
        st.markdown("---")
        st.markdown("### 🎯 你可以先试试：")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("📅 **今日运势** - 看看今天的运气怎么样")
        with col2:
            st.info("🔮 **年度运势** - 深度解读一整年的运势走向")
    else:
        for i, record in enumerate(st.session_state.history[:10]):
            with st.expander(f"[{record['time']}] {record['type']}", expanded=(i == 0)):
                st.markdown(record["content"])
                
                # 每条历史记录也有操作按钮
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 复制", key=f"copy_{i}", use_container_width=True):
                        st.code(record["content"])
                with col2:
                    if SHARE_IMAGE_AVAILABLE and st.button(f"📷 生成图片", key=f"share_{i}", use_container_width=True):
                        with st.spinner("正在生成..."):
                            img_io = generate_share_image(
                                title=f"✨ {record['type']}",
                                content=record["content"][:500] + "...",
                                theme=share_theme_key,
                            )
                            if img_io:
                                st.image(img_io)
        
        if len(st.session_state.history) > 0:
            st.markdown("---")
            if st.button("🗑️ 清空历史记录", use_container_width=True):
                st.session_state.history = []
                st.experimental_rerun()

# ========== 页脚 ==========
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #888; font-size: 13px; line-height: 1.8;">
    ⚠️ 本工具仅供娱乐，所有内容由 AI 生成，不构成任何人生建议<br>
    💖 三分天注定，七分靠打拼，命运掌握在自己手中<br>
    祝你好运 🍀
</div>
    """,
    unsafe_allow_html=True,
)
