from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Path, Query, UploadFile
from fastapi.responses import Response

from ....infrastructure.storage.local_storage import LocalStorageService
from ..schemas.file import (
    FileCleanupResponse,
    FileMetadataResponse,
    FileUploadResponse,
)

router = APIRouter(prefix="/files", tags=["files"])

storage_service = LocalStorageService(base_path="./storage")


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    summary="上传文件",
    description="上传文件到存储服务,可选设置文件生存时间(TTL)"
)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    ttl_hours: Optional[int] = Query(
        None,
        ge=1,
        le=720,
        description="文件生存时间(小时),最长30天,不设置则永久保存"
    )
) -> FileUploadResponse:
    """
    上传文件到存储服务。
    
    Args:
        file (UploadFile): 要上传的文件
        ttl_hours (Optional[int]): 文件生存时间(小时)
        
    Returns:
        FileUploadResponse: 文件上传响应
        
    Raises:
        HTTPException: 上传失败时返回400或500
    """
    try:
        file_content = await file.read()
        
        ttl = timedelta(hours=ttl_hours) if ttl_hours else None
        
        file_object = await storage_service.upload_file(
            file_content=file_content,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            ttl=ttl
        )
        
        download_url = f"/api/v1/files/{file_object.object_key}"
        
        return FileUploadResponse(
            id=file_object.id,
            object_key=file_object.object_key,
            original_filename=file_object.original_filename,
            content_type=file_object.content_type,
            size_bytes=file_object.size_bytes,
            download_url=download_url,
            created_at=file_object.created_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.get(
    "/{object_key}",
    summary="下载文件",
    description="通过对象键下载文件",
    response_class=Response
)
async def download_file(
    object_key: str = Path(..., description="文件对象键")
) -> Response:
    """
    下载文件。
    
    Args:
        object_key (str): 文件对象键
        
    Returns:
        Response: 文件内容响应
        
    Raises:
        HTTPException: 文件不存在时返回404
    """
    try:
        file_content = await storage_service.download_file(object_key)
        file_metadata = await storage_service.get_file_metadata(object_key)
        
        if file_metadata is None:
            raise HTTPException(status_code=404, detail="File metadata not found")
        
        return Response(
            content=file_content,
            media_type=file_metadata.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_metadata.original_filename}"'
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")


@router.get(
    "/{object_key}/metadata",
    response_model=FileMetadataResponse,
    summary="获取文件元数据",
    description="获取文件的元数据信息"
)
async def get_file_metadata(
    object_key: str = Path(..., description="文件对象键")
) -> FileMetadataResponse:
    """
    获取文件元数据。
    
    Args:
        object_key (str): 文件对象键
        
    Returns:
        FileMetadataResponse: 文件元数据
        
    Raises:
        HTTPException: 文件不存在时返回404
    """
    file_metadata = await storage_service.get_file_metadata(object_key)
    
    if file_metadata is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    ttl_seconds = None
    if file_metadata.ttl:
        ttl_seconds = int(file_metadata.ttl.total_seconds())
    
    return FileMetadataResponse(
        id=file_metadata.id,
        object_key=file_metadata.object_key,
        original_filename=file_metadata.original_filename,
        content_type=file_metadata.content_type,
        size_bytes=file_metadata.size_bytes,
        ttl_seconds=ttl_seconds,
        created_at=file_metadata.created_at
    )


@router.delete(
    "/{object_key}",
    summary="删除文件",
    description="删除指定的文件"
)
async def delete_file(
    object_key: str = Path(..., description="文件对象键")
) -> dict[str, str]:
    """
    删除文件。
    
    Args:
        object_key (str): 文件对象键
        
    Returns:
        dict[str, str]: 删除结果
        
    Raises:
        HTTPException: 删除失败时返回500
    """
    success = await storage_service.delete_file(object_key)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete file")
    
    return {"message": f"File {object_key} deleted successfully"}


@router.post(
    "/cleanup",
    response_model=FileCleanupResponse,
    summary="清理过期文件",
    description="清理所有已过期的临时文件"
)
async def cleanup_expired_files() -> FileCleanupResponse:
    """
    清理过期文件。
    
    Returns:
        FileCleanupResponse: 清理结果
    """
    cleaned_count = await storage_service.cleanup_expired_files()
    
    return FileCleanupResponse(
        cleaned_count=cleaned_count,
        message=f"Successfully cleaned up {cleaned_count} expired files"
    )
