import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.models.printer import Printer
from src.domain.enums.print_enums import PrinterStatus, AdapterType
from src.domain.value_objects.printer_profile import PrinterProfile
from src.domain.value_objects.connection_config import ConnectionConfig, ConnectionType
from src.shared.exceptions.domain_exceptions import PrinterBusyError


class TestPrinter:
    """
    打印机领域模型测试
    """

    @pytest.fixture
    def printer_profile(self) -> PrinterProfile:
        """
        创建打印机配置fixture
        
        Returns:
            PrinterProfile: 测试用打印机配置
        """
        return PrinterProfile(
            bed_size=(256, 256, 256),
            nozzle_diameter=0.4,
            filament_diameter=1.75,
            max_print_speed=500,
            max_travel_speed=600,
            firmware_flavor="bambu",
            supported_formats=[".gcode.3mf"]
        )

    @pytest.fixture
    def connection_config(self) -> ConnectionConfig:
        """
        创建连接配置fixture
        
        Returns:
            ConnectionConfig: 测试用连接配置
        """
        return ConnectionConfig(
            connection_type=ConnectionType.NETWORK,
            host="192.168.1.100",
            port=8883,
            access_code="12345678",
            serial_number="TEST123456",
            use_ssl=True
        )

    @pytest.fixture
    def printer(self, printer_profile, connection_config) -> Printer:
        """
        创建打印机fixture
        
        Args:
            printer_profile: 打印机配置
            connection_config: 连接配置
            
        Returns:
            Printer: 测试用打印机
        """
        return Printer(
            id="test_printer_01",
            name="Test Printer",
            model="Bambu H2D",
            adapter_type=AdapterType.BAMBU,
            connection_config=connection_config,
            profile=printer_profile
        )

    def test_create_printer(self, printer, printer_profile):
        """
        测试创建打印机
        """
        assert printer.status == PrinterStatus.OFFLINE
        assert printer.is_enabled is True
        assert printer.current_task_id is None
        assert printer.profile == printer_profile

    def test_is_available(self, printer):
        """
        测试打印机可用性检查
        """
        assert not printer.is_available()
        
        printer.update_status(PrinterStatus.IDLE)
        assert printer.is_available()

    def test_is_available_disabled(self, printer):
        """
        测试禁用的打印机不可用
        """
        printer.is_enabled = False
        printer.update_status(PrinterStatus.IDLE)
        assert not printer.is_available()

    def test_update_status(self, printer):
        """
        测试更新打印机状态
        """
        printer.update_status(PrinterStatus.IDLE)
        assert printer.status == PrinterStatus.IDLE
        assert printer.last_heartbeat is not None

    def test_assign_task(self, printer):
        """
        测试分配打印任务
        """
        printer.update_status(PrinterStatus.IDLE)
        task_id = uuid4()
        
        printer.assign_task(task_id)
        assert printer.current_task_id == task_id
        assert printer.status == PrinterStatus.BUSY

    def test_assign_task_when_busy(self, printer):
        """
        测试在打印机繁忙时分配任务
        """
        printer.update_status(PrinterStatus.BUSY)
        task_id = uuid4()
        
        with pytest.raises(PrinterBusyError):
            printer.assign_task(task_id)

    def test_release_task(self, printer):
        """
        测试释放当前任务
        """
        printer.update_status(PrinterStatus.IDLE)
        printer.assign_task(uuid4())
        
        printer.release_task()
        assert printer.current_task_id is None
        assert printer.status == PrinterStatus.IDLE

    def test_update_heartbeat(self, printer):
        """
        测试更新心跳时间
        """
        before = printer.last_heartbeat
        printer.update_heartbeat()
        after = printer.last_heartbeat
        
        assert after is not None
        assert after != before
