"""
文本转3D服务实现。

处理文本到3D模型的完整生成流程,包括预览阶段和精细化阶段。
"""

import asyncio
import logging
from typing import Optional

from infrastructure.ai.meshy_client import MeshyAPIError, MeshyClient
from infrastructure.ai.meshy_models import (
    GenerationConfig,
    MeshyTaskResponse,
    TextTo3DPreviewRequest,
    TextTo3DRefineRequest,
)

logger = logging.getLogger(__name__)


class TextTo3DService:
    """
    文本转3D服务类。

    提供预览阶段和精细化阶段的完整生成流程,包含任务状态轮询功能。
    """

    def __init__(
        self,
        meshy_client: Optional[MeshyClient] = None,
        default_config: Optional[GenerationConfig] = None,
    ):
        """
        初始化文本转3D服务。

        Args:
            meshy_client: Meshy API 客户端实例,如果为 None 则创建新实例
            default_config: 默认生成配置,如果为 None 则使用默认值
        """
        self._client = meshy_client or MeshyClient()
        self._default_config = default_config or GenerationConfig()
        self._should_close_client = meshy_client is None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._client._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._should_close_client:
            await self._client.close()

    async def create_preview_task(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        seed: Optional[int] = None,
    ) -> MeshyTaskResponse:
        """
        创建文本转3D预览任务。

        Args:
            prompt: 文本描述提示词
            config: 生成配置,如果为 None 则使用默认配置
            seed: 随机种子,用于可重现生成

        Returns:
            MeshyTaskResponse: 任务响应,包含任务ID和初始状态

        Raises:
            ValueError: 如果提示词为空或无效
            MeshyAPIError: 如果API调用失败
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        generation_config = config or self._default_config
        request = generation_config.to_text_to_3d_request(prompt=prompt, seed=seed)

        logger.info(
            f"Creating text-to-3d preview task",
            extra={"prompt": prompt, "seed": seed},
        )

        try:
            response = await self._client.create_text_to_3d_task(request)
            logger.info(f"Preview task created successfully: {response.id}")
            return response
        except MeshyAPIError as e:
            logger.error(f"Failed to create preview task: {str(e)}")
            raise

    async def create_refine_task(
        self,
        preview_task_id: str,
        enable_pbr: bool = False,
        texture_prompt: Optional[str] = None,
        texture_image_url: Optional[str] = None,
    ) -> MeshyTaskResponse:
        """
        创建文本转3D精细化任务。

        对已完成的预览任务进行纹理细化处理。

        Args:
            preview_task_id: 已完成的预览任务ID
            enable_pbr: 是否生成PBR贴图(金属度、粗糙度、法线)
            texture_prompt: 纹理引导文本,可选
            texture_image_url: 纹理参考图片URL,可选

        Returns:
            MeshyTaskResponse: 任务响应,包含任务ID和初始状态

        Raises:
            ValueError: 如果预览任务ID为空
            MeshyAPIError: 如果API调用失败
        """
        if not preview_task_id or not preview_task_id.strip():
            raise ValueError("Preview task ID cannot be empty")

        request = TextTo3DRefineRequest(
            preview_task_id=preview_task_id,
            enable_pbr=enable_pbr,
            texture_prompt=texture_prompt,
            texture_image_url=texture_image_url,
        )

        logger.info(
            f"Creating refine task for preview: {preview_task_id}",
            extra={"enable_pbr": enable_pbr},
        )

        try:
            response = await self._client.create_refine_task(request)
            logger.info(f"Refine task created successfully: {response.id}")
            return response
        except MeshyAPIError as e:
            logger.error(f"Failed to create refine task: {str(e)}")
            raise

    async def get_task_status(self, task_id: str) -> MeshyTaskResponse:
        """
        查询任务状态。

        Args:
            task_id: 任务ID

        Returns:
            MeshyTaskResponse: 任务状态信息

        Raises:
            ValueError: 如果任务ID为空
            MeshyAPIError: 如果API调用失败
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")

        try:
            response = await self._client.get_task(task_id)
            logger.debug(
                f"Task {task_id} status: {response.status}, progress: {response.progress}%"
            )
            return response
        except MeshyAPIError as e:
            logger.error(f"Failed to get task status: {str(e)}")
            raise

    async def wait_for_completion(
        self,
        task_id: str,
        check_interval: int = 5,
        max_wait_time: int = 600,
        progress_callback: Optional[callable] = None,
    ) -> MeshyTaskResponse:
        """
        等待任务完成,支持轮询和进度回调。

        Args:
            task_id: 任务ID
            check_interval: 检查间隔(秒),默认5秒
            max_wait_time: 最大等待时间(秒),默认600秒
            progress_callback: 进度回调函数,接收参数 (task_id, status, progress)

        Returns:
            MeshyTaskResponse: 完成后的任务响应

        Raises:
            ValueError: 如果任务ID为空
            MeshyAPIError: 如果任务失败或超时
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")

        elapsed_time = 0
        last_progress = -1

        logger.info(
            f"Waiting for task {task_id} to complete",
            extra={"max_wait_time": max_wait_time},
        )

        while elapsed_time < max_wait_time:
            task = await self.get_task_status(task_id)

            # 调用进度回调
            if progress_callback and task.progress != last_progress:
                try:
                    progress_callback(task_id, task.status, task.progress)
                except Exception as e:
                    logger.warning(f"Progress callback error: {str(e)}")

            last_progress = task.progress

            # 检查任务状态
            if task.status == "SUCCEEDED":
                logger.info(f"Task {task_id} completed successfully")
                return task
            elif task.status == "FAILED":
                error_msg = (
                    task.task_error.get("message", "Unknown error")
                    if task.task_error
                    else "Unknown error"
                )
                logger.error(f"Task {task_id} failed: {error_msg}")
                raise MeshyAPIError(f"Task failed: {error_msg}")
            elif task.status == "EXPIRED":
                logger.error(f"Task {task_id} expired")
                raise MeshyAPIError("Task expired")

            await asyncio.sleep(check_interval)
            elapsed_time += check_interval

        raise MeshyAPIError(
            f"Task {task_id} did not complete within {max_wait_time} seconds"
        )

    async def generate_preview_and_wait(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        seed: Optional[int] = None,
        max_wait_time: int = 600,
        progress_callback: Optional[callable] = None,
    ) -> MeshyTaskResponse:
        """
        创建预览任务并等待完成(便捷方法)。

        Args:
            prompt: 文本描述提示词
            config: 生成配置
            seed: 随机种子
            max_wait_time: 最大等待时间(秒)
            progress_callback: 进度回调函数

        Returns:
            MeshyTaskResponse: 完成后的任务响应

        Raises:
            ValueError: 如果提示词为空
            MeshyAPIError: 如果生成失败
        """
        task = await self.create_preview_task(prompt, config, seed)
        return await self.wait_for_completion(
            task.id,
            max_wait_time=max_wait_time,
            progress_callback=progress_callback,
        )

    async def generate_refined_and_wait(
        self,
        preview_task_id: str,
        enable_pbr: bool = False,
        texture_prompt: Optional[str] = None,
        texture_image_url: Optional[str] = None,
        max_wait_time: int = 600,
        progress_callback: Optional[callable] = None,
    ) -> MeshyTaskResponse:
        """
        创建精细化任务并等待完成(便捷方法)。

        Args:
            preview_task_id: 预览任务ID
            enable_pbr: 是否生成PBR贴图
            texture_prompt: 纹理引导文本
            texture_image_url: 纹理参考图片URL
            max_wait_time: 最大等待时间(秒)
            progress_callback: 进度回调函数

        Returns:
            MeshyTaskResponse: 完成后的任务响应

        Raises:
            ValueError: 如果预览任务ID为空
            MeshyAPIError: 如果生成失败
        """
        task = await self.create_refine_task(
            preview_task_id, enable_pbr, texture_prompt, texture_image_url
        )
        return await self.wait_for_completion(
            task.id,
            max_wait_time=max_wait_time,
            progress_callback=progress_callback,
        )
