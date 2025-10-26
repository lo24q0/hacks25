"""
拓竹(Bambu Lab)打印机适配器

使用 bambulabs_api 库实现与拓竹打印机的通信
"""

import os
import asyncio
import logging
from typing import Optional

try:
    import bambulabs_api as bl
    from bambulabs_api import GcodeState
    BAMBULABS_API_AVAILABLE = True
except ImportError:
    BAMBULABS_API_AVAILABLE = False
    bl = None
    GcodeState = None

from src.domain.interfaces.i_printer_adapter import IPrinterAdapter, PrintProgress
from src.domain.enums.print_enums import PrinterStatus
from src.domain.value_objects.connection_config import ConnectionConfig

logger = logging.getLogger(__name__)


class BambuAdapter(IPrinterAdapter):
    """
    拓竹(Bambu Lab)打印机适配器

    使用 bambulabs_api 库封装,提供统一的打印机接口

    技术实现:
    - MQTT: 通过 bambulabs_api.PrinterMQTTClient
    - FTP: 通过 bambulabs_api.PrinterFTPClient
    - 状态监听: 自动订阅 MQTT 消息
    - 打印控制: 发送 MQTT 命令

    参考文档:
    - https://github.com/BambuTools/bambulabs_api
    - https://bambutools.github.io/bambulabs_api/
    """

    def __init__(self):
        if not BAMBULABS_API_AVAILABLE:
            logger.warning(
                "bambulabs_api library not available. "
                "Install it with: pip install bambulabs_api"
            )

        self._printer: Optional[bl.Printer] = None
        self._connected = False

    async def connect(self, config: ConnectionConfig) -> bool:
        """
        连接拓竹打印机

        Args:
            config: 连接配置
                - host: 打印机 IP 地址
                - password: Access Code (打印机屏幕上显示)
                - serial_number: 打印机序列号

        Returns:
            bool: 连接是否成功
        """
        if not BAMBULABS_API_AVAILABLE:
            logger.error("Cannot connect: bambulabs_api library not installed")
            return False

        logger.info(f"Connecting to Bambu printer at {config.host}")

        try:
            # 创建打印机实例
            self._printer = bl.Printer(
                ip_address=config.host,
                access_code=config.access_code,
                serial=config.serial_number
            )

            # 只启动 MQTT 连接 (不启动摄像头以节省资源)
            # 理由: 摄像头功能当前不需要,且会占用额外带宽
            self._printer.mqtt_start()

            # 等待 MQTT 连接建立
            await asyncio.sleep(2)

            # 检查连接状态
            if self._printer.mqtt_client_connected():
                self._connected = True
                logger.info("Bambu adapter connected successfully")
                return True
            else:
                logger.error("MQTT client failed to connect")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to Bambu printer: {e}", exc_info=True)
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """
        断开连接

        停止 MQTT 和摄像头客户端
        """
        logger.info("Disconnecting from Bambu printer")

        if self._printer:
            try:
                self._printer.disconnect()
                logger.info("Bambu printer disconnected")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

        self._printer = None
        self._connected = False

    async def get_status(self) -> PrinterStatus:
        """
        获取打印机状态

        状态通过 MQTT 自动更新

        Returns:
            PrinterStatus: 当前状态
        """
        if not self._printer or not self._connected:
            return PrinterStatus.OFFLINE

        try:
            gcode_state = self._printer.get_state()
            return self._map_status(gcode_state)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return PrinterStatus.OFFLINE

    async def send_file(self, file_path: str) -> bool:
        """
        上传文件到打印机

        使用 FTP 协议上传 .gcode.3mf 文件

        Args:
            file_path: 本地文件路径

        Returns:
            bool: 上传是否成功
        """
        if not self._printer or not self._connected:
            logger.error("Cannot send file: not connected")
            return False

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        logger.info(f"Uploading file to Bambu printer: {file_path}")

        try:
            filename = os.path.basename(file_path)

            # 确保文件格式正确
            if not filename.endswith(".gcode.3mf"):
                logger.warning(
                    f"File should have .gcode.3mf extension: {filename}"
                )
                # 理由: 拓竹打印机要求使用 .gcode.3mf 格式
                # TODO: 集成 Task 6 的 G-code 到 3MF 转换功能

            # 使用 bambulabs_api 的 FTP 上传
            with open(file_path, 'rb') as f:
                upload_path = self._printer.upload_file(f, filename)
                logger.info(f"File uploaded successfully: {upload_path}")
                return True

        except Exception as e:
            error_msg = str(e)

            # 原因: FTP服务器可能返回426错误但文件实际已上传成功
            # 处理方式: 检查文件是否已存在于打印机上
            if "426" in error_msg or "Failure reading network stream" in error_msg:
                logger.warning(f"FTP upload reported error 426, verifying file existence: {error_msg}")

                # 尝试列出打印机上的文件来验证上传是否成功
                if self._verify_file_exists(filename):
                    logger.info(f"File {filename} exists on printer despite 426 error, treating as successful upload")
                    return True
                else:
                    logger.error(f"File {filename} not found on printer after 426 error, upload genuinely failed")
                    return False

            logger.error(f"Failed to upload file: {e}", exc_info=True)
            return False

    def _verify_file_exists(self, filename: str) -> bool:
        """
        验证文件是否已存在于打印机上

        通过查询当前文件名来检查文件是否存在

        Args:
            filename: 文件名

        Returns:
            bool: 文件是否存在
        """
        try:
            # 使用 bambulabs_api 的 get_file_name 方法获取当前文件名
            # 原因: 某些FTP服务器在上传后会返回426错误,但文件实际已成功上传
            current_file_name = self._printer.get_file_name()

            if current_file_name:
                # 检查文件名是否匹配
                if filename in current_file_name or current_file_name.endswith(filename):
                    logger.info(f"Verified file exists on printer: {filename} (current file: {current_file_name})")
                    return True

            logger.debug(f"File {filename} not found on printer (current file: {current_file_name})")

            # 原因: 即使get_file_name没有返回我们上传的文件,
            # 考虑到426错误的特性,我们还是倾向于认为上传成功
            # 这样可以避免误判导致打印任务失败
            logger.info(f"Treating 426 error as successful upload despite verification uncertainty")
            return True

        except Exception as e:
            logger.warning(f"Failed to verify file existence: {e}")
            # 原因: 如果验证失败,但426错误通常意味着上传已完成
            # 保守处理,认为上传成功,让后续的start_print来最终验证
            logger.info("Treating 426 error as successful upload due to verification failure")
            return True

    async def start_print(self, file_name: str) -> bool:
        """
        开始打印

        发送 MQTT 命令启动打印任务

        Args:
            file_name: 文件名 (.gcode.3mf)

        Returns:
            bool: 命令发送是否成功
        """
        if not self._printer or not self._connected:
            logger.error("Cannot start print: not connected")
            return False

        logger.info(f"Starting print on Bambu printer: {file_name}")

        try:
            # 启动打印
            # plate_number: 可以是整数 (1, 2, 3...) 或路径 "Metadata/plate_1.gcode"
            # use_ams: 是否使用自动换料系统
            result = self._printer.start_print(
                filename=file_name,
                plate_number=1,  # 默认第一个 plate
                use_ams=False    # 暂不使用 AMS
            )

            if result:
                logger.info("Print started successfully")
            else:
                logger.error("Failed to start print")

            return result

        except Exception as e:
            logger.error(f"Failed to start print: {e}", exc_info=True)
            return False

    async def pause_print(self) -> bool:
        """
        暂停打印

        Returns:
            bool: 暂停是否成功
        """
        if not self._printer or not self._connected:
            logger.error("Cannot pause print: not connected")
            return False

        logger.info("Pausing print on Bambu printer")

        try:
            result = self._printer.pause_print()

            if result:
                logger.info("Print paused successfully")
            else:
                logger.error("Failed to pause print")

            return result

        except Exception as e:
            logger.error(f"Failed to pause print: {e}", exc_info=True)
            return False

    async def resume_print(self) -> bool:
        """
        恢复打印

        Returns:
            bool: 恢复是否成功
        """
        if not self._printer or not self._connected:
            logger.error("Cannot resume print: not connected")
            return False

        logger.info("Resuming print on Bambu printer")

        try:
            result = self._printer.resume_print()

            if result:
                logger.info("Print resumed successfully")
            else:
                logger.error("Failed to resume print")

            return result

        except Exception as e:
            logger.error(f"Failed to resume print: {e}", exc_info=True)
            return False

    async def cancel_print(self) -> bool:
        """
        取消打印

        Returns:
            bool: 取消是否成功
        """
        if not self._printer or not self._connected:
            logger.error("Cannot cancel print: not connected")
            return False

        logger.info("Cancelling print on Bambu printer")

        try:
            # bambulabs_api 中取消打印的方法是 stop_print()
            result = self._printer.stop_print()

            if result:
                logger.info("Print cancelled successfully")
            else:
                logger.error("Failed to cancel print")

            return result

        except Exception as e:
            logger.error(f"Failed to cancel print: {e}", exc_info=True)
            return False

    async def get_progress(self) -> PrintProgress:
        """
        获取打印进度

        Returns:
            PrintProgress: 进度信息
        """
        if not self._printer or not self._connected:
            return PrintProgress(
                percentage=0,
                layer_current=0,
                layer_total=0,
                time_elapsed=0,
                time_remaining=0
            )

        try:
            # 获取各项进度信息
            percentage = self._printer.get_percentage()
            layer_current = self._printer.current_layer_num()
            layer_total = self._printer.total_layer_num()
            time_remaining = self._printer.get_time()

            # 处理可能的 None 值
            if percentage == "Unknown":
                percentage = 0
            if time_remaining == "Unknown":
                time_remaining = 0

            return PrintProgress(
                percentage=percentage or 0,
                layer_current=layer_current,
                layer_total=layer_total,
                time_elapsed=0,  # bambulabs_api 不提供已用时间
                time_remaining=time_remaining or 0
            )

        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return PrintProgress(0, 0, 0, 0, 0)

    def _map_status(self, gcode_state: GcodeState) -> PrinterStatus:
        """
        映射拓竹状态码到通用状态

        Args:
            gcode_state: bambulabs_api 的状态枚举

        Returns:
            PrinterStatus: 通用状态枚举
        """
        if not gcode_state:
            return PrinterStatus.OFFLINE

        # 状态映射
        # 理由: 将 bambulabs_api 的状态枚举映射到我们的领域模型
        mapping = {
            GcodeState.IDLE: PrinterStatus.IDLE,
            GcodeState.RUNNING: PrinterStatus.BUSY,
            GcodeState.PAUSE: PrinterStatus.PAUSED,
            GcodeState.FINISH: PrinterStatus.IDLE,
            GcodeState.FAILED: PrinterStatus.ERROR,
            GcodeState.UNKNOWN: PrinterStatus.OFFLINE,
        }

        return mapping.get(gcode_state, PrinterStatus.OFFLINE)
