#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志系统 - 统一的日志格式和输出
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "fortune", level: int = logging.INFO) -> logging.Logger:
    """
    设置并返回一个格式化好的 logger

    Args:
        name: logger 名称
        level: 日志级别

    Returns:
        配置好的 logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 如果已经有 handler 了，就不要再加了（避免重复输出）
    if logger.handlers:
        return logger

    # 格式化输出
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 全局 logger 实例，直接 import 这个就能用
logger = setup_logger()


class RequestLogger:
    """
    请求日志记录器 - 记录每一次测算的详细信息
    用于统计、分析、优化 Prompt
    """

    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0

    def log_request(
        self,
        request_type: str,
        params: dict,
        model: str,
        latency_ms: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """记录一次请求"""
        self.request_count += 1

        if success:
            self.success_count += 1
            logger.info(
                f"✅ [{request_type}] "
                f"model={model}, "
                f"latency={latency_ms:.1f}ms, "
                f"params={params}"
            )
        else:
            self.error_count += 1
            logger.error(
                f"❌ [{request_type}] "
                f"model={model}, "
                f"latency={latency_ms:.1f}ms, "
                f"error={error}"
            )

    def get_stats(self) -> dict:
        """获取统计数据"""
        success_rate = (
            self.success_count / self.request_count
            if self.request_count > 0
            else 0
        )
        return {
            "total_requests": self.request_count,
            "success": self.success_count,
            "errors": self.error_count,
            "success_rate": f"{success_rate:.1%}",
        }


# 全局请求日志实例
request_logger = RequestLogger()
