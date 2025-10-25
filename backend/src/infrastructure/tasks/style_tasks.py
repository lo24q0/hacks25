"""
风格化 Celery 异步任务模块。

提供图片风格化的异步任务处理,支持重试和错误恢复。
"""

import time
from datetime import datetime
from typing import Dict, Any

from celery import shared_task
from celery.exceptions import Retry

from src.infrastructure.ai.tencent_style import TencentCloudStyleEngine
from src.infrastructure.config.settings import settings
from src.shared.exceptions.tencent_cloud_exceptions import TencentCloudAPIError


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def process_style_transfer(
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
        engine = TencentCloudStyleEngine(
            secret_id=settings.tencent_cloud_secret_id,
            secret_key=settings.tencent_cloud_secret_key,
            region=settings.tencent_cloud_region,
        )

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result_path = loop.run_until_complete(
                engine.transfer_style(
                    image_path=image_path,
                    style_preset_id=style_preset_id,
                    output_path=output_path,
                )
            )
        finally:
            loop.close()

        actual_time = int(time.time() - start_time)

        return {
            "status": "success",
            "task_id": task_id,
            "output_path": result_path,
            "tencent_request_id": getattr(self, "_last_request_id", None),
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
            retry_delay = min(2 ** self.request.retries, 30)
            raise self.retry(exc=e, countdown=retry_delay)

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

        return error_result


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
    import os
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
