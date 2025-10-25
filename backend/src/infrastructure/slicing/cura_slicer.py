import logging
import os
import re
import asyncio
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

from domain.interfaces.i_slicer import ISlicer, GCodeResult, PrinterProfile, SlicingConfig

logger = logging.getLogger(__name__)


class CuraEngineSlicer(ISlicer):
    """
    CuraEngine 切片引擎实现

    使用 CuraEngine 命令行工具将 STL 模型切片为 G-code
    """

    def __init__(
        self,
        cura_engine_path: str = "/usr/local/bin/CuraEngine",
        definitions_dir: str = "/app/resources/cura_definitions"
    ):
        """
        初始化 CuraEngine 切片器

        Args:
            cura_engine_path: CuraEngine 可执行文件路径
            definitions_dir: 打印机定义文件目录
        """
        self.cura_engine_path = cura_engine_path
        self.definitions_dir = definitions_dir
        self._printers = self._init_printers()

        # 验证 CuraEngine 是否可用
        if not os.path.exists(cura_engine_path):
            logger.warning(
                f"CuraEngine not found at {cura_engine_path}. "
                "Slicing will fail if attempted."
            )

    def _init_printers(self) -> List[PrinterProfile]:
        """
        初始化支持的打印机配置

        Returns:
            List[PrinterProfile]: 打印机配置列表
        """
        return [
            PrinterProfile(
                id="bambu_h2d",
                name="Bambu Lab H2D",
                bed_size=(256, 256, 256),
                nozzle_diameter=0.4,
                filament_diameter=1.75,
                max_speed=500,
                firmware_flavor="Marlin"
            )
        ]

    async def slice_model(
        self,
        stl_path: str,
        printer: PrinterProfile,
        config: SlicingConfig,
        output_path: str
    ) -> GCodeResult:
        """
        切片模型生成 G-code

        Args:
            stl_path: STL 文件路径
            printer: 打印机配置
            config: 切片配置
            output_path: 输出 G-code 路径

        Returns:
            GCodeResult: 生成结果

        Raises:
            FileNotFoundError: 如果 STL 文件或 CuraEngine 不存在
            ValueError: 如果配置无效
            RuntimeError: 如果切片失败
        """
        # 验证输入
        if not os.path.exists(stl_path):
            raise FileNotFoundError(f"STL file not found: {stl_path}")

        if not config.validate():
            raise ValueError("Invalid slicing configuration")

        if not os.path.exists(self.cura_engine_path):
            raise FileNotFoundError(
                f"CuraEngine not found at {self.cura_engine_path}. "
                "Please ensure CuraEngine is installed."
            )

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 构建打印机定义文件路径
        definition_file = os.path.join(self.definitions_dir, f"{printer.id}.def.json")
        if not os.path.exists(definition_file):
            raise FileNotFoundError(
                f"Printer definition not found: {definition_file}"
            )

        logger.info(
            f"Slicing {stl_path} with CuraEngine for {printer.name}"
        )

        # 构建 CuraEngine 命令
        cmd = self._build_command(
            stl_path=stl_path,
            definition_file=definition_file,
            config=config,
            output_path=output_path
        )

        # 执行切片
        try:
            stdout, stderr = await self._execute_cura_engine(cmd)
            logger.debug(f"CuraEngine output: {stdout}")

            if stderr:
                logger.warning(f"CuraEngine stderr: {stderr}")

        except Exception as e:
            logger.error(f"CuraEngine execution failed: {e}")
            raise RuntimeError(f"CuraEngine slicing failed: {str(e)}")

        # 验证输出文件
        if not os.path.exists(output_path):
            raise RuntimeError(
                f"CuraEngine did not generate output file: {output_path}"
            )

        # 解析切片结果
        result = self._parse_gcode_file(output_path, stdout, config)

        logger.info(
            f"Slicing completed: {result.layer_count} layers, "
            f"estimated time: {result.estimated_time}, "
            f"estimated material: {result.estimated_material:.2f}g"
        )

        return result

    def _build_command(
        self,
        stl_path: str,
        definition_file: str,
        config: SlicingConfig,
        output_path: str
    ) -> List[str]:
        """
        构建 CuraEngine 命令行参数

        Args:
            stl_path: STL 文件路径
            definition_file: 打印机定义文件路径
            config: 切片配置
            output_path: 输出路径

        Returns:
            List[str]: 命令行参数列表
        """
        cmd = [
            self.cura_engine_path,
            "slice",
            "-v",  # 详细输出
            "-j", definition_file,  # 打印机定义
            "-l", stl_path,  # 输入模型
            "-o", output_path,  # 输出 G-code
        ]

        # 添加切片参数
        settings = {
            "layer_height": str(config.layer_height),
            "infill_sparse_density": str(config.infill_density),
            "speed_print": str(config.print_speed),
            "speed_travel": str(config.travel_speed),
            "support_enable": str(config.support_enabled).lower(),
            "adhesion_type": config.adhesion_type,
            "material_print_temperature": str(config.nozzle_temperature),
            "material_bed_temperature": str(config.bed_temperature),
        }

        for key, value in settings.items():
            cmd.extend(["-s", f"{key}={value}"])

        logger.debug(f"CuraEngine command: {' '.join(cmd)}")

        return cmd

    async def _execute_cura_engine(self, cmd: List[str]) -> tuple[str, str]:
        """
        异步执行 CuraEngine 命令

        Args:
            cmd: 命令行参数列表

        Returns:
            tuple[str, str]: (stdout, stderr)

        Raises:
            RuntimeError: 如果命令执行失败
        """
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 分钟超时
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise RuntimeError("CuraEngine execution timeout (5 minutes)")

        if process.returncode != 0:
            raise RuntimeError(
                f"CuraEngine failed with exit code {process.returncode}: "
                f"{stderr.decode('utf-8', errors='replace')}"
            )

        return (
            stdout.decode('utf-8', errors='replace'),
            stderr.decode('utf-8', errors='replace')
        )

    def _parse_gcode_file(
        self,
        gcode_path: str,
        cura_output: str,
        config: SlicingConfig
    ) -> GCodeResult:
        """
        解析 G-code 文件获取统计信息

        Args:
            gcode_path: G-code 文件路径
            cura_output: CuraEngine 输出
            config: 切片配置

        Returns:
            GCodeResult: 切片结果
        """
        # 从 G-code 文件中提取信息
        layer_count = 0
        estimated_time_seconds = 0
        estimated_material = 0.0

        try:
            with open(gcode_path, 'r') as f:
                for line in f:
                    # 统计层数 (查找 ;LAYER: 注释)
                    if line.startswith(';LAYER:'):
                        layer_count += 1

                    # 尝试从注释中提取时间估算
                    # CuraEngine 通常会在文件头部添加统计信息
                    if ';TIME:' in line:
                        match = re.search(r';TIME:(\d+)', line)
                        if match:
                            estimated_time_seconds = int(match.group(1))

                    # 尝试提取材料用量
                    if ';Filament used:' in line:
                        # 格式: ;Filament used: 1.23456m
                        match = re.search(r';Filament used: ([\d.]+)m', line)
                        if match:
                            filament_length_m = float(match.group(1))
                            # 估算重量: PLA 密度约 1.24 g/cm³, 1.75mm 直径
                            # 体积 = π * (直径/2)² * 长度
                            # 原因: 转换为立方厘米并乘以密度
                            filament_radius_cm = 0.175 / 2  # 1.75mm = 0.175cm
                            filament_length_cm = filament_length_m * 100
                            volume_cm3 = (
                                3.14159 * filament_radius_cm ** 2 * filament_length_cm
                            )
                            estimated_material = volume_cm3 * 1.24  # PLA 密度

        except Exception as e:
            logger.warning(f"Failed to parse G-code file: {e}")

        # 如果无法从文件中提取，使用估算值
        if layer_count == 0:
            # 原因: 估算层数 = 模型高度 / 层高 (假设 50mm 高度)
            layer_count = int(50 / config.layer_height)

        if estimated_time_seconds == 0:
            # 原因: 粗略估算 = 层数 * 每层平均时间
            # 考虑填充率的影响
            seconds_per_layer = 30 + (config.infill_density / 100 * 30)
            estimated_time_seconds = int(layer_count * seconds_per_layer)

        if estimated_material == 0.0:
            # 原因: 粗略估算材料 = 层数 * 填充率系数
            estimated_material = layer_count * (config.infill_density / 100) * 0.5

        return GCodeResult(
            gcode_path=gcode_path,
            estimated_time=timedelta(seconds=estimated_time_seconds),
            estimated_material=estimated_material,
            layer_count=layer_count
        )

    def get_available_printers(self) -> List[PrinterProfile]:
        """
        获取支持的打印机列表

        Returns:
            List[PrinterProfile]: 打印机配置列表
        """
        return self._printers

    def get_default_config(self, printer_id: str) -> SlicingConfig:
        """
        获取指定打印机的默认切片配置

        Args:
            printer_id: 打印机ID

        Returns:
            SlicingConfig: 默认配置

        Raises:
            ValueError: 如果打印机ID不存在
        """
        printer = next((p for p in self._printers if p.id == printer_id), None)
        if not printer:
            raise ValueError(f"Unknown printer ID: {printer_id}")

        # 返回适合 Bambu H2D 的默认配置
        return SlicingConfig(
            layer_height=0.2,
            infill_density=20,
            print_speed=50,
            support_enabled=False,
            adhesion_type="brim"
        )
