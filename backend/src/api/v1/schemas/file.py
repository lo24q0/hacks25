from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """
    文件上传响应模型。
    
    Args:
        id (UUID): 文件ID
        object_key (str): 对象键/存储路径
        original_filename (str): 原始文件名
        content_type (str): 内容类型
        size_bytes (int): 文件大小(字节)
        download_url (str): 下载URL
        created_at (datetime): 创建时间
    """
    id: UUID = Field(..., description="文件ID")
    object_key: str = Field(..., description="对象键/存储路径")
    original_filename: str = Field(..., description="原始文件名")
    content_type: str = Field(..., description="内容类型(MIME)")
    size_bytes: int = Field(..., description="文件大小(字节)")
    download_url: str = Field(..., description="下载URL")
    created_at: datetime = Field(..., description="创建时间")


class FileMetadataResponse(BaseModel):
    """
    文件元数据响应模型。
    
    Args:
        id (UUID): 文件ID
        object_key (str): 对象键
        original_filename (str): 原始文件名
        content_type (str): 内容类型
        size_bytes (int): 文件大小(字节)
        ttl_seconds (Optional[int]): 生存时间(秒)
        created_at (datetime): 创建时间
    """
    id: UUID = Field(..., description="文件ID")
    object_key: str = Field(..., description="对象键")
    original_filename: str = Field(..., description="原始文件名")
    content_type: str = Field(..., description="内容类型")
    size_bytes: int = Field(..., description="文件大小(字节)")
    ttl_seconds: Optional[int] = Field(None, description="生存时间(秒)")
    created_at: datetime = Field(..., description="创建时间")


class FileCleanupResponse(BaseModel):
    """
    文件清理响应模型。
    
    Args:
        cleaned_count (int): 清理的文件数量
        message (str): 响应消息
    """
    cleaned_count: int = Field(..., description="清理的文件数量")
    message: str = Field(..., description="响应消息")
