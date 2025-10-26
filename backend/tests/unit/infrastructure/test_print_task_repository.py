import pytest
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.domain.models.print_task import PrintTask
from src.domain.enums.print_enums import TaskStatus
from src.domain.value_objects.slicing_config import SlicingConfig, AdhesionType, MaterialType
from src.infrastructure.persistence.database import Base
from src.infrastructure.persistence.repositories.print_task_repository import PrintTaskRepository


@pytest.fixture
async def async_engine():
    """
    创建异步测试引擎
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """
    创建异步测试会话
    """
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_task():
    """
    创建示例打印任务
    """
    return PrintTask(
        model_id=uuid4(),
        printer_id="test_printer_01",
        slicing_config=SlicingConfig(
            layer_height=0.2,
            infill_density=20,
            print_speed=50,
            travel_speed=100,
            support_enabled=False,
            adhesion_type=AdhesionType.BRIM,
            material_type=MaterialType.PLA,
            nozzle_temperature=210,
            bed_temperature=60
        )
    )


class TestPrintTaskRepository:
    """
    打印任务仓储测试
    """

    @pytest.mark.asyncio
    async def test_save_new_task(self, async_session, sample_task):
        """
        测试保存新任务
        """
        repository = PrintTaskRepository(async_session)
        
        result = await repository.save(sample_task)
        await async_session.commit()
        
        assert result.id == sample_task.id
        assert result.printer_id == "test_printer_01"
        assert result.status == TaskStatus.PENDING

    @pytest.mark.asyncio
    async def test_save_update_task(self, async_session, sample_task):
        """
        测试更新现有任务
        """
        repository = PrintTaskRepository(async_session)
        
        # 保存
        await repository.save(sample_task)
        await async_session.commit()
        
        # 更新
        sample_task.status = TaskStatus.QUEUED
        sample_task.queue_position = 1
        await repository.save(sample_task)
        await async_session.commit()
        
        # 查询验证
        found = await repository.find_by_id(sample_task.id)
        assert found.status == TaskStatus.QUEUED
        assert found.queue_position == 1

    @pytest.mark.asyncio
    async def test_find_by_id(self, async_session, sample_task):
        """
        测试根据ID查找任务
        """
        repository = PrintTaskRepository(async_session)
        
        await repository.save(sample_task)
        await async_session.commit()
        
        found = await repository.find_by_id(sample_task.id)
        
        assert found is not None
        assert found.id == sample_task.id
        assert found.printer_id == sample_task.printer_id

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, async_session):
        """
        测试查找不存在的任务
        """
        repository = PrintTaskRepository(async_session)
        
        found = await repository.find_by_id(uuid4())
        
        assert found is None

    @pytest.mark.asyncio
    async def test_find_all(self, async_session):
        """
        测试查找所有任务
        """
        repository = PrintTaskRepository(async_session)
        
        # 创建多个任务
        for i in range(3):
            task = PrintTask(
                model_id=uuid4(),
                printer_id=f"printer_{i}",
                slicing_config=SlicingConfig(
                    layer_height=0.2,
                    infill_density=20,
                    print_speed=50,
                    travel_speed=100,
                    support_enabled=False,
                    adhesion_type=AdhesionType.BRIM,
                    material_type=MaterialType.PLA,
                    nozzle_temperature=210,
                    bed_temperature=60
                )
            )
            await repository.save(task)
        
        await async_session.commit()
        
        tasks = await repository.find_all()
        
        assert len(tasks) == 3

    @pytest.mark.asyncio
    async def test_find_by_status(self, async_session):
        """
        测试根据状态查找任务
        """
        repository = PrintTaskRepository(async_session)
        
        # 创建不同状态的任务
        for status in [TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.PRINTING]:
            task = PrintTask(
                model_id=uuid4(),
                printer_id="test_printer",
                status=status,
                slicing_config=SlicingConfig(
                    layer_height=0.2,
                    infill_density=20,
                    print_speed=50,
                    travel_speed=100,
                    support_enabled=False,
                    adhesion_type=AdhesionType.BRIM,
                    material_type=MaterialType.PLA,
                    nozzle_temperature=210,
                    bed_temperature=60
                )
            )
            await repository.save(task)
        
        await async_session.commit()
        
        queued_tasks = await repository.find_by_status(TaskStatus.QUEUED)
        
        assert len(queued_tasks) == 1
        assert queued_tasks[0].status == TaskStatus.QUEUED

    @pytest.mark.asyncio
    async def test_find_queued_tasks(self, async_session):
        """
        测试查找排队任务
        """
        repository = PrintTaskRepository(async_session)
        
        # 创建排队任务
        for i in range(3):
            task = PrintTask(
                model_id=uuid4(),
                printer_id="test_printer",
                slicing_config=SlicingConfig(
                    layer_height=0.2,
                    infill_density=20,
                    print_speed=50,
                    travel_speed=100,
                    support_enabled=False,
                    adhesion_type=AdhesionType.BRIM,
                    material_type=MaterialType.PLA,
                    nozzle_temperature=210,
                    bed_temperature=60
                )
            )
            task.enqueue(i + 1)
            await repository.save(task)
        
        await async_session.commit()
        
        tasks = await repository.find_queued_tasks()
        
        assert len(tasks) == 3
        assert tasks[0].queue_position == 1
        assert tasks[1].queue_position == 2
        assert tasks[2].queue_position == 3

    @pytest.mark.asyncio
    async def test_delete(self, async_session, sample_task):
        """
        测试删除任务
        """
        repository = PrintTaskRepository(async_session)
        
        await repository.save(sample_task)
        await async_session.commit()
        
        result = await repository.delete(sample_task.id)
        await async_session.commit()
        
        assert result is True
        
        found = await repository.find_by_id(sample_task.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_count_by_status(self, async_session):
        """
        测试统计任务数量
        """
        repository = PrintTaskRepository(async_session)
        
        # 创建多个PENDING任务
        for i in range(5):
            task = PrintTask(
                model_id=uuid4(),
                printer_id="test_printer",
                slicing_config=SlicingConfig(
                    layer_height=0.2,
                    infill_density=20,
                    print_speed=50,
                    travel_speed=100,
                    support_enabled=False,
                    adhesion_type=AdhesionType.BRIM,
                    material_type=MaterialType.PLA,
                    nozzle_temperature=210,
                    bed_temperature=60
                )
            )
            await repository.save(task)
        
        await async_session.commit()
        
        count = await repository.count_by_status(TaskStatus.PENDING)
        
        assert count == 5
