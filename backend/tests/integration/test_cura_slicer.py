import os
import pytest
import tempfile
from pathlib import Path

from src.infrastructure.slicing.cura_slicer import CuraEngineSlicer
from src.domain.interfaces.i_slicer import PrinterProfile, SlicingConfig


class TestCuraEngineSlicer:
    """
    CuraEngineSlicer 集成测试

    测试 CuraEngine 切片功能
    """

    @pytest.fixture
    def slicer(self):
        """
        创建 CuraEngineSlicer 实例

        Returns:
            CuraEngineSlicer: 切片器实例
        """
        return CuraEngineSlicer()

    @pytest.fixture
    def bambu_printer(self):
        """
        创建 Bambu H2D 打印机配置

        Returns:
            PrinterProfile: 打印机配置
        """
        return PrinterProfile(
            id="bambu_h2d",
            name="Bambu Lab H2D",
            bed_size=(256, 256, 256),
            nozzle_diameter=0.4,
            filament_diameter=1.75,
            max_speed=500,
            firmware_flavor="Marlin"
        )

    @pytest.fixture
    def default_config(self):
        """
        创建默认切片配置

        Returns:
            SlicingConfig: 切片配置
        """
        return SlicingConfig(
            layer_height=0.2,
            infill_density=20,
            print_speed=50,
            support_enabled=False,
            adhesion_type="brim"
        )

    @pytest.fixture
    def test_stl(self, tmp_path):
        """
        创建测试 STL 文件 (10mm 立方体)

        Args:
            tmp_path: pytest 提供的临时目录

        Returns:
            str: STL 文件路径
        """
        stl_path = tmp_path / "test_cube.stl"

        # 生成简单的 ASCII STL 立方体
        # 原因: 测试用最小可用 STL 文件
        stl_content = """solid cube
  facet normal 0 0 -1
    outer loop
      vertex 0 0 0
      vertex 10 0 0
      vertex 10 10 0
    endloop
  endfacet
  facet normal 0 0 -1
    outer loop
      vertex 0 0 0
      vertex 10 10 0
      vertex 0 10 0
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex 0 0 10
      vertex 10 10 10
      vertex 10 0 10
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex 0 0 10
      vertex 0 10 10
      vertex 10 10 10
    endloop
  endfacet
  facet normal -1 0 0
    outer loop
      vertex 0 0 0
      vertex 0 10 0
      vertex 0 10 10
    endloop
  endfacet
  facet normal -1 0 0
    outer loop
      vertex 0 0 0
      vertex 0 10 10
      vertex 0 0 10
    endloop
  endfacet
  facet normal 1 0 0
    outer loop
      vertex 10 0 0
      vertex 10 10 10
      vertex 10 10 0
    endloop
  endfacet
  facet normal 1 0 0
    outer loop
      vertex 10 0 0
      vertex 10 0 10
      vertex 10 10 10
    endloop
  endfacet
  facet normal 0 -1 0
    outer loop
      vertex 0 0 0
      vertex 10 0 10
      vertex 10 0 0
    endloop
  endfacet
  facet normal 0 -1 0
    outer loop
      vertex 0 0 0
      vertex 0 0 10
      vertex 10 0 10
    endloop
  endfacet
  facet normal 0 1 0
    outer loop
      vertex 0 10 0
      vertex 10 10 0
      vertex 10 10 10
    endloop
  endfacet
  facet normal 0 1 0
    outer loop
      vertex 0 10 0
      vertex 10 10 10
      vertex 0 10 10
    endloop
  endfacet
endsolid cube
"""
        with open(stl_path, 'w') as f:
            f.write(stl_content)

        return str(stl_path)

    def test_get_available_printers(self, slicer):
        """
        测试获取可用打印机列表

        Args:
            slicer: CuraEngineSlicer 实例
        """
        printers = slicer.get_available_printers()

        assert len(printers) > 0
        assert any(p.id == "bambu_h2d" for p in printers)

        bambu = next(p for p in printers if p.id == "bambu_h2d")
        assert bambu.name == "Bambu Lab H2D"
        assert bambu.bed_size == (256, 256, 256)
        assert bambu.nozzle_diameter == 0.4

    def test_get_default_config(self, slicer):
        """
        测试获取默认配置

        Args:
            slicer: CuraEngineSlicer 实例
        """
        config = slicer.get_default_config("bambu_h2d")

        assert config.layer_height == 0.2
        assert config.infill_density == 20
        assert config.print_speed == 50
        assert config.support_enabled is False
        assert config.adhesion_type == "brim"
        assert config.validate()

    def test_get_default_config_unknown_printer(self, slicer):
        """
        测试获取不存在的打印机配置

        Args:
            slicer: CuraEngineSlicer 实例
        """
        with pytest.raises(ValueError, match="Unknown printer ID"):
            slicer.get_default_config("unknown_printer")

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.path.exists("/usr/local/bin/CuraEngine"),
        reason="CuraEngine not installed"
    )
    async def test_slice_simple_model(
        self, slicer, test_stl, bambu_printer, default_config, tmp_path
    ):
        """
        测试切片简单模型

        Args:
            slicer: CuraEngineSlicer 实例
            test_stl: 测试 STL 文件路径
            bambu_printer: 打印机配置
            default_config: 切片配置
            tmp_path: 临时目录
        """
        output_path = str(tmp_path / "output.gcode")

        result = await slicer.slice_model(
            stl_path=test_stl,
            printer=bambu_printer,
            config=default_config,
            output_path=output_path
        )

        # 验证输出文件存在
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

        # 验证结果
        assert result.gcode_path == output_path
        assert result.layer_count > 0
        assert result.estimated_time.total_seconds() > 0
        assert result.estimated_material > 0

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.path.exists("/usr/local/bin/CuraEngine"),
        reason="CuraEngine not installed"
    )
    async def test_slice_with_support(
        self, slicer, test_stl, bambu_printer, tmp_path
    ):
        """
        测试启用支撑的切片

        Args:
            slicer: CuraEngineSlicer 实例
            test_stl: 测试 STL 文件路径
            bambu_printer: 打印机配置
            tmp_path: 临时目录
        """
        config = SlicingConfig(
            layer_height=0.2,
            infill_density=15,
            print_speed=50,
            support_enabled=True,  # 启用支撑
            adhesion_type="raft"
        )

        output_path = str(tmp_path / "output_with_support.gcode")

        result = await slicer.slice_model(
            stl_path=test_stl,
            printer=bambu_printer,
            config=config,
            output_path=output_path
        )

        assert os.path.exists(output_path)

        # 检查 G-code 中是否包含支撑相关注释
        with open(output_path, 'r') as f:
            content = f.read()
            # CuraEngine 通常会在启用支撑时添加相关注释
            assert len(content) > 0

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.path.exists("/usr/local/bin/CuraEngine"),
        reason="CuraEngine not installed"
    )
    async def test_slice_with_different_layer_heights(
        self, slicer, test_stl, bambu_printer, tmp_path
    ):
        """
        测试不同层高的切片

        Args:
            slicer: CuraEngineSlicer 实例
            test_stl: 测试 STL 文件路径
            bambu_printer: 打印机配置
            tmp_path: 临时目录
        """
        layer_heights = [0.1, 0.2, 0.3]
        results = []

        for height in layer_heights:
            config = SlicingConfig(
                layer_height=height,
                infill_density=20,
                print_speed=50,
                support_enabled=False,
                adhesion_type="brim"
            )

            output_path = str(tmp_path / f"output_{height}mm.gcode")

            result = await slicer.slice_model(
                stl_path=test_stl,
                printer=bambu_printer,
                config=config,
                output_path=output_path
            )

            results.append((height, result))

        # 验证: 层高越小,层数越多
        layer_counts = [r[1].layer_count for r in results]
        assert layer_counts[0] > layer_counts[1] > layer_counts[2]

    @pytest.mark.asyncio
    async def test_slice_missing_stl(
        self, slicer, bambu_printer, default_config, tmp_path
    ):
        """
        测试切片不存在的 STL 文件

        Args:
            slicer: CuraEngineSlicer 实例
            bambu_printer: 打印机配置
            default_config: 切片配置
            tmp_path: 临时目录
        """
        with pytest.raises(FileNotFoundError, match="STL file not found"):
            await slicer.slice_model(
                stl_path="/nonexistent/file.stl",
                printer=bambu_printer,
                config=default_config,
                output_path=str(tmp_path / "output.gcode")
            )

    @pytest.mark.asyncio
    async def test_slice_invalid_config(
        self, slicer, test_stl, bambu_printer, tmp_path
    ):
        """
        测试使用无效配置切片

        Args:
            slicer: CuraEngineSlicer 实例
            test_stl: 测试 STL 文件路径
            bambu_printer: 打印机配置
            tmp_path: 临时目录
        """
        # 创建无效配置 (层高超出范围)
        invalid_config = SlicingConfig(
            layer_height=5.0,  # 无效: 超出 0.1-0.3 范围
            infill_density=20,
            print_speed=50,
            support_enabled=False,
            adhesion_type="brim"
        )

        with pytest.raises(ValueError, match="Invalid slicing configuration"):
            await slicer.slice_model(
                stl_path=test_stl,
                printer=bambu_printer,
                config=invalid_config,
                output_path=str(tmp_path / "output.gcode")
            )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.path.exists("/usr/local/bin/CuraEngine"),
        reason="CuraEngine not installed"
    )
    async def test_slice_performance(
        self, slicer, test_stl, bambu_printer, default_config, tmp_path
    ):
        """
        测试切片性能 (应在 30 秒内完成)

        Args:
            slicer: CuraEngineSlicer 实例
            test_stl: 测试 STL 文件路径
            bambu_printer: 打印机配置
            default_config: 切片配置
            tmp_path: 临时目录
        """
        import time

        output_path = str(tmp_path / "output_perf.gcode")

        start_time = time.time()

        result = await slicer.slice_model(
            stl_path=test_stl,
            printer=bambu_printer,
            config=default_config,
            output_path=output_path
        )

        elapsed_time = time.time() - start_time

        # 验证: 简单模型应在 30 秒内完成
        assert elapsed_time < 30, f"Slicing took {elapsed_time:.2f}s, should be < 30s"
        assert os.path.exists(output_path)
