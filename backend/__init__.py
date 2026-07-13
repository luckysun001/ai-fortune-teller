# 后端模块初始化
# 统一导出，方便外部使用
from .config import MODEL_CONFIG, PROMPT_VERSIONS, FEATURE_FLAGS, SAFETY_CONFIG
from .logger import logger, request_logger, setup_logger
from .utils import (
    retry,
    timing,
    cached,
    cache,
    FortuneException,
    APIKeyInvalidException,
    APITimeoutException,
    ContentSafetyException,
    RateLimitException,
)
from .fortune_teller import FortuneTeller

__version__ = "2.1.0"
__all__ = [
    # 配置
    "MODEL_CONFIG",
    "PROMPT_VERSIONS",
    "FEATURE_FLAGS",
    "SAFETY_CONFIG",
    # 日志
    "logger",
    "request_logger",
    "setup_logger",
    # 工具
    "retry",
    "timing",
    "cached",
    "cache",
    # 异常
    "FortuneException",
    "APIKeyInvalidException",
    "APITimeoutException",
    "ContentSafetyException",
    "RateLimitException",
    # 核心类
    "FortuneTeller",
]
