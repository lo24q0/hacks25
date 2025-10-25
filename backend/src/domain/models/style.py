"""
风格化领域模型模块。

定义风格化任务的领域模型和业务逻辑。
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from domain.enums.status import TaskStatus
from domain.value_objects.style_metadata import ErrorInfo, StyleTaskMetadata


class StyleTask:
    """
    风格化任务聚合根。

    封装图片风格化任务的完整生命周期和业务规则。

    Args:
        id: 任务唯一标识符
        image_path: 输入图片路径
        style_preset_id: 风格预设ID
        status: 任务状态
        result_path: 风格化后的图片路径
        metadata: 任务元数据
        error_info: 错误信息
        created_at: 创建时间
        updated_at: 更新时间
    """

    def __init__(
        self,
        image_path: str,
        style_preset_id: str,
        style_preset_name: str,
        id: Optional[UUID] = None,
        status: TaskStatus = TaskStatus.PENDING,
        result_path: Optional[str] = None,
        metadata: Optional[StyleTaskMetadata] = None,
        error_info: Optional[ErrorInfo] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.image_path = image_path
        self.style_preset_id = style_preset_id
        self.status = status
        self.result_path = result_path
        self.error_info = error_info
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

        if metadata is None:
            self.metadata = StyleTaskMetadata(
                style_preset_id=style_preset_id,
                style_preset_name=style_preset_name,
            )
        else:
            self.metadata = metadata

    def start_processing(self) -> None:
        """
        开始处理任务。

        将任务状态从 PENDING 更新为 PROCESSING。

        Raises:
            ValueError: 如果任务状态不是 PENDING
        """
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"只能开始处理状态为 PENDING 的任务,当前状态: {self.status}")

        self.status = TaskStatus.PROCESSING
        self.updated_at = datetime.now()

    def mark_completed(self, result_path: str, tencent_request_id: str, actual_time: int) -> None:
        """
        标记任务为已完成。

        Args:
            result_path: 风格化后的图片路径
            tencent_request_id: 腾讯云请求ID
            actual_time: 实际处理时间(秒)

        Raises:
            ValueError: 如果任务状态不是 PROCESSING
        """
        if self.status != TaskStatus.PROCESSING:
            raise ValueError(f"只能完成状态为 PROCESSING 的任务,当前状态: {self.status}")

        self.status = TaskStatus.COMPLETED
        self.result_path = result_path
        self.updated_at = datetime.now()

        self.metadata = StyleTaskMetadata(
            style_preset_id=self.metadata.style_preset_id,
            style_preset_name=self.metadata.style_preset_name,
            estimated_time=self.metadata.estimated_time,
            actual_time=actual_time,
            tencent_request_id=tencent_request_id,
            created_at=self.metadata.created_at,
            completed_at=datetime.now(),
        )

    def mark_failed(self, error_info: ErrorInfo) -> None:
        """
        标记任务为失败。

        Args:
            error_info: 错误信息

        Raises:
            ValueError: 如果任务状态不是 PROCESSING
        """
        if self.status != TaskStatus.PROCESSING:
            raise ValueError(f"只能标记状态为 PROCESSING 的任务为失败,当前状态: {self.status}")

        self.status = TaskStatus.FAILED
        self.error_info = error_info
        self.updated_at = datetime.now()

    def is_completed(self) -> bool:
        """
        检查任务是否已完成。

        Returns:
            bool: 如果任务状态为 COMPLETED 则返回 True
        """
        return self.status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        """
        检查任务是否失败。

        Returns:
            bool: 如果任务状态为 FAILED 则返回 True
        """
        return self.status == TaskStatus.FAILED

    def can_retry(self) -> bool:
        """
        检查任务是否可以重试。

        Returns:
            bool: 如果任务失败且错误可重试则返回 True
        """
        return self.is_failed() and self.error_info is not None and self.error_info.is_retryable

    def to_dict(self) -> dict:
        """
        转换为字典格式(用于序列化)。

        Returns:
            dict: 任务的字典表示
        """
        return {
            "id": str(self.id),
            "image_path": self.image_path,
            "style_preset_id": self.style_preset_id,
            "status": self.status.value,
            "result_path": self.result_path,
            "metadata": {
                "style_preset_id": self.metadata.style_preset_id,
                "style_preset_name": self.metadata.style_preset_name,
                "estimated_time": self.metadata.estimated_time,
                "actual_time": self.metadata.actual_time,
                "tencent_request_id": self.metadata.tencent_request_id,
                "created_at": self.metadata.created_at.isoformat() if self.metadata.created_at else None,
                "completed_at": (
                    self.metadata.completed_at.isoformat() if self.metadata.completed_at else None
                ),
            },
            "error_info": (
                {
                    "error_code": self.error_info.error_code,
                    "error_message": self.error_info.error_message,
                    "tencent_error_code": self.error_info.tencent_error_code,
                    "user_message": self.error_info.user_message,
                    "suggestion": self.error_info.suggestion,
                    "is_retryable": self.error_info.is_retryable,
                }
                if self.error_info
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
