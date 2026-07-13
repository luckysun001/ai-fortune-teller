#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具函数库 - v2 优化版
✅ 完整的类型提示
✅ 更好的错误处理
✅ 可观测性增强
✅ 性能优化
"""

import time
import hashlib
import json
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple
from collections import OrderedDict

from .logger import logger

# ========== 自定义异常 ==========
class FortuneException(Exception):
    """基础异常类"""
    code: str = "UNKNOWN_ERROR"
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class APIKeyInvalidException(FortuneException):
    """API Key 无效"""
    code = "INVALID_API_KEY"


class APITimeoutException(FortuneException):
    """API 调用超时"""
    code = "API_TIMEOUT"


class ContentSafetyException(FortuneException):
    """内容安全审核不通过"""
    code = "CONTENT_SAFETY_BLOCKED"


class RateLimitException(FortuneException):
    """触发限流"""
    code = "RATE_LIMIT_EXCEEDED"


class ConfigurationException(FortuneException):
    """配置错误"""
    code = "CONFIGURATION_ERROR"


# ========== 重试装饰器 ==========
def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Exception, ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None,
):
    """
    重试装饰器 - 带指数退避
    
    Args:
        max_attempts: 最大重试次数
        delay_seconds: 初始等待时间
        backoff: 每次重试的时间倍数
        exceptions: 需要重试的异常类型
        on_retry: 重试回调函数，参数是 (重试次数, 异常)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            delay = delay_seconds
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts:
                        logger.warning(
                            f"⚠️  {func.__name__} 第 {attempt}/{max_attempts} 次失败, "
                            f"{delay:.1f}s 后重试: {e}"
                        )
                        
                        if on_retry:
                            on_retry(attempt, e)
                        
                        time.sleep(delay)
                        delay *= backoff
                    else:
                        logger.error(
                            f"❌ {func.__name__} 重试 {max_attempts} 次全部失败"
                        )
            
            raise last_exception  # type: ignore
        return wrapper
    return decorator


# ========== 计时装饰器 ==========
def timing(func: Callable):
    """统计函数执行时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            if elapsed > 1000:  # 超过 1 秒才打日志
                logger.debug(f"⏱️  {func.__name__} 耗时: {elapsed:.1f}ms")
    return wrapper


# ========== LRU 缓存 ==========
class LRUCache:
    """
    线程安全的 LRU 缓存（简单实现）
    
    支持：
    - 自动过期
    - 最大容量限制
    - 统计信息
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int = 3600,
        enabled: bool = True,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        
        # 统计
        self.hits = 0
        self.misses = 0
        
    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """根据函数参数生成缓存 key"""
        # 只序列化可 JSON 序列化的参数
        def is_serializable(v: Any) -> bool:
            try:
                json.dumps(v)
                return True
            except (TypeError, ValueError):
                return False
        
        serializable_kwargs = {
            k: v for k, v in kwargs.items()
            if is_serializable(v)
        }
        
        key_str = f"{func_name}:{args}:{json.dumps(serializable_kwargs, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(
        self,
        func_name: str,
        args: tuple,
        kwargs: dict,
    ) -> Optional[Any]:
        """
        获取缓存
        
        Returns:
            缓存的值，如果不存在或已过期返回 None
        """
        if not self.enabled:
            return None
        
        key = self._make_key(func_name, args, kwargs)
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, timestamp = self.cache[key]
        
        # 检查是否过期
        if time.time() - timestamp > self.ttl_seconds:
            del self.cache[key]
            logger.debug("🗑️ 缓存已过期")
            self.misses += 1
            return None
        
        # 移到最后（表示最近使用过）
        self.cache.move_to_end(key)
        self.hits += 1
        logger.debug(f"✅ 命中缓存 (hit_rate: {self.hit_rate:.1%})")
        return value
    
    def set(
        self,
        func_name: str,
        args: tuple,
        kwargs: dict,
        value: Any,
    ):
        """设置缓存"""
        if not self.enabled:
            return
        
        key = self._make_key(func_name, args, kwargs)
        
        self.cache[key] = (value, time.time())
        self.cache.move_to_end(key)
        
        # 超过最大容量，删掉最老的
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
            logger.debug("🗑️ 缓存已满，删除最旧条目")
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("🗑️ 缓存已清空")
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "enabled": self.enabled,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate:.1%}",
        }


# 全局缓存实例
from .config import CACHE_CONFIG
cache = LRUCache(
    max_size=CACHE_CONFIG["max_size"],
    ttl_seconds=CACHE_CONFIG["ttl_seconds"],
    enabled=CACHE_CONFIG["enabled"],
)


def cached(func: Callable):
    """缓存装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 先尝试从缓存拿
        cached_value = cache.get(func.__name__, args, kwargs)
        if cached_value is not None:
            return cached_value
        
        # 缓存没有，真正执行
        result = func(*args, **kwargs)
        
        # 保存到缓存
        cache.set(func.__name__, args, kwargs, result)
        
        return result
    return wrapper


# ========== 内容安全检查 ==========
class ContentModerator:
    """内容安全检查器"""
    
    def __init__(self, blocked_keywords: list):
        self.blocked_keywords = blocked_keywords
    
    def check_output(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        检查输出内容是否安全
        
        Returns:
            (是否安全, 不安全的原因)
        """
        if not content:
            return False, "输出内容为空"
        
        # 检查敏感词
        for keyword in self.blocked_keywords:
            if keyword in content:
                logger.warning(f"⚠️  输出包含敏感词: {keyword}")
                return False, f"包含敏感词: {keyword}"
        
        return True, None
    
    def check_input(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """检查用户输入是否安全"""
        # 这里可以加更多的输入检查
        if not user_input:
            return False, "输入不能为空"
        
        # 检查长度
        if len(user_input) > 1000:
            return False, "输入太长了"
        
        return True, None


# ========== 简单的限流工具 ==========
class RateLimiter:
    """简单的滑动窗口限流"""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}  # user_id -> [timestamp1, timestamp2, ...]
    
    def is_allowed(self, user_id: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        
        # 清理过期的记录
        if user_id in self.requests:
            self.requests[user_id] = [
                t for t in self.requests[user_id]
                if now - t < self.window_seconds
            ]
        else:
            self.requests[user_id] = []
        
        # 检查是否超限
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # 记录这次请求
        self.requests[user_id].append(now)
        return True
    
    def remaining(self, user_id: str) -> int:
        """剩余可用次数"""
        if user_id not in self.requests:
            return self.max_requests
        return self.max_requests - len(self.requests[user_id])


# ========== 通用工具函数 ==========
def calculate_age(birth_date_str: str, date_format: str = "%Y-%m-%d") -> int:
    """
    根据出生日期计算年龄
    
    Args:
        birth_date_str: 出生日期字符串
        date_format: 日期格式
    
    Returns:
        年龄（周岁）
    """
    try:
        from datetime import datetime
        birth = datetime.strptime(birth_date_str, date_format)
        now = datetime.now()
        age = now.year - birth.year
        if (now.month, now.day) < (birth.month, birth.day):
            age -= 1
        return max(0, age)
    except Exception as e:
        logger.warning(f"计算年龄失败: {e}")
        return 30  # 默认 30 岁


def random_choice_without_repeat(items: list, last: Any = None) -> Any:
    """
    随机选择，不重复选上一次的
    
    用于：加载文案、语录等，避免重复
    """
    if len(items) <= 1:
        return items[0] if items else None
    
    result = None
    max_attempts = 10
    for _ in range(max_attempts):
        result = random.choice(items)
        if result != last:
            break
    
    return result


import random  # noqa
