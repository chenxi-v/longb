"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "LongTV Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/spiders.db"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # 代理配置
    PROXY_ENABLED: bool = False
    PROXY_URL: Optional[str] = None

    # 智能代理配置
    SMART_PROXY_URL: Optional[str] = None
    MAX_FAILURES: int = 2
    RETRY_INTERVAL: int = 3600
    REQUEST_TIMEOUT: int = 10

    # 爬虫配置
    SPIDERS_DIR: str = "./spiders"
    MAX_SPIDERS: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量


# 全局配置实例
settings = Settings()
