import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from src.main import app
from src.domain.enums.print_enums import TaskStatus, AdapterType, ConnectionType
from src.domain.value_objects.slicing_config import SlicingConfig


@pytest.fixture
def client():
    """
    创建测试客户端fixture
    
    Returns:
        TestClient: FastAPI测试客户端
    """
    return TestClient(app)


class TestPrintsRouter:
    """
    打印API路由测试
    """

    def test_create_print_task(self, client):
        """
        测试创建打印任务
        """
        model_id = str(uuid4())
        payload = {
            "model_id": model_id,
            "printer_id": "test_printer",
            "priority": 0
        }
        
        response = client.post("/api/v1/prints/tasks", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == model_id
        assert data["printer_id"] == "test_printer"
        assert data["status"] == TaskStatus.QUEUED.value

    def test_create_print_task_with_config(self, client):
        """
        测试使用自定义配置创建打印任务
        """
        model_id = str(uuid4())
        payload = {
            "model_id": model_id,
            "printer_id": "test_printer",
            "slicing_config": {
                "layer_height": 0.2,
                "infill_density": 20,
                "print_speed": 50,
                "travel_speed": 100,
                "support_enabled": False,
                "adhesion_type": "brim",
                "material_type": "pla",
                "nozzle_temperature": 210,
                "bed_temperature": 60
            },
            "priority": 5
        }
        
        response = client.post("/api/v1/prints/tasks", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == model_id

    def test_list_print_tasks(self, client):
        """
        测试获取所有打印任务
        """
        response = client.get("/api/v1/prints/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_print_task_not_found(self, client):
        """
        测试获取不存在的打印任务
        """
        task_id = str(uuid4())
        response = client.get(f"/api/v1/prints/tasks/{task_id}")
        
        assert response.status_code == 404

    def test_cancel_print_task_not_found(self, client):
        """
        测试取消不存在的打印任务
        """
        task_id = str(uuid4())
        response = client.delete(f"/api/v1/prints/tasks/{task_id}")
        
        assert response.status_code == 404

    def test_register_printer(self, client):
        """
        测试注册打印机
        """
        payload = {
            "name": "Test Bambu H2D",
            "model": "Bambu H2D",
            "adapter_type": "bambu",
            "connection_config": {
                "connection_type": "network",
                "host": "192.168.1.100",
                "port": 8883,
                "access_code": "12345678",
                "serial_number": "TEST123456",
                "use_ssl": True
            },
            "profile": {
                "bed_size": [256, 256, 256],
                "nozzle_diameter": 0.4,
                "filament_diameter": 1.75,
                "max_print_speed": 500,
                "max_travel_speed": 600,
                "firmware_flavor": "bambu",
                "supported_formats": [".gcode.3mf"]
            }
        }
        
        response = client.post("/api/v1/prints/printers", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Bambu H2D"
        assert data["model"] == "Bambu H2D"

    def test_list_printers(self, client):
        """
        测试获取所有打印机
        """
        response = client.get("/api/v1/prints/printers")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_queue_status(self, client):
        """
        测试获取队列状态
        """
        response = client.get("/api/v1/prints/queue")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pending_tasks" in data
        assert "estimated_wait_time" in data
