"""
日志工具
提供统一的日志记录功能
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def get_logger(name: str) -> "logger":
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logger: 配置好的日志记录器
    """
    return logger.bind(name=name)


def setup_logger(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    log_format: Optional[str] = None
) -> None:
    """
    设置日志配置

    Args:
        log_file: 日志文件路径，如果为None则只输出到控制台
        log_level: 日志级别
        log_format: 日志格式
    """
    # 移除默认的控制台输出
    logger.remove()

    # 设置日志格式
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )

    # 添加文件输出
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=log_format,
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )


# 默认设置日志配置
setup_logger(log_file="logs/app.log")