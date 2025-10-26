from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from datetime import timedelta
from pydantic import BaseModel

from src.domain.models.print_task import PrintTask


class QueueStatus(BaseModel):
    """
    队列状态信息

    Attributes:
        total: 总任务数
        pending_tasks: 待打印任务列表
        estimated_wait_time: 估算等待时间
    """

    total: int
    pending_tasks: List[PrintTask]
    estimated_wait_time: timedelta


class IQueueManager(ABC):
    """
    打印队列管理接口
    """

    @abstractmethod
    async def enqueue(self, task: PrintTask, priority: int = 0) -> int:
        """
        任务入队

        Args:
            task: 打印任务
            priority: 优先级(数字越大优先级越高)

        Returns:
            int: 队列位置
        """
        pass

    @abstractmethod
    async def dequeue(self) -> Optional[PrintTask]:
        """
        任务出队

        Returns:
            Optional[PrintTask]: 下一个待打印任务
        """
        pass

    @abstractmethod
    async def get_queue_status(self) -> QueueStatus:
        """
        获取队列状态

        Returns:
            QueueStatus: 队列状态信息
        """
        pass

    @abstractmethod
    async def remove_task(self, task_id: UUID) -> bool:
        """
        移除任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功移除
        """
        pass

    @abstractmethod
    async def reorder_queue(self, task_id: UUID, new_position: int) -> bool:
        """
        调整任务队列位置

        Args:
            task_id: 任务ID
            new_position: 新位置

        Returns:
            bool: 是否成功调整
        """
        pass
