"""
任务管理 API 路由。

提供异步任务的提交、查询等接口。
"""

from datetime import datetime
from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Path, status

from api.v1.schemas.task import TaskStatusResponse, TaskSubmitRequest, TaskSubmitResponse
from infrastructure.tasks.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/submit",
    response_model=TaskSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="提交异步任务",
    description="提交一个异步任务到 Celery 队列",
)
async def submit_task(request: TaskSubmitRequest) -> TaskSubmitResponse:
    """
    提交异步任务。

    Args:
        request: 任务提交请求

    Returns:
        TaskSubmitResponse: 任务提交响应

    Raises:
        HTTPException: 任务提交失败时抛出
    """
    try:
        task_result = celery_app.send_task(
            request.task_name,
            args=request.args,
            kwargs=request.kwargs,
        )

        return TaskSubmitResponse(
            task_id=task_result.id,
            task_name=request.task_name,
            status="PENDING",
            submitted_at=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit task: {str(e)}",
        )


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    summary="查询任务状态",
    description="根据任务 ID 查询任务执行状态和结果",
)
async def get_task_status(
    task_id: str = Path(..., description="任务 ID"),
) -> TaskStatusResponse:
    """
    查询任务状态。

    Args:
        task_id: 任务 ID

    Returns:
        TaskStatusResponse: 任务状态响应
    """
    task_result = AsyncResult(task_id, app=celery_app)

    response_data: dict[str, Any] = {
        "task_id": task_id,
        "task_name": task_result.name or "unknown",
        "status": task_result.status,
    }

    if task_result.successful():
        response_data["result"] = task_result.result
        response_data["completed_at"] = datetime.utcnow()
    elif task_result.failed():
        response_data["error"] = str(task_result.info)
        response_data["traceback"] = task_result.traceback
    elif task_result.state == "PROGRESS":
        response_data["meta"] = task_result.info

    return TaskStatusResponse(**response_data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="撤销任务",
    description="撤销一个正在执行或等待执行的任务",
)
async def revoke_task(
    task_id: str = Path(..., description="任务 ID"),
    terminate: bool = False,
) -> None:
    """
    撤销任务。

    Args:
        task_id: 任务 ID
        terminate: 是否强制终止正在执行的任务

    Raises:
        HTTPException: 撤销失败时抛出
    """
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke task: {str(e)}",
        )


@router.post(
    "/test/delayed",
    response_model=TaskSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="提交延迟测试任务",
    description="提交一个延迟返回的测试任务,用于验证 Celery 配置",
)
async def submit_delayed_test_task(
    delay_seconds: int = 5,
    message: str = "Task completed",
) -> TaskSubmitResponse:
    """
    提交延迟测试任务。

    Args:
        delay_seconds: 延迟秒数
        message: 返回消息

    Returns:
        TaskSubmitResponse: 任务提交响应
    """
    from infrastructure.tasks.test_tasks import delayed_return

    task_result = delayed_return.delay(delay_seconds, message)

    return TaskSubmitResponse(
        task_id=task_result.id,
        task_name="test_tasks.delayed_return",
        status="PENDING",
        submitted_at=datetime.utcnow(),
    )
