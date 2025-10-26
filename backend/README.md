# 3D Print Platform - Backend

3D模型打印系统后端服务，基于 FastAPI 构建。

## 技术栈

- **Python**: 3.10-3.13
- **框架**: FastAPI 0.115+
- **ASGI服务器**: Uvicorn 0.30+
- **配置管理**: Pydantic Settings

## 项目结构

```
backend/
├── src/
│   ├── api/                 # API层
│   │   └── v1/             # API版本1
│   │       ├── routers/    # 路由
│   │       └── schemas/    # Pydantic模型
│   ├── application/        # 应用服务层
│   │   └── services/       # 业务服务
│   ├── domain/             # 领域模型层
│   │   └── models/         # 领域模型
│   ├── infrastructure/     # 基础设施层
│   │   └── config/         # 配置管理
│   ├── shared/             # 共享模块
│   │   └── utils/          # 工具函数
│   └── main.py             # 应用入口
├── tests/                  # 测试
├── requirements.txt        # 依赖列表
├── pyproject.toml         # 项目配置
├── Dockerfile             # Docker镜像
└── README.md              # 说明文档
```

## 快速开始

### 1. 环境要求

- Python 3.10 或更高版本
- pip

### 2. 安装依赖

建议使用虚拟环境：

```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或者在 Windows 上: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

### 4. 启动服务

```bash
uvicorn src.main:app --reload
```

服务将在 http://localhost:8000 启动。

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. 健康检查

```bash
curl http://localhost:8000/health
```

## Docker 部署

### 构建镜像

```bash
docker build -t 3d-print-backend .
```

### 运行容器

```bash
docker run -p 8000:8000 --env-file .env 3d-print-backend
```

## 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用 Type Hints
- 函数必须包含 Google 风格的 Docstring
- 最大行长度: 100字符

### 测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/ tests/
```

### 类型检查

```bash
mypy src/
```

## API 接口

### 健康检查

- **GET** `/health`
  - 返回服务健康状态
  - 响应示例:
    ```json
    {
      "status": "healthy",
      "service": "3D Print Platform API",
      "version": "0.1.0",
      "environment": "development"
    }
    ```

### 根路径

- **GET** `/`
  - 返回欢迎信息和文档链接

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| APP_NAME | 应用名称 | 3D Print Platform API |
| APP_VERSION | 应用版本 | 0.1.0 |
| DEBUG | 调试模式 | false |
| ENVIRONMENT | 运行环境 | development |
| HOST | 监听地址 | 0.0.0.0 |
| PORT | 监听端口 | 8000 |
| CORS_ORIGINS | CORS允许源 | ["http://localhost:5173"] |
| LOG_LEVEL | 日志级别 | INFO |

## 许可证

MIT
