"""
日志工具
"""
import logging
import os
import sys
from pathlib import Path
from typing import Optional
from app.config import settings


def is_vercel() -> bool:
    """检测是否运行在 Vercel 环境"""
    return os.environ.get("VERCEL") == "1" or os.environ.get("VERCEL_ENV") is not None


def setup_logger(
    name: str = "longtv",
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 设置日志级别
    log_level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器 - 仅在非 Vercel 环境下启用
    # Vercel serverless 环境文件系统是只读的
    if not is_vercel():
        log_file_path = log_file or settings.LOG_FILE
        if log_file_path:
            try:
                # 确保日志目录存在
                Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except (OSError, PermissionError) as e:
                # 如果无法创建日志文件，仅使用控制台输出
                logger.warning(f"无法创建日志文件: {e}")

    return logger


# 全局日志记录器
logger = setup_logger()
