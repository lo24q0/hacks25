from abc import ABC, abstractmethod
from typing import Optional, List, Generic, TypeVar
from uuid import UUID

from ..models.model3d import Model3D


T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """
    仓储接口基类。

    定义通用的数据访问方法。
    """

    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        保存实体。

        Args:
            entity (T): 要保存的实体

        Returns:
            T: 保存后的实体

        Raises:
            RuntimeError: 如果保存失败
        """
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[T]:
        """
        根据ID查找实体。

        Args:
            id (UUID): 实体ID

        Returns:
            Optional[T]: 找到的实体,不存在则返回None
        """
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """
        删除实体。

        Args:
            id (UUID): 实体ID

        Returns:
            bool: 是否删除成功

        Raises:
            ValueError: 如果实体不存在
        """
        pass


class IModelRepository(IRepository[Model3D]):
    """
    模型仓储接口。

    定义Model3D特定的数据访问方法。
    """

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID, limit: int = 20) -> List[Model3D]:
        """
        查找用户的模型列表。

        Args:
            user_id (UUID): 用户ID
            limit (int): 返回数量限制

        Returns:
            List[Model3D]: 模型列表
        """
        pass

    @abstractmethod
    async def find_pending(self, limit: int = 10) -> List[Model3D]:
        """
        查找待处理的模型。

        Args:
            limit (int): 返回数量限制

        Returns:
            List[Model3D]: 待处理模型列表
        """
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID) -> int:
        """
        统计用户的模型数量。

        Args:
            user_id (UUID): 用户ID

        Returns:
            int: 模型数量
        """
        pass
