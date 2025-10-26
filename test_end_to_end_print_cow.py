#!/usr/bin/env python3
"""
端到端测试脚本: 打印 3D 牛

完整流程:
1. 生成 3D 牛模型 STL
2. 使用 OrcaSlicer 切片生成 G-code
3. 将 G-code 转换为拓竹 3MF 格式
4. 连接拓竹打印机
5. 上传并开始打印

打印机配置:
- IP: 100.100.34.201
- Serial: 0948DB551901061
- Access Code: 5dac4f7a
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_cow_stl() -> str:
    """
    创建 3D 牛模型 STL 文件

    Returns:
        str: STL 文件路径
    """
    logger.info("步骤 1/5: 生成 3D 牛模型 STL")

    # 使用之前创建的脚本
    cow_stl_path = "/tmp/cow_model.stl"

    if os.path.exists(cow_stl_path):
        logger.info(f"✅ STL 文件已存在: {cow_stl_path}")
    else:
        import subprocess
        subprocess.run([
            "python3",
            str(Path(__file__).parent / "create_simple_cow_stl.py")
        ], check=True)
        logger.info(f"✅ STL 文件生成完成: {cow_stl_path}")

    return cow_stl_path


async def slice_model(stl_path: str) -> str:
    """
    使用 OrcaSlicer 切片模型

    Args:
        stl_path: STL 文件路径

    Returns:
        str: G-code 文件路径
    """
    logger.info("步骤 2/5: 使用 OrcaSlicer 切片模型")

    from domain.value_objects.printer_profile import PrinterProfile
    from domain.value_objects.slicing_config import SlicingConfig
    from infrastructure.slicing.orca_slicer import OrcaSlicer
    from shared.constants.default_slicer_config import DEFAULT_H2D_CONFIG

    # 创建切片器实例
    slicer = OrcaSlicer(
        orca_slicer_path="/usr/local/bin/orcaslicer"
    )

    # 拓竹 H2D 打印机配置
    printer = PrinterProfile(
        id="bambu_h2d",
        name="Bambu Lab H2D",
        bed_size=(350, 320, 325),
        nozzle_diameter=0.4,
        filament_diameter=1.75,
        max_speed=500,
        firmware_flavor="Marlin"
    )

    # 从提取的默认配置创建切片配置
    slicing_config = SlicingConfig(
        layer_height=DEFAULT_H2D_CONFIG["layer_height"],
        infill_density=int(DEFAULT_H2D_CONFIG["sparse_infill_density"].rstrip("%")),
        print_speed=DEFAULT_H2D_CONFIG["inner_wall_speed"][0],
        support_enabled=DEFAULT_H2D_CONFIG["enable_support"],
        adhesion_type=DEFAULT_H2D_CONFIG["brim_type"]
    )

    # 输出 G-code 文件路径
    gcode_path = stl_path.replace('.stl', '.gcode')

    logger.info(f"切片配置: 层高={slicing_config.layer_height}mm, 填充={slicing_config.infill_density}%, 速度={slicing_config.print_speed}mm/s")

    try:
        result = await slicer.slice_model(
            stl_path=stl_path,
            printer=printer,
            config=slicing_config,
            output_path=gcode_path
        )

        logger.info(f"✅ 切片完成:")
        logger.info(f"   - 层数: {result.layer_count}")
        logger.info(f"   - 预计时间: {result.estimated_time}")
        logger.info(f"   - 预计材料: {result.estimated_material:.2f}g")
        logger.info(f"   - G-code: {gcode_path}")

        return gcode_path

    except Exception as e:
        logger.error(f"❌ 切片失败: {e}")
        raise


def convert_to_3mf(gcode_path: str) -> str:
    """
    将 G-code 转换为拓竹 3MF 格式

    Args:
        gcode_path: G-code 文件路径

    Returns:
        str: 3MF 文件路径
    """
    logger.info("步骤 3/5: 转换 G-code 为拓竹 3MF 格式")

    from shared.utils.gcode_to_3mf import convert_gcode_to_3mf
    from shared.constants.default_slicer_config import DEFAULT_H2D_CONFIG

    # 输出 3MF 文件路径
    mf_path = gcode_path.replace('.gcode', '.gcode.3mf')

    # 使用提取的默认配置作为元数据
    metadata = {
        "model_name": "3D_Cow",
        "layer_height": DEFAULT_H2D_CONFIG["layer_height"],
        "infill_density": int(DEFAULT_H2D_CONFIG["sparse_infill_density"].rstrip("%")),
        "print_speed": DEFAULT_H2D_CONFIG["inner_wall_speed"][0],
        "nozzle_temperature": DEFAULT_H2D_CONFIG["nozzle_temperature"][0],
        "bed_temperature": DEFAULT_H2D_CONFIG["hot_plate_temp"][0],
        "material_type": DEFAULT_H2D_CONFIG["filament_type"][0]
    }

    try:
        result_path = convert_gcode_to_3mf(
            gcode_path=gcode_path,
            output_path=mf_path,
            **metadata
        )

        logger.info(f"✅ 3MF 文件生成完成: {result_path}")

        # 显示文件信息
        file_size = os.path.getsize(result_path)
        logger.info(f"   文件大小: {file_size / 1024 / 1024:.2f} MB")

        return result_path

    except Exception as e:
        logger.error(f"❌ 3MF 转换失败: {e}")
        raise


async def connect_and_print(mf_path: str) -> None:
    """
    连接打印机并开始打印

    Args:
        mf_path: 3MF 文件路径
    """
    logger.info("步骤 4/5: 连接拓竹打印机")

    from infrastructure.printer.adapters.bambu_adapter import BambuAdapter
    from domain.value_objects.connection_config import ConnectionConfig

    # 创建适配器
    adapter = BambuAdapter()

    # 打印机连接配置
    config = ConnectionConfig(
        host="100.100.34.201",
        serial_number="0948DB551901061",
        access_code="5dac4f7a"
    )

    # 连接打印机
    logger.info(f"正在连接打印机: {config.host}")
    connected = await adapter.connect(config)

    if not connected:
        logger.error("❌ 无法连接到打印机")
        raise RuntimeError("打印机连接失败")

    logger.info("✅ 打印机连接成功")

    # 获取打印机状态
    status = await adapter.get_status()
    logger.info(f"   打印机状态: {status.value}")

    # 上传文件
    logger.info("步骤 5/5: 上传文件并开始打印")
    logger.info(f"正在上传文件: {mf_path}")

    upload_success = await adapter.send_file(mf_path)

    if not upload_success:
        logger.error("❌ 文件上传失败")
        await adapter.disconnect()
        raise RuntimeError("文件上传失败")

    logger.info("✅ 文件上传成功")

    # 开始打印
    filename = os.path.basename(mf_path)
    logger.info(f"正在开始打印: {filename}")

    print_success = await adapter.start_print(filename)

    if not print_success:
        logger.error("❌ 打印启动失败")
        await adapter.disconnect()
        raise RuntimeError("打印启动失败")

    logger.info("✅ 打印已开始!")

    # 监控打印进度 (前30秒)
    logger.info("\n监控打印进度 (30秒)...")
    for i in range(6):
        await asyncio.sleep(5)
        progress = await adapter.get_progress()
        logger.info(
            f"   进度: {progress.percentage}% | "
            f"层: {progress.layer_current}/{progress.layer_total} | "
            f"剩余时间: {progress.time_remaining}s"
        )

    # 断开连接
    await adapter.disconnect()
    logger.info("\n✅ 已断开打印机连接")


async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("端到端测试: 打印 3D 牛")
    logger.info("=" * 60)
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    try:
        # 1. 生成 STL 模型
        stl_path = create_cow_stl()
        logger.info("")

        # 2. 切片生成 G-code
        gcode_path = await slice_model(stl_path)
        logger.info("")

        # 3. 转换为 3MF 格式
        mf_path = convert_to_3mf(gcode_path)
        logger.info("")

        # 4-5. 连接打印机并打印
        await connect_and_print(mf_path)

        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ 测试完成! 3D 牛正在打印中...")
        logger.info("=" * 60)
        logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        logger.info("打印文件路径:")
        logger.info(f"  - STL: {stl_path}")
        logger.info(f"  - G-code: {gcode_path}")
        logger.info(f"  - 3MF: {mf_path}")

        return 0

    except Exception as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error(f"❌ 测试失败: {e}")
        logger.error("=" * 60)
        logger.exception("详细错误信息:")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
