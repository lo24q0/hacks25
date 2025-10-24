# Docker Compose 部署指南

## 概述

本项目使用 Docker Compose 编排所有服务，实现一键启动整个应用栈。

## 服务架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户浏览器                            │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP :80
┌────────────────────▼────────────────────────────────────┐
│               Frontend (Nginx + React SPA)              │
│  - 静态文件服务                                          │
│  - API 反向代理 (/api -> backend:8000)                  │
│  - 健康检查端点                                          │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
┌─────────▼────────┐  ┌─────────▼──────────┐
│   Backend        │  │   Celery Worker    │
│   (FastAPI)      │  │   (异步任务处理)    │
│   - REST API     │  │   - 模型生成       │
│   - 健康检查     │  │   - 文件处理       │
└─────────┬────────┘  └─────────┬──────────┘
          │                     │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │      Redis          │
          │  - 消息队列         │
          │  - 缓存             │
          │  - 任务结果存储     │
          └─────────────────────┘
```

## 服务列表

### 必需服务

#### 1. Frontend (Nginx + React)
- **端口**: 80
- **功能**: 
  - 提供 React 单页应用
  - 反向代理 API 请求到后端
  - 静态资源服务
- **健康检查**: `GET /health`
- **依赖**: backend

#### 2. Backend (FastAPI)
- **端口**: 8000
- **功能**:
  - REST API 服务
  - 模型生成接口
  - 文件上传/下载
- **健康检查**: `GET /health`
- **依赖**: redis

#### 3. Redis
- **端口**: 6379
- **功能**:
  - Celery 消息队列
  - 缓存服务
  - 任务结果存储
- **持久化**: 使用 AOF (Append Only File)
- **内存限制**: 256MB (LRU 淘汰策略)

#### 4. Celery Worker
- **功能**:
  - 异步处理模型生成任务
  - 文件处理任务
  - 定时清理任务
- **并发数**: 2 workers
- **依赖**: redis, backend

### 可选服务

#### 5. Flower (监控界面)
- **端口**: 5555
- **功能**: Celery 任务监控
- **启动方式**: `docker compose --profile monitoring up -d`
- **访问地址**: http://localhost:5555

## 环境变量配置

### 必需配置

```bash
# AI 服务配置
MESHY_API_KEY=your_api_key_here  # 从 meshy.ai 获取
```

### 可选配置

```bash
# 应用配置
APP_ENV=development          # 环境: development | production
DEBUG=true                   # 调试模式
LOG_LEVEL=INFO              # 日志级别

# 端口配置
API_PORT=8000               # 后端端口
FRONTEND_PORT=80            # 前端端口
REDIS_PORT=6379             # Redis 端口
FLOWER_PORT=5555            # Flower 端口

# 存储配置
STORAGE_BACKEND=local       # 存储类型: local | minio | s3
MAX_UPLOAD_SIZE_MB=10       # 最大上传文件大小

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost
```

## 使用指南

### 首次启动

```bash
# 1. 克隆项目
git clone https://github.com/lo24q0/hacks25.git
cd hacks25

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 MESHY_API_KEY

# 3. 启动所有服务
docker compose up -d

# 4. 查看启动状态
docker compose ps

# 5. 查看日志
docker compose logs -f
```

### 验证部署

```bash
# 检查所有服务健康状态
docker compose ps

# 测试 Redis
docker exec -it 3dprint-redis redis-cli ping
# 输出: PONG

# 测试后端健康检查
curl http://localhost:8000/health
# 输出: {"status":"healthy",...}

# 测试前端健康检查
curl http://localhost/health
# 输出: healthy

# 测试 API 通过前端代理访问
curl http://localhost/api/v1/models
# 输出: 模型列表 (mock 数据)

# 访问 API 文档
# 浏览器打开: http://localhost/docs
```

### 常用操作

```bash
# 查看服务状态
docker compose ps

# 查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f celery_worker

# 重启服务
docker compose restart backend

# 停止服务
docker compose down

# 停止并删除数据卷
docker compose down -v

# 重新构建并启动
docker compose up -d --build

# 启动带监控的完整环境
docker compose --profile monitoring up -d
```

### 开发模式

```bash
# 仅启动基础设施服务 (Redis)
docker compose up -d redis

# 本地运行后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 本地运行前端
cd frontend
npm install
npm run dev
```

## 数据持久化

### 数据卷

项目使用以下 Docker volumes 持久化数据：

1. **redis_data**: Redis 数据持久化
   - 路径: `/data`
   - 使用 AOF 持久化模式

2. **backend_data**: 后端文件存储
   - 路径: `/app/data`
   - 存储上传的文件和生成的模型

### 备份与恢复

```bash
# 备份 Redis 数据
docker exec 3dprint-redis redis-cli BGSAVE
docker cp 3dprint-redis:/data/dump.rdb ./backup/redis-backup.rdb

# 备份后端数据
docker cp 3dprint-backend:/app/data ./backup/backend-data

# 恢复数据
docker compose down
docker volume rm 3dprint-redis-data 3dprint-backend-data
docker volume create 3dprint-redis-data
docker volume create 3dprint-backend-data
docker cp ./backup/redis-backup.rdb 3dprint-redis:/data/dump.rdb
docker cp ./backup/backend-data/. 3dprint-backend:/app/data/
docker compose up -d
```

## 网络配置

所有服务运行在 `3dprint-network` 桥接网络中：

- **网络名称**: 3dprint-network
- **驱动**: bridge
- **内部 DNS**: 服务可通过容器名互相访问
  - `backend:8000` - 后端服务
  - `redis:6379` - Redis 服务
  - `celery_worker` - Celery Worker

## 健康检查

所有服务都配置了健康检查：

| 服务 | 检查方式 | 间隔 | 超时 | 重试 |
|------|---------|------|------|------|
| frontend | `wget /health` | 30s | 10s | 3 |
| backend | `curl /health` | 30s | 10s | 3 |
| redis | `redis-cli ping` | 10s | 3s | 3 |
| celery_worker | `celery inspect` | 30s | 10s | 3 |
| flower | `curl /` | 30s | 10s | 3 |

## 日志管理

所有服务配置了日志轮转：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # 单个日志文件最大 10MB
    max-file: "3"      # 保留最近 3 个日志文件
```

查看日志：

```bash
# 实时查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend

# 查看最近 100 行
docker compose logs --tail=100 backend

# 查看自某时间点以来的日志
docker compose logs --since="2025-10-24T10:00:00" backend
```

## 故障排查

### 常见问题

#### 1. 服务启动失败

```bash
# 查看服务状态
docker compose ps

# 查看失败服务的日志
docker compose logs <service_name>

# 检查健康状态
docker inspect <container_name> | grep -A 10 Health
```

#### 2. 后端无法连接 Redis

```bash
# 测试 Redis 连接
docker exec -it 3dprint-redis redis-cli ping

# 检查网络连接
docker exec -it 3dprint-backend ping redis

# 查看环境变量
docker exec -it 3dprint-backend env | grep REDIS
```

#### 3. 前端无法访问后端 API

```bash
# 检查 Nginx 配置
docker exec -it 3dprint-frontend cat /etc/nginx/conf.d/default.conf

# 测试后端健康
docker exec -it 3dprint-frontend wget -O- http://backend:8000/health

# 查看 Nginx 日志
docker logs 3dprint-frontend
```

#### 4. Celery Worker 无法处理任务

```bash
# 检查 Worker 状态
docker exec -it 3dprint-celery-worker celery -A infrastructure.tasks.celery_app inspect active

# 查看 Worker 日志
docker compose logs -f celery_worker

# 测试 Redis 连接
docker exec -it 3dprint-celery-worker python -c "from redis import Redis; r = Redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

### 性能优化

#### 1. Redis 内存优化

```bash
# 查看 Redis 内存使用
docker exec -it 3dprint-redis redis-cli INFO memory

# 调整最大内存 (在 docker-compose.yml 中)
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

#### 2. Celery Worker 并发

```bash
# 调整并发数 (在 docker-compose.yml 中)
command: celery -A infrastructure.tasks.celery_app worker --concurrency=4
```

#### 3. Nginx 缓存

Nginx 已配置静态资源缓存：
- 图片、字体、CSS、JS: 1 年
- HTML: 不缓存 (no-cache)
- API 响应: 不缓存

## 生产环境部署建议

### 1. 使用生产配置

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - APP_ENV=production
      - DEBUG=false
      - LOG_LEVEL=WARNING
    restart: always

  frontend:
    restart: always

  redis:
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}

  celery_worker:
    restart: always
```

启动：

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. 使用 HTTPS

配置 Nginx SSL：

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... 其他配置
}
```

### 3. 设置资源限制

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 4. 配置监控

- 启用 Flower 监控
- 集成 Prometheus + Grafana
- 配置日志聚合 (ELK Stack)

## 参考资料

- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Nginx 配置参考](https://nginx.org/en/docs/)
- [Redis 配置指南](https://redis.io/docs/management/config/)
- [Celery 文档](https://docs.celeryproject.org/)

---

**文档版本**: v1.0  
**最后更新**: 2025-10-24
