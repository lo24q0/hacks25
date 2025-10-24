"""
任务相关的 API 数据模型。

定义任务提交、查询等接口的请求和响应模型。
"""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TaskSubmitRequest(BaseModel):
    """
    任务提交请求模型。
    """

    task_name: str = Field(..., description="任务名称", examples=["test_tasks.delayed_return"])
    args: list[Any] = Field(default=[], description="位置参数列表")
    kwargs: dict[str, Any] = Field(default={}, description="关键字参数字典")


class TaskSubmitResponse(BaseModel):
    """
    任务提交响应模型。
    """

    task_id: str = Field(..., description="任务 ID")
    task_name: str = Field(..., description="任务名称")
    status: str = Field(..., description="任务状态")
    submitted_at: datetime = Field(..., description="提交时间")


class TaskStatusResponse(BaseModel):
    """
    任务状态响应模型。
    """

    task_id: str = Field(..., description="任务 ID")
    task_name: str = Field(..., description="任务名称")
    status: Literal["PENDING", "PROGRESS", "SUCCESS", "FAILURE", "RETRY", "REVOKED"] = Field(
        ..., description="任务状态"
    )
    result: Optional[Any] = Field(None, description="任务结果(成功时)")
    error: Optional[str] = Field(None, description="错误信息(失败时)")
    traceback: Optional[str] = Field(None, description="错误堆栈(失败时)")
    meta: Optional[dict[str, Any]] = Field(None, description="任务元数据")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class TaskListResponse(BaseModel):
    """
    任务列表响应模型。
    """

    tasks: list[TaskStatusResponse] = Field(..., description="任务列表")
    total: int = Field(..., description="任务总数")
