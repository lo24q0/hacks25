"""
打印机仓储实现
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.printer import Printer
from src.domain.value_objects.printer_profile import PrinterProfile
from src.domain.value_objects.connection_config import ConnectionConfig
from src.domain.enums.print_enums import PrinterStatus
from src.infrastructure.persistence.models.printer_model import PrinterModel


class PrinterRepository:
    """
    打印机仓储

    负责Printer领域对象的持久化和查询
    """

    def __init__(self, session: AsyncSession):
        """
        初始化仓储

        Args:
            session: 数据库会话
        """
        self.session = session

    async def save(self, printer: Printer) -> None:
        """
        保存打印机

        Args:
            printer: 打印机领域对象
        """
        model = await self.session.get(PrinterModel, printer.id)

        if model is None:
            model = self._to_model(printer)
            self.session.add(model)
        else:
            self._update_model(model, printer)

        await self.session.flush()

    async def find_by_id(self, printer_id: str) -> Optional[Printer]:
        """
        根据ID查询打印机

        Args:
            printer_id: 打印机ID

        Returns:
            Optional[Printer]: 找到的打印机,不存在则返回None
        """
        model = await self.session.get(PrinterModel, printer_id)

        if model is None:
            return None

        return self._to_domain(model)

    async def find_all(self) -> List[Printer]:
        """
        查询所有打印机

        Returns:
            List[Printer]: 打印机列表
        """
        stmt = select(PrinterModel).order_by(PrinterModel.created_at)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def find_available(self) -> List[Printer]:
        """
        查询可用的打印机(在线且空闲)

        Returns:
            List[Printer]: 可用打印机列表
        """
        stmt = (
            select(PrinterModel)
            .where(PrinterModel.status == PrinterStatus.IDLE, PrinterModel.is_enabled == True)
            .order_by(PrinterModel.last_heartbeat.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def delete(self, printer_id: str) -> bool:
        """
        删除打印机

        Args:
            printer_id: 打印机ID

        Returns:
            bool: 是否删除成功
        """
        model = await self.session.get(PrinterModel, printer_id)

        if model is None:
            return False

        await self.session.delete(model)
        await self.session.flush()

        return True

    def _to_model(self, printer: Printer) -> PrinterModel:
        """
        领域对象转数据库模型

        Args:
            printer: 领域对象

        Returns:
            PrinterModel: 数据库模型
        """
        return PrinterModel(
            id=printer.id,
            name=printer.name,
            model=printer.model,
            adapter_type=printer.adapter_type,
            connection_type=printer.connection_config.connection_type,
            connection_host=printer.connection_config.host,
            connection_port=printer.connection_config.port,
            connection_access_code=printer.connection_config.access_code,
            connection_serial_number=printer.connection_config.serial_number,
            connection_use_ssl=printer.connection_config.use_ssl,
            bed_size_x=printer.profile.bed_size[0],
            bed_size_y=printer.profile.bed_size[1],
            bed_size_z=printer.profile.bed_size[2],
            nozzle_diameter=printer.profile.nozzle_diameter,
            filament_diameter=printer.profile.filament_diameter,
            max_print_speed=printer.profile.max_print_speed,
            max_travel_speed=printer.profile.max_travel_speed,
            firmware_flavor=printer.profile.firmware_flavor,
            status=printer.status,
            current_task_id=printer.current_task_id,
            is_enabled=printer.is_enabled,
            created_at=printer.created_at,
            last_heartbeat=printer.last_heartbeat,
        )

    def _update_model(self, model: PrinterModel, printer: Printer) -> None:
        """
        更新数据库模型

        Args:
            model: 数据库模型
            printer: 领域对象
        """
        model.name = printer.name
        model.model = printer.model
        model.adapter_type = printer.adapter_type
        model.connection_type = printer.connection_config.connection_type
        model.connection_host = printer.connection_config.host
        model.connection_port = printer.connection_config.port
        model.connection_access_code = printer.connection_config.access_code
        model.connection_serial_number = printer.connection_config.serial_number
        model.connection_use_ssl = printer.connection_config.use_ssl
        model.bed_size_x = printer.profile.bed_size[0]
        model.bed_size_y = printer.profile.bed_size[1]
        model.bed_size_z = printer.profile.bed_size[2]
        model.nozzle_diameter = printer.profile.nozzle_diameter
        model.filament_diameter = printer.profile.filament_diameter
        model.max_print_speed = printer.profile.max_print_speed
        model.max_travel_speed = printer.profile.max_travel_speed
        model.firmware_flavor = printer.profile.firmware_flavor
        model.status = printer.status
        model.current_task_id = printer.current_task_id
        model.is_enabled = printer.is_enabled
        model.last_heartbeat = printer.last_heartbeat

    def _to_domain(self, model: PrinterModel) -> Printer:
        """
        数据库模型转领域对象

        Args:
            model: 数据库模型

        Returns:
            Printer: 领域对象
        """
        return Printer(
            id=model.id,
            name=model.name,
            model=model.model,
            adapter_type=model.adapter_type,
            connection_config=ConnectionConfig(
                connection_type=model.connection_type,
                host=model.connection_host,
                port=model.connection_port,
                access_code=model.connection_access_code,
                serial_number=model.connection_serial_number,
                use_ssl=model.connection_use_ssl,
            ),
            profile=PrinterProfile(
                id=model.id,
                name=model.name,
                bed_size=(model.bed_size_x, model.bed_size_y, model.bed_size_z),
                nozzle_diameter=model.nozzle_diameter,
                filament_diameter=model.filament_diameter,
                max_print_speed=model.max_print_speed,
                max_travel_speed=model.max_travel_speed,
                firmware_flavor=model.firmware_flavor,
            ),
            status=model.status,
            current_task_id=model.current_task_id,
            is_enabled=model.is_enabled,
            created_at=model.created_at,
            last_heartbeat=model.last_heartbeat,
        )
