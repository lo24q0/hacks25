# Makefile for 3D Print Platform
# 提供便捷的开发和部署命令

.PHONY: help build up down restart logs status clean rebuild test

# 默认目标:显示帮助信息
help:
	@echo "3D Print Platform - Docker 管理命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make build         - 构建所有 Docker 镜像"
	@echo "  make rebuild       - 强制重新构建所有镜像(无缓存)"
	@echo "  make up            - 启动所有服务"
	@echo "  make down          - 停止所有服务"
	@echo "  make restart       - 重启所有服务"
	@echo "  make logs          - 查看所有服务日志"
	@echo "  make logs-backend  - 查看后端服务日志"
	@echo "  make logs-frontend - 查看前端服务日志"
	@echo "  make logs-celery   - 查看 Celery Worker 日志"
	@echo "  make logs-redis    - 查看 Redis 日志"
	@echo "  make status        - 查看服务运行状态"
	@echo "  make clean         - 清理所有容器、网络和卷"
	@echo "  make test          - 运行测试"
	@echo "  make shell-backend - 进入后端容器 shell"
	@echo ""

# 构建所有镜像
build:
	@echo "正在构建 Docker 镜像..."
	docker compose build

# 强制重新构建(无缓存) - 解决依赖缓存问题
rebuild:
	@echo "正在强制重新构建所有镜像(无缓存)..."
	docker compose build --no-cache

# 启动服务
up:
	@echo "正在启动所有服务..."
	docker compose up -d
	@echo ""
	@echo "服务已启动,等待健康检查..."
	@sleep 5
	@make status

# 停止服务
down:
	@echo "正在停止所有服务..."
	docker compose down

# 重启服务
restart:
	@echo "正在重启所有服务..."
	docker compose restart
	@sleep 5
	@make status

# 查看所有服务日志
logs:
	docker compose logs -f

# 查看后端日志
logs-backend:
	docker compose logs -f backend

# 查看前端日志
logs-frontend:
	docker compose logs -f frontend

# 查看 Celery Worker 日志
logs-celery:
	docker compose logs -f celery_worker

# 查看 Redis 日志
logs-redis:
	docker compose logs -f redis

# 查看服务状态
status:
	@echo "Docker Compose 服务状态:"
	@echo "========================"
	@docker compose ps
	@echo ""
	@echo "服务访问地址:"
	@echo "  - Frontend:  http://localhost:80"
	@echo "  - Backend:   http://localhost:8000"
	@echo "  - API Docs:  http://localhost:8000/docs"
	@echo "  - Redis:     localhost:6379"

# 清理所有内容
clean:
	@echo "警告: 这将删除所有容器、网络和卷!"
	@read -p "确定继续? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v --remove-orphans; \
		echo "清理完成!"; \
	else \
		echo "已取消."; \
	fi

# 进入后端容器 shell
shell-backend:
	docker compose exec backend /bin/bash

# 运行测试
test:
	docker compose exec backend pytest

# 开发模式:重新构建并启动
dev: rebuild up

# 生产模式:构建并启动
prod: build up
