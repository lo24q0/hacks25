"""
BambuAdapter 集成测试

测试使用 bambulabs_api 库的 BambuAdapter 实现

注意: 真机测试需要实际的拓竹打印机
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, MagicMock

from infrastructure.printer.adapters.bambu_adapter import BambuAdapter, BAMBULABS_API_AVAILABLE
from domain.value_objects.connection_config import ConnectionConfig
from domain.enums.print_enums import PrinterStatus


@pytest.mark.skipif(
    not BAMBULABS_API_AVAILABLE,
    reason="bambulabs_api library not installed"
)
class TestBambuAdapterWithLibrary:
    """
    使用 bambulabs_api 库的 BambuAdapter 测试

    使用 Mock 对象测试适配器逻辑
    """

    def setup_method(self):
        """测试初始化"""
        self.adapter = BambuAdapter()
        self.config = ConnectionConfig(
            host="192.168.1.100",
            port=8883,
            password="12345678",  # access_code
            serial_number="00M00A123456789"
        )

    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化状态"""
        assert self.adapter._printer is None
        assert self.adapter._connected is False

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_connect_success(self, mock_printer_class):
        """测试连接成功"""
        # Mock Printer 实例
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer_class.return_value = mock_printer

        # 执行连接
        result = await self.adapter.connect(self.config)

        # 验证结果
        assert result is True
        assert self.adapter._connected is True

        # 验证 Printer 实例化参数
        mock_printer_class.assert_called_once_with(
            ip_address="192.168.1.100",
            access_code="12345678",
            serial="00M00A123456789"
        )

        # 验证调用了 mqtt_start
        mock_printer.mqtt_start.assert_called_once()

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_connect_failure(self, mock_printer_class):
        """测试连接失败"""
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = False
        mock_printer_class.return_value = mock_printer

        result = await self.adapter.connect(self.config)

        assert result is False
        assert self.adapter._connected is False

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_disconnect(self, mock_printer_class):
        """测试断开连接"""
        # 先连接
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer_class.return_value = mock_printer

        await self.adapter.connect(self.config)

        # 执行断开
        await self.adapter.disconnect()

        # 验证
        mock_printer.disconnect.assert_called_once()
        assert self.adapter._printer is None
        assert self.adapter._connected is False

    @pytest.mark.asyncio
    async def test_get_status_not_connected(self):
        """测试未连接时获取状态"""
        status = await self.adapter.get_status()
        assert status == PrinterStatus.OFFLINE

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    @patch('bambulabs_api.GcodeState')
    async def test_get_status_connected(self, mock_gcode_state, mock_printer_class):
        """测试已连接时获取状态"""
        # Mock
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer.get_state.return_value = mock_gcode_state.RUNNING
        mock_printer_class.return_value = mock_printer

        # 添加状态枚举
        mock_gcode_state.RUNNING = "RUNNING"

        await self.adapter.connect(self.config)

        # 由于 _map_status 需要真实的 GcodeState,我们 mock 它
        with patch.object(self.adapter, '_map_status', return_value=PrinterStatus.BUSY):
            status = await self.adapter.get_status()
            assert status == PrinterStatus.BUSY

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_send_file(self, mock_printer_class):
        """测试文件上传"""
        # 创建临时测试文件
        test_file = "/tmp/test_bambu_model.gcode.3mf"
        with open(test_file, 'wb') as f:
            f.write(b'test content')

        try:
            # Mock
            mock_printer = Mock()
            mock_printer.mqtt_client_connected.return_value = True
            mock_printer.upload_file.return_value = "/path/on/printer/test_bambu_model.gcode.3mf"
            mock_printer_class.return_value = mock_printer

            await self.adapter.connect(self.config)

            # 执行上传
            result = await self.adapter.send_file(test_file)

            # 验证
            assert result is True
            mock_printer.upload_file.assert_called_once()

        finally:
            # 清理
            if os.path.exists(test_file):
                os.remove(test_file)

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_start_print(self, mock_printer_class):
        """测试开始打印"""
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer.start_print.return_value = True
        mock_printer_class.return_value = mock_printer

        await self.adapter.connect(self.config)

        result = await self.adapter.start_print("test.gcode.3mf")

        assert result is True
        mock_printer.start_print.assert_called_once_with(
            filename="test.gcode.3mf",
            plate_number=1,
            use_ams=False
        )

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_pause_print(self, mock_printer_class):
        """测试暂停打印"""
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer.pause_print.return_value = True
        mock_printer_class.return_value = mock_printer

        await self.adapter.connect(self.config)
        result = await self.adapter.pause_print()

        assert result is True
        mock_printer.pause_print.assert_called_once()

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_resume_print(self, mock_printer_class):
        """测试恢复打印"""
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer.resume_print.return_value = True
        mock_printer_class.return_value = mock_printer

        await self.adapter.connect(self.config)
        result = await self.adapter.resume_print()

        assert result is True
        mock_printer.resume_print.assert_called_once()

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_cancel_print(self, mock_printer_class):
        """测试取消打印"""
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer.stop_print.return_value = True
        mock_printer_class.return_value = mock_printer

        await self.adapter.connect(self.config)
        result = await self.adapter.cancel_print()

        assert result is True
        mock_printer.stop_print.assert_called_once()

    @pytest.mark.asyncio
    @patch('bambulabs_api.Printer')
    async def test_get_progress(self, mock_printer_class):
        """测试获取进度"""
        mock_printer = Mock()
        mock_printer.mqtt_client_connected.return_value = True
        mock_printer.get_percentage.return_value = 50
        mock_printer.current_layer_num.return_value = 120
        mock_printer.total_layer_num.return_value = 250
        mock_printer.get_time.return_value = 3600
        mock_printer_class.return_value = mock_printer

        await self.adapter.connect(self.config)
        progress = await self.adapter.get_progress()

        assert progress.percentage == 50
        assert progress.layer_current == 120
        assert progress.layer_total == 250
        assert progress.time_remaining == 3600


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("BAMBU_PRINTER_IP"),
    reason="需要真实打印机才能运行集成测试,设置 BAMBU_PRINTER_IP 环境变量"
)
@pytest.mark.skipif(
    not BAMBULABS_API_AVAILABLE,
    reason="bambulabs_api library not installed"
)
class TestBambuAdapterIntegration:
    """
    BambuAdapter 真机集成测试

    运行条件:
    - 设置环境变量 BAMBU_PRINTER_IP
    - 设置环境变量 BAMBU_ACCESS_CODE
    - 设置环境变量 BAMBU_SERIAL_NUMBER
    - 确保打印机在线且可访问
    - 安装 bambulabs_api 库

    运行示例:
    export BAMBU_PRINTER_IP=192.168.1.100
    export BAMBU_ACCESS_CODE=12345678
    export BAMBU_SERIAL_NUMBER=00M00A123456789
    pytest tests/integration/test_bambu_adapter.py::TestBambuAdapterIntegration -v -m integration
    """

    def setup_method(self):
        """测试初始化"""
        self.adapter = BambuAdapter()
        self.config = ConnectionConfig(
            host=os.getenv("BAMBU_PRINTER_IP"),
            port=8883,
            password=os.getenv("BAMBU_ACCESS_CODE"),
            serial_number=os.getenv("BAMBU_SERIAL_NUMBER")
        )

    @pytest.mark.asyncio
    async def test_real_connection(self):
        """测试真实连接"""
        result = await self.adapter.connect(self.config)
        assert result is True

        # 等待连接稳定
        await asyncio.sleep(3)

        # 检查状态
        status = await self.adapter.get_status()
        assert status in [PrinterStatus.IDLE, PrinterStatus.BUSY, PrinterStatus.PAUSED]

        # 断开连接
        await self.adapter.disconnect()
        await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_get_real_status_and_progress(self):
        """测试获取真实状态和进度"""
        await self.adapter.connect(self.config)
        await asyncio.sleep(3)

        # 获取状态
        status = await self.adapter.get_status()
        progress = await self.adapter.get_progress()

        print(f"\nPrinter status: {status}")
        print(f"Progress: {progress.percentage}%")
        print(f"Layer: {progress.layer_current}/{progress.layer_total}")
        print(f"Time remaining: {progress.time_remaining}s")

        assert status in [PrinterStatus.IDLE, PrinterStatus.BUSY, PrinterStatus.PAUSED]
        assert 0 <= progress.percentage <= 100

        await self.adapter.disconnect()
