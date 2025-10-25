"""
风格化 API 请求/响应模型模块。

定义风格化相关的 Pydantic 模型,用于 API 请求验证和响应序列化。
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StylePresetResponse(BaseModel):
    """
    风格预设响应模型。

    Args:
        id: 预设ID
        name: 中文名称
        name_en: 英文名称
        description: 风格描述
        preview_image: 预览图片路径
        tags: 风格标签列表
        recommended_strength: 推荐的风格强度
        estimated_time: 预计处理时间(秒)
    """

    id: str = Field(..., description="预设ID")
    name: str = Field(..., description="中文名称")
    name_en: str = Field(..., description="英文名称")
    description: str = Field(..., description="风格描述")
    preview_image: str = Field(..., description="预览图片路径")
    tags: List[str] = Field(default_factory=list, description="风格标签列表")
    recommended_strength: int = Field(default=80, description="推荐的风格强度(0-100)")
    estimated_time: int = Field(default=20, description="预计处理时间(秒)")


class StylePresetsResponse(BaseModel):
    """
    风格预设列表响应模型。

    Args:
        presets: 风格预设列表
        total: 总数
    """

    presets: List[StylePresetResponse] = Field(..., description="风格预设列表")
    total: int = Field(..., description="总数")


class StyleTransferRequest(BaseModel):
    """
    风格迁移请求模型。

    Args:
        image_path: 输入图片路径
        style_preset_id: 风格预设ID
    """

    image_path: str = Field(..., description="输入图片路径", min_length=1)
    style_preset_id: str = Field(..., description="风格预设ID", min_length=1)


class StyleTaskMetadataResponse(BaseModel):
    """
    风格化任务元数据响应模型。

    Args:
        style_preset_id: 风格预设ID
        style_preset_name: 风格预设名称
        estimated_time: 预计处理时间(秒)
        actual_time: 实际处理时间(秒)
        tencent_request_id: 腾讯云请求ID
        created_at: 创建时间
        completed_at: 完成时间
    """

    style_preset_id: str = Field(..., description="风格预设ID")
    style_preset_name: str = Field(..., description="风格预设名称")
    estimated_time: int = Field(default=20, description="预计处理时间(秒)")
    actual_time: Optional[int] = Field(None, description="实际处理时间(秒)")
    tencent_request_id: Optional[str] = Field(None, description="腾讯云请求ID")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class ErrorInfoResponse(BaseModel):
    """
    错误信息响应模型。

    Args:
        error_code: 系统错误码
        error_message: 错误消息
        tencent_error_code: 腾讯云原始错误码
        user_message: 用户友好的错误提示
        suggestion: 解决建议
        is_retryable: 是否可重试
    """

    error_code: str = Field(..., description="系统错误码")
    error_message: str = Field(..., description="错误消息")
    tencent_error_code: Optional[str] = Field(None, description="腾讯云原始错误码")
    user_message: Optional[str] = Field(None, description="用户友好的错误提示")
    suggestion: Optional[str] = Field(None, description="解决建议")
    is_retryable: bool = Field(default=False, description="是否可重试")


class StyleTaskResponse(BaseModel):
    """
    风格化任务响应模型。

    Args:
        id: 任务ID
        image_path: 输入图片路径
        style_preset_id: 风格预设ID
        status: 任务状态
        result_path: 风格化后的图片路径
        metadata: 任务元数据
        error_info: 错误信息
        created_at: 创建时间
        updated_at: 更新时间
    """

    id: UUID = Field(..., description="任务ID")
    image_path: str = Field(..., description="输入图片路径")
    style_preset_id: str = Field(..., description="风格预设ID")
    status: str = Field(..., description="任务状态")
    result_path: Optional[str] = Field(None, description="风格化后的图片路径")
    metadata: StyleTaskMetadataResponse = Field(..., description="任务元数据")
    error_info: Optional[ErrorInfoResponse] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class StyleTransferResponse(BaseModel):
    """
    风格迁移创建响应模型。

    Args:
        task_id: 任务ID
        status: 任务状态
        message: 提示消息
    """

    task_id: UUID = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="提示消息")
