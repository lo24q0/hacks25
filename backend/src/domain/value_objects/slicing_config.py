from pydantic import BaseModel, Field
from src.domain.enums.print_enums import AdhesionType, MaterialType


class SlicingConfig(BaseModel):
    """
    切片配置(值对象)
    
    Attributes:
        layer_height: 层高 (0.1-0.3mm)
        infill_density: 填充率 (0-100%)
        print_speed: 打印速度 mm/s
        travel_speed: 移动速度 mm/s
        support_enabled: 是否启用支撑
        adhesion_type: 底板附着类型
        material_type: 耗材类型
        nozzle_temperature: 喷嘴温度 °C
        bed_temperature: 热床温度 °C
    """
    layer_height: float = Field(..., ge=0.1, le=0.3, description="层高 mm")
    infill_density: int = Field(..., ge=0, le=100, description="填充率 %")
    print_speed: int = Field(..., gt=0, description="打印速度 mm/s")
    travel_speed: int = Field(..., gt=0, description="移动速度 mm/s")
    support_enabled: bool = Field(default=False, description="是否启用支撑")
    adhesion_type: AdhesionType = Field(..., description="底板附着类型")
    material_type: MaterialType = Field(..., description="耗材类型")
    nozzle_temperature: int = Field(..., gt=0, description="喷嘴温度 °C")
    bed_temperature: int = Field(..., ge=0, description="热床温度 °C")

    @classmethod
    def get_preset(cls, preset_name: str) -> "SlicingConfig":
        """
        获取预设配置

        Args:
            preset_name: 预设名称 (fast, standard, high_quality, bambu_h2d_standard)

        Returns:
            SlicingConfig: 预设配置
        """
        presets = {
            "fast": cls(
                layer_height=0.3,
                infill_density=10,
                print_speed=60,
                travel_speed=120,
                support_enabled=False,
                adhesion_type=AdhesionType.SKIRT,
                material_type=MaterialType.PLA,
                nozzle_temperature=200,
                bed_temperature=60
            ),
            "standard": cls(
                layer_height=0.2,
                infill_density=20,
                print_speed=50,
                travel_speed=100,
                support_enabled=True,
                adhesion_type=AdhesionType.BRIM,
                material_type=MaterialType.PLA,
                nozzle_temperature=210,
                bed_temperature=60
            ),
            "high_quality": cls(
                layer_height=0.1,
                infill_density=30,
                print_speed=30,
                travel_speed=80,
                support_enabled=True,
                adhesion_type=AdhesionType.RAFT,
                material_type=MaterialType.PLA,
                nozzle_temperature=215,
                bed_temperature=65
            ),
            # 从 box_prod.gcode.3mf 提取的拓竹 H2D 标准配置
            "bambu_h2d_standard": cls(
                layer_height=0.2,           # layer_height: "0.2"
                infill_density=15,          # sparse_infill_density: "15%"
                print_speed=200,            # outer_wall_speed: [200, ...]
                travel_speed=1000,          # travel_speed: [1000, ...]
                support_enabled=False,      # enable_support: "0"
                adhesion_type=AdhesionType.BRIM,  # brim_type: "auto_brim"
                material_type=MaterialType.PLA,   # filament_type: ["PLA"]
                nozzle_temperature=220,     # nozzle_temperature: [220, ...]
                bed_temperature=55          # hot_plate_temp: [55]
            )
        }

        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}")

        return presets[preset_name]
