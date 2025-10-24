# 3D模型打印系统技术架构设计文档

## 1. 架构概述

### 1.1 架构设计原则

本系统架构设计遵循以下核心原则：

- **高内聚低耦合**：各业务模块职责清晰，模块间通过明确的接口交互
- **分层架构**：表现层、应用层、领域层、基础设施层职责分离
- **领域驱动设计（DDD）**：以业务领域为核心组织代码结构
- **可扩展性**：支持从MVP到生产环境的平滑演进
- **容错性**：异步任务处理，支持重试和失败恢复
- **可测试性**：各层独立可测试，便于单元测试和集成测试

### 1.2 整体架构视图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户界面层                           │
│                    (React SPA + Three.js)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                      API Gateway Layer                      │
│                      (FastAPI Routers)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼─────┐  ┌────────▼────────┐  ┌────▼──────────┐
│   模型生成   │  │   风格化处理     │  │  打印适配     │
│   服务模块   │  │   服务模块       │  │  服务模块     │
└───────┬─────┘  └────────┬────────┘  └────┬──────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      领域服务层                              │
│      (Model Domain | Style Domain | Print Domain)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼─────┐  ┌────────▼────────┐  ┌────▼──────────┐
│  AI引擎层    │  │   存储服务      │  │  任务队列     │
│ (Meshy API)  │  │  (File/DB)      │  │ (Celery)      │
└─────────────┘  └─────────────────┘  └───────────────┘
```

---

## 2. 技术选型

### 2.1 前端技术栈

| 技术类别 | 选型 | 版本要求 | 选型理由 |
|---------|------|---------|---------|
| 核心框架 | React | 18.3+ | 生态成熟，组件化开发，适合SPA |
| 3D渲染引擎 | Three.js | r160+ | 功能强大，WebGL渲染性能优异 |
| React 3D库 | React Three Fiber | 8.0+ | React组件化封装Three.js，开发效率高 |
| UI框架 | Tailwind CSS | 3.4+ | 原子化CSS，快速开发，包体积小 |
| 组件库 | Headless UI | 2.0+ | 无样式UI组件，配合Tailwind使用 |
| 状态管理 | Zustand | 4.5+ | 轻量级，API简洁，适合中小型项目 |
| 文件上传 | React Dropzone | 14.0+ | 拖拽上传，预览功能完善 |
| HTTP客户端 | Axios | 1.6+ | 请求拦截、错误处理、取消请求 |
| 构建工具 | Vite | 5.0+ | 快速热更新，构建性能优异 |

### 2.2 后端技术栈

| 技术类别 | 选型 | 版本要求 | 选型理由 |
|---------|------|---------|---------|
| 编程语言 | Python | 3.10-3.12 | AI生态丰富，库兼容性最佳 |
| Web框架 | FastAPI | 0.115+ | 高性能异步框架，自动API文档 |
| ASGI服务器 | Uvicorn | 0.30+ | 高性能ASGI服务器，支持WebSocket |
| AI框架 | PyTorch | 2.5+ | 深度学习主流框架 |
| 3D处理 | trimesh | 4.5+ | STL/OBJ处理，模型修复 |
| 3D处理 | open3d | 0.18+ | 点云处理，网格优化 |
| 任务队列 | Celery | 5.5+ | 异步任务处理，支持重试 |
| 消息队列 | Redis | 7.0+ | 高性能，作为Celery broker |
| 数据库（P2） | PostgreSQL | 15+ | 关系型数据，支持JSON字段 |
| ORM（P2） | SQLAlchemy | 2.0+ | 异步支持，类型提示完善 |
| 认证（P2） | PyJWT | 2.8+ | JWT token生成和验证 |

### 2.3 AI服务选型

| 服务类别 | 选型 | 备选方案 | 说明 |
|---------|------|---------|------|
| 文本转3D | Meshy.ai API | Shap-E (OpenAI) | API稳定，效果好 |
| 图片转3D | Meshy.ai API | TripoSR (Stability AI) | 单张图片即可生成 |
| 风格化 | AnimeGANv3 | CartoonGAN | 动漫风格效果最佳 |
| 切片引擎 | CuraEngine | PrusaSlicer CLI | 拓竹官方推荐 |

### 2.4 开发和部署工具

| 类别 | 选型 | 版本 |
|-----|------|------|
| 容器化 | Docker | 24.0+ |
| 编排工具 | Docker Compose | 2.20+ |
| 反向代理 | Nginx | 1.24+ |
| 对象存储 | MinIO | Latest |
| 监控（未来） | Prometheus + Grafana | Latest |

---

## 3. 业务模块设计

### 3.1 模块划分（基于DDD）

系统按照业务领域划分为以下核心模块：

#### 3.1.1 模型生成域（Model Generation Domain）

**职责**：
- 接收用户输入（文本/图片）
- 调用AI服务生成3D模型
- 模型格式转换和验证
- 模型预览数据生成

**核心实体**：
- `ModelGenerationTask`：生成任务
- `Model3D`：3D模型聚合根
- `ModelMetadata`：模型元数据（尺寸、面数）

**对外接口**：
- `IModelGenerator`：模型生成接口
- `IModelConverter`：格式转换接口
- `IModelValidator`：模型验证接口

#### 3.1.2 风格化处理域（Style Processing Domain）

**职责**：
- 图片风格迁移
- 风格预设管理
- 风格化效果预览

**核心实体**：
- `StyleTask`：风格化任务
- `StylePreset`：风格预设
- `StyledImage`：风格化后的图片

**对外接口**：
- `IStyleTransfer`：风格迁移接口
- `IStylePresetRepository`：风格预设仓储

#### 3.1.3 打印适配域（Print Adaptation Domain）

**职责**：
- 模型切片处理
- G-code生成
- 打印参数配置
- 打印机适配

**核心实体**：
- `PrintTask`：打印任务
- `PrinterProfile`：打印机配置
- `SlicingConfig`：切片参数
- `GCode`：G-code文件

**对外接口**：
- `ISlicer`：切片引擎接口
- `IPrinterAdapter`：打印机适配器接口

#### 3.1.4 用户管理域（User Domain - P2）

**职责**：
- 用户注册和认证
- 用户历史记录
- 用户配额管理

**核心实体**：
- `User`：用户聚合根
- `UserSession`：用户会话
- `UserQuota`：用户配额

#### 3.1.5 文件存储域（Storage Domain）

**职责**：
- 文件上传下载
- 临时文件清理
- 对象存储管理

**核心实体**：
- `FileObject`：文件对象
- `StoragePolicy`：存储策略

### 3.2 模块协作关系

```
┌─────────────────────────────────────────────────────────┐
│                     API Gateway                         │
└───────┬─────────────────────┬─────────────────┬─────────┘
        │                     │                 │
        │                     │                 │
┌───────▼─────────┐  ┌────────▼──────┐  ┌──────▼─────────┐
│  模型生成域      │  │  风格化域      │  │  打印适配域     │
│                 │  │                │  │                │
│ ┌─────────────┐ │  │ ┌────────────┐ │  │ ┌────────────┐ │
│ │Generator    │ │  │ │StyleEngine │ │  │ │SliceEngine │ │
│ │Service      │ │  │ │Service     │ │  │ │Service     │ │
│ └──────┬──────┘ │  │ └─────┬──────┘ │  │ └──────┬─────┘ │
│        │        │  │       │        │  │        │       │
│ ┌──────▼──────┐ │  │ ┌─────▼──────┐ │  │ ┌──────▼─────┐ │
│ │Model Entity │ │  │ │Style Entity│ │  │ │Print Entity│ │
│ └─────────────┘ │  │ └────────────┘ │  │ └────────────┘ │
└────────┬────────┘  └────────┬───────┘  └────────┬───────┘
         │                    │                   │
         └────────────────────┼───────────────────┘
                              │
                 ┌────────────▼────────────┐
                 │   Shared Infrastructure │
                 │  ┌──────────────────┐   │
                 │  │ Storage Service  │   │
                 │  └──────────────────┘   │
                 │  ┌──────────────────┐   │
                 │  │ Task Queue       │   │
                 │  └──────────────────┘   │
                 │  ┌──────────────────┐   │
                 │  │ AI Client        │   │
                 │  └──────────────────┘   │
                 └─────────────────────────┘
```

**协作流程示例（文本生成3D模型并打印）**：

```
用户请求
   │
   ▼
API Gateway ─────┐
   │             │
   ▼             │
模型生成域        │
   │ 1. 创建生成任务
   │ 2. 调用Meshy API
   │ 3. 保存STL文件
   ▼             │
Storage Domain   │
   │             │
   ▼             │
返回模型ID ───────┤
                 │
用户请求打印 ──────┘
   │
   ▼
打印适配域
   │ 1. 读取STL文件
   │ 2. 调用CuraEngine
   │ 3. 生成G-code
   ▼
返回G-code下载链接
```

### 3.3 模块依赖关系

**依赖层级（从上到下）**：

1. **API层**：依赖应用服务层
2. **应用服务层**：依赖领域服务层
3. **领域服务层**：依赖领域模型和基础设施接口
4. **领域模型层**：不依赖任何外部模块（纯业务逻辑）
5. **基础设施层**：实现领域服务定义的接口

**关键设计点**：
- 领域层定义接口，基础设施层实现接口（依赖倒置）
- 模块间通过接口交互，不直接依赖具体实现
- 使用事件驱动处理跨模块通信（未来扩展）

---

## 4. 领域模型设计

### 4.1 核心领域对象

#### 4.1.1 模型生成域

```python
# 聚合根
class Model3D:
    """3D模型聚合根"""
    id: UUID
    user_id: Optional[UUID]  # P2阶段引入
    source_type: SourceType  # TEXT | IMAGE
    source_data: SourceData  # 文本描述或图片路径
    status: ModelStatus      # PENDING | PROCESSING | COMPLETED | FAILED
    file_path: Optional[str] # STL文件路径
    thumbnail_path: Optional[str]
    metadata: ModelMetadata
    created_at: datetime
    updated_at: datetime

    # 领域方法
    def start_generation(self) -> None
    def mark_completed(self, file_path: str) -> None
    def mark_failed(self, error: str) -> None
    def validate_for_printing(self) -> ValidationResult

# 值对象
class ModelMetadata:
    """模型元数据（值对象）"""
    dimensions: Dimensions   # 尺寸 (x, y, z) mm
    volume: float           # 体积 mm³
    triangle_count: int     # 三角面数
    vertex_count: int       # 顶点数
    is_manifold: bool       # 是否流形（可打印）
    bounding_box: BoundingBox

class SourceData:
    """源数据（值对象）"""
    text_prompt: Optional[str]
    image_paths: Optional[List[str]]
    style_preset: Optional[str]  # 风格化预设ID

# 枚举
class SourceType(Enum):
    TEXT = "text"
    IMAGE = "image"

class ModelStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

#### 4.1.2 风格化域

```python
class StyleTask:
    """风格化任务"""
    id: UUID
    image_path: str
    style_preset_id: str
    status: TaskStatus
    result_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    def apply_style(self, engine: IStyleEngine) -> None
    def is_completed(self) -> bool

class StylePreset:
    """风格预设"""
    id: str
    name: str
    description: str
    model_name: str         # AnimeGANv3, CartoonGAN
    parameters: Dict[str, Any]
    preview_image: str

    def to_config(self) -> StyleConfig
```

#### 4.1.3 打印适配域

```python
class PrintTask:
    """打印任务聚合根"""
    id: UUID
    model_id: UUID          # 关联的3D模型ID
    printer_profile_id: str
    slicing_config: SlicingConfig
    status: TaskStatus
    gcode_path: Optional[str]
    estimated_time: Optional[timedelta]
    estimated_material: Optional[float]  # 克
    created_at: datetime

    def start_slicing(self) -> None
    def update_estimates(self, time: timedelta, material: float) -> None

class PrinterProfile:
    """打印机配置（值对象）"""
    id: str
    name: str               # "拓竹 H2D"
    bed_size: Tuple[int, int, int]  # 打印尺寸 (x, y, z) mm
    nozzle_diameter: float  # 喷嘴直径 mm
    filament_diameter: float
    max_speed: int          # mm/s
    firmware_flavor: str    # Marlin, Klipper

class SlicingConfig:
    """切片配置（值对象）"""
    layer_height: float     # 层高 0.1-0.3mm
    infill_density: int     # 填充率 0-100%
    print_speed: int        # mm/s
    support_enabled: bool
    adhesion_type: str      # skirt, brim, raft

    def validate(self) -> ValidationResult
```

#### 4.1.4 用户域（P2）

```python
class User:
    """用户聚合根"""
    id: UUID
    email: str
    hashed_password: str
    username: str
    quota: UserQuota
    created_at: datetime
    last_login: Optional[datetime]

    def authenticate(self, password: str) -> bool
    def consume_quota(self, task_type: TaskType) -> None
    def can_create_task(self, task_type: TaskType) -> bool

class UserQuota:
    """用户配额（值对象）"""
    max_models: int = 50
    max_daily_generations: int = 20
    current_model_count: int
    today_generation_count: int
    reset_date: date
```

#### 4.1.5 文件存储域

```python
class FileObject:
    """文件对象"""
    id: UUID
    object_key: str         # 存储路径
    original_filename: str
    content_type: str
    size_bytes: int
    storage_backend: StorageBackend  # LOCAL | MINIO | S3
    ttl: Optional[timedelta]  # 临时文件生存时间
    created_at: datetime

    def get_download_url(self) -> str
    def should_cleanup(self) -> bool

class StorageBackend(Enum):
    LOCAL = "local"
    MINIO = "minio"
    S3 = "s3"
```

### 4.2 领域服务接口

```python
# 模型生成域服务接口
class IModelGenerator(ABC):
    @abstractmethod
    async def generate_from_text(self, prompt: str) -> Model3D:
        pass

    @abstractmethod
    async def generate_from_image(self, image_path: str) -> Model3D:
        pass

class IModelConverter(ABC):
    @abstractmethod
    def convert_to_stl(self, model_path: str) -> str:
        pass

    @abstractmethod
    def extract_metadata(self, stl_path: str) -> ModelMetadata:
        pass

# 风格化域服务接口
class IStyleEngine(ABC):
    @abstractmethod
    async def transfer_style(self, image_path: str, style: StylePreset) -> str:
        pass

# 打印适配域服务接口
class ISlicer(ABC):
    @abstractmethod
    async def slice_model(
        self,
        stl_path: str,
        printer: PrinterProfile,
        config: SlicingConfig
    ) -> GCodeResult:
        pass

# 存储域服务接口
class IStorageService(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, ttl: Optional[timedelta]) -> FileObject:
        pass

    @abstractmethod
    async def download_file(self, object_key: str) -> bytes:
        pass

    @abstractmethod
    async def cleanup_expired_files(self) -> int:
        pass
```

### 4.3 领域事件（未来扩展）

```python
class DomainEvent(ABC):
    event_id: UUID
    occurred_at: datetime
    aggregate_id: UUID

class ModelGenerationCompleted(DomainEvent):
    model_id: UUID
    file_path: str

class ModelGenerationFailed(DomainEvent):
    model_id: UUID
    error_message: str

class PrintTaskCreated(DomainEvent):
    task_id: UUID
    model_id: UUID
```

---

## 5. 项目目录结构

### 5.1 整体结构

```
3d-print-platform/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── app/             # 应用入口
│   │   ├── features/        # 功能模块（按领域划分）
│   │   ├── shared/          # 共享组件和工具
│   │   └── infrastructure/  # 基础设施（API客户端）
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                  # 后端项目
│   ├── src/
│   │   ├── api/             # API层（FastAPI路由）
│   │   ├── application/     # 应用服务层
│   │   ├── domain/          # 领域模型层
│   │   ├── infrastructure/  # 基础设施层
│   │   ├── shared/          # 共享工具
│   │   └── main.py          # 应用入口
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
│
├── infrastructure/           # 基础设施配置
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.frontend
│   │   └── Dockerfile.worker
│   ├── nginx/
│   │   └── nginx.conf
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
│
├── scripts/                  # 脚本工具
│   ├── setup.sh
│   ├── migrate.py
│   └── cleanup.py
│
├── docs/                     # 文档
│   ├── INITIAL.md
│   ├── ARCH.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── .env.example
├── .gitignore
└── README.md
```

### 5.2 后端详细结构

```
backend/src/
├── api/                      # API层（表现层）
│   ├── __init__.py
│   ├── deps.py              # 依赖注入
│   ├── errors.py            # 错误处理
│   ├── middleware.py        # 中间件
│   └── v1/                  # API版本
│       ├── __init__.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── models.py    # /api/v1/models
│       │   ├── styles.py    # /api/v1/styles
│       │   ├── prints.py    # /api/v1/prints
│       │   └── users.py     # /api/v1/users (P2)
│       ├── schemas/         # API请求/响应模型（Pydantic）
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── style.py
│       │   └── print.py
│       └── dependencies/
│           └── auth.py      # 认证依赖（P2）
│
├── application/             # 应用服务层
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── model_service.py      # 模型生成应用服务
│   │   ├── style_service.py      # 风格化应用服务
│   │   ├── print_service.py      # 打印应用服务
│   │   └── user_service.py       # 用户服务（P2）
│   ├── dto/                      # 数据传输对象
│   │   ├── __init__.py
│   │   ├── model_dto.py
│   │   └── print_dto.py
│   └── use_cases/                # 用例（可选，复杂业务流程）
│       ├── __init__.py
│       └── generate_and_slice.py
│
├── domain/                  # 领域模型层（核心业务逻辑）
│   ├── __init__.py
│   ├── models/              # 领域模型
│   │   ├── __init__.py
│   │   ├── model3d.py       # 3D模型聚合根
│   │   ├── style.py         # 风格化实体
│   │   ├── print_task.py    # 打印任务聚合根
│   │   └── user.py          # 用户聚合根（P2）
│   ├── value_objects/       # 值对象
│   │   ├── __init__.py
│   │   ├── metadata.py
│   │   ├── printer_profile.py
│   │   └── slicing_config.py
│   ├── enums/              # 枚举
│   │   ├── __init__.py
│   │   ├── status.py
│   │   └── source_type.py
│   ├── interfaces/         # 领域服务接口
│   │   ├── __init__.py
│   │   ├── i_model_generator.py
│   │   ├── i_style_engine.py
│   │   ├── i_slicer.py
│   │   └── i_repository.py
│   └── events/             # 领域事件（未来扩展）
│       ├── __init__.py
│       └── model_events.py
│
├── infrastructure/          # 基础设施层
│   ├── __init__.py
│   ├── ai/                 # AI服务实现
│   │   ├── __init__.py
│   │   ├── meshy_client.py      # Meshy.ai客户端
│   │   ├── anime_gan.py         # 风格化模型
│   │   └── base.py              # AI客户端基类
│   ├── slicing/            # 切片引擎实现
│   │   ├── __init__.py
│   │   ├── cura_engine.py
│   │   └── base.py
│   ├── storage/            # 存储实现
│   │   ├── __init__.py
│   │   ├── local_storage.py
│   │   ├── minio_storage.py
│   │   └── base.py
│   ├── persistence/        # 数据持久化（P2）
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models/         # SQLAlchemy模型
│   │   │   ├── __init__.py
│   │   │   ├── user_model.py
│   │   │   └── model_record.py
│   │   └── repositories/   # 仓储实现
│   │       ├── __init__.py
│   │       ├── model_repository.py
│   │       └── user_repository.py
│   ├── tasks/              # 异步任务
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── model_tasks.py
│   │   └── cleanup_tasks.py
│   └── config/             # 配置管理
│       ├── __init__.py
│       ├── settings.py
│       └── logging.py
│
├── shared/                  # 共享工具
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── mesh_utils.py
│   │   └── validation.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── domain_exceptions.py
│   │   └── infrastructure_exceptions.py
│   └── constants/
│       ├── __init__.py
│       └── config.py
│
└── main.py                  # FastAPI应用入口
```

### 5.3 前端详细结构

```
frontend/src/
├── app/                     # 应用入口
│   ├── App.tsx
│   ├── main.tsx
│   ├── router.tsx
│   └── store.ts             # Zustand store
│
├── features/                # 功能模块（按业务领域）
│   ├── model-generation/    # 模型生成模块
│   │   ├── components/
│   │   │   ├── TextInput.tsx
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── ModelPreview.tsx    # Three.js预览
│   │   │   └── GenerationProgress.tsx
│   │   ├── hooks/
│   │   │   ├── useModelGeneration.ts
│   │   │   └── useModelPreview.ts
│   │   ├── api/
│   │   │   └── modelApi.ts
│   │   ├── types/
│   │   │   └── model.types.ts
│   │   └── pages/
│   │       └── GenerationPage.tsx
│   │
│   ├── style-transfer/      # 风格化模块
│   │   ├── components/
│   │   │   ├── StyleSelector.tsx
│   │   │   └── StylePreview.tsx
│   │   ├── hooks/
│   │   │   └── useStyleTransfer.ts
│   │   └── api/
│   │       └── styleApi.ts
│   │
│   ├── print-preparation/   # 打印准备模块
│   │   ├── components/
│   │   │   ├── PrinterSelector.tsx
│   │   │   ├── SlicingConfig.tsx
│   │   │   └── GCodeDownload.tsx
│   │   ├── hooks/
│   │   │   └── usePrintSlicing.ts
│   │   └── api/
│   │       └── printApi.ts
│   │
│   └── user/                # 用户模块（P2）
│       ├── components/
│       │   ├── LoginForm.tsx
│       │   └── ModelHistory.tsx
│       ├── hooks/
│       │   └── useAuth.ts
│       └── api/
│           └── authApi.ts
│
├── shared/                  # 共享组件和工具
│   ├── components/
│   │   ├── ui/             # UI基础组件
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loading.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Layout.tsx
│   ├── hooks/
│   │   ├── useAsync.ts
│   │   └── useLocalStorage.ts
│   ├── utils/
│   │   ├── format.ts
│   │   └── validation.ts
│   └── types/
│       └── common.types.ts
│
├── infrastructure/          # 基础设施
│   ├── api/
│   │   ├── client.ts        # Axios配置
│   │   ├── interceptors.ts
│   │   └── endpoints.ts
│   └── three/               # Three.js封装
│       ├── SceneManager.ts
│       ├── ModelLoader.ts
│       └── Controls.ts
│
├── assets/                  # 静态资源
│   ├── images/
│   ├── fonts/
│   └── styles/
│       └── globals.css
│
└── types/                   # 全局类型定义
    └── index.d.ts
```

### 5.4 目录设计说明

#### 5.4.1 分层职责

1. **API层**：
   - 处理HTTP请求/响应
   - 数据验证（Pydantic）
   - 路由定义
   - 不包含业务逻辑

2. **应用服务层**：
   - 编排业务流程
   - 调用领域服务
   - 事务管理
   - DTO转换

3. **领域层**：
   - 核心业务逻辑
   - 领域模型和值对象
   - 定义接口（不依赖具体实现）
   - 纯粹的业务规则

4. **基础设施层**：
   - 实现领域接口
   - 外部服务集成
   - 数据持久化
   - 第三方库封装

#### 5.4.2 依赖方向

```
API层 ──→ 应用服务层 ──→ 领域层 ←── 基础设施层
                              ↑
                              │
                        定义接口，
                        基础设施实现
```

#### 5.4.3 模块化原则

- **前端按功能模块组织**：每个feature包含完整的UI、逻辑、API调用
- **后端按分层架构组织**：清晰的职责分离
- **共享代码独立管理**：避免循环依赖
- **测试代码镜像源码结构**：便于定位和维护

---

## 6. 数据流设计

### 6.1 请求处理流程

**示例：文本生成3D模型**

```
1. 用户输入文本 → React组件
                    ↓
2. 调用API → axios.post('/api/v1/models/generate/text')
                    ↓
3. API路由 → ModelRouter.generate_from_text()
                    ↓
4. 应用服务 → ModelService.create_from_text()
                    ↓
5. 创建领域对象 → Model3D(status=PENDING)
                    ↓
6. 持久化（P2）→ ModelRepository.save()
                    ↓
7. 发起异步任务 → Celery.generate_model_task.delay()
                    ↓
8. 返回任务ID → Response(task_id, status)
                    ↓
9. 前端轮询状态 → GET /api/v1/models/{id}
                    ↓
10. 异步任务执行：
    - MeshyClient.generate_from_text()
    - 下载模型文件
    - 转换为STL
    - 提取元数据
    - 更新Model3D状态为COMPLETED
                    ↓
11. 前端获取完成状态
                    ↓
12. 加载3D预览 → ModelPreview组件（Three.js）
```

### 6.2 异步任务设计

**任务类型**：

1. **模型生成任务**：
   - 执行时间：30-120秒
   - 重试策略：失败后重试3次
   - 超时时间：300秒

2. **风格化任务**：
   - 执行时间：10-30秒
   - 重试策略：失败后重试2次
   - 超时时间：60秒

3. **切片任务**：
   - 执行时间：10-30秒
   - 重试策略：失败后重试2次
   - 超时时间：60秒

4. **定时清理任务**：
   - 执行周期：每小时
   - 清理过期临时文件

**Celery配置**：
```python
# 任务队列划分
CELERY_TASK_ROUTES = {
    'tasks.model_generation.*': {'queue': 'generation'},
    'tasks.style_transfer.*': {'queue': 'style'},
    'tasks.slicing.*': {'queue': 'slicing'},
    'tasks.cleanup.*': {'queue': 'maintenance'},
}

# 并发配置
CELERY_WORKER_CONCURRENCY = {
    'generation': 2,  # GPU密集型，限制并发
    'style': 2,       # GPU密集型
    'slicing': 4,     # CPU密集型
    'maintenance': 1,
}
```

---

## 7. API设计概要

### 7.1 RESTful API规范

**基础路径**：`/api/v1`

**认证方式**（P2）：
- JWT Bearer Token
- Header: `Authorization: Bearer <token>`

**响应格式**：
```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2025-10-24T10:00:00Z"
}
```

### 7.2 核心API端点

#### 7.2.1 模型生成

```
POST   /api/v1/models/generate/text
POST   /api/v1/models/generate/image
GET    /api/v1/models/{id}
GET    /api/v1/models/{id}/download
DELETE /api/v1/models/{id}
GET    /api/v1/models (P2 - 用户历史)
```

#### 7.2.2 风格化

```
POST   /api/v1/styles/transfer
GET    /api/v1/styles/presets
GET    /api/v1/styles/tasks/{id}
```

#### 7.2.3 打印适配

```
POST   /api/v1/prints/slice
GET    /api/v1/prints/printers
GET    /api/v1/prints/tasks/{id}
GET    /api/v1/prints/tasks/{id}/gcode
```

#### 7.2.4 用户管理（P2）

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/users/me
GET    /api/v1/users/me/quota
```

### 7.3 WebSocket（未来扩展）

```
WS /ws/tasks/{task_id}
```
实时推送任务进度（生成百分比、当前步骤）。

---

## 8. 安全性设计

### 8.1 安全措施

1. **输入验证**：
   - 文本长度限制（10-1000字符）
   - 图片格式限制（JPG/PNG）
   - 文件大小限制（10MB）
   - 文件类型验证（MIME类型检查）

2. **认证授权**（P2）：
   - JWT token有效期：7天
   - Refresh token机制
   - 密码强度校验
   - 密码加密存储（bcrypt）

3. **API限流**：
   - 匿名用户：10次/小时
   - 登录用户：100次/小时
   - IP级别限流

4. **文件安全**：
   - 上传文件病毒扫描（可选）
   - 随机文件名（UUID）
   - 临时文件自动清理（24小时）
   - 路径遍历防护

5. **CORS配置**：
   - 生产环境严格限制允许的域名
   - 开发环境允许localhost

### 8.2 数据隐私

- 用户上传的图片不用于模型训练
- 生成的模型仅用户可见（P2后）
- 敏感信息加密存储
- 遵守GDPR/CCPA规范（未来）

---

## 9. 性能优化策略

### 9.1 前端优化

1. **资源优化**：
   - Three.js按需加载
   - 图片懒加载
   - 代码分割（Vite动态导入）
   - Gzip压缩

2. **渲染优化**：
   - 模型LOD（细节层次）
   - Web Worker处理大文件
   - 虚拟滚动（历史记录）

3. **缓存策略**：
   - Service Worker缓存静态资源
   - LocalStorage缓存用户配置
   - IndexedDB缓存模型元数据

### 9.2 后端优化

1. **计算优化**：
   - 异步任务处理（Celery）
   - GPU加速（PyTorch CUDA）
   - 模型批处理（未来）

2. **存储优化**：
   - 文件分片上传（大文件）
   - 对象存储CDN加速
   - 临时文件定期清理

3. **数据库优化**（P2）：
   - 索引优化（user_id, created_at）
   - 连接池管理
   - 查询缓存（Redis）

4. **API优化**：
   - 响应压缩
   - HTTP/2支持
   - API结果缓存（短期）

### 9.3 可扩展性设计

**水平扩展点**：
- Celery Worker可独立扩展（GPU节点）
- 前端静态资源CDN分发
- 对象存储分布式部署
- 数据库读写分离（未来）

**垂直扩展点**：
- GPU显存升级（支持更大模型）
- 增加CPU核心数（切片并发）

---

## 10. 监控和可观测性

### 10.1 日志设计

**日志级别**：
- **DEBUG**：详细调试信息
- **INFO**：关键业务流程节点
- **WARNING**：可恢复的异常
- **ERROR**：需要人工介入的错误
- **CRITICAL**：系统级故障

**日志内容**：
```python
{
  "timestamp": "2025-10-24T10:00:00Z",
  "level": "INFO",
  "service": "model-generation",
  "trace_id": "uuid",
  "user_id": "uuid",
  "message": "Model generation started",
  "metadata": {
    "task_id": "uuid",
    "source_type": "text"
  }
}
```

**日志存储**：
- 开发环境：控制台输出
- 生产环境：文件 + ELK Stack（未来）

### 10.2 指标监控（未来）

**业务指标**：
- 每日生成模型数
- 生成成功率
- 平均生成时间
- 用户活跃度

**技术指标**：
- API响应时间（P50/P95/P99）
- Celery队列长度
- GPU利用率
- 存储使用率
- 错误率

**监控工具**：
- Prometheus：指标采集
- Grafana：可视化
- Sentry：错误追踪

### 10.3 健康检查

```
GET /health
{
  "status": "healthy",
  "services": {
    "api": "up",
    "celery": "up",
    "redis": "up",
    "database": "up",
    "storage": "up"
  }
}
```

---

## 11. 部署架构

### 11.1 开发环境

```
docker-compose up
├── frontend (localhost:5173)
├── backend (localhost:8000)
├── redis (localhost:6379)
├── celery worker
└── flower (localhost:5555) - Celery监控
```

### 11.2 生产环境（MVP）

```
┌─────────────┐
│   Nginx     │ :80/:443 (反向代理 + 静态文件)
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼───────┐
│ SPA │  │ Backend │ :8000 (Uvicorn)
└─────┘  └────┬────┘
              │
      ┌───────┼───────┐
      │       │       │
┌─────▼──┐ ┌─▼────┐ ┌▼──────┐
│ Celery │ │ Redis│ │ MinIO │
│ Worker │ └──────┘ └───────┘
└────────┘
```

### 11.3 容器化部署

**Docker镜像**：
- `frontend:latest` - Nginx + 静态文件
- `backend:latest` - FastAPI应用
- `worker:latest` - Celery worker（含AI模型）
- `redis:7-alpine`
- `minio/minio:latest`

**资源配置**：
```yaml
services:
  backend:
    cpus: '2'
    memory: 4G

  worker:
    cpus: '4'
    memory: 8G
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 12. 技术债务和未来优化

### 12.1 已知技术债务

1. **MVP阶段**：
   - 无用户系统（匿名使用）
   - 无数据库（文件系统存储）
   - 单机部署（不支持水平扩展）
   - 无完善的错误恢复机制

2. **性能优化点**：
   - 模型生成时间较长（依赖第三方API）
   - 大文件传输优化
   - 前端3D渲染性能

### 12.2 技术演进路线

**P0 → P1**：
- 添加数据库（PostgreSQL）
- 实现用户系统
- 优化3D预览性能

**P1 → P2**：
- 模型编辑功能
- 模型修复能力
- 社区功能准备

**P2 → 生产**：
- Kubernetes部署
- 服务网格（Istio）
- 分布式存储
- 全链路追踪
- 自动化运维

### 12.3 备选技术方案

| 场景 | 当前方案 | 备选方案 | 切换条件 |
|-----|---------|---------|---------|
| 3D渲染 | Three.js | Babylon.js | 需要更强物理引擎 |
| 文本转3D | Meshy.ai | 自部署Shap-E | API成本过高 |
| 切片引擎 | CuraEngine | PrusaSlicer | 需要多机型支持 |
| 任务队列 | Celery | RabbitMQ + 自定义 | 需要更复杂的任务编排 |

---

## 13. 风险评估与应对

### 13.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| Meshy API不可用 | 严重 | 低 | 准备备用API（Shap-E） |
| GPU资源不足 | 中 | 中 | MVP使用CPU，P1引入GPU |
| 模型质量差 | 中 | 中 | 提供参数调优，用户反馈迭代 |
| 切片失败 | 低 | 中 | 模型预验证，提供修复建议 |

### 13.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| 用户期望过高 | 中 | 高 | 明确功能限制，设置合理预期 |
| 成本超支 | 中 | 中 | API调用限额，用户配额管理 |
| 数据隐私问题 | 严重 | 低 | 不保存用户数据，明确隐私政策 |

---

## 14. 开发规范

### 14.1 代码规范

**Python**：
- PEP 8风格
- Type hints必须
- Docstring必须（Google风格）
- 最大行长度：100字符

**TypeScript**：
- ESLint + Prettier
- 严格模式（strict: true）
- 组件必须类型化
- 禁止使用any

### 14.2 Git规范

**分支策略**：
- `main`：生产环境
- `develop`：开发环境
- `feature/*`：功能分支
- `hotfix/*`：紧急修复

**Commit规范**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**：
- feat：新功能
- fix：修复
- docs：文档
- style：格式
- refactor：重构
- test：测试
- chore：构建/工具

### 14.3 测试策略

**测试金字塔**：
```
    /\
   /E2E\      <- 10% (关键业务流程)
  /------\
 /  API   \   <- 30% (API集成测试)
/----------\
/   Unit    \ <- 60% (单元测试)
```

**覆盖率要求**：
- 领域层：>80%
- 应用服务层：>70%
- API层：>60%

---

## 15. 总结

### 15.1 核心设计亮点

1. **清晰的分层架构**：表现层、应用层、领域层、基础设施层职责明确
2. **领域驱动设计**：以业务领域为核心，模型设计贴合业务
3. **高内聚低耦合**：模块间通过接口交互，依赖倒置原则
4. **可扩展性**：从MVP到生产环境平滑演进
5. **异步任务处理**：长耗时操作不阻塞用户体验
6. **完善的错误处理**：多层次的异常捕获和恢复机制

### 15.2 技术栈合理性

- **前端**：React + Three.js + Tailwind，快速开发，性能优异
- **后端**：FastAPI + Celery，异步高性能，AI生态完善
- **AI服务**：Meshy.ai API，快速验证，降低初期开发成本
- **部署**：Docker Compose，简单易用，适合MVP

### 15.3 后续开发建议

1. **优先完成P0功能**：确保核心流程走通
2. **快速迭代验证**：尽早测试3D生成和打印效果
3. **逐步引入数据库**：P1阶段添加持久化
4. **性能监控**：尽早建立监控体系，发现瓶颈
5. **用户反馈**：MVP上线后快速收集反馈，调整优先级

---

**文档版本**: v1.0
**创建日期**: 2025-10-24
**作者**: Claude (Senior Architect)
**审核状态**: 待审核
**更新日志**:
- 2025-10-24: 初始版本，完成整体架构设计
