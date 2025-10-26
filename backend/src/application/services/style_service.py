"""
风格化应用服务模块。

提供图片风格化的应用层业务逻辑,包括任务创建、状态查询和风格预设管理。
"""

from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from src.domain.interfaces.i_style_engine import StylePreset
from src.domain.models.style import StyleTask
from src.domain.value_objects.style_metadata import ErrorInfo
from src.infrastructure.ai.tencent_style import TencentCloudStyleEngine
from src.infrastructure.config.settings import settings
from src.infrastructure.storage.redis_style_task_store import RedisStyleTaskStore
from src.infrastructure.tasks.style_tasks import process_style_transfer


class StyleService:
    """
    风格化应用服务。

    编排风格化任务的创建、查询和管理流程。

    Args:
        style_engine: 风格化引擎实例
        task_store: Redis 任务存储实例

    示例:
        >>> service = StyleService()
        >>> task = await service.create_style_task(
        ...     image_path="/tmp/input.jpg",
        ...     style_preset_id="anime"
        ... )
        >>> print(task.id)
    """

    FILE_VALIDATION_RULES = {
        "allowed_extensions": [".jpg", ".jpeg", ".png", ".webp"],
        "max_file_size_mb": 10,
        "min_resolution": (512, 512),
        "max_resolution": (2048, 2048),
    }

    def __init__(
        self,
        style_engine: Optional[TencentCloudStyleEngine] = None,
        task_store: Optional[RedisStyleTaskStore] = None,
    ):
        """
        初始化风格化服务。

        Args:
            style_engine: 风格化引擎实例,如果为 None 则使用默认配置创建
            task_store: Redis 任务存储实例,如果为 None 则使用默认配置创建
        """
        if style_engine is None:
            self.style_engine = TencentCloudStyleEngine(
                secret_id=settings.tencent_cloud_secret_id,
                secret_key=settings.tencent_cloud_secret_key,
                region=settings.tencent_cloud_region,
            )
        else:
            self.style_engine = style_engine

        if task_store is None:
            self._task_store = RedisStyleTaskStore(redis_url=settings.redis_url)
        else:
            self._task_store = task_store

    def validate_image_file(self, image_path: str) -> None:
        """
        验证图片文件是否符合要求。

        Args:
            image_path: 图片文件路径

        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件不符合验证规则
        """
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        if not path.is_file():
            raise ValueError(f"不是有效的文件: {image_path}")

        extension = path.suffix.lower()
        if extension not in self.FILE_VALIDATION_RULES["allowed_extensions"]:
            raise ValueError(
                f"不支持的文件格式: {extension}. "
                f"支持的格式: {', '.join(self.FILE_VALIDATION_RULES['allowed_extensions'])}"
            )

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.FILE_VALIDATION_RULES["max_file_size_mb"]:
            raise ValueError(
                f"文件大小超过限制: {file_size_mb:.2f}MB > "
                f"{self.FILE_VALIDATION_RULES['max_file_size_mb']}MB"
            )

    async def create_style_task(
        self,
        image_path: str,
        style_preset_id: str,
    ) -> StyleTask:
        """
        创建风格化任务。

        Args:
            image_path: 输入图片路径
            style_preset_id: 风格预设ID

        Returns:
            StyleTask: 创建的任务实体

        Raises:
            FileNotFoundError: 如果图片文件不存在
            ValueError: 如果文件验证失败或风格预设不存在
        """
        self.validate_image_file(image_path)

        style_preset = self.style_engine.get_style_preset(style_preset_id)

        task = StyleTask(
            image_path=image_path,
            style_preset_id=style_preset_id,
            style_preset_name=style_preset.name,
        )

        # 确保输出目录存在
        # 原因: /tmp/styled 目录可能不存在,导致任务失败
        output_dir = Path("/tmp/styled")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = f"/tmp/styled/{task.id}.jpg"

        # 保存任务到 Redis (状态为 PENDING)
        # 原因: Celery 任务启动后会将状态更新为 PROCESSING,避免任务卡在 PROCESSING 状态
        await self._task_store.save_task(task)

        # 发起异步任务
        process_style_transfer.delay(
            task_id=str(task.id),
            image_path=image_path,
            style_preset_id=style_preset_id,
            output_path=output_path,
        )

        return task

    async def get_task_status(self, task_id: UUID) -> Optional[StyleTask]:
        """
        查询任务状态。

        Args:
            task_id: 任务ID

        Returns:
            Optional[StyleTask]: 任务实体,如果任务不存在则返回 None
        """
        return await self._task_store.get_task(task_id)

    async def update_task_from_celery_result(self, task_id: UUID, celery_result: Dict) -> StyleTask:
        """
        根据 Celery 任务结果更新任务状态。

        Args:
            task_id: 任务ID
            celery_result: Celery 任务结果

        Returns:
            StyleTask: 更新后的任务实体

        Raises:
            ValueError: 如果任务不存在
        """
        task = await self._task_store.get_task(task_id)
        if task is None:
            raise ValueError(f"任务不存在: {task_id}")

        if celery_result["status"] == "success":
            task.mark_completed(
                result_path=celery_result["output_path"],
                tencent_request_id=celery_result.get("tencent_request_id", ""),
                actual_time=celery_result.get("actual_time", 0),
            )
        elif celery_result["status"] == "failed":
            error_info = ErrorInfo(
                error_code=celery_result["error_code"],
                error_message=celery_result["error_message"],
                tencent_error_code=celery_result.get("tencent_error_code"),
                user_message=celery_result.get("user_message"),
                suggestion=celery_result.get("suggestion"),
                is_retryable=celery_result.get("is_retryable", False),
            )
            task.mark_failed(error_info)

        # 更新 Redis 中的任务状态
        await self._task_store.update_task(task)

        return task

    def get_available_styles(self) -> List[StylePreset]:
        """
        获取可用的风格预设列表。

        Returns:
            List[StylePreset]: 风格预设列表
        """
        return self.style_engine.get_available_styles()

    def get_style_preset(self, preset_id: str) -> StylePreset:
        """
        根据ID获取风格预设。

        Args:
            preset_id: 预设ID

        Returns:
            StylePreset: 风格预设

        Raises:
            ValueError: 如果预设不存在
        """
        return self.style_engine.get_style_preset(preset_id)
