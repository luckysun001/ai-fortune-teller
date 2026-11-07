#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
backend/logger.py 补充测试：
- setup_logger 返回正确 Logger、不重复添加 handler
- RequestLogger 请求计数与成功率统计
"""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.logger import RequestLogger, setup_logger


def test_setup_logger_returns_logger_with_level():
    lg = setup_logger("logger_test_unit_a", logging.DEBUG)
    assert isinstance(lg, logging.Logger)
    assert lg.level == logging.DEBUG


def test_setup_logger_no_duplicate_handlers():
    # 同一 name 调用两次，不应重复追加 handler
    lg1 = setup_logger("logger_test_unit_b")
    n = len(lg1.handlers)
    lg2 = setup_logger("logger_test_unit_b")
    assert len(lg2.handlers) == n


def test_request_logger_counts_success_and_error():
    rl = RequestLogger()
    rl.log_request("daily", {"birth": "1995-03-15"}, "deepseek", 10.0, True)
    rl.log_request("fortune", {"birth": "1990-01-01"}, "deepseek", 5.0, False, error="boom")
    stats = rl.get_stats()
    assert stats["total_requests"] == 2
    assert stats["success"] == 1
    assert stats["errors"] == 1
    assert "50.0%" in stats["success_rate"]


def test_request_logger_empty_stats():
    rl = RequestLogger()
    stats = rl.get_stats()
    assert stats["total_requests"] == 0
    assert stats["success"] == 0
    assert stats["errors"] == 0
    assert stats["success_rate"] == "0.0%"
