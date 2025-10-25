"""
打印任务数据库模型
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum, JSON, Interval, Text
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

    id = Column(GUID, primary_key=True, default=uuid4)
    model_id = Column(GUID, nullable=False, index=True)
    printer_id = Column(String(100), nullable=False, index=True)
    
    status = Column(
        SQLEnum(TaskStatus, name='task_status', native_enum=False),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    
    queue_position = Column(Integer, nullable=True)
    
    slicing_config = Column(JSON, nullable=False)
    
    gcode_path = Column(String(500), nullable=True)
    
    estimated_time = Column(Interval, nullable=True)
    estimated_material = Column(Float, nullable=True)
    
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    progress = Column(Integer, default=0, nullable=False)
    
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_domain_model(self) -> 'PrintTask':
        """
        转换为领域模型
        
        Returns:
            PrintTask: 领域模型对象
        """
        from domain.models.print_task import PrintTask
        from domain.value_objects.slicing_config import SlicingConfig
        
        slicing_config = SlicingConfig(**self.slicing_config)
        
        return PrintTask(
            id=self.id,
            model_id=self.model_id,
            printer_id=self.printer_id,
            status=self.status,
            queue_position=self.queue_position,
            slicing_config=slicing_config,
            gcode_path=self.gcode_path,
            estimated_time=self.estimated_time,
            estimated_material=self.estimated_material,
            actual_start_time=self.actual_start_time,
            actual_end_time=self.actual_end_time,
            progress=self.progress,
            error_message=self.error_message,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @staticmethod
    def from_domain_model(task: 'PrintTask') -> 'PrintTaskModel':
        """
        从领域模型创建数据库模型
        
        Args:
            task: 领域模型对象
            
        Returns:
            PrintTaskModel: 数据库模型对象
        """
        return PrintTaskModel(
            id=task.id,
            model_id=task.model_id,
            printer_id=task.printer_id,
            status=task.status,
            queue_position=task.queue_position,
            slicing_config=task.slicing_config.model_dump(),
            gcode_path=task.gcode_path,
            estimated_time=task.estimated_time,
            estimated_material=task.estimated_material,
            actual_start_time=task.actual_start_time,
            actual_end_time=task.actual_end_time,
            progress=task.progress,
            error_message=task.error_message,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    def update_from_domain_model(self, task: 'PrintTask') -> None:
        """
        从领域模型更新数据库模型
        
        Args:
            task: 领域模型对象
        """
        self.model_id = task.model_id
        self.printer_id = task.printer_id
        self.status = task.status
        self.queue_position = task.queue_position
        self.slicing_config = task.slicing_config.model_dump()
        self.gcode_path = task.gcode_path
        self.estimated_time = task.estimated_time
        self.estimated_material = task.estimated_material
        self.actual_start_time = task.actual_start_time
        self.actual_end_time = task.actual_end_time
        self.progress = task.progress
        self.error_message = task.error_message
        self.updated_at = task.updated_at

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<PrintTaskModel(id={self.id}, status={self.status})>"
