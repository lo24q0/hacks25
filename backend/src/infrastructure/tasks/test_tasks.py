"""
测试任务模块。

包含用于测试 Celery 配置的示例任务。
"""

import time
from datetime import datetime

from celery import Task

from infrastructure.tasks.celery_app import celery_app


@celery_app.task(bind=True, name="test_tasks.delayed_return")
def delayed_return(self: Task, delay_seconds: int = 5, message: str = "Task completed") -> dict:
    """
    延迟返回测试任务。

    Args:
        self: Celery 任务实例
        delay_seconds: 延迟秒数
        message: 返回消息

    Returns:
        dict: 包含任务执行信息的字典
    """
    task_id = self.request.id
    start_time = datetime.utcnow()

    for i in range(delay_seconds):
        time.sleep(1)
        progress = int((i + 1) / delay_seconds * 100)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": delay_seconds,
                "progress": progress,
                "status": f"Processing step {i + 1}/{delay_seconds}",
            },
        )

    end_time = datetime.utcnow()
    elapsed = (end_time - start_time).total_seconds()

    return {
        "task_id": task_id,
        "message": message,
        "delay_seconds": delay_seconds,
        "elapsed_seconds": elapsed,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": "completed",
    }


@celery_app.task(bind=True, name="test_tasks.add_numbers")
def add_numbers(self: Task, a: int, b: int) -> dict:
    """
    简单的加法测试任务。

    Args:
        self: Celery 任务实例
        a: 第一个数字
        b: 第二个数字

    Returns:
        dict: 包含计算结果的字典
    """
    result = a + b
    return {
        "task_id": self.request.id,
        "operation": "addition",
        "input": {"a": a, "b": b},
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
    }


@celery_app.task(bind=True, name="test_tasks.task_with_retry")
def task_with_retry(self: Task, should_fail: bool = False, max_retries: int = 3) -> dict:
    """
    带重试机制的测试任务。

    Args:
        self: Celery 任务实例
        should_fail: 是否故意失败以触发重试
        max_retries: 最大重试次数

    Returns:
        dict: 任务执行结果

    Raises:
        Exception: 当 should_fail 为 True 时抛出异常
    """
    if should_fail and self.request.retries < max_retries:
        raise self.retry(
            exc=Exception(f"Intentional failure, retry {self.request.retries + 1}/{max_retries}"),
            countdown=2,
            max_retries=max_retries,
        )

    return {
        "task_id": self.request.id,
        "retries": self.request.retries,
        "max_retries": max_retries,
        "status": "completed" if not should_fail else "completed_after_retries",
        "timestamp": datetime.utcnow().isoformat(),
    }
