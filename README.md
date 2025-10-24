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

```bash
# 启动所有服务 (Redis + 前端)
docker compose up -d

# 查看服务状态
docker compose ps

# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f frontend
docker compose logs -f redis
```

#### 验证服务

```bash
# 测试 Redis 连接
docker exec -it 3dprint-redis redis-cli ping
# 应该返回: PONG

# 访问前端应用
# 打开浏览器访问: http://localhost:3000
```

> **注意**: 首次启动前端服务会构建 Docker 镜像，可能需要几分钟时间。后续启动会使用缓存的镜像，速度会快很多。

### 4. 停止服务

```bash
# 停止所有服务
docker compose down

# 停止服务并删除数据卷
docker compose down -v
```

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
