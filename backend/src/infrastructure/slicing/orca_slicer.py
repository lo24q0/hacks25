import logging
import os
import re
import asyncio
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

from src.domain.interfaces.i_slicer import ISlicer, GCodeResult, PrinterProfile, SlicingConfig

logger = logging.getLogger(__name__)


class OrcaSlicer(ISlicer):
    """
    OrcaSlicer 切片引擎实现

    OrcaSlicer 是基于 PrusaSlicer 的增强版本,专为 Bambu Lab 打印机优化。
    原生支持拓竹打印机,包括 H2D 型号。

    优势:
    - Bambu Lab 打印机原生支持
    - 内置拓竹打印机配置文件
    - 切片质量针对拓竹打印机优化
    - 命令行接口完善
    """

    def __init__(
        self,
        orca_slicer_path: str = "/usr/local/bin/orcaslicer",
        config_dir: Optional[str] = None
    ):
        """
        初始化 OrcaSlicer 切片器

        Args:
            orca_slicer_path: OrcaSlicer 可执行文件路径
            config_dir: 配置文件目录 (可选,使用默认配置)
        """
        self.orca_slicer_path = orca_slicer_path
        self.config_dir = config_dir or "/app/resources/orca_configs"
        self._printers = self._init_printers()

        # 验证 OrcaSlicer 是否可用
        if not os.path.exists(orca_slicer_path):
            logger.warning(
                f"OrcaSlicer not found at {orca_slicer_path}. "
                "Slicing will fail if attempted. "
                "Please ensure OrcaSlicer AppImage is installed."
            )

    def _init_printers(self) -> List[PrinterProfile]:
        """
        初始化支持的打印机配置

        OrcaSlicer 原生支持 Bambu Lab 全系列打印机

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
            ),
            # 未来可扩展其他 Bambu Lab 打印机
            PrinterProfile(
                id="bambu_x1c",
                name="Bambu Lab X1 Carbon",
                bed_size=(256, 256, 256),
                nozzle_diameter=0.4,
                filament_diameter=1.75,
                max_speed=500,
                firmware_flavor="Marlin"
            ),
            PrinterProfile(
                id="bambu_p1p",
                name="Bambu Lab P1P",
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
        使用 OrcaSlicer 切片模型生成 G-code

        Args:
            stl_path: STL 文件路径
            printer: 打印机配置
            config: 切片配置
            output_path: 输出 G-code 路径

        Returns:
            GCodeResult: 生成结果

        Raises:
            FileNotFoundError: 如果 STL 文件或 OrcaSlicer 不存在
            ValueError: 如果配置无效
            RuntimeError: 如果切片失败
        """
        # 验证输入
        if not os.path.exists(stl_path):
            raise FileNotFoundError(f"STL file not found: {stl_path}")

        if not config.validate():
            raise ValueError("Invalid slicing configuration")

        if not os.path.exists(self.orca_slicer_path):
            raise FileNotFoundError(
                f"OrcaSlicer not found at {self.orca_slicer_path}. "
                "Please ensure OrcaSlicer AppImage is installed."
            )

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(
            f"Slicing {stl_path} with OrcaSlicer for {printer.name}"
        )

        # 构建 OrcaSlicer 命令
        cmd = self._build_command(
            stl_path=stl_path,
            printer=printer,
            config=config,
            output_path=output_path
        )

        # 执行切片
        try:
            stdout, stderr = await self._execute_orca_slicer(cmd)
            logger.debug(f"OrcaSlicer output: {stdout}")

            if stderr:
                logger.warning(f"OrcaSlicer stderr: {stderr}")

        except Exception as e:
            logger.error(f"OrcaSlicer execution failed: {e}")
            raise RuntimeError(f"OrcaSlicer slicing failed: {str(e)}")

        # 验证输出文件
        if not os.path.exists(output_path):
            raise RuntimeError(
                f"OrcaSlicer did not generate output file: {output_path}"
            )

        # 解析切片结果
        result = self._parse_gcode_file(output_path, config)

        logger.info(
            f"Slicing completed: {result.layer_count} layers, "
            f"estimated time: {result.estimated_time}, "
            f"estimated material: {result.estimated_material:.2f}g"
        )

        return result

    def _build_command(
        self,
        stl_path: str,
        printer: PrinterProfile,
        config: SlicingConfig,
        output_path: str
    ) -> List[str]:
        """
        构建 OrcaSlicer 命令行参数

        OrcaSlicer 命令行语法与 PrusaSlicer 兼容:
        orcaslicer --export-gcode --output output.gcode input.stl

        Args:
            stl_path: STL 文件路径
            printer: 打印机配置
            config: 切片配置
            output_path: 输出路径

        Returns:
            List[str]: 命令行参数列表
        """
        cmd = [
            self.orca_slicer_path,
            "--export-gcode",  # 导出 G-code 模式
            "--output", output_path,  # 输出文件路径
        ]

        # 添加打印机配置
        # 原因: OrcaSlicer 内置 Bambu Lab 打印机配置
        # 使用 --printer 参数指定打印机型号
        printer_name_map = {
            "bambu_h2d": "Bambu Lab H2D",
            "bambu_x1c": "Bambu Lab X1 Carbon",
            "bambu_p1p": "Bambu Lab P1P"
        }

        if printer.id in printer_name_map:
            cmd.extend(["--printer", printer_name_map[printer.id]])

        # 添加切片参数
        # 原因: 通过命令行参数覆盖默认配置
        cmd.extend([
            "--layer-height", str(config.layer_height),
            "--fill-density", f"{config.infill_density}%",
            "--perimeters", "3",  # 外壁层数
            "--top-solid-layers", "4",  # 顶部实心层
            "--bottom-solid-layers", "4",  # 底部实心层
        ])

        # 打印速度配置
        if config.print_speed:
            cmd.extend(["--speed", str(config.print_speed)])

        # 支撑配置
        if config.support_enabled:
            cmd.extend(["--support-material"])

        # 底板附着类型
        adhesion_map = {
            "skirt": "--skirts 3",
            "brim": "--brim-width 5",
            "raft": "--raft-layers 3"
        }

        if config.adhesion_type in adhesion_map:
            # 分割参数字符串为列表
            adhesion_params = adhesion_map[config.adhesion_type].split()
            cmd.extend(adhesion_params)

        # 添加输入文件 (必须在最后)
        cmd.append(stl_path)

        logger.debug(f"OrcaSlicer command: {' '.join(cmd)}")

        return cmd

    async def _execute_orca_slicer(self, cmd: List[str]) -> tuple[str, str]:
        """
        异步执行 OrcaSlicer 命令

        Args:
            cmd: 命令行参数列表

        Returns:
            tuple[str, str]: (stdout, stderr)

        Raises:
            RuntimeError: 如果命令执行失败
        """
        # 设置环境变量
        # 原因: AppImage 在容器中运行需要特殊配置
        env = os.environ.copy()
        env['APPIMAGE_EXTRACT_AND_RUN'] = '1'  # 允许在容器中运行 AppImage

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 分钟超时
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise RuntimeError("OrcaSlicer execution timeout (5 minutes)")

        if process.returncode != 0:
            raise RuntimeError(
                f"OrcaSlicer failed with exit code {process.returncode}: "
                f"{stderr.decode('utf-8', errors='replace')}"
            )

        return (
            stdout.decode('utf-8', errors='replace'),
            stderr.decode('utf-8', errors='replace')
        )

    def _parse_gcode_file(
        self,
        gcode_path: str,
        config: SlicingConfig
    ) -> GCodeResult:
        """
        解析 G-code 文件获取统计信息

        OrcaSlicer 生成的 G-code 包含详细的元数据注释,
        格式与 PrusaSlicer 类似。

        Args:
            gcode_path: G-code 文件路径
            config: 切片配置

        Returns:
            GCodeResult: 切片结果
        """
        layer_count = 0
        estimated_time_seconds = 0
        estimated_material = 0.0

        try:
            with open(gcode_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 统计层数
                    # OrcaSlicer 格式: ;LAYER_CHANGE 或 ; layer num/total
                    if line.startswith(';LAYER_CHANGE') or line.startswith('; layer '):
                        layer_count += 1

                    # 提取打印时间
                    # OrcaSlicer 格式: ; estimated printing time = 1h 23m 45s
                    if 'estimated printing time' in line.lower():
                        time_match = re.search(
                            r'(\d+)h\s*(\d+)m\s*(\d+)s',
                            line
                        )
                        if time_match:
                            hours = int(time_match.group(1))
                            minutes = int(time_match.group(2))
                            seconds = int(time_match.group(3))
                            estimated_time_seconds = hours * 3600 + minutes * 60 + seconds
                        else:
                            # 尝试其他格式: ; estimated printing time = 3600s
                            time_match = re.search(r'(\d+)s', line)
                            if time_match:
                                estimated_time_seconds = int(time_match.group(1))

                    # 提取材料用量
                    # OrcaSlicer 格式: ; filament used [mm] = 1234.56
                    if 'filament used' in line.lower() and 'mm' in line.lower():
                        match = re.search(r'([\d.]+)', line)
                        if match:
                            filament_length_mm = float(match.group(1))
                            # 转换为克
                            # 原因: PLA 密度 1.24 g/cm³, 1.75mm 直径耗材
                            filament_radius_cm = 0.175 / 2  # 1.75mm = 0.175cm
                            filament_length_cm = filament_length_mm / 10
                            volume_cm3 = (
                                3.14159 * filament_radius_cm ** 2 * filament_length_cm
                            )
                            estimated_material = volume_cm3 * 1.24

                    # OrcaSlicer 也可能直接提供重量
                    # ; filament used [g] = 12.34
                    if 'filament used' in line.lower() and '[g]' in line.lower():
                        match = re.search(r'([\d.]+)', line)
                        if match:
                            estimated_material = float(match.group(1))

        except Exception as e:
            logger.warning(f"Failed to parse G-code file: {e}")

        # 如果无法从文件中提取,使用估算值
        if layer_count == 0:
            # 原因: 估算层数 = 假设高度 50mm / 层高
            layer_count = int(50 / config.layer_height)

        if estimated_time_seconds == 0:
            # 原因: 粗略估算 = 层数 * 每层时间
            # 考虑填充率和打印速度的影响
            seconds_per_layer = 30 + (config.infill_density / 100 * 30)
            if config.print_speed > 0:
                # 速度越快,时间越短
                speed_factor = 50 / config.print_speed
                seconds_per_layer *= speed_factor
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

        为 Bambu Lab 打印机提供优化的默认配置

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

        # 返回适合 Bambu Lab 打印机的默认配置
        # 原因: 拓竹打印机高速高质量,使用较高的速度和质量平衡配置
        return SlicingConfig(
            layer_height=0.2,       # 标准层高,质量与速度平衡
            infill_density=15,      # 15% 填充,适合一般模型
            print_speed=150,        # 拓竹打印机支持高速打印
            support_enabled=False,  # 默认不启用支撑,用户根据需要开启
            adhesion_type="brim"    # 使用 brim 提高附着力
        )
