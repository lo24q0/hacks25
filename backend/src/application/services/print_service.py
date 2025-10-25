import logging
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from domain.models.print_task import PrintTask
from domain.models.printer import Printer
from domain.value_objects.slicing_config import SlicingConfig
from domain.interfaces.i_queue_manager import IQueueManager
from domain.interfaces.i_printer_adapter import IPrinterAdapter
from domain.enums.print_enums import TaskStatus, PrinterStatus

logger = logging.getLogger(__name__)


class PrintService:
    """
    打印服务(应用服务层)
    
    职责:
    - 编排打印流程(切片 → 队列 → 发送)
    - 管理打印任务生命周期
    - 协调适配器和队列管理器
    """

    def __init__(
        self,
        queue_manager: IQueueManager,
    ):
        self._queue_manager = queue_manager
        self._tasks: dict[UUID, PrintTask] = {}
        self._printers: dict[str, Printer] = {}
        self._adapters: dict[str, IPrinterAdapter] = {}

    async def create_task(
        self,
        model_id: UUID,
        printer_id: str,
        slicing_config: Optional[SlicingConfig] = None,
        priority: int = 0
    ) -> PrintTask:
        """
        创建打印任务
        
        Args:
            model_id: 3D模型ID
            printer_id: 打印机ID
            slicing_config: 切片配置(可选)
            priority: 优先级(可选)
            
        Returns:
            PrintTask: 创建的打印任务
        """
        logger.info(f"Creating print task for model {model_id} on printer {printer_id}")
        
        if slicing_config is None:
            slicing_config = SlicingConfig.get_preset("standard")
        
        task = PrintTask(
            model_id=model_id,
            printer_id=printer_id,
            slicing_config=slicing_config
        )
        
        self._tasks[task.id] = task
        
        position = await self._queue_manager.enqueue(task, priority)
        logger.info(f"Task {task.id} created and enqueued at position {position}")
        
        return task

    async def get_task(self, task_id: UUID) -> Optional[PrintTask]:
        """
        获取打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[PrintTask]: 打印任务
        """
        return self._tasks.get(task_id)

    async def list_tasks(self) -> List[PrintTask]:
        """
        获取所有打印任务
        
        Returns:
            List[PrintTask]: 任务列表
        """
        return list(self._tasks.values())

    async def cancel_task(self, task_id: UUID) -> bool:
        """
        取消打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消
        """
        logger.info(f"Cancelling task {task_id}")
        
        task = self._tasks.get(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            return False
        
        if task.status == TaskStatus.QUEUED:
            await self._queue_manager.remove_task(task_id)
        
        task.cancel()
        logger.info(f"Task {task_id} cancelled")
        return True

    async def pause_task(self, task_id: UUID) -> bool:
        """
        暂停打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功暂停
        """
        logger.info(f"Pausing task {task_id}")
        
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.PRINTING:
            adapter = self._adapters.get(task.printer_id)
            if adapter:
                success = await adapter.pause_print()
                if success:
                    task.pause()
                return success
        
        return False

    async def resume_task(self, task_id: UUID) -> bool:
        """
        恢复打印任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功恢复
        """
        logger.info(f"Resuming task {task_id}")
        
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.PAUSED:
            adapter = self._adapters.get(task.printer_id)
            if adapter:
                success = await adapter.resume_print()
                if success:
                    task.resume()
                return success
        
        return False

    async def register_printer(self, printer: Printer, adapter: IPrinterAdapter) -> None:
        """
        注册打印机
        
        Args:
            printer: 打印机实体
            adapter: 打印机适配器
        """
        logger.info(f"Registering printer {printer.id}")
        self._printers[printer.id] = printer
        self._adapters[printer.id] = adapter

    async def get_printer(self, printer_id: str) -> Optional[Printer]:
        """
        获取打印机
        
        Args:
            printer_id: 打印机ID
            
        Returns:
            Optional[Printer]: 打印机实体
        """
        return self._printers.get(printer_id)

    async def list_printers(self) -> List[Printer]:
        """
        获取所有打印机
        
        Returns:
            List[Printer]: 打印机列表
        """
        return list(self._printers.values())

    async def get_available_printers(self) -> List[Printer]:
        """
        获取可用的打印机
        
        Returns:
            List[Printer]: 可用打印机列表
        """
        return [p for p in self._printers.values() if p.is_available()]
