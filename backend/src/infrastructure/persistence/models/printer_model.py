"""
打印机数据库模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from src.infrastructure.persistence.database import Base
from src.infrastructure.persistence.models.print_task_model import GUID
from src.domain.enums.print_enums import PrinterStatus, AdapterType, ConnectionType


class PrinterModel(Base):
    """
    打印机数据库模型

    对应领域模型: domain.models.printer.Printer
    """

    __tablename__ = "printers"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    model = Column(String(100), nullable=False)
    adapter_type = Column(SQLEnum(AdapterType), nullable=False)

    connection_type = Column(SQLEnum(ConnectionType), nullable=False)
    connection_host = Column(String(255), nullable=True)
    connection_port = Column(Integer, nullable=True)
    connection_access_code = Column(String(255), nullable=True)
    connection_serial_number = Column(String(255), nullable=True)
    connection_use_ssl = Column(Boolean, nullable=False, default=False)

    bed_size_x = Column(Integer, nullable=False)
    bed_size_y = Column(Integer, nullable=False)
    bed_size_z = Column(Integer, nullable=False)
    nozzle_diameter = Column(Float, nullable=False)
    filament_diameter = Column(Float, nullable=False)
    max_print_speed = Column(Integer, nullable=False)
    max_travel_speed = Column(Integer, nullable=False)
    firmware_flavor = Column(String(50), nullable=False)

    status = Column(SQLEnum(PrinterStatus), nullable=False, default=PrinterStatus.OFFLINE)
    current_task_id = Column(GUID, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_heartbeat = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<PrinterModel(id={self.id}, name={self.name}, status={self.status})>"
