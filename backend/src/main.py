"""
FastAPI 应用入口。

初始化 FastAPI 应用,配置中间件和路由。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.api.v1.routers import files, models, tasks, prints
from src.infrastructure.config.settings import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    description="""
## 3D模型打印系统 API

基于Web的用户自定义3D模型生成与打印平台,支持通过文本描述或照片生成3D模型。

### 核心功能

* **文本转3D模型**: 输入文本描述,自动生成3D模型
* **图片转3D模型**: 上传图片,生成对应的3D模型
* **异步任务处理**: 使用 Celery 处理长耗时的模型生成任务
* **多格式支持**: 支持 GLB、OBJ、FBX、STL 等多种模型格式
* **任务状态查询**: 实时查询模型生成任务的进度和状态

### 技术栈

* **后端框架**: FastAPI
* **AI服务**: Meshy.ai API
* **任务队列**: Celery + Redis
* **3D处理**: trimesh, open3d

### API使用流程

1. 调用 `/api/v1/models/generate/text` 或 `/api/v1/models/generate/image` 创建生成任务
2. 获取返回的 `celery_task_id`
3. 使用 `/api/v1/models/task/{task_id}` 查询任务状态和进度
4. 任务完成后,从 `model_files` 字段获取生成的模型文件路径
    """,
    contact={
        "name": "API Support",
        "url": "https://github.com/lo24q0/hacks25",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "models",
            "description": "3D模型生成相关接口,包括文本转3D、图片转3D等功能",
        },
        {
            "name": "files",
            "description": "文件管理接口,包括文件上传、下载等功能",
        },
        {
            "name": "tasks",
            "description": "异步任务管理接口,用于查询 Celery 任务状态",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(prints.router, prefix="/api/v1")

# 添加静态文件服务，让前端能够访问存储的文件
storage_path = Path(settings.storage_path)
if storage_path.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    健康检查接口。

    Returns:
        JSONResponse: 包含服务状态的 JSON 响应。
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        },
    )


@app.get("/")
async def root() -> dict[str, str]:
    """
    根路径接口。

    Returns:
        dict[str, str]: 欢迎信息。
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs" if settings.debug else "API documentation is disabled",
    }
