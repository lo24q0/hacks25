# 3D模型打印系统

一个基于Web的用户自定义3D模型生成与打印平台，支持通过文本描述或照片生成3D模型，并提供风格化处理和直接打印功能。

## 🎯 项目概述

本项目旨在降低3D建模门槛，让普通用户无需专业技能即可创建3D模型，并打通从创意到实物的完整链路。

### 核心功能

- **文本转3D模型**：输入文字描述，自动生成对应的3D模型
- **照片转3D模型**：上传照片，AI生成立体模型
- **风格化处理**：支持动漫、卡通等多种风格转换
- **在线预览**：360度实时预览生成的3D模型
- **打印适配**：自动生成适配拓竹H2D打印机的G-code文件
- **模型导出**：支持STL格式导出，兼容主流切片软件

## 🏗️ 技术架构

### 前端技术栈
- **框架**: React 18+ with TypeScript
- **3D渲染**: Three.js / React Three Fiber
- **UI组件**: Tailwind CSS + Headless UI
- **状态管理**: Zustand
- **构建工具**: Vite

### 后端技术栈
- **框架**: Python 3.10+ with FastAPI
- **AI推理**: PyTorch
- **3D处理**: trimesh, open3d
- **异步任务**: Celery + Redis
- **切片引擎**: CuraEngine

### AI 服务
- **文本/图片转3D**: Meshy.ai API
- **风格化处理**: AnimeGANv3

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

编辑 `.env` 文件，至少需要配置以下关键参数：

```bash
# Meshy.ai API 密钥 (必需)
MESHY_API_KEY=your_meshy_api_key_here

# 其他配置保持默认值即可
```

> **获取 Meshy.ai API Key**: 访问 [https://www.meshy.ai/](https://www.meshy.ai/) 注册并获取API密钥

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

## 🗺️ 开发路线图

### P0 - MVP核心功能 (2天)
- [x] 基础配置与环境准备
- [ ] 后端基础架构搭建
- [ ] 文本转3D模型功能
- [ ] 前端界面和3D预览
- [ ] 模型文件导出

### P1 - 增强功能
- [ ] 照片转3D模型
- [ ] 照片风格化处理
- [ ] 打印适配和G-code生成
- [ ] 用户系统

### P2 - 高级功能
- [ ] 模型在线编辑
- [ ] 社区功能
- [ ] 高级风格化

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

- [Meshy.ai](https://www.meshy.ai/) - 提供3D生成API
- [Three.js](https://threejs.org/) - 强大的3D渲染库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [CuraEngine](https://github.com/Ultimaker/CuraEngine) - 开源切片引擎

---

**项目状态**: 🚧 开发中

**最后更新**: 2025-10-24
