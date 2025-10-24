"""
Celery 应用配置模块。

配置 Celery 异步任务处理框架,包括 broker、backend 和任务路由配置。
"""

from celery import Celery
from celery.signals import task_failure, task_success

from src.infrastructure.config.settings import settings

celery_app = Celery(
    "3d_print_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_routes={
        "infrastructure.tasks.model_tasks.*": {"queue": "generation"},
        "infrastructure.tasks.style_tasks.*": {"queue": "style"},
        "infrastructure.tasks.slicing_tasks.*": {"queue": "slicing"},
        "infrastructure.tasks.test_tasks.*": {"queue": "default"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(
    [
        "infrastructure.tasks",
    ]
)


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """
    任务成功完成时的回调处理。

    Args:
        sender: 发送信号的任务
        result: 任务执行结果
        **kwargs: 其他参数
    """
    task_id = kwargs.get("task_id")
    task_name = sender.name if sender else "Unknown"
    print(f"Task {task_name} [{task_id}] succeeded with result: {result}")


@task_failure.connect
def task_failure_handler(sender=None, exception=None, **kwargs):
    """
    任务失败时的回调处理。

    Args:
        sender: 发送信号的任务
        exception: 异常信息
        **kwargs: 其他参数
    """
    task_id = kwargs.get("task_id")
    task_name = sender.name if sender else "Unknown"
    print(f"Task {task_name} [{task_id}] failed with exception: {exception}")
