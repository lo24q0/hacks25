from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ..enums import ModelStatus, SourceType
from ..value_objects import ModelMetadata, SourceData


@dataclass
class ValidationResult:
    """
    验证结果。

    Args:
        is_valid (bool): 是否验证通过
        errors (list[str]): 错误信息列表
    """
    is_valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class Model3D:
    """
    3D模型聚合根。

    Args:
        id (UUID): 模型唯一标识
        user_id (Optional[UUID]): 用户ID(P2阶段引入)
        source_type (SourceType): 源类型(TEXT或IMAGE)
        source_data (SourceData): 源数据
        status (ModelStatus): 模型状态
        file_path (Optional[str]): STL文件路径
        thumbnail_path (Optional[str]): 缩略图路径
        metadata (Optional[ModelMetadata]): 模型元数据
        error_message (Optional[str]): 错误信息
        created_at (datetime): 创建时间
        updated_at (datetime): 更新时间
    """
    id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    source_type: SourceType = SourceType.TEXT
    source_data: SourceData = field(default_factory=lambda: SourceData(text_prompt=""))
    status: ModelStatus = ModelStatus.PENDING
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    metadata: Optional[ModelMetadata] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def start_generation(self) -> None:
        """
        开始生成模型。

        Raises:
            ValueError: 如果状态不是PENDING
        """
        if self.status != ModelStatus.PENDING:
            raise ValueError(f"Cannot start generation from status: {self.status}")
        
        self.status = ModelStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, file_path: str, metadata: ModelMetadata, thumbnail_path: Optional[str] = None) -> None:
        """
        标记模型生成完成。

        Args:
            file_path (str): STL文件路径
            metadata (ModelMetadata): 模型元数据
            thumbnail_path (Optional[str]): 缩略图路径

        Raises:
            ValueError: 如果状态不是PROCESSING或文件路径为空
        """
        if self.status != ModelStatus.PROCESSING:
            raise ValueError(f"Cannot mark completed from status: {self.status}")
        
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")
        
        self.status = ModelStatus.COMPLETED
        self.file_path = file_path
        self.metadata = metadata
        self.thumbnail_path = thumbnail_path
        self.error_message = None
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """
        标记模型生成失败。

        Args:
            error (str): 错误信息

        Raises:
            ValueError: 如果错误信息为空
        """
        if not error or not error.strip():
            raise ValueError("error message cannot be empty")
        
        self.status = ModelStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.utcnow()

    def validate_for_printing(self) -> ValidationResult:
        """
        验证模型是否可以打印。

        Returns:
            ValidationResult: 验证结果
        """
        errors = []

        if self.status != ModelStatus.COMPLETED:
            errors.append(f"Model status must be COMPLETED, current: {self.status}")

        if not self.file_path:
            errors.append("Model file path is missing")

        if not self.metadata:
            errors.append("Model metadata is missing")
        elif not self.metadata.is_printable():
            if not self.metadata.is_manifold:
                errors.append("Model is not manifold (has holes or non-manifold geometry)")
            if self.metadata.volume <= 0:
                errors.append("Model has zero or negative volume")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

    def is_completed(self) -> bool:
        """
        检查模型是否已完成。

        Returns:
            bool: 是否已完成
        """
        return self.status == ModelStatus.COMPLETED

    def is_failed(self) -> bool:
        """
        检查模型是否失败。

        Returns:
            bool: 是否失败
        """
        return self.status == ModelStatus.FAILED

    def is_processing(self) -> bool:
        """
        检查模型是否正在处理。

        Returns:
            bool: 是否正在处理
        """
        return self.status == ModelStatus.PROCESSING
