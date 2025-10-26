# 3D模型打印系统

一个基于Web的用户自定义3D模型生成与打印平台，支持通过文本描述或照片生成3D模型，并提供风格化处理和直接打印功能。

## 🎯 项目概述

本项目旨在降低3D建模门槛，让普通用户无需专业技能即可创建3D模型，并打通从创意到实物的完整链路。

### ✨ 已实现功能

#### 🤖 AI 模型生成
- ✅ **文本转3D模型**: 使用 Meshy.ai API，输入文字描述自动生成高质量3D模型
- ✅ **图片转3D模型**: 单张照片即可生成立体模型，支持多种物体类型
- ✅ **异步任务处理**: Celery + Redis 实现长耗时任务的后台处理
- ✅ **任务状态查询**: 实时查询模型生成进度和状态

#### 🎨 图片风格化
- ✅ **5种预设风格**: 动漫、3D卡通、素描、水彩画、油画
- ✅ **腾讯云 API 集成**: 采用腾讯云图像风格化服务，处理速度快，效果好
- ✅ **实时进度反馈**: 完整的任务状态追踪和错误处理机制
- ✅ **原图对比预览**: 支持原图与风格化结果的对比展示

#### 🖥️ 3D 预览与交互
- ✅ **实时3D预览**: 基于 Three.js 的高性能渲染引擎
- ✅ **多格式支持**: GLB、OBJ、FBX、STL 等主流3D格式
- ✅ **交互式操作**: 360度旋转、缩放、平移查看模型
- ✅ **模型下载**: 一键下载生成的模型文件

#### 🖨️ 打印机集成
- ✅ **拓竹打印机适配**: 支持拓竹 H2D 及其他型号打印机
- ✅ **打印队列管理**: 多任务排队，智能调度打印作业
- ✅ **MQTT 通信**: 实时监控打印机状态和打印进度
- ✅ **3MF 格式支持**: 完整支持拓竹打印机的 3MF 文件格式

#### 🗄️ 数据管理
- ✅ **本地文件存储**: 模型和图片的本地存储管理
- ✅ **PostgreSQL 数据库**: 打印任务和打印机信息持久化
- ✅ **Redis 缓存**: 风格化任务状态和中间结果缓存

#### 🎨 现代化前端
- ✅ **React 18 + TypeScript**: 类型安全的现代前端架构
- ✅ **Semi Design UI**: 字节跳动开源的企业级 UI 组件库
- ✅ **响应式设计**: 完美适配桌面端和移动端
- ✅ **优雅的用户体验**: 流畅的动画效果和直观的操作流程

### 📊 技术亮点

- **分层架构设计**: API 层、应用服务层、领域层、基础设施层清晰分离
- **领域驱动设计 (DDD)**: 按业务领域组织代码，高内聚低耦合
- **异步任务处理**: Celery 实现模型生成、风格化等长耗时操作的后台处理
- **完善的错误处理**: 多层次的异常捕获和用户友好的错误提示
- **Docker 容器化**: 一键启动所有服务，开发和部署高度一致

## 🏗️ 技术架构

### 前端技术栈
- **框架**: React 18+ with TypeScript
- **UI 组件库**: Semi Design (字节跳动开源)
- **3D 渲染**: Three.js + React Three Fiber
- **样式方案**: Tailwind CSS
- **状态管理**: Zustand
- **构建工具**: Vite
- **HTTP 客户端**: Axios

### 后端技术栈
- **Web 框架**: Python 3.10+ with FastAPI
- **异步任务**: Celery + Redis
- **数据库**: PostgreSQL (打印任务持久化)
- **3D 处理**: trimesh, open3d
- **文件存储**: 本地存储 (可扩展为 MinIO/S3)
- **日志系统**: Python logging

### AI 服务集成
- **文本/图片转3D**: [Meshy.ai API](https://www.meshy.ai/) - 业界领先的3D生成服务
- **图片风格化**: 腾讯云图像风格化 API (智能创作引擎)
  - 动漫风格 (Anime)
  - 3D卡通风格 (3D Cartoon)
  - 素描风格 (Sketch)
  - 水彩画风格 (Watercolor)
  - 油画风格 (Oil Painting)

### 打印机集成
- **协议支持**: MQTT (拓竹标准协议)
- **文件传输**: FTP/FTPS
- **切片引擎**: OrcaSlicer / CuraEngine
- **支持格式**: 3MF, G-code

## 📋 前置要求

在开始之前，请确保已安装以下软件：

- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **Git**: 2.0+

### 开发环境额外要求

- **Node.js**: 18+ LTS 或 20+ LTS
- **Python**: 3.10 - 3.12
- **pnpm** 或 **npm**: 最新版本

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/lo24q0/hacks25.git
cd hacks25
```

### 2. 配置环境变量

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

```bash
# ===================
# 必需配置
# ===================

# Meshy.ai API 密钥 (文本/图片转3D模型)
MESHY_API_KEY=your_meshy_api_key_here

# 腾讯云 API 密钥 (图片风格化)
TENCENT_CLOUD_SECRET_ID=your_secret_id_here
TENCENT_CLOUD_SECRET_KEY=your_secret_key_here
TENCENT_CLOUD_REGION=ap-guangzhou

# ===================
# 可选配置 (使用默认值即可)
# ===================

# 服务端口
API_PORT=8000
FRONTEND_PORT=5173

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379

# PostgreSQL 配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=hacks25
```

> **如何获取 API 密钥**:
> - **Meshy.ai**: 访问 [https://www.meshy.ai/](https://www.meshy.ai/) 注册并获取 API Key
> - **腾讯云**: 访问 [腾讯云控制台](https://console.cloud.tencent.com/cam/capi) 获取 SecretId 和 SecretKey

### 3. 启动服务

#### 使用 Docker Compose (推荐)

**⚠️ 重要提示**：首次启动或在拉取新代码后,建议使用以下命令确保依赖正确安装:

```bash
# 方法一: 使用 Makefile (最推荐)
make up              # 启动所有服务
make rebuild         # 如遇依赖问题,强制重新构建

# 方法二: 使用 Docker Compose
# 首次启动或拉取新代码后
docker compose build --no-cache  # 强制重新构建,避免缓存问题
docker compose up -d              # 启动所有服务

# 日常使用
docker compose up -d              # 直接启动服务

# 启动所有服务并启用监控(包含 Flower)
docker compose --profile monitoring up -d

# 查看服务状态
docker compose ps

# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f celery_worker
```

#### Makefile 快捷命令

项目提供了 Makefile 来简化 Docker 操作:

```bash
make help            # 查看所有可用命令
make build           # 构建所有镜像
make rebuild         # 强制重新构建(解决依赖缓存问题)
make up              # 启动所有服务
make down            # 停止所有服务
make restart         # 重启所有服务
make status          # 查看服务状态
make logs            # 查看所有日志
make logs-backend    # 查看后端日志
make logs-celery     # 查看 Celery 日志
make clean           # 清理所有容器和卷
make shell-backend   # 进入后端容器 shell
```

#### 服务访问地址

启动成功后，可以通过以下地址访问各个服务：

**开发环境** (默认配置，`FRONTEND_PORT=5173`):
- **前端应用**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:5173/docs (通过 Nginx 代理) 或 http://localhost:8000/docs (直接访问)
- **健康检查**: http://localhost:5173/health
- **Flower 监控**: http://localhost:5555 (需启用 monitoring profile)

**生产环境** (需在 `.env` 中设置 `FRONTEND_PORT=80`):
- **前端应用**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost/docs (通过 Nginx 代理) 或 http://localhost:8000/docs (直接访问)
- **健康检查**: http://localhost/health
- **Flower 监控**: http://localhost:5555 (需启用 monitoring profile)

> **注意**: 使用 80 端口在 Mac/Linux 系统上可能需要管理员权限，且可能与本地其他服务冲突。开发环境推荐使用 5173 端口。

#### 验证服务

```bash
# 测试 Redis 连接
docker exec -it 3dprint-redis redis-cli ping
# 应该返回: PONG

# 测试后端健康检查
curl http://localhost:8000/health

# 测试前端健康检查 (开发环境)
curl http://localhost:5173/health

# 测试前端代理到后端 (开发环境)
curl http://localhost:5173/api/v1/models
# 应该返回模型列表(当前为 mock 数据)

# 查看 Celery Worker 状态
docker exec -it 3dprint-celery-worker celery -A infrastructure.tasks.celery_app inspect active

# 访问 Flower 监控界面(如果启用了 monitoring profile)
# 浏览器打开: http://localhost:5555
```

### 4. 停止服务

```bash
# 停止所有服务
docker compose down

# 停止服务并删除数据卷
docker compose down -v

# 重启特定服务
docker compose restart backend
docker compose restart frontend
```

### 5. Docker Compose 架构说明

本项目使用 Docker Compose 编排以下服务：

| 服务名 | 说明 | 端口 | 依赖 |
|--------|------|------|------|
| **frontend** | React SPA + Nginx 反向代理 | 80 | backend |
| **backend** | FastAPI 应用服务 | 8000 | redis |
| **redis** | Redis 消息队列和缓存 | 6379 | - |
| **celery_worker** | Celery 异步任务处理器 | - | redis, backend |
| **flower** | Celery 监控界面(可选) | 5555 | redis, celery_worker |

#### 服务特性

- ✅ **健康检查**: 所有服务配置了健康检查，确保服务正常启动
- ✅ **依赖管理**: 服务按正确顺序启动（Redis → Backend → Celery Worker → Frontend）
- ✅ **网络隔离**: 所有服务在 `3dprint-network` 内部网络中通信
- ✅ **数据持久化**: Redis 数据和后端文件存储在 Docker volumes 中
- ✅ **日志管理**: 配置了日志轮转，防止日志文件过大
- ✅ **环境变量**: 通过 `.env` 文件统一管理配置
- ✅ **反向代理**: Nginx 作为前端服务器，同时代理后端 API 请求

#### Nginx 反向代理配置

前端 Nginx 配置了以下路由：

- `/` - React 单页应用
- `/api` - 代理到后端 API (http://backend:8000)
- `/docs` - API 文档 (Swagger UI)
- `/redoc` - API 文档 (ReDoc)
- `/health` - 前端健康检查端点

所有 API 请求都通过 Nginx 转发到后端服务，前端和后端通过内部 Docker 网络通信。

## 🎬 使用场景

### 适用人群
- **3D打印爱好者**: 快速生成模型用于打印实验
- **设计师**: 快速制作原型和概念模型
- **教育机构**: 教学演示和学生作品创作
- **个人用户**: 制作个性化礼品和纪念品

### 典型工作流

1. **创意阶段**
   - 使用文本描述或参考图片输入创意
   - 选择合适的风格化效果(可选)

2. **生成阶段**
   - AI 自动生成3D模型(30-120秒)
   - 实时查看生成进度

3. **预览阶段**
   - 360度旋转查看模型细节
   - 检查模型完整性

4. **打印阶段**
   - 一键发送到拓竹打印机
   - 实时监控打印进度

5. **完成**
   - 获得实体模型

## 📁 项目结构

```
hacks25/
├── frontend/              # 前端项目 (React + Three.js)
│   ├── src/
│   │   ├── features/      # 功能模块
│   │   ├── shared/        # 共享组件
│   │   └── infrastructure/# 基础设施
│   └── package.json
│
├── backend/               # 后端项目 (FastAPI)
│   ├── src/
│   │   ├── api/          # API 路由
│   │   ├── application/  # 应用服务层
│   │   ├── domain/       # 领域模型
│   │   └── infrastructure/# 基础设施
│   └── requirements.txt
│
├── infrastructure/        # 基础设施配置
│   ├── docker/           # Dockerfile 文件
│   └── nginx/            # Nginx 配置
│
├── scripts/              # 脚本工具
│   ├── setup.sh          # 环境初始化脚本
│   └── cleanup.py        # 临时文件清理脚本
│
├── docs/                 # 项目文档
│   ├── INITIAL.md        # 产品设计文档
│   ├── ARCH.md           # 技术架构文档
│   └── CLAUDE.md         # 开发规范
│
├── .env.example          # 环境变量模板
├── docker-compose.yml    # Docker Compose 配置
└── README.md            # 项目说明文档
```

## ❓ 常见问题 (FAQ)

### Docker 相关问题

#### Q1: 启动时出现 `ModuleNotFoundError` 或依赖缺失错误

**问题描述**: Backend 服务启动失败,提示找不到某个 Python 模块,例如 `ModuleNotFoundError: No module named 'httpx'`。

**原因**: Docker 镜像缓存导致依赖未正确安装。当 `requirements.txt` 更新后,如果 Docker 使用了旧的缓存层,新的依赖不会被安装。

**解决方案**:

```bash
# 方法一: 使用 Makefile (推荐)
make rebuild    # 强制重新构建所有镜像(无缓存)
make up         # 启动服务

# 方法二: 使用 Docker Compose
docker compose down                      # 停止所有服务
docker compose build --no-cache backend  # 重新构建 backend 镜像
docker compose up -d                     # 启动服务

# 方法三: 清理所有内容后重新启动
docker compose down -v    # 停止并删除卷
docker system prune -a    # 清理 Docker 缓存(可选,会删除所有未使用的镜像)
make rebuild              # 重新构建
make up                   # 启动服务
```

**预防措施**:
- 拉取新代码后,优先使用 `make rebuild` 或 `docker compose build --no-cache`
- 项目已优化 Dockerfile,将依赖安装和代码复制分层,减少缓存问题

#### Q2: 服务启动后健康检查失败

**问题描述**: `docker compose ps` 显示服务状态为 `unhealthy` 或不断重启。

**解决方案**:

```bash
# 1. 查看服务日志,找出具体错误
docker compose logs backend
docker compose logs celery_worker

# 2. 检查服务依赖是否正常
docker compose ps  # 确认 Redis 是否健康

# 3. 重启特定服务
docker compose restart backend

# 4. 如果问题持续,重新构建
make rebuild
```

#### Q3: 端口冲突错误

**问题描述**: 启动时提示端口已被占用,例如 `Error: bind: address already in use`。

**解决方案**:

```bash
# 查看端口占用情况
lsof -i :8000  # Backend 端口
lsof -i :80    # Frontend 端口
lsof -i :6379  # Redis 端口

# 在 .env 文件中修改端口配置
API_PORT=8001
FRONTEND_PORT=8080
REDIS_PORT=6380

# 或者停止占用端口的进程
kill -9 <PID>
```

#### Q4: 拉取新代码后前端页面显示异常

**问题描述**: 前端页面无法加载或显示错误。

**解决方案**:

```bash
# 重新构建前端镜像
docker compose build --no-cache frontend
docker compose up -d frontend

# 清理浏览器缓存
# Chrome: Ctrl+Shift+Delete (或 Cmd+Shift+Delete)
# 选择 "缓存的图片和文件" 并清除
```

### API 相关问题

#### Q5: API 返回 CORS 错误

**问题描述**: 前端调用 API 时浏览器控制台显示 CORS 错误。

**解决方案**: 检查 `.env` 文件中的 `CORS_ORIGINS` 配置,确保包含前端地址:

```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost
```

#### Q6: Meshy.ai API 调用失败

**问题描述**: 生成 3D 模型时返回 401 或 403 错误。

**解决方案**:
1. 检查 `.env` 文件中的 `MESHY_API_KEY` 是否正确
2. 访问 [Meshy.ai Dashboard](https://www.meshy.ai/) 确认 API Key 有效
3. 检查账户配额是否用完

### 开发环境问题

#### Q7: 如何查看 Celery 任务执行情况?

**解决方案**:

```bash
# 方法一: 使用 Flower 监控界面
docker compose --profile monitoring up -d
# 访问: http://localhost:5555

# 方法二: 命令行查看
docker exec -it 3dprint-celery-worker celery -A infrastructure.tasks.celery_app inspect active
docker exec -it 3dprint-celery-worker celery -A infrastructure.tasks.celery_app inspect stats

# 方法三: 查看日志
make logs-celery
```

#### Q8: 如何进入容器内部调试?

**解决方案**:

```bash
# 进入 Backend 容器
make shell-backend
# 或
docker compose exec backend /bin/bash

# 进入 Frontend 容器
docker compose exec frontend /bin/sh

# 进入 Redis 容器
docker compose exec redis redis-cli
```

## 📚 API 使用示例

### 文本转3D模型

```bash
# 1. 创建生成任务
curl -X POST "http://localhost:8000/api/v1/models/generate/text" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "一只可爱的卡通奶牛，站立姿势"
  }'

# 响应示例
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "celery_task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  ...
}

# 2. 查询任务状态 (使用返回的 celery_task_id)
curl "http://localhost:8000/api/v1/models/task/a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# 任务完成后的响应
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "state": "SUCCESS",
  "result": {
    "model_id": "123e4567-e89b-12d3-a456-426614174000",
    "model_files": {
      "glb": "/storage/models/xxx.glb",
      "obj": "/storage/models/xxx.obj"
    }
  }
}
```

### 图片风格化

```bash
# 1. 上传图片并创建风格化任务
curl -X POST "http://localhost:8000/api/v1/styles/transfer" \
  -F "file=@/path/to/image.jpg" \
  -F "style_preset_id=anime"

# 响应示例
{
  "task_id": "456e7890-f12g-34h5-i678-jk9012345678",
  "status": "pending",
  "message": "风格化任务已创建,请轮询查询结果"
}

# 2. 查询任务状态
curl "http://localhost:8000/api/v1/styles/tasks/456e7890-f12g-34h5-i678-jk9012345678"

# 3. 下载风格化结果 (任务完成后)
curl "http://localhost:8000/api/v1/styles/tasks/456e7890-f12g-34h5-i678-jk9012345678/result" \
  -o styled_image.jpg
```

### 打印机管理

```bash
# 1. 注册打印机
curl -X POST "http://localhost:8000/api/v1/prints/printers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Bambu Printer",
    "model": "X1 Carbon",
    "adapter_type": "bambu",
    "connection_config": {
      "host": "192.168.1.100",
      "access_code": "12345678",
      "serial_number": "01S00A1234567890"
    }
  }'

# 2. 创建打印任务
curl -X POST "http://localhost:8000/api/v1/prints/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "123e4567-e89b-12d3-a456-426614174000",
    "printer_id": "bambu_my_bambu_printer",
    "priority": 1
  }'

# 3. 查询打印队列状态
curl "http://localhost:8000/api/v1/prints/queue"
```

### 完整 API 文档

启动服务后访问 Swagger UI 查看完整 API 文档:
- **开发环境**: http://localhost:5173/docs
- **直接访问后端**: http://localhost:8000/docs

## 🔧 开发指南

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 测试异步任务

启动服务后,可以通过 API 测试异步任务功能:

```bash
# 提交一个延迟 5 秒的测试任务
curl -X POST "http://localhost:8000/api/v1/tasks/test/delayed?delay_seconds=5&message=Hello"

# 返回示例:
# {
#   "task_id": "abc123...",
#   "task_name": "test_tasks.delayed_return",
#   "status": "PENDING",
#   "submitted_at": "2025-10-24T12:00:00Z"
# }

# 查询任务状态(使用上面返回的 task_id)
curl "http://localhost:8000/api/v1/tasks/{task_id}"

# 也可以通过 Swagger UI 测试: http://localhost:8000/docs
```

### 代码规范

请遵循项目的代码规范，详见 `CLAUDE.md`。

**关键规范**：
- 使用语义化的 commit 消息 (feat/fix/docs/chore等)
- 单个文件不超过 500 行代码
- 为每个函数编写 Google 风格的 docstring
- 代码变更拆分成多个小的 commit

## 📖 文档

- [产品设计文档](INITIAL.md) - 功能模块和需求说明
- [技术架构文档](ARCH.md) - 架构设计和技术选型
- [开发规范](CLAUDE.md) - 代码规范和开发流程
- [任务清单](TASK.md) - 开发任务和进度跟踪

## 🗺️ 功能开发进度

### ✅ 已完成 (P0-P1)

#### 核心功能
- [x] **基础架构**: Docker Compose 容器化部署
- [x] **后端架构**: FastAPI + DDD 分层架构 + Celery 异步任务
- [x] **前端架构**: React 18 + TypeScript + Semi Design
- [x] **文本转3D**: Meshy.ai API 集成,异步任务处理
- [x] **图片转3D**: 单张图片生成立体模型
- [x] **3D预览**: Three.js 实时渲染,支持多种格式
- [x] **模型下载**: 支持 GLB/OBJ/FBX/STL 格式导出

#### 风格化功能
- [x] **腾讯云集成**: 图像风格化 API 接入
- [x] **5种风格**: 动漫、3D卡通、素描、水彩画、油画
- [x] **任务管理**: Redis 缓存 + 轮询状态查询
- [x] **对比预览**: 原图与风格化结果对比展示
- [x] **错误处理**: 完善的错误映射和用户提示

#### 打印机功能
- [x] **拓竹适配器**: MQTT 协议通信 + FTP 文件传输
- [x] **打印队列**: 多任务排队管理
- [x] **3MF 支持**: G-code 转 3MF 格式
- [x] **数据持久化**: PostgreSQL 存储打印任务和打印机信息

### 🚧 进行中 (P2)

- [ ] **用户系统**: 注册登录、历史记录管理
- [ ] **模型编辑**: 在线缩放、旋转、添加文字
- [ ] **云存储**: MinIO/S3 对象存储集成
- [ ] **WebSocket**: 实时任务进度推送

### 📋 计划中 (P3+)

- [ ] **社区功能**: 模型分享、点赞、评论
- [ ] **高级风格化**: 自定义风格训练、风格混合
- [ ] **打印优化**: AI 自动修复模型缺陷
- [ ] **AR 预览**: 手机端 AR 模型预览
- [ ] **多语言支持**: 国际化 i18n

## 🤝 贡献指南

欢迎贡献代码！请遵循以下流程：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/lo24q0/hacks25/issues)
- 项目维护者: [@lo24q0](https://github.com/lo24q0)

## 🙏 致谢

### 核心技术
- [Meshy.ai](https://www.meshy.ai/) - 提供业界领先的3D生成API
- [腾讯云](https://cloud.tencent.com/) - 提供图像风格化服务
- [Three.js](https://threejs.org/) - 强大的WebGL 3D渲染库
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Python Web框架
- [Semi Design](https://semi.design/) - 字节跳动开源UI组件库
- [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) - 优秀的3D打印切片软件
- [Celery](https://docs.celeryq.dev/) - 分布式任务队列

### 打印机支持
- [Bambu Lab](https://bambulab.com/) - 拓竹科技3D打印机

### 开源社区
感谢所有为开源社区做出贡献的开发者！

---

**项目状态**: 🎉 核心功能已完成，持续优化中

**当前版本**: v0.2.0 (MVP+)

**最后更新**: 2025-10-26
