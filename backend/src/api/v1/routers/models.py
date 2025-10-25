from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Path, Query

from ..schemas.model import (
    BoundingBoxResponse,
    DimensionsResponse,
    ImageGenerationRequest,
    ModelListResponse,
    ModelMetadataResponse,
    ModelResponse,
    TextGenerationRequest,
)

router = APIRouter(prefix="/models", tags=["models"])


@router.post(
    "/generate/text",
    response_model=ModelResponse,
    summary="文本转3D模型",
    description="""
根据文本描述生成3D模型。

**使用流程**:
1. 提交文本描述(10-1000字符)
2. 获取返回的模型 ID 和初始状态 `pending`
3. 使用 GET `/models/{id}` 轮询任务状态
4. 当状态为 `completed` 时,可下载模型文件

**示例提示词**:
- "一个圆形的咖啡杯,带有手柄"
- "现代风格的花瓶,表面有几何纹理"
- "卡通风格的小熊玩偶"

**注意**: P0 MVP 版本返回 mock 数据,实际 AI 生成功能将在后续版本实现。
    """,
    responses={
        200: {
            "description": "成功创建生成任务",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "source_type": "text",
                        "status": "pending",
                        "file_path": None,
                        "thumbnail_path": None,
                        "metadata": None,
                        "error_message": None,
                        "created_at": "2025-10-25T10:00:00Z",
                        "updated_at": "2025-10-25T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def generate_from_text(request: TextGenerationRequest) -> ModelResponse:
    """
    根据文本描述生成3D模型。

    Args:
        request (TextGenerationRequest): 文本生成请求

    Returns:
        ModelResponse: 模型响应(包含任务ID和状态)
    """
    mock_id = uuid4()
    now = datetime.utcnow()

    return ModelResponse(
        id=mock_id,
        source_type="text",
        status="pending",
        file_path=None,
        thumbnail_path=None,
        metadata=None,
        error_message=None,
        created_at=now,
        updated_at=now,
    )


@router.post(
    "/generate/image",
    response_model=ModelResponse,
    summary="图片转3D模型",
    description="""
根据上传的图片生成3D模型。

**使用流程**:
1. 先使用 POST `/files/upload` 上传图片,获取文件路径
2. 提交图片路径列表(最多5张)
3. 获取返回的模型 ID 和初始状态 `pending`
4. 轮询任务状态直到完成

**支持的图片格式**: JPG, PNG
**图片要求**:
- 清晰的主体对象
- 良好的光照条件
- 最大文件大小 10MB

**注意**: P1 功能,当前返回 mock 数据。
    """,
    responses={
        200: {
            "description": "成功创建生成任务",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "source_type": "image",
                        "status": "pending",
                        "file_path": None,
                        "thumbnail_path": None,
                        "metadata": None,
                        "error_message": None,
                        "created_at": "2025-10-25T10:00:00Z",
                        "updated_at": "2025-10-25T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def generate_from_image(request: ImageGenerationRequest) -> ModelResponse:
    """
    根据图片生成3D模型。

    Args:
        request (ImageGenerationRequest): 图片生成请求

    Returns:
        ModelResponse: 模型响应(包含任务ID和状态)
    """
    mock_id = uuid4()
    now = datetime.utcnow()

    return ModelResponse(
        id=mock_id,
        source_type="image",
        status="pending",
        file_path=None,
        thumbnail_path=None,
        metadata=None,
        error_message=None,
        created_at=now,
        updated_at=now,
    )


@router.get(
    "/{model_id}",
    response_model=ModelResponse,
    summary="获取模型信息",
    description="""
根据 ID 获取3D模型的详细信息和任务状态。

**用途**:
- 轮询异步任务状态
- 获取完成后的模型元数据
- 检查任务错误信息

**状态说明**:
- `pending`: 任务排队中
- `processing`: 生成进行中
- `completed`: 生成完成,可下载
- `failed`: 生成失败,查看 error_message

**建议轮询间隔**: 5-10秒
    """,
    responses={
        200: {
            "description": "成功获取模型信息",
            "content": {
                "application/json": {
                    "examples": {
                        "completed": {
                            "summary": "生成完成",
                            "value": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "source_type": "text",
                                "status": "completed",
                                "file_path": "/storage/models/550e8400-e29b-41d4-a716-446655440000.stl",
                                "thumbnail_path": "/storage/thumbnails/550e8400-e29b-41d4-a716-446655440000.png",
                                "metadata": {
                                    "dimensions": {"x": 100.0, "y": 100.0, "z": 50.0},
                                    "volume": 50000.0,
                                    "triangle_count": 1024,
                                    "vertex_count": 512,
                                    "is_manifold": True,
                                    "bounding_box": {
                                        "min_point": [0.0, 0.0, 0.0],
                                        "max_point": [100.0, 100.0, 50.0]
                                    }
                                },
                                "error_message": None,
                                "created_at": "2025-10-25T10:00:00Z",
                                "updated_at": "2025-10-25T10:01:30Z"
                            }
                        },
                        "processing": {
                            "summary": "生成中",
                            "value": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "source_type": "text",
                                "status": "processing",
                                "file_path": None,
                                "thumbnail_path": None,
                                "metadata": None,
                                "error_message": None,
                                "created_at": "2025-10-25T10:00:00Z",
                                "updated_at": "2025-10-25T10:00:45Z"
                            }
                        },
                        "failed": {
                            "summary": "生成失败",
                            "value": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "source_type": "text",
                                "status": "failed",
                                "file_path": None,
                                "thumbnail_path": None,
                                "metadata": None,
                                "error_message": "AI service timeout: failed to generate model within 300s",
                                "created_at": "2025-10-25T10:00:00Z",
                                "updated_at": "2025-10-25T10:05:00Z"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "模型不存在"
        }
    }
)
async def get_model(
    model_id: UUID = Path(..., description="模型ID")
) -> ModelResponse:
    """
    获取指定ID的3D模型信息。

    Args:
        model_id (UUID): 模型ID

    Returns:
        ModelResponse: 模型详细信息

    Raises:
        HTTPException: 模型不存在时返回404
    """
    now = datetime.utcnow()
    
    mock_metadata = ModelMetadataResponse(
        dimensions=DimensionsResponse(x=100.0, y=100.0, z=50.0),
        volume=50000.0,
        triangle_count=1024,
        vertex_count=512,
        is_manifold=True,
        bounding_box=BoundingBoxResponse(
            min_point=(0.0, 0.0, 0.0),
            max_point=(100.0, 100.0, 50.0)
        )
    )

    return ModelResponse(
        id=model_id,
        source_type="text",
        status="completed",
        file_path=f"/storage/models/{model_id}.stl",
        thumbnail_path=f"/storage/thumbnails/{model_id}.png",
        metadata=mock_metadata,
        error_message=None,
        created_at=now,
        updated_at=now,
    )


@router.get(
    "/",
    response_model=ModelListResponse,
    summary="获取模型列表",
    description="获取用户的模型列表(P2功能 - 返回mock数据)"
)
async def list_models(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数")
) -> ModelListResponse:
    """
    获取模型列表(分页)。

    Args:
        skip (int): 跳过的记录数
        limit (int): 返回的记录数(最多100)

    Returns:
        ModelListResponse: 模型列表响应
    """
    now = datetime.utcnow()
    
    mock_models = [
        ModelResponse(
            id=uuid4(),
            source_type="text",
            status="completed",
            file_path=f"/storage/models/mock_{i}.stl",
            thumbnail_path=f"/storage/thumbnails/mock_{i}.png",
            metadata=ModelMetadataResponse(
                dimensions=DimensionsResponse(x=100.0, y=100.0, z=50.0),
                volume=50000.0,
                triangle_count=1024,
                vertex_count=512,
                is_manifold=True,
                bounding_box=BoundingBoxResponse(
                    min_point=(0.0, 0.0, 0.0),
                    max_point=(100.0, 100.0, 50.0)
                )
            ),
            error_message=None,
            created_at=now,
            updated_at=now,
        )
        for i in range(min(limit, 3))
    ]

    return ModelListResponse(
        total=3,
        items=mock_models
    )


@router.delete(
    "/{model_id}",
    summary="删除模型",
    description="删除指定的3D模型(P2功能 - 返回mock响应)"
)
async def delete_model(
    model_id: UUID = Path(..., description="模型ID")
) -> dict[str, str]:
    """
    删除指定的3D模型。

    Args:
        model_id (UUID): 模型ID

    Returns:
        dict[str, str]: 删除结果

    Raises:
        HTTPException: 模型不存在时返回404
    """
    return {
        "message": f"Model {model_id} deleted successfully (mock)"
    }


@router.get(
    "/{model_id}/download",
    summary="下载模型文件",
    description="下载指定模型的STL文件(P0功能 - 返回mock响应)"
)
async def download_model(
    model_id: UUID = Path(..., description="模型ID")
) -> dict[str, str]:
    """
    下载模型的STL文件。

    Args:
        model_id (UUID): 模型ID

    Returns:
        dict[str, str]: 下载链接信息

    Raises:
        HTTPException: 模型不存在或未完成时返回404
    """
    return {
        "download_url": f"/storage/models/{model_id}.stl",
        "filename": f"model_{model_id}.stl",
        "message": "Mock download URL (actual file streaming not implemented yet)"
    }
