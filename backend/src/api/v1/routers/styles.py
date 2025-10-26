"""
风格化 API 路由模块。

提供图片风格化相关的 HTTP API 端点。
"""

import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from src.api.v1.schemas.style import (
    ErrorInfoResponse,
    StylePresetResponse,
    StylePresetsResponse,
    StyleTaskMetadataResponse,
    StyleTaskResponse,
    StyleTransferResponse,
)
from src.application.services.style_service import StyleService
from src.infrastructure.ai.tencent_style import TencentCloudStyleEngine
from src.infrastructure.config.settings import settings
from src.infrastructure.storage.local_storage import LocalStorageService
from src.infrastructure.storage.redis_style_task_store import RedisStyleTaskStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/styles", tags=["styles"])

# 全局 Redis 任务存储实例（复用连接池）
_task_store: RedisStyleTaskStore | None = None


def get_task_store() -> RedisStyleTaskStore:
    """
    获取 Redis 任务存储实例（单例模式）。

    Returns:
        RedisStyleTaskStore: Redis 任务存储实例
    """
    global _task_store
    if _task_store is None:
        _task_store = RedisStyleTaskStore(redis_url=settings.redis_url)
    return _task_store


def get_style_service() -> StyleService:
    """
    获取风格化服务实例。

    Returns:
        StyleService: 风格化服务实例
    """
    style_engine = TencentCloudStyleEngine(
        secret_id=settings.tencent_cloud_secret_id,
        secret_key=settings.tencent_cloud_secret_key,
        region=settings.tencent_cloud_region,
    )
    task_store = get_task_store()
    return StyleService(style_engine=style_engine, task_store=task_store)


def get_storage_service() -> LocalStorageService:
    """
    获取存储服务实例。

    Returns:
        LocalStorageService: 存储服务实例
    """
    return LocalStorageService()


@router.get(
    "/presets",
    response_model=StylePresetsResponse,
    summary="获取风格预设列表",
    description="获取所有可用的图片风格化预设列表,包括风格ID、名称、描述和预览图",
)
async def get_style_presets(
    service: StyleService = Depends(get_style_service),
) -> StylePresetsResponse:
    """
    获取风格预设列表。

    Returns:
        StylePresetsResponse: 包含所有风格预设的响应
    """
    presets = service.get_available_styles()

    preset_responses = [
        StylePresetResponse(
            id=preset.id,
            name=preset.name,
            name_en=preset.name_en,
            description=preset.description,
            preview_image=preset.preview_image,
            tags=preset.tags,
            recommended_strength=preset.recommended_strength,
            estimated_time=preset.estimated_time,
        )
        for preset in presets
    ]

    return StylePresetsResponse(
        presets=preset_responses,
        total=len(preset_responses),
    )


@router.get(
    "/presets/{preset_id}",
    response_model=StylePresetResponse,
    summary="获取指定风格预设",
    description="根据风格预设ID获取详细信息",
)
async def get_style_preset(
    preset_id: str,
    service: StyleService = Depends(get_style_service),
) -> StylePresetResponse:
    """
    获取指定风格预设。

    Args:
        preset_id: 风格预设ID
        service: 风格化服务实例

    Returns:
        StylePresetResponse: 风格预设详情

    Raises:
        HTTPException: 如果风格预设不存在
    """
    try:
        preset = service.get_style_preset(preset_id)
        return StylePresetResponse(
            id=preset.id,
            name=preset.name,
            name_en=preset.name_en,
            description=preset.description,
            preview_image=preset.preview_image,
            tags=preset.tags,
            recommended_strength=preset.recommended_strength,
            estimated_time=preset.estimated_time,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/transfer",
    response_model=StyleTransferResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="创建风格化任务",
    description="上传图片并创建风格化任务,任务将异步处理",
)
async def create_style_transfer_task(
    file: UploadFile = File(..., description="上传的图片文件"),
    style_preset_id: str = File(..., description="风格预设ID"),
    service: StyleService = Depends(get_style_service),
    storage_service: LocalStorageService = Depends(get_storage_service),
) -> StyleTransferResponse:
    """
    创建风格化任务。

    Args:
        file: 上传的图片文件
        style_preset_id: 风格预设ID
        service: 风格化服务实例
        storage_service: 存储服务实例

    Returns:
        StyleTransferResponse: 任务创建响应

    Raises:
        HTTPException: 如果文件验证失败或风格预设不存在
    """
    file_size_mb = len(await file.read()) / (1024 * 1024)
    await file.seek(0)  # 重置文件指针

    logger.debug(
        f"收到风格化任务创建请求 | filename={file.filename}, "
        f"size={file_size_mb:.2f}MB, style_id={style_preset_id}, "
        f"content_type={file.content_type}"
    )

    try:
        # 读取文件内容
        file_content = await file.read()

        # 上传文件到存储服务
        file_object = await storage_service.upload_file(
            file_content=file_content,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
        )

        logger.debug(f"文件上传成功 | object_key={file_object.object_key}")

        # 使用完整的文件路径
        image_path = str(Path(storage_service.base_path) / file_object.object_key)

        task = await service.create_style_task(
            image_path=image_path,
            style_preset_id=style_preset_id,
        )

        logger.info(
            f"风格化任务创建成功 | task_id={task.id}, status={task.status.value}, "
            f"style_id={style_preset_id}"
        )

        return StyleTransferResponse(
            task_id=task.id,
            status=task.status.value,
            message="风格化任务已创建,请轮询查询结果",
        )

    except FileNotFoundError as e:
        logger.error(f"文件不存在 | error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        logger.error(f"参数验证失败 | error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"创建任务失败 | error_type={type(e).__name__}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建任务失败: {str(e)}",
        )


@router.get(
    "/tasks/{task_id}",
    response_model=StyleTaskResponse,
    summary="查询任务状态",
    description="根据任务ID查询风格化任务的状态和结果",
)
async def get_style_task(
    task_id: UUID,
    service: StyleService = Depends(get_style_service),
) -> StyleTaskResponse:
    """
    查询任务状态。

    Args:
        task_id: 任务ID
        service: 风格化服务实例

    Returns:
        StyleTaskResponse: 任务状态响应

    Raises:
        HTTPException: 如果任务不存在
    """
    logger.debug(f"查询任务状态 | task_id={task_id}")

    task = await service.get_task_status(task_id)

    if task is None:
        logger.warning(f"任务不存在 | task_id={task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_id}",
        )

    logger.debug(
        f"返回任务状态 | task_id={task_id}, status={task.status.value}, "
        f"has_result={task.result_path is not None}"
    )

    metadata_response = StyleTaskMetadataResponse(
        style_preset_id=task.metadata.style_preset_id,
        style_preset_name=task.metadata.style_preset_name,
        estimated_time=task.metadata.estimated_time,
        actual_time=task.metadata.actual_time,
        tencent_request_id=task.metadata.tencent_request_id,
        created_at=task.metadata.created_at,
        completed_at=task.metadata.completed_at,
    )

    error_info_response = None
    if task.error_info:
        error_info_response = ErrorInfoResponse(
            error_code=task.error_info.error_code,
            error_message=task.error_info.error_message,
            tencent_error_code=task.error_info.tencent_error_code,
            user_message=task.error_info.user_message,
            suggestion=task.error_info.suggestion,
            is_retryable=task.error_info.is_retryable,
        )

    return StyleTaskResponse(
        id=task.id,
        image_path=task.image_path,
        style_preset_id=task.style_preset_id,
        status=task.status.value,
        result_path=task.result_path,
        metadata=metadata_response,
        error_info=error_info_response,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get(
    "/tasks/{task_id}/result",
    response_class=FileResponse,
    summary="下载风格化结果",
    description="下载风格化后的图片文件",
)
async def download_style_result(
    task_id: UUID,
    service: StyleService = Depends(get_style_service),
) -> FileResponse:
    """
    下载风格化结果。

    Args:
        task_id: 任务ID
        service: 风格化服务实例

    Returns:
        FileResponse: 图片文件响应

    Raises:
        HTTPException: 如果任务不存在或未完成
    """
    task = await service.get_task_status(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_id}",
        )

    if not task.is_completed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务尚未完成,当前状态: {task.status.value}",
        )

    if task.result_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="结果文件不存在",
        )

    return FileResponse(
        path=task.result_path,
        media_type="image/jpeg",
        filename=f"styled_{task_id}.jpg",
    )
