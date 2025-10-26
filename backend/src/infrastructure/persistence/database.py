"""
数据库配置和会话管理

使用SQLAlchemy 2.0+异步ORM实现数据库访问
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from src.infrastructure.config.settings import get_settings


settings = get_settings()


Base = declarative_base()


def get_database_url() -> str:
    """
    获取数据库连接URL

    Returns:
        str: 数据库URL
    """
    if settings.DATABASE_URL.startswith("postgresql://"):
        return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif settings.DATABASE_URL.startswith("sqlite:///"):
        return settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return settings.DATABASE_URL


def create_engine() -> AsyncEngine:
    """
    创建异步数据库引擎

    Returns:
        AsyncEngine: 数据库引擎
    """
    database_url = get_database_url()

    if database_url.startswith("sqlite"):
        engine = create_async_engine(
            database_url,
            echo=settings.DATABASE_ECHO,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
    else:
        engine = create_async_engine(
            database_url,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

    return engine


async_engine = create_engine()


AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话(依赖注入)

    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """
    初始化数据库(创建所有表)
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_database() -> None:
    """
    删除所有表(仅用于测试)
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
