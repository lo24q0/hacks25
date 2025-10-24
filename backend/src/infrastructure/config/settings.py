"""
应用配置管理模块。

使用 pydantic-settings 管理环境变量和应用配置。
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类。

    从环境变量加载配置,支持 .env 文件。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="3D Print Platform API", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: Literal["development", "production", "test"] = Field(
        default="development", description="运行环境"
    )

    host: str = Field(default="0.0.0.0", description="服务监听地址")
    port: int = Field(default=8000, description="服务监听端口")

    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="CORS 允许的源",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="日志级别"
    )

    redis_host: str = Field(default="redis", description="Redis 主机地址")
    redis_port: int = Field(default=6379, description="Redis 端口")
    redis_password: str = Field(default="", description="Redis 密码")
    redis_db: int = Field(default=0, description="Redis 数据库编号")

    celery_broker_url: str = Field(
        default="redis://redis:6379/0", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://redis:6379/0", description="Celery result backend URL"
    )
    celery_task_time_limit: int = Field(
        default=300, description="Celery 任务超时时间(秒)"
    )
    celery_task_soft_time_limit: int = Field(
        default=270, description="Celery 任务软超时时间(秒)"
    )

    @property
    def redis_url(self) -> str:
        """
        构建 Redis 连接 URL。

        Returns:
            str: Redis 连接字符串
        """
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
