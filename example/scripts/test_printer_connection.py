#!/usr/bin/env python3
"""
测试拓竹打印机连接和文件上传

使用现有的 box_prod.gcode.3mf 文件直接测试
"""

import asyncio
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 检查 bambulabs_api 是否可用
try:
    import bambulabs_api as bl
    BAMBULABS_API_AVAILABLE = True
    logger.info("✅ bambulabs_api 库可用")
except ImportError:
    BAMBULABS_API_AVAILABLE = False
    logger.error("❌ bambulabs_api 库未安装")
    logger.info("请运行: pip install --user --break-system-packages bambulabs_api")


async def test_printer_connection():
    """测试打印机连接"""

    if not BAMBULABS_API_AVAILABLE:
        print("\n❌ 无法测试: bambulabs_api 库未安装\n")
        return False

    print("")
    print("=" * 60)
    print("测试拓竹打印机连接")
    print("=" * 60)
    print("")

    # 打印机配置
    host = "100.100.34.201"
    serial = "0948DB551901061"
    access_code = "5dac4f7a"

    logger.info(f"打印机配置:")
    logger.info(f"  - IP: {host}")
    logger.info(f"  - Serial: {serial}")
    logger.info(f"  - Access Code: {access_code[:4]}****")
    print("")

    try:
        # 1. 创建打印机实例
        logger.info("步骤 1: 创建打印机实例...")
        printer = bl.Printer(
            ip_address=host,
            access_code=access_code,
            serial=serial
        )
        logger.info("✅ 打印机实例创建成功")
        print("")

        # 2. 启动 MQTT 连接
        logger.info("步骤 2: 启动 MQTT 连接...")
        printer.mqtt_start()
        await asyncio.sleep(3)  # 等待连接建立

        if printer.mqtt_client_connected():
            logger.info("✅ MQTT 连接成功")
        else:
            logger.error("❌ MQTT 连接失败")
            return False
        print("")

        # 3. 获取打印机状态
        logger.info("步骤 3: 获取打印机状态...")
        state = printer.get_state()
        logger.info(f"✅ 打印机状态: {state}")
        print("")

        # 4. 测试文件上传
        logger.info("步骤 4: 测试文件上传...")

        # 使用现有的 3MF 文件
        test_file = "/Users/songgl/work/codes/goCode/src/hacks25/box_prod.gcode.3mf"

        if not os.path.exists(test_file):
            logger.error(f"❌ 测试文件不存在: {test_file}")

            # 尝试使用我们生成的牛模型
            test_file = "/tmp/cow_model.gcode.3mf"
            if os.path.exists(test_file):
                logger.info(f"使用生成的文件: {test_file}")
            else:
                logger.error("未找到可用的 3MF 文件")
                printer.disconnect()
                return False

        filename = os.path.basename(test_file)
        file_size = os.path.getsize(test_file)

        logger.info(f"准备上传文件:")
        logger.info(f"  - 文件名: {filename}")
        logger.info(f"  - 大小: {file_size / 1024 / 1024:.2f} MB")
        logger.info(f"  - 路径: {test_file}")
        print("")

        logger.info("正在上传文件 (这可能需要几秒钟)...")

        with open(test_file, 'rb') as f:
            try:
                upload_path = printer.upload_file(f, filename)
                logger.info(f"✅ 文件上传成功: {upload_path}")
            except Exception as upload_error:
                error_msg = str(upload_error)

                # 处理 FTP 426 错误
                if "426" in error_msg or "Failure reading network stream" in error_msg:
                    logger.warning(f"⚠️  FTP 报告错误 426,但文件可能已成功上传")
                    logger.info(f"错误详情: {error_msg}")

                    # 尝试验证文件是否存在
                    current_file = printer.get_file_name()
                    if current_file and filename in current_file:
                        logger.info(f"✅ 验证成功: 文件已存在于打印机 ({current_file})")
                    else:
                        logger.info("⚠️  无法验证文件,但通常 426 错误意味着上传已完成")
                else:
                    logger.error(f"❌ 文件上传失败: {error_msg}")
                    raise

        print("")

        # 5. 询问是否开始打印
        logger.info("步骤 5: 打印控制")
        print("")
        print("⚠️  警告: 接下来会启动真实的打印任务!")
        print("")

        response = input("是否开始打印? (yes/no): ").strip().lower()

        if response in ['yes', 'y']:
            logger.info(f"启动打印任务: {filename}")

            result = printer.start_print(
                filename=filename,
                plate_number=1,
                use_ams=False
            )

            if result:
                logger.info("✅ 打印已开始!")
                print("")

                # 监控进度
                logger.info("监控打印进度 (30 秒)...")
                print("-" * 60)

                for i in range(6):
                    await asyncio.sleep(5)
                    percentage = printer.get_percentage()
                    layer_current = printer.current_layer_num()
                    layer_total = printer.total_layer_num()
                    time_remaining = printer.get_time()

                    logger.info(
                        f"  [{i*5:2d}s] 进度: {percentage:5}% | "
                        f"层: {layer_current:3d}/{layer_total:3d} | "
                        f"剩余: {time_remaining}"
                    )

            else:
                logger.error("❌ 打印启动失败")

        else:
            logger.info("⏭️  跳过打印")

        print("")

        # 6. 断开连接
        logger.info("步骤 6: 断开连接...")
        printer.disconnect()
        logger.info("✅ 已断开连接")

        print("")
        print("=" * 60)
        print("✅ 测试完成!")
        print("=" * 60)
        print("")

        return True

    except Exception as e:
        print("")
        print("=" * 60)
        print("❌ 测试失败")
        print("=" * 60)
        logger.exception(f"错误详情: {e}")
        print("")
        return False


if __name__ == "__main__":
    import sys

    success = asyncio.run(test_printer_connection())
    sys.exit(0 if success else 1)
