"""
应用配置管理模块。

使用 pydantic-settings 管理环境变量和应用配置。
"""

from typing import Literal, Union

from pydantic import Field, field_validator
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
        # 禁用自动 JSON 解析,使用 field_validator 手动处理
        env_parse_none_str=None,
    )

    app_name: str = Field(default="3D Print Platform API", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: Literal["development", "production", "test"] = Field(
        default="development", description="运行环境"
    )

    host: str = Field(default="0.0.0.0", description="服务监听地址")
    port: int = Field(default=8000, description="服务监听端口")

    cors_origins: Union[str, list[str]] = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="CORS 允许的源(逗号分隔的字符串或列表)",
    )

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        解析 CORS 源配置。

        支持逗号分隔的字符串或列表。

        Args:
            v: 环境变量值

        Returns:
            list[str]: 解析后的源列表
        """
        if isinstance(v, str):
            # 如果是逗号分隔的字符串,拆分为列表
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="日志级别"
    )

    # 数据库配置
    database_url: str = Field(
        default="sqlite+aiosqlite:///./print_platform.db",
        description="数据库连接URL"
    )
    database_echo: bool = Field(default=False, description="是否打印SQL语句")
    database_pool_size: int = Field(default=5, description="数据库连接池大小")
    database_max_overflow: int = Field(default=10, description="数据库连接池最大溢出")

    redis_host: str = Field(default="redis", description="Redis 主机地址")
    redis_port: int = Field(default=6379, description="Redis 端口")
    redis_password: str = Field(default="", description="Redis 密码")
    redis_db: int = Field(default=0, description="Redis 数据库编号")

    celery_broker_url: str = Field(default="redis://redis:6379/0", description="Celery broker URL")
    celery_result_backend: str = Field(
        default="redis://redis:6379/0", description="Celery result backend URL"
    )
    celery_task_time_limit: int = Field(default=300, description="Celery 任务超时时间(秒)")
    celery_task_soft_time_limit: int = Field(default=270, description="Celery 任务软超时时间(秒)")

    meshy_api_key: str = Field(
        default="", description="Meshy AI API 密钥"
    )
    meshy_base_url: str = Field(
        default="https://api.meshy.ai", description="Meshy AI API 基础 URL"
    )
    meshy_timeout: int = Field(
        default=300, description="Meshy AI API 请求超时时间(秒)"
    )
    meshy_max_retries: int = Field(
        default=3, description="Meshy AI API 最大重试次数"
    )
    meshy_default_model: str = Field(
        default="meshy-5", description="Meshy AI 默认模型版本"
    )
    
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/app.db",
        description="数据库连接URL"
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        description="是否打印SQL语句"
    )

    @property
    def redis_url(self) -> str:
        """
        构建 Redis 连接 URL。

        Returns:
            str: Redis 连接字符串
        """
        if self.redis_password:
            return (
                f"redis://:{self.redis_password}@"
                f"{self.redis_host}:{self.redis_port}/{self.redis_db}"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()


def get_settings() -> Settings:
    """
    获取全局配置实例
    
    Returns:
        Settings: 配置对象
    """
    return settings

