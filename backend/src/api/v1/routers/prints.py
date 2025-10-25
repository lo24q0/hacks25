import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from src.api.v1.schemas.print import (
    CreatePrintTaskRequest,
    PrintTaskResponse,
    RegisterPrinterRequest,
    PrinterResponse,
    QueueStatusResponse,
    PrintTaskSummary
)
from src.application.services.print_service import PrintService
from src.domain.models.printer import Printer
from src.infrastructure.printer.adapters.bambu_adapter import BambuAdapter
from src.infrastructure.printer.queue.queue_manager import QueueManager
from src.domain.enums.print_enums import AdapterType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prints", tags=["prints"])


def get_print_service() -> PrintService:
    """
    获取打印服务实例(依赖注入)
    
    Returns:
        PrintService: 打印服务实例
    """
    queue_manager = QueueManager()
    return PrintService(queue_manager=queue_manager)


@router.post("/tasks", response_model=PrintTaskResponse)
async def create_print_task(
    request: CreatePrintTaskRequest,
    print_service: PrintService = Depends(get_print_service)
) -> PrintTaskResponse:
    """
    创建打印任务
    
    Args:
        request: 请求参数
        print_service: 打印服务
        
    Returns:
        PrintTaskResponse: 任务信息
    """
    logger.info(f"Creating print task for model {request.model_id}")
    
    task = await print_service.create_task(
        model_id=request.model_id,
        printer_id=request.printer_id,
        slicing_config=request.slicing_config,
        priority=request.priority
    )
    
    return PrintTaskResponse.from_domain(task)


@router.get("/tasks", response_model=List[PrintTaskResponse])
async def list_print_tasks(
    print_service: PrintService = Depends(get_print_service)
) -> List[PrintTaskResponse]:
    """
    获取所有打印任务
    
    Args:
        print_service: 打印服务
        
    Returns:
        List[PrintTaskResponse]: 任务列表
    """
    logger.info("Listing all print tasks")
    
    tasks = await print_service.list_tasks()
    return [PrintTaskResponse.from_domain(t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=PrintTaskResponse)
async def get_print_task(
    task_id: UUID,
    print_service: PrintService = Depends(get_print_service)
) -> PrintTaskResponse:
    """
    获取打印任务详情
    
    Args:
        task_id: 任务ID
        print_service: 打印服务
        
    Returns:
        PrintTaskResponse: 任务信息
    """
    logger.info(f"Getting print task {task_id}")
    
    task = await print_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return PrintTaskResponse.from_domain(task)


@router.delete("/tasks/{task_id}")
async def cancel_print_task(
    task_id: UUID,
    print_service: PrintService = Depends(get_print_service)
) -> dict:
    """
    取消打印任务
    
    Args:
        task_id: 任务ID
        print_service: 打印服务
        
    Returns:
        dict: 操作结果
    """
    logger.info(f"Cancelling print task {task_id}")
    
    success = await print_service.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return {"success": True, "message": f"Task {task_id} cancelled"}


@router.post("/tasks/{task_id}/pause")
async def pause_print_task(
    task_id: UUID,
    print_service: PrintService = Depends(get_print_service)
) -> dict:
    """
    暂停打印任务
    
    Args:
        task_id: 任务ID
        print_service: 打印服务
        
    Returns:
        dict: 操作结果
    """
    logger.info(f"Pausing print task {task_id}")
    
    success = await print_service.pause_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to pause task {task_id}")
    
    return {"success": True, "message": f"Task {task_id} paused"}


@router.post("/tasks/{task_id}/resume")
async def resume_print_task(
    task_id: UUID,
    print_service: PrintService = Depends(get_print_service)
) -> dict:
    """
    恢复打印任务
    
    Args:
        task_id: 任务ID
        print_service: 打印服务
        
    Returns:
        dict: 操作结果
    """
    logger.info(f"Resuming print task {task_id}")
    
    success = await print_service.resume_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to resume task {task_id}")
    
    return {"success": True, "message": f"Task {task_id} resumed"}


@router.post("/printers", response_model=PrinterResponse)
async def register_printer(
    request: RegisterPrinterRequest,
    print_service: PrintService = Depends(get_print_service)
) -> PrinterResponse:
    """
    注册打印机
    
    Args:
        request: 请求参数
        print_service: 打印服务
        
    Returns:
        PrinterResponse: 打印机信息
    """
    logger.info(f"Registering printer: {request.name}")
    
    printer = Printer(
        id=f"{request.adapter_type.value}_{request.name.replace(' ', '_').lower()}",
        name=request.name,
        model=request.model,
        adapter_type=request.adapter_type,
        connection_config=request.connection_config,
        profile=request.profile
    )

    if request.adapter_type == AdapterType.BAMBU:
        adapter = BambuAdapter()
        await adapter.connect(request.connection_config)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported adapter type: {request.adapter_type}")
    
    await print_service.register_printer(printer, adapter)
    
    return PrinterResponse.from_domain(printer)


@router.get("/printers", response_model=List[PrinterResponse])
async def list_printers(
    print_service: PrintService = Depends(get_print_service)
) -> List[PrinterResponse]:
    """
    获取所有打印机
    
    Args:
        print_service: 打印服务
        
    Returns:
        List[PrinterResponse]: 打印机列表
    """
    logger.info("Listing all printers")
    
    printers = await print_service.list_printers()
    return [PrinterResponse.from_domain(p) for p in printers]


@router.get("/printers/{printer_id}", response_model=PrinterResponse)
async def get_printer(
    printer_id: str,
    print_service: PrintService = Depends(get_print_service)
) -> PrinterResponse:
    """
    获取打印机详情
    
    Args:
        printer_id: 打印机ID
        print_service: 打印服务
        
    Returns:
        PrinterResponse: 打印机信息
    """
    logger.info(f"Getting printer {printer_id}")
    
    printer = await print_service.get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail=f"Printer {printer_id} not found")
    
    return PrinterResponse.from_domain(printer)


@router.get("/queue", response_model=QueueStatusResponse)
async def get_queue_status(
    print_service: PrintService = Depends(get_print_service)
) -> QueueStatusResponse:
    """
    获取打印队列状态
    
    Args:
        print_service: 打印服务
        
    Returns:
        QueueStatusResponse: 队列状态
    """
    logger.info("Getting queue status")
    
    queue_manager = print_service._queue_manager
    status = await queue_manager.get_queue_status()
    
    return QueueStatusResponse(
        total=status.total,
        pending_tasks=[PrintTaskResponse.from_domain(t) for t in status.pending_tasks],
        estimated_wait_time=int(status.estimated_wait_time.total_seconds())
    )
