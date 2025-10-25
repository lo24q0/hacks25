"""
打印任务仓储接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.models.print_task import PrintTask
from domain.enums.print_enums import TaskStatus


class IPrintTaskRepository(ABC):
    """
    打印任务仓储接口
    
    定义打印任务的数据访问操作
    """

    @abstractmethod
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
        pass

    @abstractmethod
    async def find_by_id(self, task_id: UUID) -> Optional[PrintTask]:
        """
        根据ID查找打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[PrintTask]: 任务对象,不存在则返回None
        """
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[PrintTask]:
        """
        查找所有打印任务
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[PrintTask]: 任务列表
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def find_queued_tasks(self, limit: int = 100) -> List[PrintTask]:
        """
        查找排队中的任务
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[PrintTask]: 排队任务列表(按队列位置排序)
        """
        pass

    @abstractmethod
    async def find_active_tasks(self, limit: int = 100) -> List[PrintTask]:
        """
        查找活跃任务(正在切片、排队、打印)
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[PrintTask]: 活跃任务列表
        """
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """
        删除打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def count_by_status(self, status: TaskStatus) -> int:
        """
        统计指定状态的任务数量
        
        Args:
            status: 任务状态
            
        Returns:
            int: 任务数量
        """
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """
        统计总任务数量
        
        Returns:
            int: 总任务数量
        """
        pass
