from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Tuple


@dataclass
class PrinterProfile:
    """
    打印机配置。

    Args:
        id (str): 配置ID
        name (str): 打印机名称
        bed_size (Tuple[int, int, int]): 打印床尺寸(x, y, z)毫米
        nozzle_diameter (float): 喷嘴直径(毫米)
        filament_diameter (float): 耗材直径(毫米)
        max_speed (int): 最大打印速度(mm/s)
        firmware_flavor (str): 固件类型
    """
    id: str
    name: str
    bed_size: Tuple[int, int, int]
    nozzle_diameter: float
    filament_diameter: float
    max_speed: int
    firmware_flavor: str


@dataclass
class SlicingConfig:
    """
    切片配置。

    Args:
        layer_height (float): 层高(毫米)
        infill_density (int): 填充率(0-100)
        print_speed (int): 打印速度(mm/s)
        support_enabled (bool): 是否启用支撑
        adhesion_type (str): 底板附着类型(skirt/brim/raft)
    """
    layer_height: float
    infill_density: int
    print_speed: int
    support_enabled: bool
    adhesion_type: str

    def validate(self) -> bool:
        """
        验证配置是否有效。

        Returns:
            bool: 配置是否有效
        """
        if not (0.1 <= self.layer_height <= 0.3):
            return False
        if not (0 <= self.infill_density <= 100):
            return False
        if not (10 <= self.print_speed <= 300):
            return False
        if self.adhesion_type not in ["skirt", "brim", "raft"]:
            return False
        return True


@dataclass
class GCodeResult:
    """
    G-code生成结果。

    Args:
        gcode_path (str): G-code文件路径
        estimated_time (timedelta): 预估打印时间
        estimated_material (float): 预估耗材量(克)
        layer_count (int): 层数
    """
    gcode_path: str
    estimated_time: timedelta
    estimated_material: float
    layer_count: int


class ISlicer(ABC):
    """
    切片引擎接口。

    定义3D模型切片和G-code生成的抽象方法。
    """

    @abstractmethod
    async def slice_model(
        self,
        stl_path: str,
        printer: PrinterProfile,
        config: SlicingConfig,
        output_path: str
    ) -> GCodeResult:
        """
        切片模型生成G-code。

        Args:
            stl_path (str): STL文件路径
            printer (PrinterProfile): 打印机配置
            config (SlicingConfig): 切片配置
            output_path (str): 输出G-code路径

        Returns:
            GCodeResult: 生成结果

        Raises:
            FileNotFoundError: 如果STL文件不存在
            ValueError: 如果配置无效
            RuntimeError: 如果切片失败
        """
        pass

    @abstractmethod
    def get_available_printers(self) -> list[PrinterProfile]:
        """
        获取支持的打印机列表。

        Returns:
            list[PrinterProfile]: 打印机配置列表
        """
        pass

    @abstractmethod
    def get_default_config(self, printer_id: str) -> SlicingConfig:
        """
        获取指定打印机的默认切片配置。

        Args:
            printer_id (str): 打印机ID

        Returns:
            SlicingConfig: 默认配置

        Raises:
            ValueError: 如果打印机ID不存在
        """
        pass
