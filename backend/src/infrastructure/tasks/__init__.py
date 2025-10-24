"""
异步任务模块初始化

Celery 任务队列配置和任务注册
"""

from src.infrastructure.tasks.celery_app import celery_app

__all__ = ["celery_app"]
