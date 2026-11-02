#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
backend/utils.py 中尚未被覆盖的单元补充测试：
- FortuneException 及子类
- timing / cached 装饰器
- RateLimiter 限流
- random_choice_without_repeat
- ContentModerator.check_input
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.utils import (
    FortuneException,
    APIKeyInvalidException,
    APITimeoutException,
    ContentSafetyException,
    RateLimitException,
    ConfigurationException,
    timing,
    cached,
    RateLimiter,
    random_choice_without_repeat,
    ContentModerator,
    cache,
)


@pytest.fixture(autouse=True)
def _clear_global_cache():
    """每个用例前后清空全局缓存，避免相互污染"""
    cache.clear()
    yield
    cache.clear()


# ========== 异常族 ==========
def test_fortune_exception_basic():
    e = FortuneException("出错了", {"code": 1})
    assert e.message == "出错了"
    assert e.details == {"code": 1}
    assert "UNKNOWN_ERROR" in str(e)


@pytest.mark.parametrize(
    "exc_cls,expected_code",
    [
        (APIKeyInvalidException, "INVALID_API_KEY"),
        (APITimeoutException, "API_TIMEOUT"),
        (ContentSafetyException, "CONTENT_SAFETY_BLOCKED"),
        (RateLimitException, "RATE_LIMIT_EXCEEDED"),
        (ConfigurationException, "CONFIGURATION_ERROR"),
    ],
)
def test_exception_codes(exc_cls, expected_code):
    e = exc_cls("msg")
    assert e.code == expected_code
    assert isinstance(e, FortuneException)
    assert expected_code in str(e)


def test_exception_is_raisable_as_base():
    with pytest.raises(FortuneException):
        raise APIKeyInvalidException("bad key")


# ========== timing 装饰器 ==========
def test_timing_returns_result():
    @timing
    def add(a, b):
        return a + b

    assert add(2, 3) == 5


# ========== cached 装饰器 ==========
def test_cached_hits_after_first_call():
    calls = []

    @cached
    def double(x):
        calls.append(x)
        return x * 2

    assert double(2) == 4
    assert double(2) == 4
    # 第二次应当命中缓存，不再真正执行
    assert len(calls) == 1


def test_cached_disabled_recomputes():
    original = cache.enabled
    cache.enabled = False
    try:
        calls = []

        @cached
        def ident(x):
            calls.append(x)
            return x

        ident(7)
        ident(7)
        assert len(calls) == 2
    finally:
        cache.enabled = original


def test_cached_distinct_args_not_shared():
    calls = []

    @cached
    def sq(x):
        calls.append(x)
        return x ** 2

    assert sq(2) == 4
    assert sq(3) == 9
    assert len(calls) == 2  # 不同参数各自计算


# ========== RateLimiter ==========
def test_rate_limiter_allows_within_limit():
    rl = RateLimiter(max_requests=2, window_seconds=60)
    assert rl.is_allowed("user_a") is True
    assert rl.is_allowed("user_a") is True
    assert rl.is_allowed("user_a") is False


def test_rate_limiter_remaining():
    rl = RateLimiter(max_requests=3, window_seconds=60)
    rl.is_allowed("u")
    rl.is_allowed("u")
    assert rl.remaining("u") == 1
    rl.is_allowed("u")
    assert rl.remaining("u") == 0


def test_rate_limiter_isolated_per_user():
    rl = RateLimiter(max_requests=1, window_seconds=60)
    assert rl.is_allowed("a") is True
    assert rl.is_allowed("b") is True  # 不同用户互不影响


# ========== random_choice_without_repeat ==========
def test_random_choice_single_item():
    assert random_choice_without_repeat([42]) == 42
    assert random_choice_without_repeat([]) is None


def test_random_choice_returns_from_items():
    items = ["x", "y", "z"]
    for _ in range(20):
        assert random_choice_without_repeat(items) in items


def test_random_choice_avoids_last_mostly():
    items = [1, 2, 3]
    last = 1
    # 多次调用，绝大多数结果不应等于上一次（避免重复）
    repeats = sum(1 for _ in range(50) if random_choice_without_repeat(items, last=last) == last)
    assert repeats < 50  # 应当尽量不重复


# ========== ContentModerator.check_input ==========
def test_check_input_empty_rejected():
    cm = ContentModerator(["暴力"])
    ok, reason = cm.check_input("")
    assert ok is False
    assert "空" in reason


def test_check_input_too_long_rejected():
    cm = ContentModerator(["暴力"])
    ok, reason = cm.check_input("正常" * 600)
    assert ok is False
    assert "长" in reason


def test_check_input_normal_accepted():
    cm = ContentModerator(["暴力"])
    ok, reason = cm.check_input("我想看看今年的事业运")
    assert ok is True
    assert reason is None
