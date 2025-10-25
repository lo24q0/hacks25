from enum import Enum


class ModelStatus(Enum):
    """
    3D模型的状态枚举。

    Attributes:
        PENDING: 等待处理状态
        PROCESSING: 正在生成中
        COMPLETED: 生成完成
        FAILED: 生成失败
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(Enum):
    """
    任务通用状态枚举。

    Attributes:
        PENDING: 等待处理
        PROCESSING: 处理中
        COMPLETED: 已完成
        FAILED: 失败
        CANCELLED: 已取消
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
