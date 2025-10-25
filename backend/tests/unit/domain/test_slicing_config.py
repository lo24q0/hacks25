import pytest

from src.domain.value_objects.slicing_config import SlicingConfig
from src.domain.enums.print_enums import AdhesionType, MaterialType


class TestSlicingConfig:
    """
    切片配置值对象测试
    """

    def test_create_slicing_config(self):
        """
        测试创建切片配置
        """
        config = SlicingConfig(
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
        
        assert config.layer_height == 0.2
        assert config.infill_density == 20
        assert config.print_speed == 50
        assert config.adhesion_type == AdhesionType.BRIM

    def test_get_preset_fast(self):
        """
        测试获取快速预设
        """
        config = SlicingConfig.get_preset("fast")
        
        assert config.layer_height == 0.3
        assert config.infill_density == 10
        assert config.print_speed == 60

    def test_get_preset_standard(self):
        """
        测试获取标准预设
        """
        config = SlicingConfig.get_preset("standard")
        
        assert config.layer_height == 0.2
        assert config.infill_density == 20
        assert config.print_speed == 50
        assert config.support_enabled is True

    def test_get_preset_high_quality(self):
        """
        测试获取高质量预设
        """
        config = SlicingConfig.get_preset("high_quality")
        
        assert config.layer_height == 0.1
        assert config.infill_density == 30
        assert config.print_speed == 30

    def test_get_preset_invalid(self):
        """
        测试获取无效预设
        """
        with pytest.raises(ValueError):
            SlicingConfig.get_preset("invalid_preset")

    def test_layer_height_validation(self):
        """
        测试层高验证
        """
        with pytest.raises(ValueError):
            SlicingConfig(
                layer_height=0.05,
                infill_density=20,
                print_speed=50,
                travel_speed=100,
                support_enabled=False,
                adhesion_type=AdhesionType.BRIM,
                material_type=MaterialType.PLA,
                nozzle_temperature=210,
                bed_temperature=60
            )

    def test_infill_density_validation(self):
        """
        测试填充率验证
        """
        with pytest.raises(ValueError):
            SlicingConfig(
                layer_height=0.2,
                infill_density=150,
                print_speed=50,
                travel_speed=100,
                support_enabled=False,
                adhesion_type=AdhesionType.BRIM,
                material_type=MaterialType.PLA,
                nozzle_temperature=210,
                bed_temperature=60
            )
