"""
风格化 Celery 异步任务模块。

提供图片风格化的异步任务处理,支持重试和错误恢复。
"""

import asyncio
import base64
import logging
import time
from pathlib import Path
from typing import Any, Dict
from uuid import UUID

from src.domain.value_objects.style_metadata import ErrorInfo
from src.infrastructure.ai.tencent_style import TencentCloudStyleEngine
from src.infrastructure.config.settings import settings
from src.infrastructure.storage.local_storage import LocalStorageService
from src.infrastructure.storage.redis_style_task_store import RedisStyleTaskStore
from src.infrastructure.tasks.celery_app import celery_app
from src.shared.exceptions.tencent_cloud_exceptions import TencentCloudAPIError

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="style_tasks.process_style_transfer",
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
    image_object_key: str,
    style_preset_id: str,
    storage_path: str,
) -> Dict[str, Any]:
    """
    处理图片风格化任务。

    Args:
        task_id: 任务ID
        image_object_key: 输入图片的对象键(相对于 storage_path)
        style_preset_id: 风格预设ID
        storage_path: 存储根路径

    Returns:
        dict: 任务结果,包含以下字段:
            - status: 'success' 或 'failed'
            - task_id: 任务ID
            - result_object_key: 结果文件的对象键(成功时)
            - tencent_request_id: 腾讯云请求ID(成功时)
            - actual_time: 实际处理时间(秒)
            - error_code: 错误码(失败时)
            - error_message: 错误消息(失败时)
            - is_retryable: 是否可重试(失败时)

    Raises:
        Retry: 如果任务需要重试
    """
    logger.info(
        f"开始处理风格化任务 | task_id={task_id}, style_id={style_preset_id}, "
        f"image_object_key={image_object_key}, storage_path={storage_path}"
    )

    start_time = time.time()

    # 初始化存储服务
    # 原因: 使用统一的存储抽象层,便于后续替换为 MinIO/S3
    storage_service = LocalStorageService(base_path=storage_path)

    try:
        # 更新任务状态为 PROCESSING
        # 原因: 确保只有在 Celery worker 实际开始处理时才更新状态
        try:
            logger.info(f"更新任务状态为 PROCESSING | task_id={task_id}")
            _update_task_status_to_processing(task_id)
            logger.info(f"任务状态已更新为 PROCESSING | task_id={task_id}")
        except Exception as update_error:
            logger.error(
                f"更新任务状态为 PROCESSING 失败 | task_id={task_id}, "
                f"error_type={type(update_error).__name__}, error={str(update_error)}",
                exc_info=True,
            )
            # 原因: Redis 更新失败可能导致前端看到的一直是 PENDING 状态
            # 抛出异常，触发 Celery 重试
            raise

        # 获取输入图片的完整路径
        # 原因: TencentCloudStyleEngine 需要读取文件内容
        image_full_path = str(Path(storage_path) / image_object_key)
        logger.debug(f"输入图片路径 | image_full_path={image_full_path}")

        logger.debug(f"初始化腾讯云引擎 | task_id={task_id}")
        engine = TencentCloudStyleEngine(
            secret_id=settings.tencent_cloud_secret_id,
            secret_key=settings.tencent_cloud_secret_key,
            region=settings.tencent_cloud_region,
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            logger.debug(f"调用腾讯云风格化 API | task_id={task_id}, style_id={style_preset_id}")
            api_start_time = time.time()

            # 调用风格化 API,返回 Base64 数据
            result = loop.run_until_complete(
                engine.transfer_style(
                    image_path=image_full_path,
                    style_preset_id=style_preset_id,
                )
            )
            result_image_base64 = result["result_image_base64"]
            tencent_request_id = result["request_id"]

            api_elapsed_time = time.time() - api_start_time
            logger.debug(
                f"腾讯云 API 调用完成 | task_id={task_id}, request_id={tencent_request_id}, "
                f"api_time={api_elapsed_time:.2f}s"
            )

            # 将 Base64 结果保存到存储服务
            # 原因: 使用统一的存储抽象层,所有文件都由 StorageService 管理
            result_filename = f"{task_id}.jpg"
            result_image_bytes = base64.b64decode(result_image_base64)

            logger.debug(
                f"保存风格化结果 | filename={result_filename}, size={len(result_image_bytes)} bytes"
            )

            file_object = loop.run_until_complete(
                storage_service.upload_file(
                    file_content=result_image_bytes,
                    filename=result_filename,
                    content_type="image/jpeg",
                )
            )

            result_object_key = file_object.object_key
            logger.info(f"风格化结果已保存 | result_object_key={result_object_key}")

        finally:
            loop.close()

        actual_time = int(time.time() - start_time)

        logger.info(
            f"风格化任务处理成功 | task_id={task_id}, request_id={tencent_request_id}, "
            f"total_time={actual_time}s, result_object_key={result_object_key}"
        )

        # 更新 Redis 中的任务状态
        try:
            logger.info(f"更新 Redis 任务状态为 success | task_id={task_id}")
            _update_task_in_redis(
                task_id=task_id,
                status="success",
                result_object_key=result_object_key,
                tencent_request_id=tencent_request_id,
                actual_time=actual_time,
            )
            logger.info(
                f"Redis 任务状态已更新为 COMPLETED | task_id={task_id}, "
                f"result_object_key={result_object_key}"
            )
        except Exception as update_error:
            logger.error(
                f"更新 Redis 任务状态失败 | task_id={task_id}, "
                f"error_type={type(update_error).__name__}, error={str(update_error)}",
                exc_info=True,
            )
            # 原因: 虽然风格化成功，但状态更新失败会导致前端无法获取结果
            # 抛出异常，触发 Celery 重试
            raise

        return {
            "status": "success",
            "task_id": task_id,
            "result_object_key": result_object_key,
            "tencent_request_id": tencent_request_id,
            "actual_time": actual_time,
        }

    except TencentCloudAPIError as e:
        actual_time = int(time.time() - start_time)

        logger.error(
            f"风格化任务失败(腾讯云 API 错误) | task_id={task_id}, "
            f"error_code={e.error_code}, tencent_error_code={e.tencent_error_code}, "
            f"request_id={e.tencent_request_id}, is_retryable={e.is_retryable}, "
            f"total_time={actual_time}s, message={e.message}"
        )

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
            logger.warning(
                f"任务将重试 | task_id={task_id}, retry_count={self.request.retries + 1}, "
                f"retry_delay={retry_delay}s"
            )
            raise self.retry(exc=e, countdown=retry_delay)

        # 更新 Redis 中的任务状态
        try:
            logger.info(f"更新 Redis 任务状态为 failed | task_id={task_id}")
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
            logger.info(f"Redis 任务状态已更新为 FAILED | task_id={task_id}")
        except Exception as update_error:
            logger.error(
                f"更新 Redis 任务状态失败 | task_id={task_id}, "
                f"error_type={type(update_error).__name__}, error={str(update_error)}",
                exc_info=True,
            )

        return error_result

    except Exception as e:
        actual_time = int(time.time() - start_time)

        logger.error(
            f"风格化任务失败(未知错误) | task_id={task_id}, "
            f"total_time={actual_time}s, error_type={type(e).__name__}, "
            f"error_message={str(e)}"
        )

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
            logger.info(f"更新 Redis 任务状态为 failed (unknown error) | task_id={task_id}")
            _update_task_in_redis(
                task_id=task_id,
                status="failed",
                error_code="UNKNOWN_ERROR",
                error_message=str(e),
                is_retryable=False,
            )
            logger.info(f"Redis 任务状态已更新为 FAILED | task_id={task_id}")
        except Exception as update_error:
            logger.error(
                f"更新 Redis 任务状态失败 | task_id={task_id}, "
                f"error_type={type(update_error).__name__}, error={str(update_error)}",
                exc_info=True,
            )

        return error_result


def _update_task_status_to_processing(task_id: str) -> None:
    """
    将任务状态更新为 PROCESSING。

    Args:
        task_id: 任务ID

    Raises:
        Exception: 如果更新失败
    """
    logger.debug(f"开始更新任务状态 | task_id={task_id}, target_status=PROCESSING")

    task_store = RedisStyleTaskStore(redis_url=settings.redis_url)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 从 Redis 获取任务
        logger.debug(f"从 Redis 获取任务 | task_id={task_id}")
        task = loop.run_until_complete(task_store.get_task(UUID(task_id)))

        if task is None:
            error_msg = f"任务不存在于 Redis | task_id={task_id}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug(f"任务当前状态 | task_id={task_id}, current_status={task.status.value}")

        # 更新任务状态为 PROCESSING
        task.start_processing()
        logger.debug(f"任务状态已更新为 PROCESSING (内存) | task_id={task_id}")

        # 保存更新后的任务
        loop.run_until_complete(task_store.update_task(task))
        logger.info(f"任务状态已保存到 Redis | task_id={task_id}, status=PROCESSING")

    except Exception as e:
        logger.error(
            f"更新任务状态失败 | task_id={task_id}, error_type={type(e).__name__}, error={str(e)}",
            exc_info=True,
        )
        raise
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
    logger.debug(f"开始更新 Redis 任务状态 | task_id={task_id}, target_status={status}")

    task_store = RedisStyleTaskStore(redis_url=settings.redis_url)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 从 Redis 获取任务
        logger.debug(f"从 Redis 获取任务 | task_id={task_id}")
        task = loop.run_until_complete(task_store.get_task(UUID(task_id)))

        if task is None:
            error_msg = f"任务不存在于 Redis | task_id={task_id}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug(f"任务当前状态 | task_id={task_id}, current_status={task.status.value}")

        # 更新任务状态
        if status == "success":
            logger.debug(f"标记任务为完成 | task_id={task_id}")
            # 使用 result_object_key 或兼容旧的 result_path
            result_path = kwargs.get("result_object_key") or kwargs.get("result_path", "")
            task.mark_completed(
                result_path=result_path,
                tencent_request_id=kwargs.get("tencent_request_id", ""),
                actual_time=kwargs.get("actual_time", 0),
            )
        elif status == "failed":
            logger.debug(f"标记任务为失败 | task_id={task_id}")
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
        logger.debug(f"保存任务到 Redis | task_id={task_id}, status={task.status.value}")
        loop.run_until_complete(task_store.update_task(task))
        logger.info(
            f"任务状态已保存到 Redis | task_id={task_id}, "
            f"status={task.status.value}, updated_at={task.updated_at.isoformat()}"
        )

    except Exception as e:
        logger.error(
            f"更新 Redis 任务状态失败 | task_id={task_id}, target_status={status}, "
            f"error_type={type(e).__name__}, error={str(e)}",
            exc_info=True,
        )
        raise
    finally:
        loop.run_until_complete(task_store.close())
        loop.close()


@celery_app.task(name="style_tasks.cleanup_expired_style_results")
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
    logger.info(f"开始清理过期风格化结果 | days={days}")

    # 使用统一的存储服务
    # 原因: 符合存储抽象层原则,便于后续替换为 MinIO/S3
    storage_service = LocalStorageService(base_path=settings.storage_path)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 调用存储服务的清理方法
        cleaned_count = loop.run_until_complete(storage_service.cleanup_expired_files())

        logger.info(f"清理完成 | cleaned_count={cleaned_count}")

        return {
            "cleaned_count": cleaned_count,
            "freed_space_mb": 0,  # LocalStorageService 暂不返回释放空间,可后续扩展
        }
    finally:
        loop.close()
