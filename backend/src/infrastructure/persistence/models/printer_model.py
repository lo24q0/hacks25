"""
打印机SQLAlchemy模型
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR

from domain.enums.print_enums import AdapterType, PrinterStatus
from infrastructure.persistence.database import Base


class GUID(TypeDecorator):
    """
    跨数据库的UUID类型
    
    在PostgreSQL使用UUID类型,其他数据库使用CHAR(36)
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, UUID):
                return str(UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, UUID):
            return UUID(value)
        return value


class PrinterModel(Base):
    """
    打印机数据库模型
    
    对应domain.models.printer.Printer实体
    """
    __tablename__ = 'printers'

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    model = Column(String(200), nullable=False)
    
    adapter_type = Column(
        SQLEnum(AdapterType, name='adapter_type', native_enum=False),
        nullable=False
    )
    
    # 连接配置(存储为JSON)
    connection_config = Column(JSON, nullable=False)
    
    # 打印机配置(存储为JSON)
    profile = Column(JSON, nullable=False)
    
    status = Column(
        SQLEnum(PrinterStatus, name='printer_status', native_enum=False),
        nullable=False,
        default=PrinterStatus.OFFLINE,
        index=True
    )
    
    current_task_id = Column(GUID(), nullable=True, index=True)
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_heartbeat = Column(DateTime, nullable=True, index=True)

    def to_domain_model(self) -> 'Printer':
        """
        转换为领域模型
        
        Returns:
            Printer: 领域模型对象
        """
        from domain.models.printer import Printer
        from domain.value_objects.connection_config import ConnectionConfig
        from domain.value_objects.printer_profile import PrinterProfile
        
        # 重建值对象
        connection_config = ConnectionConfig(**self.connection_config)
        profile = PrinterProfile(**self.profile)
        
        return Printer(
            id=self.id,
            name=self.name,
            model=self.model,
            adapter_type=self.adapter_type,
            connection_config=connection_config,
            profile=profile,
            status=self.status,
            current_task_id=self.current_task_id,
            is_enabled=self.is_enabled,
            created_at=self.created_at,
            last_heartbeat=self.last_heartbeat
        )

    @staticmethod
    def from_domain_model(printer: 'Printer') -> 'PrinterModel':
        """
        从领域模型创建数据库模型
        
        Args:
            printer: 领域模型对象
            
        Returns:
            PrinterModel: 数据库模型对象
        """
        return PrinterModel(
            id=printer.id,
            name=printer.name,
            model=printer.model,
            adapter_type=printer.adapter_type,
            connection_config=printer.connection_config.model_dump(),
            profile=printer.profile.model_dump(),
            status=printer.status,
            current_task_id=printer.current_task_id,
            is_enabled=printer.is_enabled,
            created_at=printer.created_at,
            last_heartbeat=printer.last_heartbeat
        )

    def update_from_domain_model(self, printer: 'Printer') -> None:
        """
        从领域模型更新数据库模型
        
        Args:
            printer: 领域模型对象
        """
        self.name = printer.name
        self.model = printer.model
        self.adapter_type = printer.adapter_type
        self.connection_config = printer.connection_config.model_dump()
        self.profile = printer.profile.model_dump()
        self.status = printer.status
        self.current_task_id = printer.current_task_id
        self.is_enabled = printer.is_enabled
        self.last_heartbeat = printer.last_heartbeat
