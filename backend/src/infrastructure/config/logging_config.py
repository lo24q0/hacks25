"""
应用日志配置模块。

提供统一的日志配置,支持不同环境的日志级别和格式。
"""

import logging
import sys
from typing import Dict

from src.infrastructure.config.settings import settings


class ColoredFormatter(logging.Formatter):
    """
    彩色日志格式化器。

    为不同级别的日志添加颜色标记,便于控制台查看。
    """

    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录。

        Args:
            record: 日志记录对象

        Returns:
            str: 格式化后的日志字符串
        """
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname:8}{self.RESET}"
        record.name = f"\033[94m{record.name}\033[0m"  # 蓝色模块名
        return super().format(record)


def setup_logging() -> None:
    """
    配置应用日志系统。

    根据环境变量设置日志级别和格式。
    开发环境使用彩色输出,生产环境使用 JSON 格式。
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # 创建根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除已存在的 handlers
    root_logger.handlers.clear()

    # 创建控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # 根据环境选择日志格式
    if settings.environment == "production":
        # 生产环境: JSON 格式,便于日志聚合
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"module": "%(name)s", "message": "%(message)s", '
            '"file": "%(filename)s", "line": %(lineno)d}'
        )
    else:
        # 开发环境: 彩色格式,便于阅读
        formatter = ColoredFormatter(
            "[%(asctime)s] %(levelname)s [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 配置第三方库的日志级别
    configure_third_party_loggers()

    # 记录日志系统初始化信息
    logger = logging.getLogger(__name__)
    logger.info(
        f"日志系统已初始化 | level={settings.log_level.upper()}, "
        f"environment={settings.environment}"
    )


def configure_third_party_loggers() -> None:
    """
    配置第三方库的日志级别。

    避免第三方库的 DEBUG 日志过多干扰。
    """
    third_party_levels: Dict[str, int] = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING,
        "uvicorn.error": logging.INFO,
        "celery": logging.INFO,
        "celery.worker": logging.INFO,
        "celery.task": logging.INFO,
        "redis": logging.WARNING,
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "tencentcloud": logging.WARNING,  # 腾讯云 SDK
    }

    for logger_name, level in third_party_levels.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的 logger。

    Args:
        name: logger 名称,通常使用 __name__

    Returns:
        logging.Logger: logger 实例
    """
    return logging.getLogger(name)
