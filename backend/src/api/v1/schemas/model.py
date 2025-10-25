from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TextGenerationRequest(BaseModel):
    """
    文本转3D模型请求。

    Args:
        prompt (str): 文本描述提示词
        style_preset (Optional[str]): 风格化预设ID
    """

    prompt: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="文本描述提示词,长度10-1000字符",
        examples=["一个圆形的咖啡杯,带有手柄"],
    )
    style_preset: Optional[str] = Field(
        None, description="风格化预设ID(可选)", examples=["anime", "cartoon"]
    )


class ImageGenerationRequest(BaseModel):
    """
    图片转3D模型请求。

    Args:
        image_paths (list[str]): 图片文件路径列表
        style_preset (Optional[str]): 风格化预设ID
    """

    image_paths: list[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="图片文件路径列表,最多5张",
        examples=[["uploads/image1.jpg", "uploads/image2.jpg"]],
    )
    style_preset: Optional[str] = Field(None, description="风格化预设ID(可选)")


class DimensionsResponse(BaseModel):
    """
    模型尺寸响应。

    Args:
        x (float): X轴尺寸(毫米)
        y (float): Y轴尺寸(毫米)
        z (float): Z轴尺寸(毫米)
    """

    x: float = Field(..., description="X轴尺寸(毫米)")
    y: float = Field(..., description="Y轴尺寸(毫米)")
    z: float = Field(..., description="Z轴尺寸(毫米)")


class BoundingBoxResponse(BaseModel):
    """
    包围盒响应。

    Args:
        min_point (tuple[float, float, float]): 最小点坐标
        max_point (tuple[float, float, float]): 最大点坐标
    """

    min_point: tuple[float, float, float] = Field(..., description="最小点坐标(x,y,z)")
    max_point: tuple[float, float, float] = Field(..., description="最大点坐标(x,y,z)")


class ModelMetadataResponse(BaseModel):
    """
    模型元数据响应。

    Args:
        dimensions (DimensionsResponse): 模型尺寸
        volume (float): 体积(立方毫米)
        triangle_count (int): 三角面数量
        vertex_count (int): 顶点数量
        is_manifold (bool): 是否流形
        bounding_box (BoundingBoxResponse): 包围盒
    """

    dimensions: DimensionsResponse
    volume: float = Field(..., description="体积(立方毫米)")
    triangle_count: int = Field(..., description="三角面数量")
    vertex_count: int = Field(..., description="顶点数量")
    is_manifold: bool = Field(..., description="是否流形(可打印)")
    bounding_box: BoundingBoxResponse


class ModelResponse(BaseModel):
    """
    3D模型响应。

    Args:
        id (UUID): 模型ID
        source_type (str): 源类型(text/image)
        status (str): 状态(pending/processing/completed/failed)
        file_path (Optional[str]): STL文件路径
        thumbnail_path (Optional[str]): 缩略图路径
        metadata (Optional[ModelMetadataResponse]): 模型元数据
        error_message (Optional[str]): 错误信息
        celery_task_id (Optional[str]): Celery任务ID
        model_files (Optional[dict]): 模型文件路径字典(glb/obj/fbx/mtl)
        created_at (datetime): 创建时间
        updated_at (datetime): 更新时间
    """

    id: UUID = Field(..., description="模型唯一标识")
    source_type: str = Field(..., description="源类型(text/image)")
    status: str = Field(
        ..., description="模型状态", examples=["pending", "processing", "completed", "failed"]
    )
    file_path: Optional[str] = Field(None, description="STL文件路径(已废弃,使用model_files)")
    thumbnail_path: Optional[str] = Field(None, description="缩略图路径")
    metadata: Optional[ModelMetadataResponse] = Field(None, description="模型元数据")
    error_message: Optional[str] = Field(None, description="错误信息")
    celery_task_id: Optional[str] = Field(None, description="Celery异步任务ID,用于查询任务状态")
    model_files: Optional[dict[str, str]] = Field(
        None, 
        description="模型文件路径字典,包含glb/obj/fbx/mtl等格式",
        examples=[{"glb": "/storage/models/xxx.glb", "obj": "/storage/models/xxx.obj"}]
    )
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ModelListResponse(BaseModel):
    """
    模型列表响应。

    Args:
        total (int): 总数
        items (list[ModelResponse]): 模型列表
    """

    total: int = Field(..., description="模型总数")
    items: list[ModelResponse] = Field(..., description="模型列表")
