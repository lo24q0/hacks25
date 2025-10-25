"""
风格化元数据值对象模块。

包含风格化任务相关的元数据和错误信息值对象。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class StyleTaskMetadata:
    """
    风格化任务元数据值对象。

    包含风格化任务执行过程中的元数据信息。

    Args:
        style_preset_id: 风格预设ID
        style_preset_name: 风格预设名称
        estimated_time: 预计处理时间(秒)
        actual_time: 实际处理时间(秒)
        tencent_request_id: 腾讯云请求ID
        created_at: 创建时间
        completed_at: 完成时间
    """

    style_preset_id: str
    style_preset_name: str
    estimated_time: int = 20
    actual_time: Optional[int] = None
    tencent_request_id: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """初始化后设置默认值"""
        if self.created_at is None:
            object.__setattr__(self, "created_at", datetime.now())


@dataclass(frozen=True)
class ErrorInfo:
    """
    错误信息值对象。

    封装任务失败时的错误详情。

    Args:
        error_code: 系统错误码
        error_message: 错误消息
        tencent_error_code: 腾讯云原始错误码
        user_message: 用户友好的错误提示
        suggestion: 解决建议
        is_retryable: 是否可重试
    """

    error_code: str
    error_message: str
    tencent_error_code: Optional[str] = None
    user_message: Optional[str] = None
    suggestion: Optional[str] = None
    is_retryable: bool = False
