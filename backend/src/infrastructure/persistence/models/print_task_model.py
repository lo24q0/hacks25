"""
打印任务SQLAlchemy模型
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum, JSON, Interval
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR

from domain.enums.print_enums import TaskStatus
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


class PrintTaskModel(Base):
    """
    打印任务数据库模型
    
    对应domain.models.print_task.PrintTask聚合根
    """
    __tablename__ = 'print_tasks'

    id = Column(GUID(), primary_key=True, default=uuid4)
    model_id = Column(GUID(), nullable=False, index=True)
    printer_id = Column(String(100), nullable=False, index=True)
    
    status = Column(
        SQLEnum(TaskStatus, name='task_status', native_enum=False),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    
    queue_position = Column(Integer, nullable=True)
    
    # 切片配置(存储为JSON)
    slicing_config = Column(JSON, nullable=False)
    
    # 文件路径
    gcode_path = Column(String(500), nullable=True)
    
    # 预估信息
    estimated_time = Column(Interval, nullable=True)
    estimated_material = Column(Float, nullable=True)
    
    # 实际执行时间
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    # 进度
    progress = Column(Integer, default=0, nullable=False)
    
    # 错误信息
    error_message = Column(String(1000), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_domain_model(self) -> 'PrintTask':
        """
        转换为领域模型
        
        Returns:
            PrintTask: 领域模型对象
        """
        from domain.models.print_task import PrintTask
        from domain.value_objects.slicing_config import SlicingConfig
        
        # 重建切片配置
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
