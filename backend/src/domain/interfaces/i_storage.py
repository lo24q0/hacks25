from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional
from uuid import UUID

from ..enums import StorageBackend


@dataclass
class FileObject:
    """
    文件对象。

    Args:
        id (UUID): 文件ID
        object_key (str): 存储路径/键
        original_filename (str): 原始文件名
        content_type (str): 内容类型(MIME)
        size_bytes (int): 文件大小(字节)
        storage_backend (StorageBackend): 存储后端
        ttl (Optional[timedelta]): 生存时间
        created_at (datetime): 创建时间
    """
    id: UUID
    object_key: str
    original_filename: str
    content_type: str
    size_bytes: int
    storage_backend: StorageBackend
    ttl: Optional[timedelta]
    created_at: datetime

    def get_download_url(self, base_url: str) -> str:
        """
        获取下载URL。

        Args:
            base_url (str): 基础URL

        Returns:
            str: 完整的下载URL
        """
        return f"{base_url}/files/{self.object_key}"

    def should_cleanup(self, current_time: datetime) -> bool:
        """
        检查是否应该清理。

        Args:
            current_time (datetime): 当前时间

        Returns:
            bool: 是否应该清理
        """
        if self.ttl is None:
            return False
        
        expiry_time = self.created_at + self.ttl
        return current_time >= expiry_time


class IStorageService(ABC):
    """
    存储服务接口。

    定义文件上传、下载和管理的抽象方法。
    """

    @abstractmethod
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        ttl: Optional[timedelta] = None
    ) -> FileObject:
        """
        上传文件。

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
        pass

    @abstractmethod
    async def download_file(self, object_key: str) -> bytes:
        """
        下载文件。

        Args:
            object_key (str): 对象键

        Returns:
            bytes: 文件内容

        Raises:
            FileNotFoundError: 如果文件不存在
            RuntimeError: 如果下载失败
        """
        pass

    @abstractmethod
    async def delete_file(self, object_key: str) -> bool:
        """
        删除文件。

        Args:
            object_key (str): 对象键

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def file_exists(self, object_key: str) -> bool:
        """
        检查文件是否存在。

        Args:
            object_key (str): 对象键

        Returns:
            bool: 文件是否存在
        """
        pass

    @abstractmethod
    async def cleanup_expired_files(self) -> int:
        """
        清理过期文件。

        Returns:
            int: 清理的文件数量
        """
        pass

    @abstractmethod
    async def get_file_metadata(self, object_key: str) -> Optional[FileObject]:
        """
        获取文件元数据。

        Args:
            object_key (str): 对象键

        Returns:
            Optional[FileObject]: 文件对象,不存在则返回None
        """
        pass
