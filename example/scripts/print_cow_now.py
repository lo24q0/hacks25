#!/usr/bin/env python3
"""
直接打印 3D 牛 - 自动化脚本

使用 box_prod.gcode.3mf 文件立即开始打印
"""

import asyncio
import logging
import os
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import bambulabs_api as bl
except ImportError:
    print("❌ bambulabs_api 库未安装")
    print("运行: pip3 install --user --break-system-packages bambulabs_api")
    sys.exit(1)


async def print_cow():
    """连接打印机并开始打印"""

    print("")
    print("=" * 70)
    print("   🐄  自动化打印 3D 牛")
    print("=" * 70)
    print("")

    # 打印机配置
    host = "100.100.34.201"
    serial = "0948DB551901061"
    access_code = "5dac4f7a"

    # 文件路径
    test_file = "/Users/songgl/work/codes/goCode/src/hacks25/box_prod.gcode.3mf"

    if not os.path.exists(test_file):
        logger.error(f"文件不存在: {test_file}")
        return False

    try:
        # 1. 连接打印机
        logger.info(f"📡 连接打印机: {host}")
        printer = bl.Printer(
            ip_address=host,
            access_code=access_code,
            serial=serial
        )

        printer.mqtt_start()
        await asyncio.sleep(3)

        if not printer.mqtt_client_connected():
            logger.error("❌ MQTT 连接失败")
            return False

        logger.info("✅ 打印机连接成功")
        print("")

        # 2. 获取状态
        state = printer.get_state()
        logger.info(f"🔍 打印机状态: {state}")

        if state.value != "IDLE" and state.value != "FINISH" and state.value != "FAILED":
            logger.warning(f"⚠️  打印机忙碌,当前状态: {state.value}")
            response = input("\n继续吗? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                printer.disconnect()
                return False

        print("")

        # 3. 上传文件
        filename = os.path.basename(test_file)
        file_size = os.path.getsize(test_file)

        logger.info(f"📤 上传文件: {filename} ({file_size / 1024:.1f} KB)")

        with open(test_file, 'rb') as f:
            try:
                upload_path = printer.upload_file(f, filename)
                logger.info(f"✅ 上传成功: {upload_path}")
            except Exception as e:
                error_msg = str(e)
                if "426" in error_msg:
                    logger.info("✅ 上传成功 (忽略 FTP 426 错误)")
                else:
                    logger.error(f"❌ 上传失败: {error_msg}")
                    printer.disconnect()
                    return False

        print("")

        # 4. 开始打印
        logger.info(f"🖨️  启动打印任务...")

        result = printer.start_print(
            filename=filename,
            plate_number=1,
            use_ams=False
        )

        if not result:
            logger.error("❌ 打印启动失败")
            printer.disconnect()
            return False

        logger.info("✅ 打印已开始!")
        print("")

        # 5. 监控进度
        logger.info("📊 监控打印进度 (前 60 秒)...")
        print("=" * 70)

        for i in range(12):
            await asyncio.sleep(5)

            try:
                percentage = printer.get_percentage()
                if percentage == "Unknown":
                    percentage = 0
                else:
                    percentage = float(percentage) if percentage else 0

                layer_current = printer.current_layer_num() or 0
                layer_total = printer.total_layer_num() or 0
                time_remaining = printer.get_time()

                if time_remaining == "Unknown":
                    time_remaining = "计算中..."

                print(
                    f"  [{(i+1)*5:3d}s] "
                    f"进度: {percentage:5.1f}% | "
                    f"层: {layer_current:3d}/{layer_total:3d} | "
                    f"剩余: {time_remaining}"
                )

            except Exception as e:
                logger.warning(f"读取进度失败: {e}")

        print("=" * 70)
        print("")

        # 6. 断开连接
        logger.info("🔌 断开连接 (打印继续运行)")
        printer.disconnect()

        print("")
        print("=" * 70)
        print("✅ 打印任务已启动!")
        print("=" * 70)
        print("")
        print("💡 提示:")
        print("   - 打印任务将继续在打印机上运行")
        print("   - 你可以在打印机屏幕上查看实时进度")
        print("   - 打印文件: " + filename)
        print("")

        return True

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        if 'printer' in locals():
            printer.disconnect()
        return False

    except Exception as e:
        logger.error(f"❌ 错误: {e}")
        logger.exception("详细错误信息:")
        if 'printer' in locals():
            printer.disconnect()
        return False


if __name__ == "__main__":
    print("\n⚠️  警告: 这将启动真实的打印任务!\n")

    response = input("确认开始打印? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ 已取消\n")
        sys.exit(0)

    success = asyncio.run(print_cow())
    sys.exit(0 if success else 1)
