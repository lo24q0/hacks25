from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Path, Query

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
    description="根据文本描述生成3D模型(P0 MVP - 返回mock数据)",
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
    description="根据图片生成3D模型(P1功能 - 返回mock数据)",
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
    description="根据ID获取3D模型的详细信息(返回mock数据)",
)
async def get_model(model_id: UUID = Path(..., description="模型ID")) -> ModelResponse:
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
        bounding_box=BoundingBoxResponse(min_point=(0.0, 0.0, 0.0), max_point=(100.0, 100.0, 50.0)),
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
    description="获取用户的模型列表(P2功能 - 返回mock数据)",
)
async def list_models(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
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
                    min_point=(0.0, 0.0, 0.0), max_point=(100.0, 100.0, 50.0)
                ),
            ),
            error_message=None,
            created_at=now,
            updated_at=now,
        )
        for i in range(min(limit, 3))
    ]

    return ModelListResponse(total=3, items=mock_models)


@router.delete(
    "/{model_id}", summary="删除模型", description="删除指定的3D模型(P2功能 - 返回mock响应)"
)
async def delete_model(model_id: UUID = Path(..., description="模型ID")) -> dict[str, str]:
    """
    删除指定的3D模型。

    Args:
        model_id (UUID): 模型ID

    Returns:
        dict[str, str]: 删除结果

    Raises:
        HTTPException: 模型不存在时返回404
    """
    return {"message": f"Model {model_id} deleted successfully (mock)"}


@router.get(
    "/{model_id}/download",
    summary="下载模型文件",
    description="下载指定模型的STL文件(P0功能 - 返回mock响应)",
)
async def download_model(model_id: UUID = Path(..., description="模型ID")) -> dict[str, str]:
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
        "message": "Mock download URL (actual file streaming not implemented yet)",
    }
