import logging
from uuid import UUID
from datetime import timedelta
from typing import Optional, List

from domain.interfaces.i_queue_manager import IQueueManager, QueueStatus
from domain.models.print_task import PrintTask

logger = logging.getLogger(__name__)


class QueueManager(IQueueManager):
    """
    基于Redis的打印队列管理器(骨架实现)
    
    使用Redis Sorted Set实现优先级队列
    """

    def __init__(self):
        self._queue_key = "print_queue"
        self._task_key_prefix = "print_task:"
        self._in_memory_queue: List[PrintTask] = []

    async def enqueue(self, task: PrintTask, priority: int = 0) -> int:
        """
        任务入队
        
        实现步骤:
        1. 序列化任务对象
        2. 存储到Redis(task_id -> task_data)
        3. 加入优先级队列(Sorted Set)
        4. 计算队列位置
        
        Args:
            task: 打印任务
            priority: 优先级(数字越大越靠前)
            
        Returns:
            int: 队列位置(从1开始)
        """
        logger.info(f"Enqueuing print task {task.id} with priority {priority}")
        
        self._in_memory_queue.append(task)
        self._in_memory_queue.sort(key=lambda t: priority, reverse=True)
        
        position = self._in_memory_queue.index(task) + 1
        task.enqueue(position)
        
        logger.info(f"Task {task.id} enqueued at position {position}")
        return position

    async def dequeue(self) -> Optional[PrintTask]:
        """
        任务出队(FIFO + 优先级)
        
        Returns:
            Optional[PrintTask]: 下一个待打印任务
        """
        logger.info("Dequeuing next print task")
        
        if not self._in_memory_queue:
            logger.info("Queue is empty")
            return None
        
        task = self._in_memory_queue.pop(0)
        task.queue_position = None
        
        logger.info(f"Dequeued task {task.id}")
        return task

    async def get_queue_status(self) -> QueueStatus:
        """
        获取队列状态
        
        Returns:
            QueueStatus: 队列状态信息
        """
        logger.info("Getting queue status")
        
        queue_length = len(self._in_memory_queue)
        pending_tasks = self._in_memory_queue[:5]
        
        estimated_wait_time = self._estimate_wait_time(pending_tasks)
        
        return QueueStatus(
            total=queue_length,
            pending_tasks=pending_tasks,
            estimated_wait_time=estimated_wait_time
        )

    async def remove_task(self, task_id: UUID) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功移除
        """
        logger.info(f"Removing task {task_id} from queue")
        
        for i, task in enumerate(self._in_memory_queue):
            if task.id == task_id:
                self._in_memory_queue.pop(i)
                logger.info(f"Task {task_id} removed from queue")
                return True
        
        logger.warning(f"Task {task_id} not found in queue")
        return False

    async def reorder_queue(self, task_id: UUID, new_position: int) -> bool:
        """
        调整任务队列位置
        
        Args:
            task_id: 任务ID
            new_position: 新位置
            
        Returns:
            bool: 是否成功调整
        """
        logger.info(f"Reordering task {task_id} to position {new_position}")
        
        for i, task in enumerate(self._in_memory_queue):
            if task.id == task_id:
                self._in_memory_queue.pop(i)
                self._in_memory_queue.insert(new_position - 1, task)
                
                for idx, t in enumerate(self._in_memory_queue):
                    t.queue_position = idx + 1
                
                logger.info(f"Task {task_id} reordered to position {new_position}")
                return True
        
        logger.warning(f"Task {task_id} not found in queue")
        return False

    def _estimate_wait_time(self, tasks: List[PrintTask]) -> timedelta:
        """
        估算等待时间
        
        Args:
            tasks: 队列中的任务列表
            
        Returns:
            timedelta: 估算的等待时长
        """
        total_seconds = sum(
            (task.estimated_time or timedelta(0)).total_seconds()
            for task in tasks
        )
        return timedelta(seconds=total_seconds)
