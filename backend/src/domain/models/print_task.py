from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

from src.domain.enums.print_enums import TaskStatus
from src.domain.value_objects.slicing_config import SlicingConfig
from src.shared.exceptions.domain_exceptions import InvalidStateError


class PrintTask(BaseModel):
    """
    打印任务聚合根

    Attributes:
        id: 任务唯一标识
        model_id: 关联的3D模型ID
        printer_id: 目标打印机ID
        status: 任务状态
        queue_position: 队列位置
        slicing_config: 切片配置
        gcode_path: G-code文件路径
        estimated_time: 预估打印时长
        estimated_material: 预估耗材量(克)
        actual_start_time: 实际开始时间
        actual_end_time: 实际结束时间
        progress: 打印进度(0-100)
        error_message: 错误信息
        created_at: 创建时间
        updated_at: 更新时间
    """

    id: UUID = Field(default_factory=uuid4)
    model_id: UUID = Field(...)
    printer_id: str = Field(...)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    queue_position: Optional[int] = Field(default=None)
    slicing_config: SlicingConfig = Field(...)
    gcode_path: Optional[str] = Field(default=None)
    estimated_time: Optional[timedelta] = Field(default=None)
    estimated_material: Optional[float] = Field(default=None)
    actual_start_time: Optional[datetime] = Field(default=None)
    actual_end_time: Optional[datetime] = Field(default=None)
    progress: int = Field(default=0, ge=0, le=100)
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = False

    def start_slicing(self) -> None:
        """
        开始切片处理

        Raises:
            InvalidStateError: 如果任务状态不允许切片
        """
        if self.status != TaskStatus.PENDING:
            raise InvalidStateError(f"Cannot start slicing: task status is {self.status}")
        self.status = TaskStatus.SLICING
        self.updated_at = datetime.utcnow()

    def enqueue(self, position: int) -> None:
        """
        加入打印队列

        Args:
            position: 队列位置
        """
        self.status = TaskStatus.QUEUED
        self.queue_position = position
        self.updated_at = datetime.utcnow()

    def start_printing(self) -> None:
        """
        开始打印

        Raises:
            InvalidStateError: 如果任务状态不允许打印
        """
        if self.status != TaskStatus.QUEUED:
            raise InvalidStateError(f"Cannot start printing: task status is {self.status}")
        self.status = TaskStatus.PRINTING
        self.actual_start_time = datetime.utcnow()
        self.queue_position = None
        self.updated_at = datetime.utcnow()

    def update_progress(self, progress: int) -> None:
        """
        更新打印进度

        Args:
            progress: 进度百分比(0-100)
        """
        if progress < 0 or progress > 100:
            raise ValueError(f"Progress must be between 0 and 100, got {progress}")
        self.progress = progress
        self.updated_at = datetime.utcnow()

    def mark_completed(self) -> None:
        """
        标记任务完成
        """
        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.actual_end_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """
        标记任务失败

        Args:
            error: 错误信息
        """
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.actual_end_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """
        取消任务

        Raises:
            InvalidStateError: 如果任务状态不允许取消
        """
        if self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise InvalidStateError(f"Cannot cancel: task is already in final state {self.status}")
        self.status = TaskStatus.CANCELLED
        self.actual_end_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def pause(self) -> None:
        """
        暂停任务

        Raises:
            InvalidStateError: 如果任务状态不允许暂停
        """
        if self.status != TaskStatus.PRINTING:
            raise InvalidStateError(f"Cannot pause: task status is {self.status}")
        self.status = TaskStatus.PAUSED
        self.updated_at = datetime.utcnow()

    def resume(self) -> None:
        """
        恢复任务

        Raises:
            InvalidStateError: 如果任务状态不允许恢复
        """
        if self.status != TaskStatus.PAUSED:
            raise InvalidStateError(f"Cannot resume: task status is {self.status}")
        self.status = TaskStatus.PRINTING
        self.updated_at = datetime.utcnow()
