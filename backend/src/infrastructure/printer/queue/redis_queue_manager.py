import logging
import json
from uuid import UUID
from datetime import timedelta
from typing import Optional, List
import redis.asyncio as aioredis

from src.domain.interfaces.i_queue_manager import IQueueManager, QueueStatus
from src.domain.models.print_task import PrintTask

logger = logging.getLogger(__name__)


class RedisQueueManager(IQueueManager):
    """
    基于Redis的打印队列管理器

    使用Redis Sorted Set实现优先级队列
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._queue_key = "print_queue"
        self._task_key_prefix = "print_task:"

    async def _get_redis(self) -> aioredis.Redis:
        """
        获取Redis连接

        Returns:
            aioredis.Redis: Redis客户端
        """
        if self._redis is None:
            self._redis = await aioredis.from_url(
                self._redis_url, encoding="utf-8", decode_responses=True
            )
        return self._redis

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

        redis = await self._get_redis()
        task_key = f"{self._task_key_prefix}{task.id}"
        task_data = task.model_dump_json()

        await redis.set(task_key, task_data)

        score = -priority
        await redis.zadd(self._queue_key, {str(task.id): score})

        position = await redis.zrank(self._queue_key, str(task.id))

        task.enqueue(position + 1 if position is not None else 1)

        logger.info(
            f"Task {task.id} enqueued at position {position + 1 if position is not None else 1}"
        )
        return position + 1 if position is not None else 1

    async def dequeue(self) -> Optional[PrintTask]:
        """
        任务出队(FIFO + 优先级)

        Returns:
            Optional[PrintTask]: 下一个待打印任务
        """
        logger.info("Dequeuing next print task")

        redis = await self._get_redis()

        result = await redis.zpopmin(self._queue_key, 1)

        if not result:
            logger.info("Queue is empty")
            return None

        task_id, _ = result[0]
        task_key = f"{self._task_key_prefix}{task_id}"
        task_data = await redis.get(task_key)

        if not task_data:
            logger.warning(f"Task data not found for {task_id}")
            return None

        task = PrintTask.model_validate_json(task_data)
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

        redis = await self._get_redis()

        queue_length = await redis.zcard(self._queue_key)

        task_ids = await redis.zrange(self._queue_key, 0, 4)

        tasks = []
        for task_id in task_ids:
            task_key = f"{self._task_key_prefix}{task_id}"
            task_data = await redis.get(task_key)
            if task_data:
                tasks.append(PrintTask.model_validate_json(task_data))

        estimated_wait_time = self._estimate_wait_time(tasks)

        return QueueStatus(
            total=queue_length, pending_tasks=tasks, estimated_wait_time=estimated_wait_time
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

        redis = await self._get_redis()

        removed = await redis.zrem(self._queue_key, str(task_id))

        if removed:
            task_key = f"{self._task_key_prefix}{task_id}"
            await redis.delete(task_key)
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

        redis = await self._get_redis()

        score = await redis.zscore(self._queue_key, str(task_id))
        if score is None:
            logger.warning(f"Task {task_id} not found in queue")
            return False

        await redis.zrem(self._queue_key, str(task_id))

        new_score = -(1000 - new_position)
        await redis.zadd(self._queue_key, {str(task_id): new_score})

        logger.info(f"Task {task_id} reordered to position {new_position}")
        return True

    def _estimate_wait_time(self, tasks: List[PrintTask]) -> timedelta:
        """
        估算等待时间

        Args:
            tasks: 队列中的任务列表

        Returns:
            timedelta: 估算的等待时长
        """
        total_seconds = sum((task.estimated_time or timedelta(0)).total_seconds() for task in tasks)
        return timedelta(seconds=total_seconds)

    async def close(self):
        """
        关闭Redis连接
        """
        if self._redis:
            await self._redis.close()
