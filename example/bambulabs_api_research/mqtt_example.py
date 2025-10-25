"""
Bambu Lab 打印机 MQTT 通信示例

演示如何使用 paho-mqtt 库连接到拓竹打印机并监听状态
"""

import json
import ssl
import paho.mqtt.client as mqtt
from typing import Optional, Callable


class BambuMQTTClient:
    """
    Bambu Lab 打印机 MQTT 客户端

    功能:
    - 连接到打印机
    - 订阅状态报告
    - 发送控制命令
    """

    def __init__(
        self,
        host: str,
        serial_number: str,
        access_code: str,
        on_status_update: Optional[Callable] = None
    ):
        """
        初始化 MQTT 客户端

        Args:
            host: 打印机 IP 地址
            serial_number: 打印机序列号
            access_code: 访问码
            on_status_update: 状态更新回调函数
        """
        self.host = host
        self.serial_number = serial_number
        self.access_code = access_code
        self.on_status_update = on_status_update

        # MQTT 配置
        self.port = 8883
        self.username = "bblp"

        # 主题
        self.report_topic = f"device/{serial_number}/report"
        self.request_topic = f"device/{serial_number}/request"

        # 创建客户端
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.access_code)

        # 配置 TLS (拓竹使用自签名证书)
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)

        # 设置回调
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        self.connected = False

    def connect(self) -> bool:
        """
        连接到打印机

        Returns:
            bool: 连接是否成功
        """
        try:
            print(f"Connecting to Bambu printer at {self.host}:{self.port}")
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()  # 启动后台线程处理网络流量
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        print("Disconnected from printer")

    def send_command(self, command: dict) -> bool:
        """
        发送控制命令

        Args:
            command: 命令字典

        Returns:
            bool: 发送是否成功
        """
        try:
            payload = json.dumps(command)
            result = self.client.publish(self.request_topic, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Command sent successfully: {command}")
                return True
            else:
                print(f"Failed to send command: {result.rc}")
                return False
        except Exception as e:
            print(f"Error sending command: {e}")
            return False

    def start_print(self, file_name: str) -> bool:
        """
        开始打印

        Args:
            file_name: .gcode.3mf 文件名

        Returns:
            bool: 命令发送是否成功
        """
        command = {
            "print": {
                "command": "project_file",
                "param": "Metadata/plate_1.gcode",
                "file": file_name,
                "bed_type": "auto",
                "use_ams": False
            }
        }
        return self.send_command(command)

    def pause_print(self) -> bool:
        """暂停打印"""
        command = {"print": {"command": "pause"}}
        return self.send_command(command)

    def resume_print(self) -> bool:
        """恢复打印"""
        command = {"print": {"command": "resume"}}
        return self.send_command(command)

    def stop_print(self) -> bool:
        """停止打印"""
        command = {"print": {"command": "stop"}}
        return self.send_command(command)

    def _on_connect(self, client, userdata, flags, rc):
        """
        连接成功回调

        Args:
            rc: 返回码 (0 = 成功)
        """
        if rc == 0:
            print("Connected to Bambu printer MQTT broker")
            self.connected = True

            # 订阅状态报告主题
            client.subscribe(self.report_topic)
            print(f"Subscribed to {self.report_topic}")
        else:
            print(f"Connection failed with code {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        print(f"Disconnected from printer (code: {rc})")
        self.connected = False

    def _on_message(self, client, userdata, msg):
        """
        接收到消息回调

        Args:
            msg: MQTT 消息对象
        """
        try:
            # 解析 JSON 消息
            data = json.loads(msg.payload.decode('utf-8'))

            # 提取打印状态信息
            if "print" in data:
                print_data = data["print"]

                status_info = {
                    "gcode_state": print_data.get("gcode_state"),
                    "progress": print_data.get("mc_percent", 0),
                    "layer_current": print_data.get("layer_num", 0),
                    "layer_total": print_data.get("total_layer_num", 0),
                    "time_remaining": print_data.get("mc_remaining_time", 0),
                    "nozzle_temp": print_data.get("nozzle_temper", 0),
                    "bed_temp": print_data.get("bed_temper", 0),
                    "file_name": print_data.get("subtask_name", "")
                }

                print(f"Status update: {status_info}")

                # 调用状态更新回调
                if self.on_status_update:
                    self.on_status_update(status_info)

        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")


# 使用示例
if __name__ == "__main__":
    def status_callback(status):
        """状态更新回调函数"""
        print(f"Printer status changed: {status}")

    # 创建客户端
    client = BambuMQTTClient(
        host="192.168.1.100",  # 替换为实际 IP
        serial_number="00M00A123456789",  # 替换为实际序列号
        access_code="12345678",  # 替换为实际访问码
        on_status_update=status_callback
    )

    # 连接
    if client.connect():
        try:
            # 保持连接,监听状态
            import time
            print("Listening for status updates... (Press Ctrl+C to exit)")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            client.disconnect()
