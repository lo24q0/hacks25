"""
FastAPI 应用入口。

初始化 FastAPI 应用,配置中间件和路由。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.routers import files, models, tasks, prints
from src.infrastructure.config.settings import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
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
