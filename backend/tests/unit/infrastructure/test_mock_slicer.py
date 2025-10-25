import pytest
import os
import tempfile
from datetime import timedelta

from src.infrastructure.slicing.mock_slicer import MockSlicer
from src.domain.interfaces.i_slicer import SlicingConfig, PrinterProfile


class TestMockSlicer:
    """
    Mock切片引擎测试
    """

    @pytest.fixture
    def slicer(self) -> MockSlicer:
        """
        创建Mock切片引擎fixture
        
        Returns:
            MockSlicer: 测试用切片引擎
        """
        return MockSlicer()

    @pytest.fixture
    def printer(self) -> PrinterProfile:
        """
        创建打印机配置fixture
        
        Returns:
            PrinterProfile: 测试用打印机配置
        """
        return PrinterProfile(
            id="bambu_h2d",
            name="Bambu H2D",
            bed_size=(256, 256, 256),
            nozzle_diameter=0.4,
            filament_diameter=1.75,
            max_speed=500,
            firmware_flavor="bambu"
        )

    @pytest.fixture
    def config(self) -> SlicingConfig:
        """
        创建切片配置fixture
        
        Returns:
            SlicingConfig: 测试用切片配置
        """
        return SlicingConfig(
            layer_height=0.2,
            infill_density=20,
            print_speed=50,
            support_enabled=False,
            adhesion_type="brim"
        )

    @pytest.fixture
    def temp_stl_file(self):
        """
        创建临时STL文件fixture
        
        Yields:
            str: 临时STL文件路径
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.stl', delete=False) as f:
            f.write("solid test\n")
            f.write("  facet normal 0 0 0\n")
            f.write("    outer loop\n")
            f.write("      vertex 0 0 0\n")
            f.write("      vertex 1 0 0\n")
            f.write("      vertex 0 1 0\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
            f.write("endsolid test\n")
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_get_available_printers(self, slicer):
        """
        测试获取可用打印机列表
        """
        printers = slicer.get_available_printers()
        
        assert len(printers) > 0
        assert printers[0].id == "bambu_h2d"

    def test_get_default_config(self, slicer):
        """
        测试获取默认配置
        """
        config = slicer.get_default_config("bambu_h2d")
        
        assert config.layer_height == 0.2
        assert config.infill_density == 20

    def test_get_default_config_invalid_printer(self, slicer):
        """
        测试获取无效打印机的默认配置
        """
        with pytest.raises(ValueError):
            slicer.get_default_config("invalid_printer")

    @pytest.mark.asyncio
    async def test_slice_model(self, slicer, printer, config, temp_stl_file):
        """
        测试切片模型
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.gcode")
            
            result = await slicer.slice_model(
                stl_path=temp_stl_file,
                printer=printer,
                config=config,
                output_path=output_path
            )
            
            assert os.path.exists(result.gcode_path)
            assert result.layer_count == 100
            assert isinstance(result.estimated_time, timedelta)
            assert result.estimated_material > 0

    @pytest.mark.asyncio
    async def test_slice_model_file_not_found(self, slicer, printer, config):
        """
        测试切片不存在的文件
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.gcode")
            
            with pytest.raises(FileNotFoundError):
                await slicer.slice_model(
                    stl_path="/non/existent/file.stl",
                    printer=printer,
                    config=config,
                    output_path=output_path
                )

    @pytest.mark.asyncio
    async def test_slice_model_invalid_config(self, slicer, printer, temp_stl_file):
        """
        测试使用无效配置切片
        """
        invalid_config = SlicingConfig(
            layer_height=0.5,
            infill_density=20,
            print_speed=50,
            support_enabled=False,
            adhesion_type="brim"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.gcode")
            
            with pytest.raises(ValueError):
                await slicer.slice_model(
                    stl_path=temp_stl_file,
                    printer=printer,
                    config=invalid_config,
                    output_path=output_path
                )
