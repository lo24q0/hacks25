"""
Redis 风格化任务存储模块。

提供基于 Redis 的风格化任务状态持久化存储。
"""

import json
import logging
from datetime import timedelta
from typing import Any, Optional
from uuid import UUID

import redis.asyncio as aioredis

from src.domain.models.style import StyleTask

logger = logging.getLogger(__name__)


class RedisStyleTaskStore:
    """
    基于 Redis 的风格化任务存储。

    使用 Redis 作为任务状态的持久化存储,解决内存缓存跨请求无法查询的问题。

    存储结构:
        - Key: "style_task:{task_id}"
        - Value: JSON 序列化的任务数据
        - TTL: 7天(可配置)

    Args:
        redis_url: Redis 连接URL
        ttl_days: 任务数据保留天数,默认7天

    示例:
        >>> store = RedisStyleTaskStore("redis://localhost:6379/0")
        >>> await store.save_task(task)
        >>> task = await store.get_task(task_id)
    """

    def __init__(self, redis_url: str, ttl_days: int = 7):
        """
        初始化 Redis 任务存储。

        Args:
            redis_url: Redis 连接URL
            ttl_days: 任务数据保留天数
        """
        self._redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._task_key_prefix = "style_task:"
        self._ttl = timedelta(days=ttl_days)

    async def _get_redis(self) -> aioredis.Redis:
        """
        获取 Redis 连接。

        采用延迟初始化,仅在首次使用时建立连接。

        Returns:
            aioredis.Redis: Redis 客户端实例
        """
        if self._redis is None:
            self._redis = await aioredis.from_url(
                self._redis_url, encoding="utf-8", decode_responses=True
            )
            logger.info(f"Redis connection established: {self._redis_url}")
        return self._redis

    def _get_task_key(self, task_id: UUID) -> str:
        """
        生成任务的 Redis key。

        Args:
            task_id: 任务ID

        Returns:
            str: Redis key
        """
        return f"{self._task_key_prefix}{task_id}"

    async def save_task(self, task: StyleTask) -> None:
        """
        保存任务到 Redis。

        Args:
            task: 风格化任务对象

        Raises:
            Exception: 如果 Redis 操作失败
        """
        logger.info(f"Saving task {task.id} to Redis")

        try:
            redis = await self._get_redis()
            task_key = self._get_task_key(task.id)
            task_data = json.dumps(task.to_dict())

            # 保存任务数据并设置过期时间
            await redis.setex(task_key, int(self._ttl.total_seconds()), task_data)

            logger.debug(f"Task {task.id} saved successfully with TTL {self._ttl}")

        except Exception as e:
            logger.error(f"Failed to save task {task.id} to Redis: {e}")
            raise

    async def get_task(self, task_id: UUID) -> Optional[StyleTask]:
        """
        从 Redis 获取任务。

        Args:
            task_id: 任务ID

        Returns:
            Optional[StyleTask]: 任务对象,如果不存在则返回 None

        Raises:
            Exception: 如果 Redis 操作或数据反序列化失败
        """
        logger.info(f"Getting task {task_id} from Redis")

        try:
            redis = await self._get_redis()
            task_key = self._get_task_key(task_id)
            task_data = await redis.get(task_key)

            if not task_data:
                logger.warning(f"Task {task_id} not found in Redis")
                return None

            # 反序列化任务数据
            task_dict = json.loads(task_data)
            # 重建 StyleTask 对象
            task = self._dict_to_task(task_dict)

            logger.debug(f"Task {task_id} retrieved successfully")
            return task

        except Exception as e:
            logger.error(f"Failed to get task {task_id} from Redis: {e}")
            raise

    async def update_task(self, task: StyleTask) -> None:
        """
        更新 Redis 中的任务。

        Args:
            task: 更新后的任务对象

        Raises:
            Exception: 如果 Redis 操作失败
        """
        logger.info(f"Updating task {task.id} in Redis")

        try:
            # 更新操作等同于重新保存
            await self.save_task(task)
            logger.debug(f"Task {task.id} updated successfully")

        except Exception as e:
            logger.error(f"Failed to update task {task.id} in Redis: {e}")
            raise

    async def delete_task(self, task_id: UUID) -> bool:
        """
        从 Redis 删除任务。

        Args:
            task_id: 任务ID

        Returns:
            bool: 删除是否成功

        Raises:
            Exception: 如果 Redis 操作失败
        """
        logger.info(f"Deleting task {task_id} from Redis")

        try:
            redis = await self._get_redis()
            task_key = self._get_task_key(task_id)
            deleted = await redis.delete(task_key)

            if deleted:
                logger.debug(f"Task {task_id} deleted successfully")
                return True
            else:
                logger.warning(f"Task {task_id} not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Failed to delete task {task_id} from Redis: {e}")
            raise

    def _dict_to_task(self, task_dict: dict[str, Any]) -> StyleTask:
        """
        将字典转换为 StyleTask 对象。

        Args:
            task_dict: 任务字典数据

        Returns:
            StyleTask: 任务对象
        """
        from datetime import datetime
        from src.domain.enums.status import TaskStatus
        from src.domain.value_objects.style_metadata import ErrorInfo, StyleTaskMetadata

        # 重建 metadata
        metadata_dict = task_dict.get("metadata", {})

        # 处理 created_at - 如果不存在则使用当前时间
        created_at_value = datetime.now()
        if metadata_dict.get("created_at"):
            created_at_value = datetime.fromisoformat(metadata_dict["created_at"])

        metadata = StyleTaskMetadata(
            style_preset_id=metadata_dict.get("style_preset_id", ""),
            style_preset_name=metadata_dict.get("style_preset_name", ""),
            estimated_time=metadata_dict.get("estimated_time"),
            actual_time=metadata_dict.get("actual_time"),
            tencent_request_id=metadata_dict.get("tencent_request_id"),
            created_at=created_at_value,
            completed_at=(
                datetime.fromisoformat(metadata_dict["completed_at"])
                if metadata_dict.get("completed_at")
                else None
            ),
        )

        # 重建 error_info
        error_info = None
        error_info_dict = task_dict.get("error_info")
        if error_info_dict:
            error_info = ErrorInfo(
                error_code=error_info_dict["error_code"],
                error_message=error_info_dict["error_message"],
                tencent_error_code=error_info_dict.get("tencent_error_code"),
                user_message=error_info_dict.get("user_message"),
                suggestion=error_info_dict.get("suggestion"),
                is_retryable=error_info_dict.get("is_retryable", False),
            )

        # 重建 StyleTask
        task = StyleTask(
            id=UUID(task_dict["id"]),
            image_path=task_dict["image_path"],
            style_preset_id=task_dict["style_preset_id"],
            style_preset_name=metadata.style_preset_name,
            status=TaskStatus(task_dict["status"]),
            result_path=task_dict.get("result_path"),
            metadata=metadata,
            error_info=error_info,
            created_at=datetime.fromisoformat(task_dict["created_at"]),
            updated_at=datetime.fromisoformat(task_dict["updated_at"]),
        )

        return task

    async def close(self) -> None:
        """
        关闭 Redis 连接。

        在应用关闭时调用,释放资源。
        """
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")
