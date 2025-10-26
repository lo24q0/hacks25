from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

from src.domain.enums.print_enums import (
    TaskStatus,
    PrinterStatus,
    AdapterType,
    MaterialType,
    AdhesionType,
)
from src.domain.value_objects.slicing_config import SlicingConfig
from src.domain.value_objects.printer_profile import PrinterProfile
from src.domain.value_objects.connection_config import ConnectionConfig
from src.domain.models.print_task import PrintTask
from src.domain.models.printer import Printer


class CreatePrintTaskRequest(BaseModel):
    """
    创建打印任务请求
    """

    model_config = {"protected_namespaces": ()}

    model_id: UUID = Field(..., description="3D模型ID")
    printer_id: str = Field(..., description="打印机ID")
    slicing_config: Optional[SlicingConfig] = Field(None, description="切片配置")
    priority: int = Field(default=0, description="优先级")


class PrintTaskResponse(BaseModel):
    """
    打印任务响应
    """

    model_config = {"protected_namespaces": ()}

    id: UUID
    model_id: UUID
    printer_id: str
    status: TaskStatus
    queue_position: Optional[int]
    progress: int
    estimated_time: Optional[int]
    estimated_material: Optional[float]
    created_at: datetime

    @classmethod
    def from_domain(cls, task: PrintTask) -> "PrintTaskResponse":
        """
        从领域对象转换

        Args:
            task: 打印任务领域对象

        Returns:
            PrintTaskResponse: API响应对象
        """
        return cls(
            id=task.id,
            model_id=task.model_id,
            printer_id=task.printer_id,
            status=task.status,
            queue_position=task.queue_position,
            progress=task.progress,
            estimated_time=(
                int(task.estimated_time.total_seconds()) if task.estimated_time else None
            ),
            estimated_material=task.estimated_material,
            created_at=task.created_at,
        )


class RegisterPrinterRequest(BaseModel):
    """
    注册打印机请求
    """

    name: str = Field(..., description="打印机名称")
    model: str = Field(..., description="打印机型号")
    adapter_type: AdapterType = Field(..., description="适配器类型")
    connection_config: ConnectionConfig = Field(..., description="连接配置")
    profile: PrinterProfile = Field(..., description="打印机配置")


class PrinterResponse(BaseModel):
    """
    打印机响应
    """

    id: str
    name: str
    model: str
    status: PrinterStatus
    is_available: bool
    current_task_id: Optional[UUID]

    @classmethod
    def from_domain(cls, printer: Printer) -> "PrinterResponse":
        """
        从领域对象转换

        Args:
            printer: 打印机领域对象

        Returns:
            PrinterResponse: API响应对象
        """
        return cls(
            id=printer.id,
            name=printer.name,
            model=printer.model,
            status=printer.status,
            is_available=printer.is_available(),
            current_task_id=printer.current_task_id,
        )


class QueueStatusResponse(BaseModel):
    """
    队列状态响应
    """

    total: int = Field(..., description="总任务数")
    pending_tasks: list[PrintTaskResponse] = Field(..., description="待打印任务列表")
    estimated_wait_time: int = Field(..., description="估算等待时间(秒)")


class PrintTaskSummary(BaseModel):
    """
    打印任务摘要
    """

    model_config = {"protected_namespaces": ()}

    id: UUID
    model_id: UUID
    printer_id: str
    status: TaskStatus
    queue_position: Optional[int]

    @classmethod
    def from_domain(cls, task: PrintTask) -> "PrintTaskSummary":
        """
        从领域对象转换

        Args:
            task: 打印任务领域对象

        Returns:
            PrintTaskSummary: 任务摘要对象
        """
        return cls(
            id=task.id,
            model_id=task.model_id,
            printer_id=task.printer_id,
            status=task.status,
            queue_position=task.queue_position,
        )
