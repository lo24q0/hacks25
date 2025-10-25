"""
Meshy 模型生成器实现。

实现 IModelGenerator 接口,统一处理文本和图片两种输入类型的3D模型生成。
"""

import logging
from pathlib import Path
from typing import Optional

from domain.enums import ModelStatus, SourceType
from domain.interfaces.i_model_generator import IModelGenerator
from domain.models.model3d import Model3D
from domain.value_objects import ModelMetadata, SourceData
from infrastructure.ai.image_to_3d_service import ImageTo3DService
from infrastructure.ai.meshy_client import MeshyAPIError, MeshyClient
from infrastructure.ai.meshy_models import GenerationConfig, MeshyTaskResponse
from infrastructure.ai.text_to_3d_service import TextTo3DService

logger = logging.getLogger(__name__)


class MeshyModelGenerator(IModelGenerator):
    """
    Meshy 模型生成器。

    实现 IModelGenerator 接口,提供统一的文本和图片转3D模型生成功能。
    内部使用 TextTo3DService 和 ImageTo3DService 处理具体生成逻辑。
    """

    def __init__(
        self,
        meshy_client: Optional[MeshyClient] = None,
        default_config: Optional[GenerationConfig] = None,
    ):
        """
        初始化 Meshy 模型生成器。

        Args:
            meshy_client: Meshy API 客户端实例,如果为 None 则创建新实例
            default_config: 默认生成配置,如果为 None 则使用默认值
        """
        self._client = meshy_client or MeshyClient()
        self._default_config = default_config or GenerationConfig()

        self._text_service = TextTo3DService(
            meshy_client=self._client,
            default_config=self._default_config,
        )
        self._image_service = ImageTo3DService(
            meshy_client=self._client,
            default_config=self._default_config,
        )

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._client._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self._client.close()

    def _task_response_to_metadata(
        self, task_response: MeshyTaskResponse
    ) -> ModelMetadata:
        """
        将 Meshy 任务响应转换为模型元数据。

        Args:
            task_response: Meshy 任务响应

        Returns:
            ModelMetadata: 模型元数据对象
        """
        # 由于 Meshy API 不直接返回模型尺寸等元数据,
        # 这里创建一个基础的元数据对象,实际元数据需要后续从下载的模型文件中提取
        return ModelMetadata(
            dimensions=(0.0, 0.0, 0.0),  # 需要后续从实际模型文件提取
            volume=0.0,
            triangle_count=0,
            vertex_count=0,
            is_manifold=True,  # 假设 Meshy 生成的模型是流形的
            bounding_box=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        )

    async def generate_from_text(
        self, prompt: str, style_preset: Optional[str] = None
    ) -> tuple[Model3D, str]:
        """
        从文本描述生成3D模型。

        创建预览任务并返回 Model3D 对象和任务ID。
        注意: 此方法仅创建预览阶段的模型,不包含精细化纹理。

        Args:
            prompt: 文本提示词
            style_preset: 风格预设ID(暂未实现,保留参数)

        Returns:
            tuple[Model3D, str]: (创建的模型对象, Meshy任务ID)

        Raises:
            ValueError: 如果提示词为空或无效
            RuntimeError: 如果生成过程失败
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        logger.info(f"Generating 3D model from text", extra={"prompt": prompt})

        # 创建领域模型对象
        model = Model3D(
            source_type=SourceType.TEXT,
            source_data=SourceData(
                text_prompt=prompt,
                style_preset=style_preset,
            ),
            status=ModelStatus.PENDING,
        )

        try:
            # 标记为处理中
            model.start_generation()

            # 创建 Meshy 预览任务
            task_response = await self._text_service.create_preview_task(
                prompt=prompt,
                config=self._default_config,
            )

            logger.info(
                f"Text-to-3D task created",
                extra={
                    "model_id": str(model.id),
                    "task_id": task_response.id,
                },
            )

            # 返回模型对象和任务ID
            return model, task_response.id

        except MeshyAPIError as e:
            error_msg = f"Failed to generate model from text: {str(e)}"
            logger.error(error_msg)
            model.mark_failed(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during text-to-3D generation: {str(e)}"
            logger.error(error_msg)
            model.mark_failed(error_msg)
            raise RuntimeError(error_msg) from e

    async def generate_from_image(
        self, image_path: str, style_preset: Optional[str] = None
    ) -> tuple[Model3D, str]:
        """
        从图片生成3D模型。

        创建图片转3D任务并返回 Model3D 对象和任务ID。

        Args:
            image_path: 图片文件路径
            style_preset: 风格预设ID(暂未实现,保留参数)

        Returns:
            tuple[Model3D, str]: (创建的模型对象, Meshy任务ID)

        Raises:
            ValueError: 如果图片路径无效
            FileNotFoundError: 如果图片文件不存在
            RuntimeError: 如果生成过程失败
        """
        if not image_path or not image_path.strip():
            raise ValueError("Image path cannot be empty")

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        logger.info(
            f"Generating 3D model from image", extra={"image_path": image_path}
        )

        # 创建领域模型对象
        model = Model3D(
            source_type=SourceType.IMAGE,
            source_data=SourceData(
                image_paths=[image_path],
                style_preset=style_preset,
            ),
            status=ModelStatus.PENDING,
        )

        try:
            # 标记为处理中
            model.start_generation()

            # 创建 Meshy 图片转3D任务
            task_response = await self._image_service.create_task_from_file(
                image_path=image_path,
                config=self._default_config,
            )

            logger.info(
                f"Image-to-3D task created",
                extra={
                    "model_id": str(model.id),
                    "task_id": task_response.id,
                },
            )

            # 返回模型对象和任务ID
            return model, task_response.id

        except (FileNotFoundError, ValueError) as e:
            error_msg = str(e)
            logger.error(error_msg)
            model.mark_failed(error_msg)
            raise
        except MeshyAPIError as e:
            error_msg = f"Failed to generate model from image: {str(e)}"
            logger.error(error_msg)
            model.mark_failed(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during image-to-3D generation: {str(e)}"
            logger.error(error_msg)
            model.mark_failed(error_msg)
            raise RuntimeError(error_msg) from e

    async def get_generation_status(self, task_id: str) -> dict:
        """
        获取生成任务状态。

        查询 Meshy 任务状态并返回标准化的状态信息。
        自动识别任务类型(文本转3D或图片转3D)并调用相应的API。

        Args:
            task_id: Meshy 任务ID

        Returns:
            dict: 任务状态信息,包含以下字段:
                - task_id (str): 任务ID
                - status (str): 任务状态 (PENDING/IN_PROGRESS/SUCCEEDED/FAILED/EXPIRED)
                - progress (int): 进度百分比 (0-100)
                - model_urls (dict): 模型文件URLs(如果已完成)
                - thumbnail_url (str): 缩略图URL(如果可用)
                - error (str): 错误信息(如果失败)

        Raises:
            ValueError: 如果任务ID无效
            RuntimeError: 如果查询失败
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")

        try:
            # 尝试作为文本转3D任务查询
            try:
                task_response = await self._text_service.get_task_status(task_id)
            except MeshyAPIError:
                # 如果失败,尝试作为图片转3D任务查询
                task_response = await self._image_service.get_task_status(task_id)

            # 构建标准化的状态响应
            status_dict = {
                "task_id": task_response.id,
                "status": task_response.status,
                "progress": task_response.progress,
                "model_urls": None,
                "thumbnail_url": task_response.thumbnail_url,
                "error": None,
            }

            # 如果任务完成,添加模型URLs
            if task_response.status == "SUCCEEDED" and task_response.model_urls:
                status_dict["model_urls"] = {
                    "glb": task_response.model_urls.glb,
                    "fbx": task_response.model_urls.fbx,
                    "obj": task_response.model_urls.obj,
                    "usdz": task_response.model_urls.usdz,
                }

            # 如果任务失败,添加错误信息
            if task_response.status == "FAILED" and task_response.task_error:
                status_dict["error"] = task_response.task_error.get(
                    "message", "Unknown error"
                )

            logger.debug(
                f"Task status retrieved",
                extra={
                    "task_id": task_id,
                    "status": status_dict["status"],
                    "progress": status_dict["progress"],
                },
            )

            return status_dict

        except MeshyAPIError as e:
            error_msg = f"Failed to get generation status: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting generation status: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def wait_for_completion(
        self,
        task_id: str,
        max_wait_time: int = 600,
        progress_callback: Optional[callable] = None,
    ) -> dict:
        """
        等待任务完成。

        轮询任务状态直到完成、失败或超时。

        Args:
            task_id: Meshy 任务ID
            max_wait_time: 最大等待时间(秒),默认600秒
            progress_callback: 进度回调函数,接收参数 (task_id, status, progress)

        Returns:
            dict: 完成后的任务状态信息

        Raises:
            ValueError: 如果任务ID无效
            RuntimeError: 如果任务失败或超时
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")

        logger.info(
            f"Waiting for task completion",
            extra={"task_id": task_id, "max_wait_time": max_wait_time},
        )

        try:
            # 尝试作为文本转3D任务等待
            try:
                task_response = await self._text_service.wait_for_completion(
                    task_id=task_id,
                    max_wait_time=max_wait_time,
                    progress_callback=progress_callback,
                )
            except MeshyAPIError:
                # 如果失败,尝试作为图片转3D任务等待
                task_response = await self._image_service.wait_for_completion(
                    task_id=task_id,
                    max_wait_time=max_wait_time,
                    progress_callback=progress_callback,
                )

            # 返回最终状态
            return await self.get_generation_status(task_id)

        except MeshyAPIError as e:
            error_msg = f"Task failed or timed out: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error waiting for task: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
