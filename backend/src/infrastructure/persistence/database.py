"""
数据库连接和会话管理模块
"""
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

# 创建声明式基类
Base = declarative_base()


class DatabaseManager:
    """
    数据库管理器
    
    负责数据库引擎的创建、会话管理和连接池配置
    """
    
    def __init__(self):
        """
        初始化数据库管理器
        """
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
    
    def create_engine(self) -> AsyncEngine:
        """
        创建数据库引擎
        
        Returns:
            AsyncEngine: SQLAlchemy异步引擎
        """
        if self._engine is not None:
            return self._engine
        
        # 根据数据库类型选择连接池策略
        is_sqlite = settings.database_url.startswith('sqlite')
        
        pool_config = {}
        if is_sqlite:
            # SQLite使用NullPool,避免并发问题
            pool_config['poolclass'] = NullPool
        else:
            # PostgreSQL/MySQL使用连接池
            pool_config.update({
                'poolclass': AsyncAdaptedQueuePool,
                'pool_size': settings.database_pool_size,
                'max_overflow': settings.database_max_overflow,
                'pool_pre_ping': True,  # 检查连接是否有效
                'pool_recycle': 3600,  # 1小时后回收连接
            })
        
        self._engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            future=True,
            **pool_config
        )
        
        logger.info(f"Database engine created: {settings.database_url}")
        return self._engine
    
    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        获取会话工厂
        
        Returns:
            async_sessionmaker: 异步会话工厂
        """
        if self._session_factory is None:
            if self._engine is None:
                self.create_engine()
            
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,  # 提交后不过期对象
                autocommit=False,
                autoflush=False
            )
        
        return self._session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        获取数据库会话上下文管理器
        
        Yields:
            AsyncSession: 数据库会话
            
        Example:
            async with db_manager.get_session() as session:
                result = await session.execute(query)
        """
        session_factory = self.get_session_factory()
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """
        创建所有表
        
        注意: 生产环境应使用Alembic进行数据库迁移
        """
        if self._engine is None:
            self.create_engine()
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created")
    
    async def drop_tables(self):
        """
        删除所有表
        
        警告: 此操作将删除所有数据!
        """
        if self._engine is None:
            self.create_engine()
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.warning("Database tables dropped")
    
    async def close(self):
        """
        关闭数据库连接
        """
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database connection closed")


# 全局数据库管理器实例
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI依赖注入函数
    
    Yields:
        AsyncSession: 数据库会话
        
    Example:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with db_manager.get_session() as session:
        yield session


async def init_database():
    """
    初始化数据库
    
    在应用启动时调用
    """
    logger.info("Initializing database...")
    db_manager.create_engine()
    await db_manager.create_tables()
    logger.info("Database initialized successfully")


async def close_database():
    """
    关闭数据库连接
    
    在应用关闭时调用
    """
    logger.info("Closing database...")
    await db_manager.close()
    logger.info("Database closed successfully")
