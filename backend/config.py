#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理 - v2 优化版
✅ 支持环境变量覆盖
✅ 配置校验
✅ 类型安全
"""

import os
from typing import Dict, Any

# ========== 模型配置 ==========
MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    "default": {
        "model": os.getenv("FORTUNE_MODEL", "deepseek-chat"),
        "base_url": os.getenv("FORTUNE_BASE_URL", "https://api.deepseek.com"),
        "temperature": float(os.getenv("FORTUNE_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("FORTUNE_MAX_TOKENS", "2048")),
        "timeout": int(os.getenv("FORTUNE_TIMEOUT", "30")),
    },
    "gpt-3.5": {
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "creative": {
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "temperature": 0.9,
        "max_tokens": 2048,
    },
    "conservative": {
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "temperature": 0.5,
        "max_tokens": 2048,
    },
}

# ========== Prompt 版本配置 ==========
PROMPT_VERSIONS: Dict[str, Dict[str, str]] = {
    "fortune": {
        "v1": "prompts/fortune_reading.md",
        "v2": "prompts/fortune_reading_v2.md",
        "latest": "prompts/fortune_reading_v2.md",
    },
    "daily": {
        "v1": "prompts/daily_fortune.md",
        "latest": "prompts/daily_fortune.md",
    },
    "relation": {
        "v1": "prompts/relation_reading.md",
        "latest": "prompts/relation_reading.md",
    },
}

# ========== 功能开关 ==========
FEATURE_FLAGS: Dict[str, bool] = {
    "stream_output": os.getenv("FEATURE_STREAM", "true").lower() == "true",
    "share_image": os.getenv("FEATURE_SHARE", "true").lower() == "true",
    "history": os.getenv("FEATURE_HISTORY", "true").lower() == "true",
    "user_auth": os.getenv("FEATURE_AUTH", "false").lower() == "true",
    "moderation": os.getenv("FEATURE_MODERATION", "true").lower() == "true",
}

# ========== 限流配置 ==========
RATE_LIMIT_CONFIG: Dict[str, int] = {
    "max_requests_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "30")),
    "max_tokens_per_minute": int(os.getenv("RATE_LIMIT_TOKENS", "100000")),
    "max_requests_per_user_per_day": int(os.getenv("RATE_LIMIT_PER_USER_DAY", "50")),
}

# ========== 缓存配置 ==========
CACHE_CONFIG: Dict[str, Any] = {
    "enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
    "ttl_seconds": int(os.getenv("CACHE_TTL", "3600")),
    "max_size": int(os.getenv("CACHE_MAX_SIZE", "1000")),
}

# ========== 内容安全配置 ==========
SAFETY_CONFIG: Dict[str, Any] = {
    "enable_moderation": os.getenv("SAFETY_MODERATION", "true").lower() == "true",
    "blocked_keywords": [
        # 医疗相关
        "治病", "治疗", "药方", "偏方", "医院", "医生",
        # 投资相关
        "股票", "基金", "理财", "投资", "赌博", "彩票",
        # 违法相关
        "自杀", "自残", "暴力", "恐怖", "犯罪",
        # 注: 政治敏感词请根据部署环境的法律法规要求，
        # 在 SAFETY_CONFIG 环境变量或外部配置文件中自行配置
    ],
    "max_output_length": int(os.getenv("SAFETY_MAX_OUTPUT", "5000")),
    "min_output_length": int(os.getenv("SAFETY_MIN_OUTPUT", "100")),
}

# ========== 提示文案 ==========
TEXTS: Dict[str, Any] = {
    "loading_messages": [
        "🔮 正在连接宇宙能量...",
        "📅 正在查看你的星盘...",
        "✨ 正在为你解读运势...",
        "🧘 深呼吸，答案马上就来...",
        "🌙 正在询问月亮的意见...",
        "⭐ 正在收集星光...",
        "🍀 正在召唤好运...",
    ],
    "disclaimer": "⚠️ 本工具仅供娱乐，所有内容由 AI 生成，不构成任何人生建议",
    "footer": "💖 三分天注定，七分靠打拼，命运掌握在自己手中",
    "quotes": [
        "✨ 好运正在向你走来",
        "🌟 相信自己，你比想象中更强大",
        "🍀 今天会有小惊喜等着你",
        "💫 所有的努力都会有回报",
        "🌈 风雨过后一定会有彩虹",
        "🌙 好好休息，明天又是新的一天",
        "☀️ 保持微笑，好运自然来",
    ],
}


def validate_config() -> bool:
    """
    校验配置是否合法
    Returns: True 如果配置合法
    Raises: ValueError 如果配置有问题
    """
    # 校验温度范围
    for name, config in MODEL_CONFIG.items():
        if not 0 <= config["temperature"] <= 2:
            raise ValueError(
                f"模型 {name} 的 temperature 必须在 0-2 之间，当前是 {config['temperature']}"
            )
    
    # 校验缓存 TTL
    if CACHE_CONFIG["ttl_seconds"] < 0:
        raise ValueError("缓存 TTL 不能为负数")
    
    # 校验缓存大小
    if CACHE_CONFIG["max_size"] < 1:
        raise ValueError("缓存大小必须大于 0")
    
    return True


def get_current_config() -> Dict[str, Any]:
    """获取当前的完整配置（用于调试和监控）"""
    return {
        "version": "2.1.0",
        "model_config": MODEL_CONFIG,
        "feature_flags": FEATURE_FLAGS,
        "cache_config": CACHE_CONFIG,
        "safety_config": SAFETY_CONFIG,
        "rate_limit": RATE_LIMIT_CONFIG,
    }


# 启动时自动校验配置
try:
    validate_config()
except ValueError as e:
    import warnings
    warnings.warn(f"配置校验警告: {e}", RuntimeWarning)
