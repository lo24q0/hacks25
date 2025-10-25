from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Dimensions:
    """
    3D模型的尺寸值对象。

    Args:
        x (float): X轴尺寸(毫米)
        y (float): Y轴尺寸(毫米)
        z (float): Z轴尺寸(毫米)
    """

    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0 or self.z < 0:
            raise ValueError("Dimensions must be non-negative")


@dataclass(frozen=True)
class BoundingBox:
    """
    3D模型的包围盒值对象。

    Args:
        min_point (Tuple[float, float, float]): 最小点坐标(x, y, z)
        max_point (Tuple[float, float, float]): 最大点坐标(x, y, z)
    """

    min_point: Tuple[float, float, float]
    max_point: Tuple[float, float, float]

    def __post_init__(self) -> None:
        if len(self.min_point) != 3 or len(self.max_point) != 3:
            raise ValueError("Points must have exactly 3 coordinates")

        for i in range(3):
            if self.min_point[i] > self.max_point[i]:
                raise ValueError(f"min_point[{i}] must be <= max_point[{i}]")

    def get_dimensions(self) -> Dimensions:
        """
        计算包围盒的尺寸。

        Returns:
            Dimensions: 包围盒的尺寸
        """
        return Dimensions(
            x=self.max_point[0] - self.min_point[0],
            y=self.max_point[1] - self.min_point[1],
            z=self.max_point[2] - self.min_point[2],
        )


@dataclass(frozen=True)
class ModelMetadata:
    """
    3D模型元数据值对象。

    Args:
        dimensions (Dimensions): 模型尺寸(毫米)
        volume (float): 模型体积(立方毫米)
        triangle_count (int): 三角面数量
        vertex_count (int): 顶点数量
        is_manifold (bool): 是否为流形网格(可打印)
        bounding_box (BoundingBox): 包围盒
    """

    dimensions: Dimensions
    volume: float
    triangle_count: int
    vertex_count: int
    is_manifold: bool
    bounding_box: BoundingBox

    def __post_init__(self) -> None:
        if self.volume < 0:
            raise ValueError("Volume must be non-negative")
        if self.triangle_count < 0:
            raise ValueError("Triangle count must be non-negative")
        if self.vertex_count < 0:
            raise ValueError("Vertex count must be non-negative")

    def is_printable(self) -> bool:
        """
        检查模型是否可打印。

        Returns:
            bool: 是否可打印(需要是流形且有体积)
        """
        return self.is_manifold and self.volume > 0
