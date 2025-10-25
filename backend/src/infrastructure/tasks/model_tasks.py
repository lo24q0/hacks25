"""
模型生成异步任务模块。

实现文本转3D和图片转3D的异步任务处理。
"""

import logging
from typing import Dict, Any, Optional

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded

from infrastructure.tasks.celery_app import celery_app
from infrastructure.ai.meshy_client import MeshyClient, MeshyAPIError
from infrastructure.ai.meshy_models import (
    TextTo3DPreviewRequest,
    ImageTo3DRequest,
)
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class ModelGenerationTask(Task):
    """
    模型生成任务基类。
    
    提供任务状态更新和错误处理的通用逻辑。
    """
    
    def on_success(self, retval, task_id, args, kwargs):
        """
        任务成功时的回调。
        
        Args:
            retval: 任务返回值
            task_id: 任务ID
            args: 任务参数
            kwargs: 任务关键字参数
        """
        logger.info(f"Model generation task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        任务失败时的回调。
        
        Args:
            exc: 异常对象
            task_id: 任务ID
            args: 任务参数
            kwargs: 任务关键字参数
            einfo: 异常信息
        """
        logger.error(
            f"Model generation task {task_id} failed: {exc}",
            exc_info=einfo
        )
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        任务重试时的回调。
        
        Args:
            exc: 异常对象
            task_id: 任务ID
            args: 任务参数
            kwargs: 任务关键字参数
            einfo: 异常信息
        """
        logger.warning(f"Model generation task {task_id} retrying due to: {exc}")


def _create_mock_model_result(prompt: str, task_type: str) -> Dict[str, Any]:
    """
    创建 mock 模型生成结果。
    
    Args:
        prompt: 提示词或描述
        task_type: 任务类型 (text 或 image)
        
    Returns:
        Dict[str, Any]: mock 结果数据
    """
    import uuid
    from datetime import datetime
    
    mock_task_id = f"mock_{uuid.uuid4().hex[:16]}"
    
    return {
        "task_id": mock_task_id,
        "status": "SUCCEEDED",
        "progress": 100,
        "model_urls": {
            "glb": f"https://example.com/models/{mock_task_id}.glb",
            "fbx": f"https://example.com/models/{mock_task_id}.fbx",
            "usdz": f"https://example.com/models/{mock_task_id}.usdz",
        },
        "thumbnail_url": f"https://example.com/thumbnails/{mock_task_id}.png",
        "prompt": prompt,
        "task_type": task_type,
        "created_at": datetime.utcnow().isoformat(),
        "finished_at": datetime.utcnow().isoformat(),
        "mock_mode": True,
    }


@celery_app.task(
    bind=True,
    base=ModelGenerationTask,
    name="infrastructure.tasks.model_tasks.generate_model_from_text_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(MeshyAPIError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def generate_model_from_text_task(
    self,
    prompt: str,
    art_style: str = "realistic",
    negative_prompt: Optional[str] = None,
    enable_pbr: bool = True,
    mock_mode: bool = False,
) -> Dict[str, Any]:
    """
    文本转3D模型异步任务。
    
    Args:
        prompt: 文本提示词
        art_style: 艺术风格 (realistic, cartoon, anime等)
        negative_prompt: 负面提示词
        enable_pbr: 是否启用PBR材质
        mock_mode: 是否使用mock模式
        
    Returns:
        Dict[str, Any]: 任务结果
        
    Raises:
        MeshyAPIError: API调用失败
        SoftTimeLimitExceeded: 任务超时
    """
    try:
        logger.info(
            f"Starting text-to-3D task: {self.request.id}",
            extra={
                "prompt": prompt,
                "art_style": art_style,
                "mock_mode": mock_mode,
            }
        )
        
        if mock_mode:
            logger.info(f"Task {self.request.id}: Using mock mode")
            import time
            time.sleep(2)
            result = _create_mock_model_result(prompt, "text")
            logger.info(f"Task {self.request.id}: Mock result generated")
            return result
        
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "initializing",
                "progress": 0,
                "message": "正在初始化任务...",
            }
        )
        
        async def _generate():
            async with MeshyClient() as client:
                request = TextTo3DPreviewRequest(
                    prompt=prompt,
                    art_style=art_style,
                    negative_prompt=negative_prompt,
                    enable_pbr=enable_pbr,
                )
                
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "status": "creating_task",
                        "progress": 10,
                        "message": "正在创建Meshy任务...",
                    }
                )
                
                task_response = await client.create_text_to_3d_task(request)
                meshy_task_id = task_response.id
                
                logger.info(
                    f"Task {self.request.id}: Meshy task created: {meshy_task_id}"
                )
                
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "status": "generating",
                        "progress": 30,
                        "message": "AI正在生成3D模型...",
                        "meshy_task_id": meshy_task_id,
                    }
                )
                
                completed_task = await client.wait_for_task_completion(
                    task_id=meshy_task_id,
                    check_interval=5,
                    max_wait_time=settings.celery_task_soft_time_limit - 30,
                )
                
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "status": "finalizing",
                        "progress": 90,
                        "message": "正在完成任务...",
                    }
                )
                
                result = {
                    "task_id": completed_task.id,
                    "status": completed_task.status,
                    "progress": completed_task.progress,
                    "model_urls": completed_task.model_urls,
                    "thumbnail_url": completed_task.thumbnail_url,
                    "prompt": prompt,
                    "art_style": art_style,
                    "created_at": completed_task.created_at,
                    "finished_at": completed_task.finished_at,
                }
                
                logger.info(
                    f"Task {self.request.id}: Model generated successfully"
                )
                
                return result
        
        import asyncio
        result = asyncio.run(_generate())
        
        return result
        
    except SoftTimeLimitExceeded:
        logger.error(f"Task {self.request.id}: Soft time limit exceeded")
        raise
    except MeshyAPIError as e:
        logger.error(
            f"Task {self.request.id}: Meshy API error: {e.message}",
            extra={"status_code": e.status_code}
        )
        raise
    except Exception as e:
        logger.error(
            f"Task {self.request.id}: Unexpected error: {str(e)}",
            exc_info=True
        )
        raise


@celery_app.task(
    bind=True,
    base=ModelGenerationTask,
    name="infrastructure.tasks.model_tasks.generate_model_from_image_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(MeshyAPIError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def generate_model_from_image_task(
    self,
    image_url: str,
    enable_pbr: bool = True,
    mock_mode: bool = False,
) -> Dict[str, Any]:
    """
    图片转3D模型异步任务。
    
    Args:
        image_url: 图片URL
        enable_pbr: 是否启用PBR材质
        mock_mode: 是否使用mock模式
        
    Returns:
        Dict[str, Any]: 任务结果
        
    Raises:
        MeshyAPIError: API调用失败
        SoftTimeLimitExceeded: 任务超时
    """
    try:
        logger.info(
            f"Starting image-to-3D task: {self.request.id}",
            extra={
                "image_url": image_url,
                "mock_mode": mock_mode,
            }
        )
        
        if mock_mode:
            logger.info(f"Task {self.request.id}: Using mock mode")
            import time
            time.sleep(2)
            result = _create_mock_model_result(image_url, "image")
            logger.info(f"Task {self.request.id}: Mock result generated")
            return result
        
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "initializing",
                "progress": 0,
                "message": "正在初始化任务...",
            }
        )
        
        async def _generate():
            async with MeshyClient() as client:
                request = ImageTo3DRequest(
                    image_url=image_url,
                    enable_pbr=enable_pbr,
                )
                
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "status": "creating_task",
                        "progress": 10,
                        "message": "正在创建Meshy任务...",
                    }
                )
                
                task_response = await client.create_image_to_3d_task(request)
                meshy_task_id = task_response.id
                
                logger.info(
                    f"Task {self.request.id}: Meshy task created: {meshy_task_id}"
                )
                
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "status": "generating",
                        "progress": 30,
                        "message": "AI正在从图片生成3D模型...",
                        "meshy_task_id": meshy_task_id,
                    }
                )
                
                completed_task = await client.wait_for_task_completion(
                    task_id=meshy_task_id,
                    check_interval=5,
                    max_wait_time=settings.celery_task_soft_time_limit - 30,
                )
                
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "status": "finalizing",
                        "progress": 90,
                        "message": "正在完成任务...",
                    }
                )
                
                result = {
                    "task_id": completed_task.id,
                    "status": completed_task.status,
                    "progress": completed_task.progress,
                    "model_urls": completed_task.model_urls,
                    "thumbnail_url": completed_task.thumbnail_url,
                    "image_url": image_url,
                    "created_at": completed_task.created_at,
                    "finished_at": completed_task.finished_at,
                }
                
                logger.info(
                    f"Task {self.request.id}: Model generated successfully"
                )
                
                return result
        
        import asyncio
        result = asyncio.run(_generate())
        
        return result
        
    except SoftTimeLimitExceeded:
        logger.error(f"Task {self.request.id}: Soft time limit exceeded")
        raise
    except MeshyAPIError as e:
        logger.error(
            f"Task {self.request.id}: Meshy API error: {e.message}",
            extra={"status_code": e.status_code}
        )
        raise
    except Exception as e:
        logger.error(
            f"Task {self.request.id}: Unexpected error: {str(e)}",
            exc_info=True
        )
        raise
