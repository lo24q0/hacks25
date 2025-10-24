import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import uuid4

from ...domain.enums import StorageBackend
from ...domain.interfaces.i_storage import FileObject
from .base import BaseStorageService


class LocalStorageService(BaseStorageService):
    """
    本地文件存储服务实现。
    
    将文件存储在本地文件系统中,并维护元数据索引。
    """
    
    METADATA_FILE = "metadata.json"
    
    def __init__(self, base_path: str = "./storage"):
        """
        初始化本地存储服务。
        
        Args:
            base_path (str): 存储根路径,默认为 ./storage
        """
        super().__init__(base_path)
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self) -> None:
        """
        确保存储目录存在。
        """
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        metadata_path = Path(self.base_path) / self.METADATA_FILE
        if not metadata_path.exists():
            self._save_metadata({})
    
    def _get_metadata_path(self) -> Path:
        """
        获取元数据文件路径。
        
        Returns:
            Path: 元数据文件路径
        """
        return Path(self.base_path) / self.METADATA_FILE
    
    def _load_metadata(self) -> dict:
        """
        加载元数据。
        
        Returns:
            dict: 元数据字典
        """
        metadata_path = self._get_metadata_path()
        if not metadata_path.exists():
            return {}
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: dict) -> None:
        """
        保存元数据。
        
        Args:
            metadata (dict): 元数据字典
        """
        metadata_path = self._get_metadata_path()
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def _generate_object_key(self, filename: str) -> str:
        """
        生成唯一的对象键。
        
        Args:
            filename (str): 原始文件名
            
        Returns:
            str: 对象键
        """
        file_id = uuid4().hex
        file_extension = Path(filename).suffix
        return f"{file_id}{file_extension}"
    
    def _get_file_path(self, object_key: str) -> Path:
        """
        获取文件的完整路径。
        
        Args:
            object_key (str): 对象键
            
        Returns:
            Path: 文件路径
        """
        return Path(self.base_path) / object_key
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        ttl: Optional[timedelta] = None
    ) -> FileObject:
        """
        上传文件到本地存储。
        
        Args:
            file_content (bytes): 文件内容
            filename (str): 文件名
            content_type (str): 内容类型
            ttl (Optional[timedelta]): 生存时间
            
        Returns:
            FileObject: 文件对象
            
        Raises:
            ValueError: 如果文件内容为空或文件名无效
            RuntimeError: 如果上传失败
        """
        self._validate_filename(filename)
        self._validate_file_content(file_content)
        
        object_key = self._generate_object_key(filename)
        file_path = self._get_file_path(object_key)
        
        try:
            await asyncio.to_thread(file_path.write_bytes, file_content)
            
            file_object = FileObject(
                id=uuid4(),
                object_key=object_key,
                original_filename=filename,
                content_type=content_type,
                size_bytes=len(file_content),
                storage_backend=StorageBackend.LOCAL,
                ttl=ttl,
                created_at=datetime.utcnow()
            )
            
            metadata = self._load_metadata()
            metadata[object_key] = {
                "id": str(file_object.id),
                "object_key": object_key,
                "original_filename": filename,
                "content_type": content_type,
                "size_bytes": len(file_content),
                "storage_backend": StorageBackend.LOCAL.value,
                "ttl_seconds": ttl.total_seconds() if ttl else None,
                "created_at": file_object.created_at.isoformat()
            }
            self._save_metadata(metadata)
            
            return file_object
            
        except Exception as e:
            if file_path.exists():
                await asyncio.to_thread(file_path.unlink)
            raise RuntimeError(f"Failed to upload file: {str(e)}") from e
    
    async def download_file(self, object_key: str) -> bytes:
        """
        从本地存储下载文件。
        
        Args:
            object_key (str): 对象键
            
        Returns:
            bytes: 文件内容
            
        Raises:
            FileNotFoundError: 如果文件不存在
            RuntimeError: 如果下载失败
        """
        file_path = self._get_file_path(object_key)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {object_key}")
        
        try:
            return await asyncio.to_thread(file_path.read_bytes)
        except Exception as e:
            raise RuntimeError(f"Failed to download file: {str(e)}") from e
    
    async def delete_file(self, object_key: str) -> bool:
        """
        删除文件。
        
        Args:
            object_key (str): 对象键
            
        Returns:
            bool: 是否删除成功
        """
        file_path = self._get_file_path(object_key)
        
        try:
            if file_path.exists():
                await asyncio.to_thread(file_path.unlink)
            
            metadata = self._load_metadata()
            if object_key in metadata:
                del metadata[object_key]
                self._save_metadata(metadata)
            
            return True
        except Exception:
            return False
    
    async def file_exists(self, object_key: str) -> bool:
        """
        检查文件是否存在。
        
        Args:
            object_key (str): 对象键
            
        Returns:
            bool: 文件是否存在
        """
        file_path = self._get_file_path(object_key)
        return file_path.exists()
    
    async def cleanup_expired_files(self) -> int:
        """
        清理过期文件。
        
        Returns:
            int: 清理的文件数量
        """
        metadata = self._load_metadata()
        current_time = datetime.utcnow()
        cleaned_count = 0
        
        keys_to_delete = []
        for object_key, meta in metadata.items():
            ttl_seconds = meta.get("ttl_seconds")
            if ttl_seconds is None:
                continue
            
            created_at = datetime.fromisoformat(meta["created_at"])
            ttl = timedelta(seconds=ttl_seconds)
            
            if current_time >= created_at + ttl:
                keys_to_delete.append(object_key)
        
        for object_key in keys_to_delete:
            if await self.delete_file(object_key):
                cleaned_count += 1
        
        return cleaned_count
    
    async def get_file_metadata(self, object_key: str) -> Optional[FileObject]:
        """
        获取文件元数据。
        
        Args:
            object_key (str): 对象键
            
        Returns:
            Optional[FileObject]: 文件对象,不存在则返回None
        """
        metadata = self._load_metadata()
        meta = metadata.get(object_key)
        
        if not meta:
            return None
        
        ttl = None
        if meta.get("ttl_seconds") is not None:
            ttl = timedelta(seconds=meta["ttl_seconds"])
        
        return FileObject(
            id=meta["id"],
            object_key=meta["object_key"],
            original_filename=meta["original_filename"],
            content_type=meta["content_type"],
            size_bytes=meta["size_bytes"],
            storage_backend=StorageBackend(meta["storage_backend"]),
            ttl=ttl,
            created_at=datetime.fromisoformat(meta["created_at"])
        )
