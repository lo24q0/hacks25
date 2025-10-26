#!/usr/bin/env python3
"""
端到端测试脚本: 打印 3D 牛 (使用 Mock Slicer)

完整流程:
1. 生成 3D 牛模型 STL
2. 使用 MockSlicer 生成 G-code
3. 将 G-code 转换为拓竹 3MF 格式
4. 连接拓竹打印机
5. 上传并开始打印
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_cow_stl() -> str:
    """生成 3D 牛模型 STL 文件"""
    logger.info("=" * 60)
    logger.info("步骤 1/5: 生成 3D 牛模型 STL")
    logger.info("=" * 60)

    cow_stl_path = "/tmp/cow_model.stl"

    if os.path.exists(cow_stl_path):
        logger.info(f"✅ STL 文件已存在: {cow_stl_path}")
        file_size = os.path.getsize(cow_stl_path)
        logger.info(f"   文件大小: {file_size / 1024:.2f} KB")
    else:
        import subprocess
        result = subprocess.run([
            "python3",
            str(Path(__file__).parent / "create_simple_cow_stl.py")
        ], capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"✅ STL 文件生成完成: {cow_stl_path}")
        else:
            logger.error(f"❌ STL 生成失败: {result.stderr}")
            raise RuntimeError("STL 生成失败")

    return cow_stl_path


async def slice_model(stl_path: str) -> str:
    """使用 MockSlicer 切片模型"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤 2/5: 使用 MockSlicer 切片模型")
    logger.info("=" * 60)

    from domain.value_objects.printer_profile import PrinterProfile
    from domain.value_objects.slicing_config import SlicingConfig
    from infrastructure.slicing.mock_slicer import MockSlicer

    # 创建 Mock 切片器
    slicer = MockSlicer()
    logger.info("✅ MockSlicer 初始化成功")

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

    # 切片配置
    slicing_config = SlicingConfig(
        layer_height=0.2,
        infill_density=15,
        print_speed=300,
        support_enabled=False,
        adhesion_type="brim"
    )

    gcode_path = stl_path.replace('.stl', '.gcode')

    logger.info(f"切片配置:")
    logger.info(f"  - 层高: {slicing_config.layer_height}mm")
    logger.info(f"  - 填充: {slicing_config.infill_density}%")
    logger.info(f"  - 速度: {slicing_config.print_speed}mm/s")

    try:
        result = await slicer.slice_model(
            stl_path=stl_path,
            printer=printer,
            config=slicing_config,
            output_path=gcode_path
        )

        logger.info(f"✅ 切片完成:")
        logger.info(f"  - 层数: {result.layer_count}")
        logger.info(f"  - 预计时间: {result.estimated_time}")
        logger.info(f"  - 预计材料: {result.estimated_material:.2f}g")
        logger.info(f"  - G-code: {gcode_path}")

        return gcode_path

    except Exception as e:
        logger.error(f"❌ 切片失败: {e}")
        raise


def convert_to_3mf(gcode_path: str) -> str:
    """将 G-code 转换为拓竹 3MF 格式"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤 3/5: 转换 G-code 为拓竹 3MF 格式")
    logger.info("=" * 60)

    from shared.utils.gcode_to_3mf import convert_gcode_to_3mf

    mf_path = gcode_path.replace('.gcode', '.gcode.3mf')

    metadata = {
        "model_name": "3D_Cow",
        "layer_height": 0.2,
        "infill_density": 15,
        "print_speed": 300,
        "nozzle_temperature": 220,
        "bed_temperature": 55,
        "material_type": "PLA"
    }

    try:
        result_path = convert_gcode_to_3mf(
            gcode_path=gcode_path,
            output_path=mf_path,
            **metadata
        )

        logger.info(f"✅ 3MF 文件生成完成: {result_path}")
        file_size = os.path.getsize(result_path)
        logger.info(f"  - 文件大小: {file_size / 1024:.2f} KB")

        return result_path

    except Exception as e:
        logger.error(f"❌ 3MF 转换失败: {e}")
        raise


async def connect_and_print(mf_path: str) -> None:
    """连接打印机并开始打印"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤 4/5: 连接拓竹打印机")
    logger.info("=" * 60)

    from infrastructure.printer.adapters.bambu_adapter import BambuAdapter, BAMBULABS_API_AVAILABLE
    from domain.value_objects.connection_config import ConnectionConfig

    if not BAMBULABS_API_AVAILABLE:
        logger.error("❌ bambulabs_api 库未安装")
        logger.info("请运行: pip install bambulabs_api")
        raise ImportError("bambulabs_api 库未安装")

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
    logger.info(f"  - Serial: {config.serial_number}")
    logger.info(f"  - Access Code: {config.access_code[:4]}****")

    connected = await adapter.connect(config)

    if not connected:
        logger.error("❌ 无法连接到打印机")
        logger.info("请检查:")
        logger.info("  1. 打印机是否开机")
        logger.info("  2. 网络连接是否正常: ping 100.100.34.201")
        logger.info("  3. Access Code 是否正确")
        raise RuntimeError("打印机连接失败")

    logger.info("✅ 打印机连接成功")

    # 获取打印机状态
    status = await adapter.get_status()
    logger.info(f"  - 打印机状态: {status.value}")

    # 上传文件
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤 5/5: 上传文件并开始打印")
    logger.info("=" * 60)

    filename = os.path.basename(mf_path)
    logger.info(f"正在上传文件: {filename}")
    logger.info(f"  - 本地路径: {mf_path}")
    logger.info(f"  - 文件大小: {os.path.getsize(mf_path) / 1024:.2f} KB")

    upload_success = await adapter.send_file(mf_path)

    if not upload_success:
        logger.error("❌ 文件上传失败")
        await adapter.disconnect()
        raise RuntimeError("文件上传失败")

    logger.info("✅ 文件上传成功")

    # 开始打印
    logger.info(f"正在启动打印任务...")

    print_success = await adapter.start_print(filename)

    if not print_success:
        logger.error("❌ 打印启动失败")
        await adapter.disconnect()
        raise RuntimeError("打印启动失败")

    logger.info("✅ 打印已开始!")

    # 监控打印进度
    logger.info("")
    logger.info("监控打印进度 (前 30 秒)...")
    logger.info("-" * 60)

    for i in range(6):
        await asyncio.sleep(5)
        progress = await adapter.get_progress()
        logger.info(
            f"  [{i*5:2d}s] 进度: {progress.percentage:5.1f}% | "
            f"层: {progress.layer_current:3d}/{progress.layer_total:3d} | "
            f"剩余: {progress.time_remaining:5d}s"
        )

    # 断开连接
    logger.info("")
    await adapter.disconnect()
    logger.info("✅ 已断开打印机连接 (打印任务继续运行)")


async def main():
    """主函数"""
    start_time = datetime.now()

    print("")
    print("=" * 60)
    print("     端到端测试: 打印 3D 牛 🐄")
    print("=" * 60)
    print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    try:
        # 1. 生成 STL 模型
        stl_path = create_cow_stl()

        # 2. 切片生成 G-code
        gcode_path = await slice_model(stl_path)

        # 3. 转换为 3MF 格式
        mf_path = convert_to_3mf(gcode_path)

        # 4-5. 连接打印机并打印
        await connect_and_print(mf_path)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("")
        print("=" * 60)
        print("✅ 测试完成! 3D 牛正在打印中... 🎉")
        print("=" * 60)
        print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration:.1f} 秒")
        print("")
        print("生成的文件:")
        print(f"  📄 STL:   {stl_path}")
        print(f"  📄 G-code: {gcode_path}")
        print(f"  📦 3MF:   {mf_path}")
        print("")
        print("你可以在拓竹打印机屏幕上查看打印进度")
        print("=" * 60)
        print("")

        return 0

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("")
        print("=" * 60)
        print(f"❌ 测试失败")
        print("=" * 60)
        print(f"错误: {e}")
        print(f"耗时: {duration:.1f} 秒")
        print("=" * 60)
        logger.exception("详细错误信息:")
        print("")

        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
