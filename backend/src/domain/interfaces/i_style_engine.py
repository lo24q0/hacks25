from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StylePreset:
    """
    风格预设数据类。

    用于定义图像风格化的预设配置，包括风格类型、推荐参数等。

    Args:
        id (str): 预设ID，如 'anime', 'cartoon_3d'
        name (str): 中文名称
        description (str): 风格描述
        model_name (str): 使用的模型名称或 API 提供商，如 'TencentCloud'
        preview_image (str): 预览图片路径
        name_en (Optional[str]): 英文名称
        tags (Optional[List[str]]): 风格标签列表
        recommended_strength (int): 推荐的风格强度 (0-100)
        tencent_style_id (Optional[int]): 腾讯云 API 的 StyleId
        estimated_time (int): 预计处理时间（秒）

    示例:
        >>> preset = StylePreset(
        ...     id="anime",
        ...     name="动漫风格",
        ...     description="日系二次元动漫风格",
        ...     model_name="TencentCloud",
        ...     preview_image="/assets/anime.jpg",
        ...     tencent_style_id=201,
        ...     recommended_strength=80
        ... )
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        model_name: str,
        preview_image: str,
        name_en: Optional[str] = None,
        tags: Optional[List[str]] = None,
        recommended_strength: int = 80,
        tencent_style_id: Optional[int] = None,
        estimated_time: int = 20,
    ):
        self.id = id
        self.name = name
        self.name_en = name_en or name
        self.description = description
        self.model_name = model_name
        self.preview_image = preview_image
        self.tags = tags or []
        self.recommended_strength = recommended_strength
        self.tencent_style_id = tencent_style_id
        self.estimated_time = estimated_time

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（用于 API 响应）。

        Returns:
            dict: 风格预设的字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "description": self.description,
            "model_name": self.model_name,
            "preview_image": self.preview_image,
            "tags": self.tags,
            "recommended_strength": self.recommended_strength,
            "estimated_time": self.estimated_time,
        }


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
