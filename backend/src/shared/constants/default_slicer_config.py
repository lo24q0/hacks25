"""
默认切片配置

从 box_prod.gcode.3mf 提取的拓竹 H2D 标准切片参数
"""

from typing import Dict, Any

# 拓竹 H2D 默认切片配置
DEFAULT_H2D_CONFIG: Dict[str, Any] = {
    # 基础打印参数
    "layer_height": 0.2,  # 层高 (mm)
    "initial_layer_print_height": 0.2,  # 首层高度 (mm)
    "initial_layer_line_width": 0.5,  # 首层线宽 (mm)

    # 线宽设置
    "line_width": 0.42,  # 默认线宽 (mm)
    "inner_wall_line_width": 0.45,  # 内墙线宽 (mm)
    "outer_wall_line_width": 0.42,  # 外墙线宽 (mm)
    "top_surface_line_width": 0.42,  # 顶面线宽 (mm)
    "sparse_infill_line_width": 0.45,  # 填充线宽 (mm)

    # 壳体设置
    "wall_loops": 2,  # 壁厚层数
    "top_shell_layers": 5,  # 顶部实心层数
    "bottom_shell_layers": 3,  # 底部实心层数
    "top_shell_thickness": 1,  # 顶部厚度 (mm)
    "bottom_shell_thickness": 0,  # 底部厚度 (mm)

    # 填充设置
    "sparse_infill_density": "15%",  # 填充密度
    "sparse_infill_pattern": "grid",  # 填充图案
    "infill_direction": 45,  # 填充方向 (度)

    # 速度设置 (mm/s)
    "outer_wall_speed": [200, 500, 200, 500],  # 外墙速度
    "inner_wall_speed": [300, 600, 300, 600],  # 内墙速度
    "sparse_infill_speed": [350, 600, 350, 600],  # 填充速度
    "internal_solid_infill_speed": [250, 600, 250, 600],  # 实心填充速度
    "top_surface_speed": [200, 200, 200, 200],  # 顶面速度
    "initial_layer_speed": [50, 50, 50, 50],  # 首层速度
    "travel_speed": [1000, 1000, 1000, 1000],  # 空移速度
    "bridge_speed": [50, 50, 50, 50],  # 桥接速度

    # 加速度设置 (mm/s²)
    "default_acceleration": [8000, 8000, 8000, 8000],  # 默认加速度
    "outer_wall_acceleration": [5000, 5000, 5000, 5000],  # 外墙加速度
    "initial_layer_acceleration": [500, 500, 500, 500],  # 首层加速度
    "travel_acceleration": [10000, 10000, 10000, 10000],  # 空移加速度

    # Jerk 设置 (mm/s)
    "default_jerk": 0,
    "initial_layer_jerk": 9,
    "infill_jerk": 9,
    "inner_wall_jerk": 9,
    "outer_wall_jerk": 9,
    "top_surface_jerk": 9,
    "travel_jerk": 9,

    # 支撑设置
    "enable_support": False,  # 是否启用支撑
    "support_type": "tree(auto)",  # 支撑类型
    "support_angle": 0,  # 支撑角度
    "support_threshold_angle": 30,  # 支撑阈值角度
    "support_on_build_plate_only": False,  # 仅从打印床生成支撑

    # 粘附设置
    "brim_type": "auto_brim",  # Brim 类型
    "brim_width": 5,  # Brim 宽度 (mm)
    "brim_object_gap": 0.1,  # Brim 与对象间隙 (mm)
    "skirt_loops": 0,  # Skirt 圈数
    "skirt_distance": 2,  # Skirt 距离 (mm)

    # 温度设置 (°C)
    "nozzle_temperature": [220, 220],  # 喷嘴温度
    "nozzle_temperature_initial_layer": [220, 220],  # 首层喷嘴温度
    "hot_plate_temp": [55],  # 热床温度
    "hot_plate_temp_initial_layer": [55],  # 首层热床温度
    "textured_plate_temp": [55],  # 纹理板温度
    "textured_plate_temp_initial_layer": [55],  # 首层纹理板温度

    # 风扇设置 (%)
    "fan_max_speed": [80],  # 最大风扇速度
    "fan_min_speed": [60],  # 最小风扇速度
    "close_fan_the_first_x_layers": [1],  # 前 N 层关闭风扇
    "full_fan_speed_layer": [0],  # 全速风扇起始层

    # 回抽设置
    "retraction_length": [0.8, 0.8, 0.8, 0.8],  # 回抽长度 (mm)
    "retraction_speed": [30, 30, 30, 30],  # 回抽速度 (mm/s)
    "deretraction_speed": [30, 30, 30, 30],  # 反回抽速度 (mm/s)
    "retraction_minimum_travel": [1, 1, 1, 1],  # 最小空移回抽距离 (mm)
    "retract_when_changing_layer": [True, True, True, True],  # 换层时回抽
    "z_hop": [0.4, 0.4, 0.4, 0.4],  # Z 抬升高度 (mm)
    "z_hop_types": ["Auto Lift", "Auto Lift", "Auto Lift", "Auto Lift"],  # Z 抬升类型

    # 料丝设置
    "filament_type": ["PLA"],  # 料丝类型
    "filament_diameter": [1.75],  # 料丝直径 (mm)
    "filament_density": [1.26],  # 料丝密度 (g/cm³)
    "filament_flow_ratio": [0.98, 0.98],  # 流量比
    "filament_max_volumetric_speed": [25, 40],  # 最大体积速度 (mm³/s)

    # 打印机设置
    "printer_model": "Bambu Lab H2D",
    "nozzle_diameter": [0.4, 0.4],  # 喷嘴直径 (mm)
    "nozzle_type": ["hardened_steel", "hardened_steel", "hardened_steel", "hardened_steel"],
    "printable_height": 325,  # 可打印高度 (mm)
    "printable_area": ["0x0", "350x0", "350x320", "0x320"],  # 可打印区域

    # 高级设置
    "enable_arc_fitting": True,  # 启用圆弧拟合
    "elefant_foot_compensation": 0.15,  # 大象脚补偿 (mm)
    "seam_position": "aligned",  # 缝隙位置
    "wall_sequence": "inner wall/outer wall",  # 墙体顺序
    "infill_wall_overlap": "15%",  # 填充与墙体重叠
    "detect_thin_wall": False,  # 检测薄壁
    "detect_overhang_wall": True,  # 检测悬垂墙
    "gcode_flavor": "marlin",  # G-code 风格
    "use_relative_e_distances": True,  # 使用相对 E 距离
    "resolution": 0.012,  # 分辨率 (mm)

    # 其他设置
    "print_sequence": "by layer",  # 打印顺序
    "curr_bed_type": "Textured PEI Plate",  # 当前热床类型
    "auxiliary_fan": True,  # 辅助风扇
    "enable_prime_tower": True,  # 启用清洁塔
    "prime_tower_width": 60,  # 清洁塔宽度 (mm)
}

# 拓竹 H2D 打印机配置
H2D_PRINTER_PROFILE: Dict[str, Any] = {
    "name": "Bambu Lab H2D",
    "model_id": "O1D",
    "bed_size": (350, 320, 325),  # (x, y, z) mm
    "nozzle_diameter": 0.4,  # mm
    "filament_diameter": 1.75,  # mm
    "max_speed_x": 1000,  # mm/s
    "max_speed_y": 1000,  # mm/s
    "max_speed_z": 30,  # mm/s
    "max_speed_e": 50,  # mm/s
    "max_acceleration_x": 20000,  # mm/s²
    "max_acceleration_y": 20000,  # mm/s²
    "max_acceleration_z": 500,  # mm/s²
    "max_acceleration_e": 5000,  # mm/s²
    "max_jerk_x": 9,  # mm/s
    "max_jerk_y": 9,  # mm/s
    "max_jerk_z": 3,  # mm/s
    "max_jerk_e": 2.5,  # mm/s
    "firmware_flavor": "marlin",
    "gcode_flavor": "marlin",
    "use_relative_e_distances": True,
    "extruder_count": 2,
    "extruder_type": ["Direct Drive", "Direct Drive"],
}

# OrcaSlicer 映射配置
ORCASLICER_PARAM_MAPPING: Dict[str, str] = {
    # 将我们的参数名映射到 OrcaSlicer 的参数名
    "layer_height": "layer_height",
    "initial_layer_print_height": "first_layer_height",
    "line_width": "line_width",
    "wall_loops": "wall_loops",
    "top_shell_layers": "top_shell_layers",
    "bottom_shell_layers": "bottom_shell_layers",
    "sparse_infill_density": "infill_density",
    "sparse_infill_pattern": "infill_pattern",
    "nozzle_temperature": "nozzle_temperature",
    "hot_plate_temp": "bed_temperature",
    "retraction_length": "retraction_length",
    "retraction_speed": "retraction_speed",
    "travel_speed": "travel_speed",
}


def get_default_config() -> Dict[str, Any]:
    """
    获取默认切片配置

    Returns:
        Dict[str, Any]: 默认切片配置字典
    """
    return DEFAULT_H2D_CONFIG.copy()


def get_printer_profile() -> Dict[str, Any]:
    """
    获取打印机配置

    Returns:
        Dict[str, Any]: 打印机配置字典
    """
    return H2D_PRINTER_PROFILE.copy()


def map_to_orcaslicer_params(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    将配置参数映射到 OrcaSlicer 参数名

    Args:
        config: 输入配置字典

    Returns:
        Dict[str, Any]: 映射后的配置字典
    """
    mapped_config = {}
    for our_key, orca_key in ORCASLICER_PARAM_MAPPING.items():
        if our_key in config:
            mapped_config[orca_key] = config[our_key]
    return mapped_config
