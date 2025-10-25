from datetime import datetime
from uuid import UUID, uuid4

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Path, Query

from infrastructure.tasks.model_tasks import generate_text_to_3d, generate_image_to_3d
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
    description="根据文本描述异步生成3D模型",
    responses={
        200: {
            "description": "任务创建成功,返回模型ID和任务ID",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "source_type": "text",
                        "status": "pending",
                        "file_path": None,
                        "thumbnail_path": None,
                        "metadata": None,
                        "error_message": None,
                        "celery_task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "model_files": None,
                        "created_at": "2025-10-25T10:00:00",
                        "updated_at": "2025-10-25T10:00:00",
                    }
                }
            },
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"},
    },
)
async def generate_from_text(request: TextGenerationRequest) -> ModelResponse:
    """
    根据文本描述生成3D模型。

    创建异步任务,使用 Meshy AI 生成3D模型。
    任务完成后,模型文件将自动下载到本地存储。

    Args:
        request (TextGenerationRequest): 文本生成请求

    Returns:
        ModelResponse: 模型响应(包含任务ID和状态)
    """
    model_id = uuid4()
    now = datetime.utcnow()

    task = generate_text_to_3d.delay(
        prompt=request.prompt,
        model_id=str(model_id),
    )

    return ModelResponse(
        id=model_id,
        source_type="text",
        status="pending",
        file_path=None,
        thumbnail_path=None,
        metadata=None,
        error_message=None,
        created_at=now,
        updated_at=now,
        celery_task_id=task.id,
    )


@router.post(
    "/generate/image",
    response_model=ModelResponse,
    summary="图片转3D模型",
    description="根据图片异步生成3D模型"
)
async def generate_from_image(request: ImageGenerationRequest) -> ModelResponse:
    """
    根据图片生成3D模型。

    创建异步任务,使用 Meshy AI 从图片生成3D模型。
    任务完成后,模型文件将自动下载到本地存储。

    Args:
        request (ImageGenerationRequest): 图片生成请求

    Returns:
        ModelResponse: 模型响应(包含任务ID和状态)
    """
    model_id = uuid4()
    now = datetime.utcnow()

    if not request.image_paths or len(request.image_paths) == 0:
        raise HTTPException(status_code=400, detail="At least one image path is required")

    image_url = request.image_paths[0]

    task = generate_image_to_3d.delay(
        image_url=image_url,
        model_id=str(model_id),
    )

    return ModelResponse(
        id=model_id,
        source_type="image",
        status="pending",
        file_path=None,
        thumbnail_path=None,
        metadata=None,
        error_message=None,
        created_at=now,
        updated_at=now,
        celery_task_id=task.id,
    )


@router.get(
    "/task/{task_id}",
    summary="查询任务状态",
    description="根据Celery任务ID查询异步任务的执行状态和进度",
    responses={
        200: {
            "description": "任务状态查询成功",
            "content": {
                "application/json": {
                    "examples": {
                        "pending": {
                            "summary": "任务等待中",
                            "value": {
                                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                "state": "PENDING",
                                "ready": False,
                            },
                        },
                        "progress": {
                            "summary": "任务进行中",
                            "value": {
                                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                "state": "PROGRESS",
                                "ready": False,
                                "info": {
                                    "stage": "generating_preview",
                                    "progress": 45,
                                    "status": "Generating preview: 45%",
                                },
                            },
                        },
                        "success": {
                            "summary": "任务完成",
                            "value": {
                                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                "state": "SUCCESS",
                                "ready": True,
                                "result": {
                                    "model_id": "123e4567-e89b-12d3-a456-426614174000",
                                    "model_files": {
                                        "glb": "/storage/models/xxx.glb",
                                        "obj": "/storage/models/xxx.obj",
                                    },
                                    "thumbnail_path": "/storage/thumbnails/xxx.png",
                                },
                            },
                        },
                        "failure": {
                            "summary": "任务失败",
                            "value": {
                                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                "state": "FAILURE",
                                "ready": True,
                                "error": "MeshyAPIError: Rate limit exceeded",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def get_task_status(
    task_id: str = Path(..., description="Celery任务ID")
) -> dict:
    """
    查询Celery任务状态。

    Args:
        task_id (str): Celery任务ID

    Returns:
        dict: 任务状态信息,包括state, progress, result等
    """
    result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "state": result.state,
        "ready": result.ready(),
    }
    
    if result.state == "PROGRESS":
        response["info"] = result.info
    elif result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.info)
    
    return response


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
