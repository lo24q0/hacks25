from abc import ABC, abstractmethod
from typing import List


class StylePreset:
    """
    风格预设数据类。

    Args:
        id (str): 预设ID
        name (str): 预设名称
        description (str): 预设描述
        model_name (str): 使用的模型名称
        preview_image (str): 预览图片路径
    """

    def __init__(self, id: str, name: str, description: str, model_name: str, preview_image: str):
        self.id = id
        self.name = name
        self.description = description
        self.model_name = model_name
        self.preview_image = preview_image


class IStyleEngine(ABC):
    """
    风格迁移引擎接口。

    定义图片风格化处理的抽象方法。
    """

    @abstractmethod
    async def transfer_style(self, image_path: str, style_preset_id: str, output_path: str) -> str:
        """
        应用风格迁移。

        Args:
            image_path (str): 源图片路径
            style_preset_id (str): 风格预设ID
            output_path (str): 输出文件路径

        Returns:
            str: 风格化后的图片路径

        Raises:
            FileNotFoundError: 如果源图片不存在
            ValueError: 如果风格预设不存在
            RuntimeError: 如果风格迁移失败
        """
        pass

    @abstractmethod
    def get_available_styles(self) -> List[StylePreset]:
        """
        获取可用的风格预设列表。

        Returns:
            List[StylePreset]: 风格预设列表
        """
        pass

    @abstractmethod
    def get_style_preset(self, preset_id: str) -> StylePreset:
        """
        根据ID获取风格预设。

        Args:
            preset_id (str): 预设ID

        Returns:
            StylePreset: 风格预设

        Raises:
            ValueError: 如果预设不存在
        """
        pass
