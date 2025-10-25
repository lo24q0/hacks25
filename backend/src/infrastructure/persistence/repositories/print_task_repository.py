"""
打印任务仓储实现
"""
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.interfaces.i_print_task_repository import IPrintTaskRepository
from domain.models.print_task import PrintTask
from domain.enums.print_enums import TaskStatus
from infrastructure.persistence.models.print_task_model import PrintTaskModel

logger = logging.getLogger(__name__)


class PrintTaskRepository(IPrintTaskRepository):
    """
    打印任务仓储SQLAlchemy实现
    """

    def __init__(self, session: AsyncSession):
        """
        初始化仓储
        
        Args:
            session: 数据库会话
        """
        self._session = session

    async def save(self, task: PrintTask) -> PrintTask:
        """
        保存打印任务
        
        Args:
            task: 打印任务对象
            
        Returns:
            PrintTask: 保存后的任务对象
            
        Raises:
            RuntimeError: 如果保存失败
        """
        try:
            # 查找现有记录
            stmt = select(PrintTaskModel).where(PrintTaskModel.id == task.id)
            result = await self._session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # 更新现有记录
                existing.update_from_domain_model(task)
                logger.debug(f"Updated print task: {task.id}")
            else:
                # 创建新记录
                model = PrintTaskModel.from_domain_model(task)
                self._session.add(model)
                logger.debug(f"Created new print task: {task.id}")

            await self._session.flush()
            return task

        except Exception as e:
            logger.error(f"Failed to save print task {task.id}: {e}")
            raise RuntimeError(f"Failed to save print task: {e}")

    async def find_by_id(self, task_id: UUID) -> Optional[PrintTask]:
        """
        根据ID查找打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[PrintTask]: 任务对象,不存在则返回None
        """
        stmt = select(PrintTaskModel).where(PrintTaskModel.id == task_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return model.to_domain_model()
        return None

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[PrintTask]:
        """
        查找所有打印任务
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[PrintTask]: 任务列表
        """
        stmt = (
            select(PrintTaskModel)
            .order_by(PrintTaskModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_by_status(
        self,
        status: TaskStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[PrintTask]:
        """
        根据状态查找打印任务
        
        Args:
            status: 任务状态
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[PrintTask]: 任务列表
        """
        stmt = (
            select(PrintTaskModel)
            .where(PrintTaskModel.status == status)
            .order_by(PrintTaskModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_by_printer_id(
        self,
        printer_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[PrintTask]:
        """
        根据打印机ID查找任务
        
        Args:
            printer_id: 打印机ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[PrintTask]: 任务列表
        """
        stmt = (
            select(PrintTaskModel)
            .where(PrintTaskModel.printer_id == printer_id)
            .order_by(PrintTaskModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_by_model_id(
        self,
        model_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[PrintTask]:
        """
        根据模型ID查找任务
        
        Args:
            model_id: 模型ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[PrintTask]: 任务列表
        """
        stmt = (
            select(PrintTaskModel)
            .where(PrintTaskModel.model_id == model_id)
            .order_by(PrintTaskModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_queued_tasks(self, limit: int = 100) -> List[PrintTask]:
        """
        查找排队中的任务
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[PrintTask]: 排队任务列表(按队列位置排序)
        """
        stmt = (
            select(PrintTaskModel)
            .where(PrintTaskModel.status == TaskStatus.QUEUED)
            .order_by(PrintTaskModel.queue_position.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_active_tasks(self, limit: int = 100) -> List[PrintTask]:
        """
        查找活跃任务(正在切片、排队、打印)
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[PrintTask]: 活跃任务列表
        """
        stmt = (
            select(PrintTaskModel)
            .where(
                or_(
                    PrintTaskModel.status == TaskStatus.SLICING,
                    PrintTaskModel.status == TaskStatus.QUEUED,
                    PrintTaskModel.status == TaskStatus.PRINTING,
                    PrintTaskModel.status == TaskStatus.PAUSED
                )
            )
            .order_by(PrintTaskModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def delete(self, task_id: UUID) -> bool:
        """
        删除打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        stmt = delete(PrintTaskModel).where(PrintTaskModel.id == task_id)
        result = await self._session.execute(stmt)
        await self._session.flush()

        return result.rowcount > 0

    async def count_by_status(self, status: TaskStatus) -> int:
        """
        统计指定状态的任务数量
        
        Args:
            status: 任务状态
            
        Returns:
            int: 任务数量
        """
        stmt = (
            select(func.count())
            .select_from(PrintTaskModel)
            .where(PrintTaskModel.status == status)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_total(self) -> int:
        """
        统计总任务数量
        
        Returns:
            int: 总任务数量
        """
        stmt = select(func.count()).select_from(PrintTaskModel)
        result = await self._session.execute(stmt)
        return result.scalar_one()
