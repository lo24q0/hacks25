"""
异步任务模块初始化

Celery 任务队列配置和任务注册
"""

from src.infrastructure.tasks.celery_app import celery_app

# 导入所有任务模块以确保任务被注册
from src.infrastructure.tasks import test_tasks, model_tasks, cleanup_tasks  # noqa: F401

__all__ = ["celery_app"]
