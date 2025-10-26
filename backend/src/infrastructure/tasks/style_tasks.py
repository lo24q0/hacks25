"""
风格化 Celery 异步任务模块。

提供图片风格化的异步任务处理,支持重试和错误恢复。
"""

import asyncio
import logging
import time
from typing import Any, Dict
from uuid import UUID

from celery import shared_task

from src.domain.value_objects.style_metadata import ErrorInfo
from src.infrastructure.ai.tencent_style import TencentCloudStyleEngine
from src.infrastructure.config.settings import settings
from src.infrastructure.storage.redis_style_task_store import RedisStyleTaskStore
from src.shared.exceptions.tencent_cloud_exceptions import TencentCloudAPIError

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def process_style_transfer(  # noqa: C901
    self,
    task_id: str,
    image_path: str,
    style_preset_id: str,
    output_path: str,
) -> Dict[str, Any]:
    """
    处理图片风格化任务。

    Args:
        task_id: 任务ID
        image_path: 输入图片路径
        style_preset_id: 风格预设ID
        output_path: 输出图片路径

    Returns:
        dict: 任务结果,包含以下字段:
            - status: 'success' 或 'failed'
            - task_id: 任务ID
            - output_path: 输出路径(成功时)
            - tencent_request_id: 腾讯云请求ID(成功时)
            - actual_time: 实际处理时间(秒)
            - error_code: 错误码(失败时)
            - error_message: 错误消息(失败时)
            - is_retryable: 是否可重试(失败时)

    Raises:
        Retry: 如果任务需要重试
    """
    start_time = time.time()

    try:
        # 更新任务状态为 PROCESSING
        # 原因: 确保只有在 Celery worker 实际开始处理时才更新状态
        try:
            _update_task_status_to_processing(task_id)
        except Exception as update_error:
            logger.error(f"Failed to update task {task_id} to PROCESSING: {update_error}")
            # 不影响主流程,继续执行

        engine = TencentCloudStyleEngine(
            secret_id=settings.tencent_cloud_secret_id,
            secret_key=settings.tencent_cloud_secret_key,
            region=settings.tencent_cloud_region,
        )

        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                engine.transfer_style(
                    image_path=image_path,
                    style_preset_id=style_preset_id,
                    output_path=output_path,
                )
            )
            result_path = result["result_path"]
            tencent_request_id = result["request_id"]
        finally:
            loop.close()

        actual_time = int(time.time() - start_time)

        # 更新 Redis 中的任务状态
        try:
            _update_task_in_redis(
                task_id=task_id,
                status="success",
                result_path=result_path,
                tencent_request_id=tencent_request_id,
                actual_time=actual_time,
            )
        except Exception as update_error:
            logger.error(f"Failed to update task {task_id} in Redis: {update_error}")
            # 不影响主流程,继续返回结果

        return {
            "status": "success",
            "task_id": task_id,
            "output_path": result_path,
            "tencent_request_id": tencent_request_id,
            "actual_time": actual_time,
        }

    except TencentCloudAPIError as e:
        actual_time = int(time.time() - start_time)

        error_result = {
            "status": "failed",
            "task_id": task_id,
            "error_code": e.error_code,
            "error_message": e.message,
            "tencent_error_code": e.tencent_error_code,
            "tencent_request_id": e.tencent_request_id,
            "user_message": e.user_message,
            "suggestion": e.suggestion,
            "is_retryable": e.is_retryable,
            "actual_time": actual_time,
        }

        if e.is_retryable and self.request.retries < self.max_retries:
            retry_delay = min(2**self.request.retries, 30)
            raise self.retry(exc=e, countdown=retry_delay)

        # 更新 Redis 中的任务状态
        try:
            _update_task_in_redis(
                task_id=task_id,
                status="failed",
                error_code=e.error_code,
                error_message=e.message,
                tencent_error_code=e.tencent_error_code,
                user_message=e.user_message,
                suggestion=e.suggestion,
                is_retryable=e.is_retryable,
            )
        except Exception as update_error:
            logger.error(f"Failed to update task {task_id} in Redis: {update_error}")

        return error_result

    except Exception as e:
        actual_time = int(time.time() - start_time)

        error_result = {
            "status": "failed",
            "task_id": task_id,
            "error_code": "UNKNOWN_ERROR",
            "error_message": str(e),
            "is_retryable": False,
            "actual_time": actual_time,
        }

        # 更新 Redis 中的任务状态
        try:
            _update_task_in_redis(
                task_id=task_id,
                status="failed",
                error_code="UNKNOWN_ERROR",
                error_message=str(e),
                is_retryable=False,
            )
        except Exception as update_error:
            logger.error(f"Failed to update task {task_id} in Redis: {update_error}")

        return error_result


def _update_task_status_to_processing(task_id: str) -> None:
    """
    将任务状态更新为 PROCESSING。

    Args:
        task_id: 任务ID

    Raises:
        Exception: 如果更新失败
    """
    task_store = RedisStyleTaskStore(redis_url=settings.redis_url)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 从 Redis 获取任务
        task = loop.run_until_complete(task_store.get_task(UUID(task_id)))

        if task is None:
            logger.warning(f"Task {task_id} not found in Redis for status update")
            return

        # 更新任务状态为 PROCESSING
        task.start_processing()

        # 保存更新后的任务
        loop.run_until_complete(task_store.update_task(task))
        logger.info(f"Task {task_id} status updated to PROCESSING")

    finally:
        loop.run_until_complete(task_store.close())
        loop.close()


def _update_task_in_redis(task_id: str, status: str, **kwargs: Any) -> None:
    """
    更新 Redis 中的任务状态。

    Args:
        task_id: 任务ID
        status: 任务状态 ('success' 或 'failed')
        **kwargs: 其他更新字段

    Raises:
        Exception: 如果更新失败
    """
    task_store = RedisStyleTaskStore(redis_url=settings.redis_url)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 从 Redis 获取任务
        task = loop.run_until_complete(task_store.get_task(UUID(task_id)))

        if task is None:
            logger.warning(f"Task {task_id} not found in Redis for update")
            return

        # 更新任务状态
        if status == "success":
            task.mark_completed(
                result_path=kwargs.get("result_path", ""),
                tencent_request_id=kwargs.get("tencent_request_id", ""),
                actual_time=kwargs.get("actual_time", 0),
            )
        elif status == "failed":
            error_info = ErrorInfo(
                error_code=kwargs.get("error_code", "UNKNOWN_ERROR"),
                error_message=kwargs.get("error_message", "Unknown error"),
                tencent_error_code=kwargs.get("tencent_error_code"),
                user_message=kwargs.get("user_message"),
                suggestion=kwargs.get("suggestion"),
                is_retryable=kwargs.get("is_retryable", False),
            )
            task.mark_failed(error_info)

        # 保存更新后的任务
        loop.run_until_complete(task_store.update_task(task))
        logger.info(f"Task {task_id} updated in Redis with status: {status}")

    finally:
        loop.run_until_complete(task_store.close())
        loop.close()


@shared_task
def cleanup_expired_style_results(days: int = 7) -> Dict[str, Any]:
    """
    清理过期的风格化结果文件。

    Args:
        days: 保留天数,默认7天

    Returns:
        dict: 清理结果,包含:
            - cleaned_count: 清理的文件数量
            - freed_space_mb: 释放的空间(MB)
    """
    from pathlib import Path

    cleaned_count = 0
    freed_space = 0
    cutoff_time = time.time() - (days * 86400)

    style_output_dir = Path("/tmp/styled")

    if not style_output_dir.exists():
        return {"cleaned_count": 0, "freed_space_mb": 0}

    for file_path in style_output_dir.glob("*.jpg"):
        if file_path.stat().st_mtime < cutoff_time:
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                cleaned_count += 1
                freed_space += file_size
            except Exception:
                pass

    freed_space_mb = freed_space / (1024 * 1024)

    return {
        "cleaned_count": cleaned_count,
        "freed_space_mb": round(freed_space_mb, 2),
    }
