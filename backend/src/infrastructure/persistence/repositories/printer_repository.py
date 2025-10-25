"""
打印机仓储实现
"""
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.interfaces.i_printer_repository import IPrinterRepository
from domain.models.printer import Printer
from domain.enums.print_enums import PrinterStatus, AdapterType
from infrastructure.persistence.models.printer_model import PrinterModel

logger = logging.getLogger(__name__)


class PrinterRepository(IPrinterRepository):
    """
    打印机仓储SQLAlchemy实现
    """

    def __init__(self, session: AsyncSession):
        """
        初始化仓储
        
        Args:
            session: 数据库会话
        """
        self._session = session

    async def save(self, printer: Printer) -> Printer:
        """
        保存打印机
        
        Args:
            printer: 打印机对象
            
        Returns:
            Printer: 保存后的打印机对象
            
        Raises:
            RuntimeError: 如果保存失败
        """
        try:
            # 查找现有记录
            stmt = select(PrinterModel).where(PrinterModel.id == printer.id)
            result = await self._session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # 更新现有记录
                existing.update_from_domain_model(printer)
                logger.debug(f"Updated printer: {printer.id}")
            else:
                # 创建新记录
                model = PrinterModel.from_domain_model(printer)
                self._session.add(model)
                logger.debug(f"Created new printer: {printer.id}")

            await self._session.flush()
            return printer

        except Exception as e:
            logger.error(f"Failed to save printer {printer.id}: {e}")
            raise RuntimeError(f"Failed to save printer: {e}")

    async def find_by_id(self, printer_id: str) -> Optional[Printer]:
        """
        根据ID查找打印机
        
        Args:
            printer_id: 打印机ID
            
        Returns:
            Optional[Printer]: 打印机对象,不存在则返回None
        """
        stmt = select(PrinterModel).where(PrinterModel.id == printer_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return model.to_domain_model()
        return None

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Printer]:
        """
        查找所有打印机
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Printer]: 打印机列表
        """
        stmt = (
            select(PrinterModel)
            .order_by(PrinterModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_by_status(
        self,
        status: PrinterStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[Printer]:
        """
        根据状态查找打印机
        
        Args:
            status: 打印机状态
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Printer]: 打印机列表
        """
        stmt = (
            select(PrinterModel)
            .where(PrinterModel.status == status)
            .order_by(PrinterModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_by_adapter_type(
        self,
        adapter_type: AdapterType,
        limit: int = 100,
        offset: int = 0
    ) -> List[Printer]:
        """
        根据适配器类型查找打印机
        
        Args:
            adapter_type: 适配器类型
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Printer]: 打印机列表
        """
        stmt = (
            select(PrinterModel)
            .where(PrinterModel.adapter_type == adapter_type)
            .order_by(PrinterModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_available(self, limit: int = 100) -> List[Printer]:
        """
        查找可用的打印机(在线、空闲、已启用)
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[Printer]: 可用打印机列表
        """
        stmt = (
            select(PrinterModel)
            .where(
                PrinterModel.is_enabled == True,
                PrinterModel.status == PrinterStatus.IDLE,
                PrinterModel.current_task_id.is_(None)
            )
            .order_by(PrinterModel.last_heartbeat.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain_model() for model in models]

    async def find_by_task_id(self, task_id: UUID) -> Optional[Printer]:
        """
        根据任务ID查找打印机
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Printer]: 打印机对象,不存在则返回None
        """
        stmt = select(PrinterModel).where(PrinterModel.current_task_id == task_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return model.to_domain_model()
        return None

    async def delete(self, printer_id: str) -> bool:
        """
        删除打印机
        
        Args:
            printer_id: 打印机ID
            
        Returns:
            bool: 是否删除成功
        """
        stmt = delete(PrinterModel).where(PrinterModel.id == printer_id)
        result = await self._session.execute(stmt)
        await self._session.flush()

        return result.rowcount > 0

    async def count_by_status(self, status: PrinterStatus) -> int:
        """
        统计指定状态的打印机数量
        
        Args:
            status: 打印机状态
            
        Returns:
            int: 打印机数量
        """
        stmt = (
            select(func.count())
            .select_from(PrinterModel)
            .where(PrinterModel.status == status)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_total(self) -> int:
        """
        统计总打印机数量
        
        Returns:
            int: 总打印机数量
        """
        stmt = select(func.count()).select_from(PrinterModel)
        result = await self._session.execute(stmt)
        return result.scalar_one()
