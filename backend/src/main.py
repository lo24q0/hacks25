"""
FastAPI 应用入口。

初始化 FastAPI 应用,配置中间件和路由。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.routers import files, models, tasks
from src.infrastructure.config.settings import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## 3D模型打印平台 API

基于 AI 的 3D 模型生成与打印平台,支持文本和图片转3D模型功能。

### 功能特性

- **文本转3D**: 通过文本描述生成 3D 模型
- **图片转3D**: 通过照片生成 3D 模型
- **模型管理**: 模型的查询、下载和删除
- **文件上传**: 支持图片文件上传
- **任务追踪**: 异步任务状态查询

### API 使用流程

1. **文本生成模型**: POST `/api/v1/models/generate/text` → 返回模型 ID
2. **查询任务状态**: GET `/api/v1/models/{id}` → 轮询直到 `status: completed`
3. **下载模型文件**: GET `/api/v1/models/{id}/download` → 下载 STL 文件

### 认证方式

当前版本为 MVP,暂不需要认证。P2 阶段将支持 JWT 认证。

### 技术栈

- **框架**: FastAPI
- **AI 服务**: Meshy.ai API
- **异步任务**: Celery + Redis
- **3D 处理**: trimesh, open3d
    """,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "3D Print Platform Team",
        "email": "support@3dprint.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "models",
            "description": "3D模型生成和管理相关接口",
        },
        {
            "name": "files",
            "description": "文件上传和下载相关接口",
        },
        {
            "name": "tasks",
            "description": "异步任务状态查询接口",
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
