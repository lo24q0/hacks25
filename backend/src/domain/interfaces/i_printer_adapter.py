from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

from src.domain.enums.print_enums import PrinterStatus
from src.domain.value_objects.connection_config import ConnectionConfig


class PrintProgress(BaseModel):
    """
    打印进度信息

    Attributes:
        percentage: 进度百分比(0-100)
        layer_current: 当前层数
        layer_total: 总层数
        time_elapsed: 已用时间(秒)
        time_remaining: 剩余时间(秒)
    """

    percentage: int
    layer_current: Optional[int] = None
    layer_total: Optional[int] = None
    time_elapsed: Optional[int] = None
    time_remaining: Optional[int] = None


class IPrinterAdapter(ABC):
    """
    打印机适配器接口

    所有打印机适配器必须实现此接口
    """

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> bool:
        """
        连接打印机

        Args:
            config: 连接配置

        Returns:
            bool: 连接是否成功
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        断开连接
        """
        pass

    @abstractmethod
    async def get_status(self) -> PrinterStatus:
        """
        获取打印机状态

        Returns:
            PrinterStatus: 当前状态
        """
        pass

    @abstractmethod
    async def send_file(self, file_path: str) -> bool:
        """
        发送打印文件

        Args:
            file_path: 文件路径(.gcode 或 .3mf)

        Returns:
            bool: 发送是否成功
        """
        pass

    @abstractmethod
    async def start_print(self, file_name: str) -> bool:
        """
        开始打印

        Args:
            file_name: 文件名

        Returns:
            bool: 启动是否成功
        """
        pass

    @abstractmethod
    async def pause_print(self) -> bool:
        """
        暂停打印

        Returns:
            bool: 暂停是否成功
        """
        pass

    @abstractmethod
    async def resume_print(self) -> bool:
        """
        恢复打印

        Returns:
            bool: 恢复是否成功
        """
        pass

    @abstractmethod
    async def cancel_print(self) -> bool:
        """
        取消打印

        Returns:
            bool: 取消是否成功
        """
        pass

    @abstractmethod
    async def get_progress(self) -> PrintProgress:
        """
        获取打印进度

        Returns:
            PrintProgress: 进度信息
        """
        pass
