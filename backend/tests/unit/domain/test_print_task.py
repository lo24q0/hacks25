import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from src.domain.models.print_task import PrintTask
from src.domain.enums.print_enums import TaskStatus
from src.domain.value_objects.slicing_config import SlicingConfig, AdhesionType, MaterialType
from src.shared.exceptions.domain_exceptions import InvalidStateError


class TestPrintTask:
    """
    打印任务领域模型测试
    """

    @pytest.fixture
    def slicing_config(self) -> SlicingConfig:
        """
        创建切片配置fixture
        
        Returns:
            SlicingConfig: 测试用切片配置
        """
        return SlicingConfig(
            layer_height=0.2,
            infill_density=20,
            print_speed=50,
            travel_speed=100,
            support_enabled=False,
            adhesion_type=AdhesionType.BRIM,
            material_type=MaterialType.PLA,
            nozzle_temperature=210,
            bed_temperature=60
        )

    @pytest.fixture
    def print_task(self, slicing_config) -> PrintTask:
        """
        创建打印任务fixture
        
        Args:
            slicing_config: 切片配置
            
        Returns:
            PrintTask: 测试用打印任务
        """
        return PrintTask(
            model_id=uuid4(),
            printer_id="test_printer",
            slicing_config=slicing_config
        )

    def test_create_print_task(self, print_task, slicing_config):
        """
        测试创建打印任务
        """
        assert print_task.status == TaskStatus.PENDING
        assert print_task.queue_position is None
        assert print_task.progress == 0
        assert print_task.slicing_config == slicing_config

    def test_start_slicing(self, print_task):
        """
        测试开始切片
        """
        print_task.start_slicing()
        assert print_task.status == TaskStatus.SLICING

    def test_start_slicing_invalid_state(self, print_task):
        """
        测试在无效状态下开始切片
        """
        print_task.start_slicing()
        with pytest.raises(InvalidStateError):
            print_task.start_slicing()

    def test_enqueue(self, print_task):
        """
        测试任务入队
        """
        print_task.enqueue(1)
        assert print_task.status == TaskStatus.QUEUED
        assert print_task.queue_position == 1

    def test_start_printing(self, print_task):
        """
        测试开始打印
        """
        print_task.enqueue(1)
        print_task.start_printing()
        assert print_task.status == TaskStatus.PRINTING
        assert print_task.actual_start_time is not None
        assert print_task.queue_position is None

    def test_start_printing_invalid_state(self, print_task):
        """
        测试在无效状态下开始打印
        """
        with pytest.raises(InvalidStateError):
            print_task.start_printing()

    def test_update_progress(self, print_task):
        """
        测试更新打印进度
        """
        print_task.update_progress(50)
        assert print_task.progress == 50

    def test_update_progress_invalid_value(self, print_task):
        """
        测试更新无效的打印进度
        """
        with pytest.raises(ValueError):
            print_task.update_progress(150)

    def test_mark_completed(self, print_task):
        """
        测试标记任务完成
        """
        print_task.mark_completed()
        assert print_task.status == TaskStatus.COMPLETED
        assert print_task.progress == 100
        assert print_task.actual_end_time is not None

    def test_mark_failed(self, print_task):
        """
        测试标记任务失败
        """
        error_msg = "Test error"
        print_task.mark_failed(error_msg)
        assert print_task.status == TaskStatus.FAILED
        assert print_task.error_message == error_msg
        assert print_task.actual_end_time is not None

    def test_cancel(self, print_task):
        """
        测试取消任务
        """
        print_task.cancel()
        assert print_task.status == TaskStatus.CANCELLED
        assert print_task.actual_end_time is not None

    def test_cancel_completed_task(self, print_task):
        """
        测试取消已完成的任务
        """
        print_task.mark_completed()
        with pytest.raises(InvalidStateError):
            print_task.cancel()

    def test_pause(self, print_task):
        """
        测试暂停任务
        """
        print_task.enqueue(1)
        print_task.start_printing()
        print_task.pause()
        assert print_task.status == TaskStatus.PAUSED

    def test_pause_invalid_state(self, print_task):
        """
        测试在无效状态下暂停任务
        """
        with pytest.raises(InvalidStateError):
            print_task.pause()

    def test_resume(self, print_task):
        """
        测试恢复任务
        """
        print_task.enqueue(1)
        print_task.start_printing()
        print_task.pause()
        print_task.resume()
        assert print_task.status == TaskStatus.PRINTING

    def test_resume_invalid_state(self, print_task):
        """
        测试在无效状态下恢复任务
        """
        with pytest.raises(InvalidStateError):
            print_task.resume()
