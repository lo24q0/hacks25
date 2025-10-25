from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

from ...domain.interfaces.i_storage import FileObject, IStorageService


class BaseStorageService(IStorageService, ABC):
    """
    存储服务基类。

    提供存储服务的通用功能和接口定义。
    子类需实现具体的存储逻辑。
    """

    def __init__(self, base_path: str):
        """
        初始化存储服务。

        Args:
            base_path (str): 存储根路径
        """
        self.base_path = base_path

    @abstractmethod
    async def upload_file(
        self, file_content: bytes, filename: str, content_type: str, ttl: Optional[timedelta] = None
    ) -> FileObject:
        pass

    @abstractmethod
    async def download_file(self, object_key: str) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, object_key: str) -> bool:
        pass

    @abstractmethod
    async def file_exists(self, object_key: str) -> bool:
        pass

    @abstractmethod
    async def cleanup_expired_files(self) -> int:
        pass

    @abstractmethod
    async def get_file_metadata(self, object_key: str) -> Optional[FileObject]:
        pass

    def _validate_filename(self, filename: str) -> None:
        """
        验证文件名合法性。

        Args:
            filename (str): 文件名

        Raises:
            ValueError: 文件名无效
        """
        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty")

        if ".." in filename or "/" in filename or "\\" in filename:
            raise ValueError("Filename contains invalid characters")

    def _validate_file_content(self, file_content: bytes) -> None:
        """
        验证文件内容。

        Args:
            file_content (bytes): 文件内容

        Raises:
            ValueError: 文件内容为空
        """
        if not file_content:
            raise ValueError("File content cannot be empty")
