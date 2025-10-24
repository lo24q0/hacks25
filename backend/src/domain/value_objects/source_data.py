from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class SourceData:
    """
    3D模型生成源数据值对象。

    Args:
        text_prompt (Optional[str]): 文本描述提示词
        image_paths (Optional[List[str]]): 图片文件路径列表
        style_preset (Optional[str]): 风格化预设ID
    """
    text_prompt: Optional[str] = None
    image_paths: Optional[List[str]] = None
    style_preset: Optional[str] = None

    def __post_init__(self) -> None:
        if self.text_prompt is None and self.image_paths is None:
            raise ValueError("Either text_prompt or image_paths must be provided")
        
        if self.text_prompt is not None and len(self.text_prompt.strip()) == 0:
            raise ValueError("text_prompt cannot be empty")
        
        if self.image_paths is not None and len(self.image_paths) == 0:
            raise ValueError("image_paths cannot be empty list")

    def has_text(self) -> bool:
        """
        检查是否包含文本提示词。

        Returns:
            bool: 是否有文本提示词
        """
        return self.text_prompt is not None

    def has_images(self) -> bool:
        """
        检查是否包含图片。

        Returns:
            bool: 是否有图片
        """
        return self.image_paths is not None and len(self.image_paths) > 0
