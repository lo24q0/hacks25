import os
import json
import logging
from typing import Optional

from domain.interfaces.i_printer_adapter import IPrinterAdapter, PrintProgress
from domain.enums.print_enums import PrinterStatus
from domain.value_objects.connection_config import ConnectionConfig

logger = logging.getLogger(__name__)


class BambuAdapter(IPrinterAdapter):
    """
    拓竹(Bambu Lab)打印机适配器
    
    主要功能:
    - 状态监控(MQTT订阅)
    - 文件传输(FTP/MQTT)
    - 打印控制(通过MQTT发送命令)
    """

    def __init__(self):
        self._mqtt_client: Optional[any] = None
        self._ftp_client: Optional[any] = None
        self._current_status: PrinterStatus = PrinterStatus.OFFLINE
        self._current_progress: int = 0
        self._layer_current: int = 0
        self._layer_total: int = 0
        self._time_elapsed: int = 0
        self._time_remaining: int = 0
        self._serial_number: Optional[str] = None

    async def connect(self, config: ConnectionConfig) -> bool:
        """
        连接拓竹打印机
        
        实现步骤:
        1. 建立MQTT连接(监听状态)
        2. 建立FTP连接(传输文件)
        3. 订阅状态主题
        
        Args:
            config: 连接配置(包含IP、端口、access_code)
            
        Returns:
            bool: 连接是否成功
        """
        logger.info(f"Connecting to Bambu printer at {config.host}:{config.port}")
        
        try:
            self._serial_number = config.serial_number
            self._current_status = PrinterStatus.IDLE
            logger.info("Bambu adapter connected successfully (skeleton)")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Bambu printer: {e}")
            return False

    async def disconnect(self) -> None:
        """
        断开连接
        """
        logger.info("Disconnecting from Bambu printer")
        self._current_status = PrinterStatus.OFFLINE

    async def get_status(self) -> PrinterStatus:
        """
        获取打印机状态
        
        状态来源于MQTT订阅的消息
        
        Returns:
            PrinterStatus: 当前状态
        """
        return self._current_status

    async def send_file(self, file_path: str) -> bool:
        """
        发送.gcode.3mf文件到打印机
        
        实现步骤:
        1. 转换G-code为3MF格式(拓竹要求)
        2. 通过FTP上传文件
        3. 验证上传成功
        
        Args:
            file_path: 本地文件路径
            
        Returns:
            bool: 上传是否成功
        """
        logger.info(f"Sending file to Bambu printer: {file_path}")
        
        try:
            if not file_path.endswith(".gcode.3mf"):
                file_path = self._convert_to_3mf(file_path)
            
            logger.info(f"File sent successfully (skeleton): {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False

    async def start_print(self, file_name: str) -> bool:
        """
        通过MQTT发送打印指令
        
        Args:
            file_name: 文件名
            
        Returns:
            bool: 指令发送是否成功
        """
        logger.info(f"Starting print on Bambu printer: {file_name}")
        
        try:
            command = {
                "print": {
                    "command": "project_file",
                    "param": "Metadata/plate_1.gcode",
                    "file": file_name
                }
            }
            logger.info(f"Print command sent (skeleton): {json.dumps(command)}")
            self._current_status = PrinterStatus.BUSY
            return True
        except Exception as e:
            logger.error(f"Failed to start print: {e}")
            return False

    async def pause_print(self) -> bool:
        """
        暂停打印
        
        Returns:
            bool: 暂停是否成功
        """
        logger.info("Pausing print on Bambu printer")
        try:
            self._current_status = PrinterStatus.PAUSED
            return True
        except Exception as e:
            logger.error(f"Failed to pause print: {e}")
            return False

    async def resume_print(self) -> bool:
        """
        恢复打印
        
        Returns:
            bool: 恢复是否成功
        """
        logger.info("Resuming print on Bambu printer")
        try:
            self._current_status = PrinterStatus.BUSY
            return True
        except Exception as e:
            logger.error(f"Failed to resume print: {e}")
            return False

    async def cancel_print(self) -> bool:
        """
        取消打印
        
        Returns:
            bool: 取消是否成功
        """
        logger.info("Cancelling print on Bambu printer")
        try:
            self._current_status = PrinterStatus.IDLE
            self._current_progress = 0
            return True
        except Exception as e:
            logger.error(f"Failed to cancel print: {e}")
            return False

    async def get_progress(self) -> PrintProgress:
        """
        获取打印进度
        
        Returns:
            PrintProgress: 进度信息
        """
        return PrintProgress(
            percentage=self._current_progress,
            layer_current=self._layer_current,
            layer_total=self._layer_total,
            time_elapsed=self._time_elapsed,
            time_remaining=self._time_remaining
        )

    def _on_message(self, client, userdata, msg):
        """
        MQTT消息回调
        
        解析拓竹打印机的状态报告并更新内部状态
        """
        try:
            data = json.loads(msg.payload)
            
            self._current_progress = data.get("print", {}).get("mc_percent", 0)
            
            status_code = data.get("print", {}).get("gcode_state", "")
            self._current_status = self._map_status(status_code)
            
            self._layer_current = data.get("print", {}).get("layer_num", 0)
            self._layer_total = data.get("print", {}).get("total_layer_num", 0)
        except Exception as e:
            logger.error(f"Failed to parse MQTT message: {e}")

    def _map_status(self, status_code: str) -> PrinterStatus:
        """
        映射拓竹状态码到通用状态
        
        Args:
            status_code: 拓竹状态码
            
        Returns:
            PrinterStatus: 通用状态
        """
        mapping = {
            "IDLE": PrinterStatus.IDLE,
            "RUNNING": PrinterStatus.BUSY,
            "PAUSE": PrinterStatus.PAUSED,
            "FINISH": PrinterStatus.IDLE,
            "FAILED": PrinterStatus.ERROR,
        }
        return mapping.get(status_code, PrinterStatus.OFFLINE)

    def _convert_to_3mf(self, gcode_path: str) -> str:
        """
        转换G-code为拓竹3MF格式
        
        拓竹打印机要求使用.gcode.3mf格式
        
        Args:
            gcode_path: G-code文件路径
            
        Returns:
            str: 转换后的文件路径
        """
        logger.info(f"Converting G-code to 3MF format: {gcode_path}")
        return gcode_path
