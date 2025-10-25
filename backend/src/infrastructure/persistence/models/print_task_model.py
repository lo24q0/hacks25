"""
打印任务数据库模型
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import TypeDecorator, CHAR

from infrastructure.persistence.database import Base
from domain.enums.print_enums import TaskStatus


class GUID(TypeDecorator):
    """
    UUID类型适配器,兼容SQLite和PostgreSQL
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, UUID):
                return value.hex
            else:
                return UUID(value).hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, UUID):
                return value
            else:
                if dialect.name == 'postgresql':
                    return UUID(value)
                else:
                    return UUID(value)


class PrintTaskModel(Base):
    """
    打印任务数据库模型
    
    对应领域模型: domain.models.print_task.PrintTask
    """
    __tablename__ = "print_tasks"

    id = Column(GUID, primary_key=True)
    model_id = Column(GUID, nullable=False, index=True)
    printer_id = Column(String(100), nullable=False, index=True)
    status = Column(
        SQLEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    queue_position = Column(Integer, nullable=True)
    
    gcode_path = Column(String(500), nullable=True)
    
    layer_height = Column(Float, nullable=False)
    infill_density = Column(Integer, nullable=False)
    print_speed = Column(Integer, nullable=False)
    support_enabled = Column(Integer, nullable=False, default=0)
    adhesion_type = Column(String(50), nullable=False)
    
    estimated_time_seconds = Column(Integer, nullable=True)
    estimated_material = Column(Float, nullable=True)
    
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    progress = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<PrintTaskModel(id={self.id}, status={self.status})>"
