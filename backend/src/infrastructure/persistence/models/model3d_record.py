"""
3D模型数据库模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum as SQLEnum

from src.infrastructure.persistence.database import Base
from src.infrastructure.persistence.models.print_task_model import GUID
from src.domain.enums.status import ModelStatus
from src.domain.enums.source_type import SourceType


class Model3DRecord(Base):
    """
    3D模型数据库模型

    对应领域模型: domain.models.model3d.Model3D
    """

    __tablename__ = "model3d_records"

    id = Column(GUID, primary_key=True)
    user_id = Column(GUID, nullable=True, index=True)

    source_type = Column(SQLEnum(SourceType), nullable=False)
    source_text_prompt = Column(Text, nullable=True)
    source_image_paths = Column(Text, nullable=True)
    source_style_preset = Column(String(100), nullable=True)

    status = Column(SQLEnum(ModelStatus), nullable=False, default=ModelStatus.PENDING, index=True)

    file_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)

    dimensions_x = Column(Float, nullable=True)
    dimensions_y = Column(Float, nullable=True)
    dimensions_z = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    triangle_count = Column(Integer, nullable=True)
    vertex_count = Column(Integer, nullable=True)
    is_manifold = Column(Boolean, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    error_message = Column(Text, nullable=True)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<Model3DRecord(id={self.id}, status={self.status})>"
