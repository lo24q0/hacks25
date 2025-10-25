"""
异步任务模块初始化

Celery 任务队列配置和任务注册
"""

from src.infrastructure.tasks.celery_app import celery_app

# 导入任务模块以确保任务被注册
from src.infrastructure.tasks import model_tasks, test_tasks  # noqa: F401

__all__ = ["celery_app"]
