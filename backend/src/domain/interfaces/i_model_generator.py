from abc import ABC, abstractmethod
from typing import Optional

from ..models.model3d import Model3D


class IModelGenerator(ABC):
    """
    模型生成器接口。

    定义从不同源生成3D模型的抽象方法。
    """

    @abstractmethod
    async def generate_from_text(self, prompt: str, style_preset: Optional[str] = None) -> Model3D:
        """
        从文本描述生成3D模型。

        Args:
            prompt (str): 文本提示词
            style_preset (Optional[str]): 风格预设ID

        Returns:
            Model3D: 创建的模型对象

        Raises:
            ValueError: 如果提示词为空或无效
            RuntimeError: 如果生成过程失败
        """
        pass

    @abstractmethod
    async def generate_from_image(
        self, image_path: str, style_preset: Optional[str] = None
    ) -> Model3D:
        """
        从图片生成3D模型。

        Args:
            image_path (str): 图片文件路径
            style_preset (Optional[str]): 风格预设ID

        Returns:
            Model3D: 创建的模型对象

        Raises:
            ValueError: 如果图片路径无效
            FileNotFoundError: 如果图片文件不存在
            RuntimeError: 如果生成过程失败
        """
        pass

    @abstractmethod
    async def get_generation_status(self, task_id: str) -> dict:
        """
        获取生成任务状态。

        Args:
            task_id (str): 任务ID

        Returns:
            dict: 任务状态信息

        Raises:
            ValueError: 如果任务ID无效
        """
        pass
