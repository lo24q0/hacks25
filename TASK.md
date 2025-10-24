# 任务清单

## 当前任务

### P0 - MVP 核心功能 (2025-10-24 开始)

- [x] **基础配置与环境准备** (#12, 2025-10-24)
  - [x] 创建根目录结构 (frontend/, backend/, infrastructure/, scripts/)
  - [x] 创建 .env.example 环境变量模板
  - [x] 创建 docker-compose.yml 基础配置(只包含 Redis)
  - [x] 创建 README.md 项目说明文档

- [x] **领域模型定义** (#24, 2025-10-24)
  - [x] 实现 domain/enums (status.py, source_type.py)
  - [x] 实现 domain/value_objects (metadata.py, source_data.py)
  - [x] 实现 domain/models (model3d.py)
  - [x] 实现 domain/interfaces (i_model_generator.py, i_model_converter.py, i_style_engine.py, i_slicer.py, i_repository.py, i_storage.py)
  - [x] 验证所有导入和类型检查

- [ ] **后端基础架构搭建**
  - [ ] 初始化 FastAPI 项目结构
  - [ ] 配置开发环境 (Docker Compose)
  - [ ] 实现基础配置管理
  - [ ] 搭建日志系统

- [ ] **模型生成功能**
  - [ ] 集成 Meshy.ai API
  - [ ] 实现文本转 3D 模型接口
  - [ ] 实现图片转 3D 模型接口
  - [ ] 文件格式转换 (转 STL)
  - [ ] 模型元数据提取

- [ ] **前端基础搭建** (#16, 2025-10-24)
  - [x] 初始化 React + Vite 项目
  - [x] 配置 Tailwind CSS
  - [x] 创建 frontend/src/ 目录结构(按 ARCH.md 5.3 节)
  - [x] 实现基础布局组件
  - [x] 创建路由配置
  - [ ] 创建 frontend/Dockerfile
  - [x] 集成 Three.js / React Three Fiber

- [ ] **Three.js 集成** (#30, 2025-10-24)
  - [ ] 实现 infrastructure/three/SceneManager.ts
  - [ ] 实现 features/model-generation/components/ModelPreview.tsx
  - [ ] 准备测试 STL 文件
  - [ ] 集成 3D 预览到 GenerationPage

- [ ] **前端基础组件** (#26, 2025-10-24)
  - [ ] 实现 shared/components/ui/ 基础组件(Button, Input, Loading)
  - [ ] 创建 features/model-generation/ 目录结构
  - [ ] 创建 infrastructure/api/client.ts Axios 配置
  - [ ] 配置 Zustand 状态管理

- [ ] **模型预览功能**
  - [ ] 3D 模型加载和渲染
  - [ ] 相机控制 (旋转、缩放)
  - [ ] 光照和材质设置

- [ ] **异步任务处理**
  - [ ] 配置 Redis 和 Celery
  - [ ] 实现模型生成异步任务
  - [ ] 任务状态查询接口
  - [ ] 前端轮询机制

### P1 - 增强功能

- [ ] **打印适配功能**
  - [ ] 集成 CuraEngine
  - [ ] 实现模型切片接口
  - [ ] G-code 生成和下载
  - [ ] 打印机配置管理
  - [ ] 打印参数配置 UI

- [ ] **用户系统**
  - [ ] 用户注册和登录
  - [ ] JWT 认证
  - [ ] 用户历史记录
  - [ ] 用户配额管理

- [ ] **数据持久化**
  - [ ] PostgreSQL 集成
  - [ ] SQLAlchemy 模型定义
  - [ ] 数据库迁移工具

### P2 - 高级功能

- [ ] **风格化处理**
  - [ ] AnimeGAN 模型集成
  - [ ] 图片风格迁移接口
  - [ ] 风格预设管理

- [ ] **模型编辑**
  - [ ] 基础模型修复
  - [ ] 尺寸调整
  - [ ] 模型合并

- [ ] **社区功能准备**
  - [ ] 模型分享机制
  - [ ] 点赞和收藏

## 已完成任务

- [x] 2025-10-24: 添加项目开发规范文档 (CLAUDE.md)
- [x] 2025-10-24: 添加技术架构设计文档 (ARCH.md)
- [x] 2025-10-24: 添加 .gitignore 配置

## 工作中发现的子任务

### 待添加
- 需要创建 README.md 说明项目设置和运行方式
- 需要准备 Docker Compose 配置模板
- 需要准备环境变量模板 (.env.example)

### 技术债务
- INITAL.md 文件名拼写错误 (应为 INITIAL.md)

## 备注

- 优先完成 P0 MVP 核心功能,确保端到端流程走通
- 每个任务完成后立即标记并提交代码
- 遇到问题及时记录到"工作中发现"部分
