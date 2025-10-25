from typing import List, Tuple
from pydantic import BaseModel, Field


class PrinterProfile(BaseModel):
    """
    打印机硬件配置(值对象)
    
    Attributes:
        bed_size: 打印平台尺寸 (x, y, z) mm
        nozzle_diameter: 喷嘴直径 mm
        filament_diameter: 耗材直径 mm
        max_print_speed: 最大打印速度 mm/s
        max_travel_speed: 最大移动速度 mm/s
        firmware_flavor: 固件类型
        supported_formats: 支持的文件格式列表
    """
    bed_size: Tuple[int, int, int] = Field(..., description="打印平台尺寸(x,y,z)mm")
    nozzle_diameter: float = Field(..., description="喷嘴直径 mm")
    filament_diameter: float = Field(..., description="耗材直径 mm")
    max_print_speed: int = Field(..., description="最大打印速度 mm/s")
    max_travel_speed: int = Field(..., description="最大移动速度 mm/s")
    firmware_flavor: str = Field(..., description="固件类型")
    supported_formats: List[str] = Field(..., description="支持的文件格式列表")

    def validate_config(self) -> bool:
        """
        验证配置有效性
        
        Returns:
            bool: 配置是否有效
        """
        if self.nozzle_diameter <= 0 or self.filament_diameter <= 0:
            return False
        if any(size <= 0 for size in self.bed_size):
            return False
        if self.max_print_speed <= 0 or self.max_travel_speed <= 0:
            return False
        return True
