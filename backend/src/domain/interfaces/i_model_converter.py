from abc import ABC, abstractmethod

from ..value_objects import ModelMetadata


class IModelConverter(ABC):
    """
    模型转换器接口。

    定义3D模型格式转换和元数据提取的抽象方法。
    """

    @abstractmethod
    def convert_to_stl(self, model_path: str, output_path: str) -> str:
        """
        将模型转换为STL格式。

        Args:
            model_path (str): 源模型文件路径
            output_path (str): 输出STL文件路径

        Returns:
            str: 输出文件的实际路径

        Raises:
            FileNotFoundError: 如果源文件不存在
            ValueError: 如果模型格式不支持
            RuntimeError: 如果转换失败
        """
        pass

    @abstractmethod
    def extract_metadata(self, stl_path: str) -> ModelMetadata:
        """
        从STL文件提取元数据。

        Args:
            stl_path (str): STL文件路径

        Returns:
            ModelMetadata: 模型元数据

        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件格式无效
            RuntimeError: 如果提取失败
        """
        pass

    @abstractmethod
    def validate_model(self, stl_path: str) -> bool:
        """
        验证STL模型是否有效。

        Args:
            stl_path (str): STL文件路径

        Returns:
            bool: 模型是否有效

        Raises:
            FileNotFoundError: 如果文件不存在
        """
        pass

    @abstractmethod
    def repair_model(self, stl_path: str, output_path: str) -> str:
        """
        修复模型(填补破洞、修复非流形等)。

        Args:
            stl_path (str): 源STL文件路径
            output_path (str): 输出文件路径

        Returns:
            str: 修复后的文件路径

        Raises:
            FileNotFoundError: 如果源文件不存在
            RuntimeError: 如果修复失败
        """
        pass
