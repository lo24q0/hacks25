"""
打印机仓储接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.printer import Printer
from src.domain.enums.print_enums import PrinterStatus, AdapterType


class IPrinterRepository(ABC):
    """
    打印机仓储接口

    定义打印机的数据访问操作
    """

    @abstractmethod
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
        pass

    @abstractmethod
    async def find_by_id(self, printer_id: str) -> Optional[Printer]:
        """
        根据ID查找打印机

        Args:
            printer_id: 打印机ID

        Returns:
            Optional[Printer]: 打印机对象,不存在则返回None
        """
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Printer]:
        """
        查找所有打印机

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Printer]: 打印机列表
        """
        pass

    @abstractmethod
    async def find_by_status(
        self, status: PrinterStatus, limit: int = 100, offset: int = 0
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
        pass

    @abstractmethod
    async def find_by_adapter_type(
        self, adapter_type: AdapterType, limit: int = 100, offset: int = 0
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
        pass

    @abstractmethod
    async def find_available(self, limit: int = 100) -> List[Printer]:
        """
        查找可用的打印机(在线、空闲、已启用)

        Args:
            limit: 返回数量限制

        Returns:
            List[Printer]: 可用打印机列表
        """
        pass

    @abstractmethod
    async def find_by_task_id(self, task_id: UUID) -> Optional[Printer]:
        """
        根据任务ID查找打印机

        Args:
            task_id: 任务ID

        Returns:
            Optional[Printer]: 打印机对象,不存在则返回None
        """
        pass

    @abstractmethod
    async def delete(self, printer_id: str) -> bool:
        """
        删除打印机

        Args:
            printer_id: 打印机ID

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def count_by_status(self, status: PrinterStatus) -> int:
        """
        统计指定状态的打印机数量

        Args:
            status: 打印机状态

        Returns:
            int: 打印机数量
        """
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """
        统计总打印机数量

        Returns:
            int: 总打印机数量
        """
        pass
