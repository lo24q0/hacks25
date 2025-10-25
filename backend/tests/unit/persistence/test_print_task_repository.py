"""
打印任务仓储单元测试
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from domain.models.print_task import PrintTask
from domain.value_objects.slicing_config import SlicingConfig
from domain.enums.print_enums import TaskStatus
from infrastructure.persistence.database import Base
from infrastructure.persistence.repositories.print_task_repository import PrintTaskRepository


@pytest.fixture
async def engine():
    """
    创建测试数据库引擎
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def session(engine):
    """
    创建数据库会话
    """
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def sample_task():
    """
    创建示例打印任务
    """
    return PrintTask(
        id=uuid4(),
        model_id=uuid4(),
        printer_id="bambu_h2d_01",
        status=TaskStatus.PENDING,
        slicing_config=SlicingConfig(
            layer_height=0.2,
            infill_density=20,
            print_speed=50,
            support_enabled=False,
            adhesion_type="brim"
        )
    )


@pytest.mark.asyncio
class TestPrintTaskRepository:
    """
    测试PrintTaskRepository
    """
    
    async def test_save_new_task(self, session: AsyncSession, sample_task: PrintTask):
        """
        测试保存新任务
        """
        repo = PrintTaskRepository(session)
        
        await repo.save(sample_task)
        await session.commit()
        
        found = await repo.find_by_id(sample_task.id)
        
        assert found is not None
        assert found.id == sample_task.id
        assert found.model_id == sample_task.model_id
        assert found.printer_id == sample_task.printer_id
        assert found.status == TaskStatus.PENDING
    
    async def test_save_update_task(self, session: AsyncSession, sample_task: PrintTask):
        """
        测试更新现有任务
        """
        repo = PrintTaskRepository(session)
        
        await repo.save(sample_task)
        await session.commit()
        
        sample_task.start_slicing()
        sample_task.gcode_path = "/tmp/test.gcode"
        sample_task.estimated_time = timedelta(hours=2)
        
        await repo.save(sample_task)
        await session.commit()
        
        found = await repo.find_by_id(sample_task.id)
        
        assert found is not None
        assert found.status == TaskStatus.SLICING
        assert found.gcode_path == "/tmp/test.gcode"
        assert found.estimated_time == timedelta(hours=2)
    
    async def test_find_by_id_not_found(self, session: AsyncSession):
        """
        测试查询不存在的任务
        """
        repo = PrintTaskRepository(session)
        
        found = await repo.find_by_id(uuid4())
        
        assert found is None
    
    async def test_find_by_printer(self, session: AsyncSession):
        """
        测试按打印机ID查询
        """
        repo = PrintTaskRepository(session)
        
        task1 = PrintTask(
            id=uuid4(),
            model_id=uuid4(),
            printer_id="printer1",
            status=TaskStatus.PENDING,
            slicing_config=SlicingConfig(
                layer_height=0.2,
                infill_density=20,
                print_speed=50,
                support_enabled=False,
                adhesion_type="brim"
            )
        )
        
        task2 = PrintTask(
            id=uuid4(),
            model_id=uuid4(),
            printer_id="printer1",
            status=TaskStatus.QUEUED,
            slicing_config=SlicingConfig(
                layer_height=0.2,
                infill_density=20,
                print_speed=50,
                support_enabled=False,
                adhesion_type="brim"
            )
        )
        
        task3 = PrintTask(
            id=uuid4(),
            model_id=uuid4(),
            printer_id="printer2",
            status=TaskStatus.PENDING,
            slicing_config=SlicingConfig(
                layer_height=0.2,
                infill_density=20,
                print_speed=50,
                support_enabled=False,
                adhesion_type="brim"
            )
        )
        
        await repo.save(task1)
        await repo.save(task2)
        await repo.save(task3)
        await session.commit()
        
        tasks = await repo.find_by_printer("printer1")
        
        assert len(tasks) == 2
        assert all(t.printer_id == "printer1" for t in tasks)
    
    async def test_find_by_status(self, session: AsyncSession):
        """
        测试按状态查询
        """
        repo = PrintTaskRepository(session)
        
        task1 = PrintTask(
            id=uuid4(),
            model_id=uuid4(),
            printer_id="printer1",
            status=TaskStatus.PENDING,
            slicing_config=SlicingConfig(
                layer_height=0.2,
                infill_density=20,
                print_speed=50,
                support_enabled=False,
                adhesion_type="brim"
            )
        )
        
        task2 = PrintTask(
            id=uuid4(),
            model_id=uuid4(),
            printer_id="printer2",
            status=TaskStatus.QUEUED,
            slicing_config=SlicingConfig(
                layer_height=0.2,
                infill_density=20,
                print_speed=50,
                support_enabled=False,
                adhesion_type="brim"
            )
        )
        
        await repo.save(task1)
        await repo.save(task2)
        await session.commit()
        
        pending_tasks = await repo.find_by_status(TaskStatus.PENDING)
        
        assert len(pending_tasks) == 1
        assert pending_tasks[0].status == TaskStatus.PENDING
    
    async def test_delete_task(self, session: AsyncSession, sample_task: PrintTask):
        """
        测试删除任务
        """
        repo = PrintTaskRepository(session)
        
        await repo.save(sample_task)
        await session.commit()
        
        deleted = await repo.delete(sample_task.id)
        await session.commit()
        
        assert deleted is True
        
        found = await repo.find_by_id(sample_task.id)
        assert found is None
    
    async def test_delete_nonexistent_task(self, session: AsyncSession):
        """
        测试删除不存在的任务
        """
        repo = PrintTaskRepository(session)
        
        deleted = await repo.delete(uuid4())
        
        assert deleted is False
