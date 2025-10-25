"""
打印任务仓储实现
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.print_task import PrintTask
from domain.value_objects.slicing_config import SlicingConfig
from domain.enums.print_enums import TaskStatus
from infrastructure.persistence.models.print_task_model import PrintTaskModel


class PrintTaskRepository:
    """
    打印任务仓储
    
    负责PrintTask领域对象的持久化和查询
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化仓储
        
        Args:
            session: 数据库会话
        """
        self.session = session
    
    async def save(self, task: PrintTask) -> None:
        """
        保存打印任务
        
        Args:
            task: 打印任务领域对象
        """
        model = await self.session.get(PrintTaskModel, task.id)
        
        if model is None:
            model = self._to_model(task)
            self.session.add(model)
        else:
            self._update_model(model, task)
        
        await self.session.flush()
    
    async def find_by_id(self, task_id: UUID) -> Optional[PrintTask]:
        """
        根据ID查询任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[PrintTask]: 找到的任务,不存在则返回None
        """
        model = await self.session.get(PrintTaskModel, task_id)
        
        if model is None:
            return None
        
        return self._to_domain(model)
    
    async def find_by_printer(self, printer_id: str) -> List[PrintTask]:
        """
        查询指定打印机的任务
        
        Args:
            printer_id: 打印机ID
            
        Returns:
            List[PrintTask]: 任务列表
        """
        stmt = select(PrintTaskModel).where(
            PrintTaskModel.printer_id == printer_id
        ).order_by(PrintTaskModel.created_at.desc())
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_domain(model) for model in models]
    
    async def find_by_status(self, status: TaskStatus) -> List[PrintTask]:
        """
        查询指定状态的任务
        
        Args:
            status: 任务状态
            
        Returns:
            List[PrintTask]: 任务列表
        """
        stmt = select(PrintTaskModel).where(
            PrintTaskModel.status == status
        ).order_by(PrintTaskModel.created_at.desc())
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_domain(model) for model in models]
    
    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[PrintTask]:
        """
        查询所有任务(分页)
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[PrintTask]: 任务列表
        """
        stmt = select(PrintTaskModel).order_by(
            PrintTaskModel.created_at.desc()
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_domain(model) for model in models]
    
    async def delete(self, task_id: UUID) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        stmt = delete(PrintTaskModel).where(PrintTaskModel.id == task_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        
        return result.rowcount > 0
    
    def _to_model(self, task: PrintTask) -> PrintTaskModel:
        """
        领域对象转数据库模型
        
        Args:
            task: 领域对象
            
        Returns:
            PrintTaskModel: 数据库模型
        """
        return PrintTaskModel(
            id=task.id,
            model_id=task.model_id,
            printer_id=task.printer_id,
            status=task.status,
            queue_position=task.queue_position,
            gcode_path=task.gcode_path,
            layer_height=task.slicing_config.layer_height,
            infill_density=task.slicing_config.infill_density,
            print_speed=task.slicing_config.print_speed,
            support_enabled=1 if task.slicing_config.support_enabled else 0,
            adhesion_type=task.slicing_config.adhesion_type,
            estimated_time_seconds=int(task.estimated_time.total_seconds()) if task.estimated_time else None,
            estimated_material=task.estimated_material,
            actual_start_time=task.actual_start_time,
            actual_end_time=task.actual_end_time,
            progress=task.progress,
            error_message=task.error_message,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    
    def _update_model(self, model: PrintTaskModel, task: PrintTask) -> None:
        """
        更新数据库模型
        
        Args:
            model: 数据库模型
            task: 领域对象
        """
        model.status = task.status
        model.queue_position = task.queue_position
        model.gcode_path = task.gcode_path
        model.layer_height = task.slicing_config.layer_height
        model.infill_density = task.slicing_config.infill_density
        model.print_speed = task.slicing_config.print_speed
        model.support_enabled = 1 if task.slicing_config.support_enabled else 0
        model.adhesion_type = task.slicing_config.adhesion_type
        model.estimated_time_seconds = int(task.estimated_time.total_seconds()) if task.estimated_time else None
        model.estimated_material = task.estimated_material
        model.actual_start_time = task.actual_start_time
        model.actual_end_time = task.actual_end_time
        model.progress = task.progress
        model.error_message = task.error_message
        model.updated_at = datetime.utcnow()
    
    def _to_domain(self, model: PrintTaskModel) -> PrintTask:
        """
        数据库模型转领域对象
        
        Args:
            model: 数据库模型
            
        Returns:
            PrintTask: 领域对象
        """
        from datetime import timedelta
        
        return PrintTask(
            id=model.id,
            model_id=model.model_id,
            printer_id=model.printer_id,
            status=model.status,
            queue_position=model.queue_position,
            slicing_config=SlicingConfig(
                layer_height=model.layer_height,
                infill_density=model.infill_density,
                print_speed=model.print_speed,
                support_enabled=bool(model.support_enabled),
                adhesion_type=model.adhesion_type,
            ),
            gcode_path=model.gcode_path,
            estimated_time=timedelta(seconds=model.estimated_time_seconds) if model.estimated_time_seconds else None,
            estimated_material=model.estimated_material,
            actual_start_time=model.actual_start_time,
            actual_end_time=model.actual_end_time,
            progress=model.progress,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
