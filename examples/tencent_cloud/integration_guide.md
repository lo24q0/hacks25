# 图像风格化模块集成指南

## 概述

本文档说明如何将腾讯云图像风格化 API 集成到 3D 模型打印系统中。

## 在架构中的定位

根据 `ARCH.md` 设计,图像风格化属于 **风格化处理域(Style Processing Domain)**:

```
API Gateway
    ↓
风格化域 (Style Processing Domain)
    ↓
StyleEngine Service → 腾讯云图像风格化 API
    ↓
Storage Domain (保存风格化后的图片)
```

## 集成步骤

### 1. 目录结构

按照 `ARCH.md` 第 5.2 节的设计,相关代码应放置在:

```
backend/src/
├── domain/
│   ├── models/
│   │   └── style.py              # 风格化实体
│   ├── value_objects/
│   │   └── style_preset.py       # 风格预设值对象
│   └── interfaces/
│       └── i_style_engine.py     # 风格引擎接口
│
├── application/
│   └── services/
│       └── style_service.py      # 风格化应用服务
│
├── infrastructure/
│   └── ai/
│       ├── tencent_style_client.py  # 腾讯云客户端实现
│       └── base.py                   # AI客户端基类
│
├── api/
│   └── v1/
│       ├── routers/
│       │   └── styles.py         # 风格化路由
│       └── schemas/
│           └── style.py          # 请求/响应模型
│
└── infrastructure/
    └── tasks/
        └── style_tasks.py        # 异步风格化任务
```

### 2. 领域模型定义

#### 2.1 风格化任务实体 (domain/models/style.py)

```python
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class StyleTask:
    """风格化任务聚合根"""
    
    def __init__(
        self,
        id: UUID,
        image_path: str,
        style_preset_id: str,
        status: TaskStatus = TaskStatus.PENDING,
        result_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        self.id = id
        self.image_path = image_path
        self.style_preset_id = style_preset_id
        self.status = status
        self.result_path = result_path
        self.error_message = error_message
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def start_processing(self) -> None:
        """开始处理"""
        self.status = TaskStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self, result_path: str) -> None:
        """标记为完成"""
        self.status = TaskStatus.COMPLETED
        self.result_path = result_path
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, error_message: str) -> None:
        """标记为失败"""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == TaskStatus.COMPLETED
```

#### 2.2 风格预设值对象 (domain/value_objects/style_preset.py)

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class StylePreset:
    """风格预设值对象"""
    
    id: str
    name: str
    description: str
    tencent_style_code: str  # 腾讯云风格码
    strength_default: int    # 默认强度 0-100
    preview_image: str       # 预览图路径
    
    # 预定义的风格预设
    PRESETS = {
        "anime": {
            "id": "anime",
            "name": "动漫风格",
            "description": "将照片转换为日系动漫风格",
            "tencent_style_code": "101",
            "strength_default": 70,
            "preview_image": "/static/previews/anime.jpg",
        },
        "cartoon": {
            "id": "cartoon",
            "name": "卡通风格",
            "description": "美式卡通风格转换",
            "tencent_style_code": "102",
            "strength_default": 65,
            "preview_image": "/static/previews/cartoon.jpg",
        },
        "cartoon_3d": {
            "id": "cartoon_3d",
            "name": "3D卡通",
            "description": "3D卡通角色风格",
            "tencent_style_code": "103",
            "strength_default": 60,
            "preview_image": "/static/previews/cartoon_3d.jpg",
        },
    }
    
    @classmethod
    def from_id(cls, preset_id: str) -> "StylePreset":
        """从预设ID创建"""
        preset_data = cls.PRESETS.get(preset_id)
        if not preset_data:
            raise ValueError(f"未知的风格预设: {preset_id}")
        return cls(**preset_data)
    
    @classmethod
    def get_all_presets(cls) -> list["StylePreset"]:
        """获取所有预设"""
        return [cls(**data) for data in cls.PRESETS.values()]
```

#### 2.3 风格引擎接口 (domain/interfaces/i_style_engine.py)

```python
from abc import ABC, abstractmethod
from domain.models.style import StyleTask
from domain.value_objects.style_preset import StylePreset

class IStyleEngine(ABC):
    """风格引擎接口"""
    
    @abstractmethod
    async def transfer_style(
        self,
        image_path: str,
        style_preset: StylePreset,
        strength: int = None,
    ) -> str:
        """
        执行风格迁移
        
        Args:
            image_path: 输入图片路径
            style_preset: 风格预设
            strength: 风格强度,不传则使用预设默认值
            
        Returns:
            风格化后的图片路径
        """
        pass
```

### 3. 基础设施层实现

#### 3.1 腾讯云风格客户端 (infrastructure/ai/tencent_style_client.py)

参考 `examples/tencent_cloud/async_example.py` 中的 `TencentCloudStyleClient`,实现 `IStyleEngine` 接口:

```python
from domain.interfaces.i_style_engine import IStyleEngine
from domain.value_objects.style_preset import StylePreset
from infrastructure.config.settings import settings
# ... 其他导入

class TencentStyleEngine(IStyleEngine):
    """腾讯云风格引擎实现"""
    
    def __init__(self):
        self.client = TencentCloudStyleClient(
            secret_id=settings.TENCENT_SECRET_ID,
            secret_key=settings.TENCENT_SECRET_KEY,
            region=settings.TENCENT_REGION,
        )
    
    async def transfer_style(
        self,
        image_path: str,
        style_preset: StylePreset,
        strength: int = None,
    ) -> str:
        """实现风格迁移"""
        # 使用预设的强度或传入的强度
        strength = strength or style_preset.strength_default
        
        # 生成输出路径
        output_path = self._generate_output_path(image_path, style_preset.id)
        
        # 调用腾讯云 API
        result = self.client.transfer_style(
            input_image=image_path,
            output_path=output_path,
            style=style_preset.id,
            strength=strength,
        )
        
        if not result["success"]:
            raise StyleTransferException(result.get("error_message"))
        
        return output_path
```

### 4. 应用服务层

#### 4.1 风格化服务 (application/services/style_service.py)

```python
from uuid import uuid4
from domain.models.style import StyleTask, TaskStatus
from domain.value_objects.style_preset import StylePreset
from domain.interfaces.i_style_engine import IStyleEngine
from infrastructure.storage.base import IStorageService

class StyleService:
    """风格化应用服务"""
    
    def __init__(
        self,
        style_engine: IStyleEngine,
        storage_service: IStorageService,
    ):
        self.style_engine = style_engine
        self.storage_service = storage_service
    
    async def create_style_task(
        self,
        uploaded_file_path: str,
        style_preset_id: str,
        strength: int = None,
    ) -> StyleTask:
        """
        创建风格化任务
        
        Args:
            uploaded_file_path: 上传的图片路径
            style_preset_id: 风格预设ID
            strength: 风格强度
            
        Returns:
            创建的任务对象
        """
        # 创建任务
        task = StyleTask(
            id=uuid4(),
            image_path=uploaded_file_path,
            style_preset_id=style_preset_id,
        )
        
        # 发起异步处理(使用Celery)
        from infrastructure.tasks.style_tasks import process_style_task
        process_style_task.delay(
            task_id=str(task.id),
            image_path=uploaded_file_path,
            style_preset_id=style_preset_id,
            strength=strength,
        )
        
        return task
    
    async def get_task_status(self, task_id: str) -> StyleTask:
        """获取任务状态"""
        # 从缓存或数据库读取任务状态
        # MVP 阶段可以从 Redis 读取
        pass
    
    def get_available_styles(self) -> list[StylePreset]:
        """获取可用的风格列表"""
        return StylePreset.get_all_presets()
```

### 5. API 路由层

#### 5.1 风格化路由 (api/v1/routers/styles.py)

```python
from fastapi import APIRouter, UploadFile, File, Depends
from api.v1.schemas.style import (
    StyleTransferRequest,
    StyleTransferResponse,
    StylePresetResponse,
)
from application.services.style_service import StyleService

router = APIRouter(prefix="/styles", tags=["styles"])

@router.post("/transfer", response_model=StyleTransferResponse)
async def transfer_style(
    file: UploadFile = File(...),
    style_preset_id: str = "anime",
    strength: int = None,
    service: StyleService = Depends(get_style_service),
):
    """
    图片风格化转换
    
    - **file**: 上传的图片文件
    - **style_preset_id**: 风格预设ID (anime, cartoon, cartoon_3d)
    - **strength**: 风格强度 0-100(可选,不传则使用预设默认值)
    """
    # 保存上传文件
    file_path = await save_uploaded_file(file)
    
    # 创建风格化任务
    task = await service.create_style_task(
        uploaded_file_path=file_path,
        style_preset_id=style_preset_id,
        strength=strength,
    )
    
    return StyleTransferResponse(
        task_id=str(task.id),
        status=task.status.value,
        message="风格化任务已创建,正在处理中",
    )

@router.get("/presets", response_model=list[StylePresetResponse])
async def get_style_presets(
    service: StyleService = Depends(get_style_service),
):
    """获取所有可用的风格预设"""
    presets = service.get_available_styles()
    return [
        StylePresetResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            preview_image=p.preview_image,
        )
        for p in presets
    ]

@router.get("/tasks/{task_id}", response_model=StyleTransferResponse)
async def get_task_status(
    task_id: str,
    service: StyleService = Depends(get_style_service),
):
    """查询风格化任务状态"""
    task = await service.get_task_status(task_id)
    return StyleTransferResponse(
        task_id=str(task.id),
        status=task.status.value,
        result_url=task.result_path if task.is_completed() else None,
        error_message=task.error_message,
    )
```

### 6. 异步任务处理

#### 6.1 Celery 任务 (infrastructure/tasks/style_tasks.py)

```python
from infrastructure.tasks.celery_app import celery_app
from infrastructure.ai.tencent_style_client import TencentStyleEngine
from domain.value_objects.style_preset import StylePreset

@celery_app.task(bind=True, max_retries=3)
def process_style_task(
    self,
    task_id: str,
    image_path: str,
    style_preset_id: str,
    strength: int = None,
):
    """
    异步风格化任务
    
    Args:
        task_id: 任务ID
        image_path: 输入图片路径
        style_preset_id: 风格预设ID
        strength: 风格强度
    """
    try:
        # 获取风格预设
        style_preset = StylePreset.from_id(style_preset_id)
        
        # 执行风格化
        engine = TencentStyleEngine()
        result_path = await engine.transfer_style(
            image_path=image_path,
            style_preset=style_preset,
            strength=strength,
        )
        
        # 更新任务状态(存储到Redis或数据库)
        update_task_status(task_id, "completed", result_path=result_path)
        
    except Exception as exc:
        # 重试或标记失败
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=5)
        else:
            update_task_status(task_id, "failed", error_message=str(exc))
```

### 7. 配置管理

在 `infrastructure/config/settings.py` 添加:

```python
class Settings(BaseSettings):
    # ... 其他配置
    
    # 腾讯云配置
    TENCENT_SECRET_ID: str
    TENCENT_SECRET_KEY: str
    TENCENT_REGION: str = "ap-guangzhou"
    
    class Config:
        env_file = ".env"
```

在 `.env.example` 添加:

```bash
# 腾讯云 API 密钥
TENCENT_SECRET_ID=your_secret_id_here
TENCENT_SECRET_KEY=your_secret_key_here
TENCENT_REGION=ap-guangzhou
```

### 8. 前端集成

#### 8.1 API 客户端 (frontend/src/features/style-transfer/api/styleApi.ts)

```typescript
import axios from 'axios';

export interface StylePreset {
  id: string;
  name: string;
  description: string;
  preview_image: string;
}

export interface StyleTaskResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result_url?: string;
  error_message?: string;
}

export const styleApi = {
  // 获取风格预设列表
  async getPresets(): Promise<StylePreset[]> {
    const response = await axios.get('/api/v1/styles/presets');
    return response.data;
  },
  
  // 上传图片并开始风格化
  async transferStyle(
    file: File,
    styleId: string,
    strength?: number
  ): Promise<StyleTaskResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('style_preset_id', styleId);
    if (strength) {
      formData.append('strength', strength.toString());
    }
    
    const response = await axios.post('/api/v1/styles/transfer', formData);
    return response.data;
  },
  
  // 查询任务状态
  async getTaskStatus(taskId: string): Promise<StyleTaskResponse> {
    const response = await axios.get(`/api/v1/styles/tasks/${taskId}`);
    return response.data;
  },
};
```

## 测试清单

### 单元测试
- [ ] StyleTask 领域模型测试
- [ ] StylePreset 值对象测试
- [ ] TencentStyleEngine 单元测试(使用 mock)

### 集成测试
- [ ] API 端点测试
- [ ] 文件上传和风格化流程测试
- [ ] 异步任务执行测试

### 性能测试
- [ ] 单张图片处理时间 < 30秒
- [ ] 并发处理能力测试
- [ ] 大图片(5MB)处理测试

## 部署注意事项

1. **密钥安全**: SecretKey 必须通过环境变量传入,不能硬编码
2. **成本控制**: 建议设置每日调用次数上限
3. **超时处理**: Celery 任务超时时间建议设置为 60-90 秒
4. **错误重试**: 建议最多重试 3 次,使用指数退避
5. **结果缓存**: 相同图片+风格的结果可以缓存,避免重复调用

## 参考文档

- [INITIAL.md 第 2.2.2 节](../../INITIAL.md#222-照片风格化转动漫风格)
- [ARCH.md 第 3.1.2 节](../../ARCH.md#312-风格化处理域style-processing-domain)
- [腾讯云图像风格化 API 文档](https://cloud.tencent.com/document/product/1668/88066)
