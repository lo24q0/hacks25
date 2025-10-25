from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from domain.enums.print_enums import AdapterType, PrinterStatus
from domain.value_objects.printer_profile import PrinterProfile
from domain.value_objects.connection_config import ConnectionConfig
from shared.exceptions.domain_exceptions import PrinterBusyError


class Printer(BaseModel):
    """
    打印机实体
    
    Attributes:
        id: 打印机唯一标识
        name: 打印机名称
        model: 打印机型号
        adapter_type: 适配器类型
        connection_config: 连接配置
        profile: 打印机硬件配置
        status: 打印机状态
        current_task_id: 当前打印任务ID
        is_enabled: 是否启用
        created_at: 创建时间
        last_heartbeat: 最后心跳时间
    """
    id: str = Field(...)
    name: str = Field(...)
    model: str = Field(...)
    adapter_type: AdapterType = Field(...)
    connection_config: ConnectionConfig = Field(...)
    profile: PrinterProfile = Field(...)
    status: PrinterStatus = Field(default=PrinterStatus.OFFLINE)
    current_task_id: Optional[UUID] = Field(default=None)
    is_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = False

    def is_available(self) -> bool:
        """
        检查打印机是否可用
        
        Returns:
            bool: 打印机在线、空闲且已启用则返回True
        """
        return (
            self.is_enabled
            and self.status == PrinterStatus.IDLE
            and self.current_task_id is None
        )

    def update_status(self, status: PrinterStatus) -> None:
        """
        更新打印机状态
        
        Args:
            status: 新状态
        """
        self.status = status
        self.last_heartbeat = datetime.utcnow()

    def assign_task(self, task_id: UUID) -> None:
        """
        分配打印任务
        
        Args:
            task_id: 任务ID
            
        Raises:
            PrinterBusyError: 如果打印机不可用
        """
        if not self.is_available():
            raise PrinterBusyError(
                f"Printer {self.id} is not available (status: {self.status})"
            )
        self.current_task_id = task_id
        self.status = PrinterStatus.BUSY

    def release_task(self) -> None:
        """
        释放当前任务
        """
        self.current_task_id = None
        self.status = PrinterStatus.IDLE

    def update_heartbeat(self) -> None:
        """
        更新心跳时间
        """
        self.last_heartbeat = datetime.utcnow()
