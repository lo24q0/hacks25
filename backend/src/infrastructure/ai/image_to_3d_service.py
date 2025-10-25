"""
图片转3D服务实现。

处理单张或多张图片到3D模型的生成流程,包括图片预处理和格式转换。
"""

import asyncio
import base64
import logging
import os
from pathlib import Path
from typing import Optional, Union

from src.infrastructure.ai.meshy_client import MeshyAPIError, MeshyClient
from src.infrastructure.ai.meshy_models import (
    GenerationConfig,
    ImageTo3DRequest,
    MeshyTaskResponse,
)

logger = logging.getLogger(__name__)


class ImageTo3DService:
    """
    图片转3D服务类。

    支持单张和多张图片输入,提供图片预处理和格式转换功能。
    """

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(
        self,
        meshy_client: Optional[MeshyClient] = None,
        default_config: Optional[GenerationConfig] = None,
    ):
        """
        初始化图片转3D服务。

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

    def _validate_image_file(self, image_path: str) -> None:
        """
        验证图片文件。

        Args:
            image_path: 图片文件路径

        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件格式或大小不符合要求
        """
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")

        # 检查文件扩展名
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # 检查文件大小
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Image file too large: {file_size} bytes. "
                f"Maximum allowed: {self.MAX_FILE_SIZE} bytes"
            )

    def _image_to_base64_data_uri(self, image_path: str) -> str:
        """
        将图片文件转换为 base64 data URI。

        Args:
            image_path: 图片文件路径

        Returns:
            str: base64 data URI 格式字符串

        Raises:
            IOError: 如果读取文件失败
        """
        path = Path(image_path)
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }

        mime_type = mime_types.get(path.suffix.lower(), "image/jpeg")

        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            base64_data = base64.b64encode(image_data).decode("utf-8")
            return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            raise IOError(f"Failed to read image file: {str(e)}")

    async def create_task_from_file(
        self,
        image_path: str,
        config: Optional[GenerationConfig] = None,
        texture_prompt: Optional[str] = None,
        texture_image_path: Optional[str] = None,
    ) -> MeshyTaskResponse:
        """
        从本地图片文件创建图片转3D任务。

        Args:
            image_path: 图片文件路径
            config: 生成配置,如果为 None 则使用默认配置
            texture_prompt: 纹理引导文本
            texture_image_path: 纹理参考图片路径

        Returns:
            MeshyTaskResponse: 任务响应,包含任务ID和初始状态

        Raises:
            FileNotFoundError: 如果图片文件不存在
            ValueError: 如果图片格式或大小不符合要求
            MeshyAPIError: 如果API调用失败
        """
        # 验证主图片
        self._validate_image_file(image_path)
        image_data_uri = self._image_to_base64_data_uri(image_path)

        # 验证纹理图片(如果提供)
        texture_data_uri = None
        if texture_image_path:
            self._validate_image_file(texture_image_path)
            texture_data_uri = self._image_to_base64_data_uri(texture_image_path)

        logger.info(
            f"Creating image-to-3d task from file",
            extra={"image_path": image_path, "has_texture": texture_image_path is not None},
        )

        return await self.create_task_from_url(
            image_url=image_data_uri,
            config=config,
            texture_prompt=texture_prompt,
            texture_image_url=texture_data_uri,
        )

    async def create_task_from_url(
        self,
        image_url: str,
        config: Optional[GenerationConfig] = None,
        texture_prompt: Optional[str] = None,
        texture_image_url: Optional[str] = None,
    ) -> MeshyTaskResponse:
        """
        从图片URL或base64 data URI创建图片转3D任务。

        Args:
            image_url: 图片URL或base64 data URI
            config: 生成配置,如果为 None 则使用默认配置
            texture_prompt: 纹理引导文本
            texture_image_url: 纹理参考图片URL

        Returns:
            MeshyTaskResponse: 任务响应,包含任务ID和初始状态

        Raises:
            ValueError: 如果图片URL为空
            MeshyAPIError: 如果API调用失败
        """
        if not image_url or not image_url.strip():
            raise ValueError("Image URL cannot be empty")

        generation_config = config or self._default_config
        request = generation_config.to_image_to_3d_request(
            image_url=image_url,
            texture_prompt=texture_prompt,
            texture_image_url=texture_image_url,
        )

        logger.info(
            f"Creating image-to-3d task from URL",
            extra={
                "has_texture_prompt": texture_prompt is not None,
                "has_texture_image": texture_image_url is not None,
            },
        )

        try:
            response = await self._client.create_image_to_3d_task(request)
            logger.info(f"Image-to-3d task created successfully: {response.id}")
            return response
        except MeshyAPIError as e:
            logger.error(f"Failed to create image-to-3d task: {str(e)}")
            raise

    async def create_task_from_multiple_files(
        self,
        image_paths: list[str],
        config: Optional[GenerationConfig] = None,
        texture_prompt: Optional[str] = None,
    ) -> list[MeshyTaskResponse]:
        """
        从多张图片文件批量创建图片转3D任务。

        每张图片创建独立的任务,适用于批量处理场景。

        Args:
            image_paths: 图片文件路径列表
            config: 生成配置,如果为 None 则使用默认配置
            texture_prompt: 纹理引导文本(应用于所有任务)

        Returns:
            list[MeshyTaskResponse]: 任务响应列表

        Raises:
            ValueError: 如果图片列表为空
            FileNotFoundError: 如果任何图片文件不存在
            ValueError: 如果任何图片格式或大小不符合要求
        """
        if not image_paths:
            raise ValueError("Image paths list cannot be empty")

        logger.info(
            f"Creating {len(image_paths)} image-to-3d tasks",
            extra={"count": len(image_paths)},
        )

        tasks = []
        for image_path in image_paths:
            try:
                task = await self.create_task_from_file(
                    image_path=image_path,
                    config=config,
                    texture_prompt=texture_prompt,
                )
                tasks.append(task)
            except Exception as e:
                logger.error(
                    f"Failed to create task for image {image_path}: {str(e)}"
                )
                raise

        logger.info(f"Successfully created {len(tasks)} image-to-3d tasks")
        return tasks

    async def get_task_status(self, task_id: str) -> MeshyTaskResponse:
        """
        查询图片转3D任务状态。

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
            response = await self._client.get_image_to_3d_task(task_id)
            logger.debug(
                f"Image-to-3d task {task_id} status: {response.status}, progress: {response.progress}%"
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
            f"Waiting for image-to-3d task {task_id} to complete",
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
                logger.info(f"Image-to-3d task {task_id} completed successfully")
                return task
            elif task.status == "FAILED":
                error_msg = (
                    task.task_error.get("message", "Unknown error")
                    if task.task_error
                    else "Unknown error"
                )
                logger.error(f"Image-to-3d task {task_id} failed: {error_msg}")
                raise MeshyAPIError(f"Task failed: {error_msg}")
            elif task.status == "EXPIRED":
                logger.error(f"Image-to-3d task {task_id} expired")
                raise MeshyAPIError("Task expired")

            await asyncio.sleep(check_interval)
            elapsed_time += check_interval

        raise MeshyAPIError(
            f"Task {task_id} did not complete within {max_wait_time} seconds"
        )

    async def generate_and_wait(
        self,
        image_source: Union[str, list[str]],
        config: Optional[GenerationConfig] = None,
        texture_prompt: Optional[str] = None,
        max_wait_time: int = 600,
        progress_callback: Optional[callable] = None,
    ) -> Union[MeshyTaskResponse, list[MeshyTaskResponse]]:
        """
        创建任务并等待完成(便捷方法)。

        支持单张图片或多张图片批量处理。

        Args:
            image_source: 图片文件路径(单张)或路径列表(多张)
            config: 生成配置
            texture_prompt: 纹理引导文本
            max_wait_time: 最大等待时间(秒)
            progress_callback: 进度回调函数

        Returns:
            MeshyTaskResponse 或 list[MeshyTaskResponse]: 完成后的任务响应

        Raises:
            ValueError: 如果图片源为空
            MeshyAPIError: 如果生成失败
        """
        # 单张图片
        if isinstance(image_source, str):
            task = await self.create_task_from_file(
                image_path=image_source,
                config=config,
                texture_prompt=texture_prompt,
            )
            return await self.wait_for_completion(
                task.id,
                max_wait_time=max_wait_time,
                progress_callback=progress_callback,
            )

        # 多张图片
        elif isinstance(image_source, list):
            tasks = await self.create_task_from_multiple_files(
                image_paths=image_source,
                config=config,
                texture_prompt=texture_prompt,
            )

            completed_tasks = []
            for task in tasks:
                completed_task = await self.wait_for_completion(
                    task.id,
                    max_wait_time=max_wait_time,
                    progress_callback=progress_callback,
                )
                completed_tasks.append(completed_task)

            return completed_tasks

        else:
            raise ValueError(
                "image_source must be a string (single image) or list[str] (multiple images)"
            )
