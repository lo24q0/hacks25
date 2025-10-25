# 任务清单

## 当前任务

### P0 - MVP 核心功能 (2025-10-24 开始)

- [x] **基础配置与环境准备** (#12, 2025-10-24)
  - [x] 创建根目录结构 (frontend/, backend/, infrastructure/, scripts/)
  - [x] 创建 .env.example 环境变量模板
  - [x] 创建 docker-compose.yml 基础配置(只包含 Redis)
  - [x] 创建 README.md 项目说明文档

- [x] **完整 Docker Compose 集成** (#34, 2025-10-24)
  - [x] 更新 docker-compose.yml 包含所有服务
  - [x] 添加 Nginx 反向代理配置
  - [x] 配置服务间网络
  - [x] 添加健康检查
  - [x] 配置环境变量支持
  - [x] 添加日志管理配置
  - [x] 更新 README 文档说明

- [x] **领域模型定义** (#24, 2025-10-24)
  - [x] 实现 domain/enums (status.py, source_type.py)
  - [x] 实现 domain/value_objects (metadata.py, source_data.py)
  - [x] 实现 domain/models (model3d.py)
  - [x] 实现 domain/interfaces (i_model_generator.py, i_model_converter.py, i_style_engine.py, i_slicer.py, i_repository.py, i_storage.py)
  - [x] 验证所有导入和类型检查

- [ ] **后端基础架构搭建**
  - [x] 初始化 FastAPI 项目结构
  - [ ] 配置开发环境 (Docker Compose)
  - [x] 实现基础配置管理
  - [ ] 搭建日志系统

- [x] **API 路由骨架** (#29, 2025-10-24)
  - [x] 实现 api/v1/schemas/model.py (请求/响应模型)
  - [x] 实现 api/v1/routers/models.py (模型生成路由 - mock数据)
  - [x] 在 main.py 中注册路由
  - [x] 配置 CORS 中间件

- [x] **存储服务实现** (#31, 2025-10-24)
  - [x] 实现 infrastructure/storage/base.py 存储接口
  - [x] 实现 infrastructure/storage/local_storage.py 本地存储
  - [x] 实现文件上传 API 路由
  - [x] 实现临时文件清理机制
  - [x] 验证:可以通过 API 上传文件并返回下载链接

- [ ] **模型生成功能** (#53, 2025-10-25)
  - [x] 集成 Meshy.ai API
  - [x] 实现文本转 3D 模型服务 (TextTo3DService)
  - [x] 实现图片转 3D 模型服务 (ImageTo3DService)
  - [x] 实现统一模型生成器 (MeshyModelGenerator)
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

- [x] **前端基础组件** (#26, 2025-10-24)
  - [x] 实现 shared/components/ui/ 基础组件(Button, Input, Loading)
  - [x] 创建 features/model-generation/ 目录结构
  - [x] 创建 infrastructure/api/client.ts Axios 配置
  - [x] 配置 Zustand 状态管理
  - [x] 使用 semi-design 美化所有组件

- [x] **文本生成界面美化** (#60, 2025-10-25)
  - [x] 添加示例模板快速填充功能
  - [x] 优化输入提示和占位符
  - [x] 增强视觉反馈(状态标签、渐变按钮)
  - [x] 改进用户体验(Tooltip、动画效果)

- [ ] **模型预览功能**
  - [ ] 3D 模型加载和渲染
  - [ ] 相机控制 (旋转、缩放)
  - [ ] 光照和材质设置

- [x] **异步任务处理** (#32, 2025-10-24)
  - [x] 配置 Redis 和 Celery
  - [x] 实现测试任务(delayed_return)
  - [x] 任务状态查询接口
  - [x] Docker Compose 添加 Celery Worker 服务
  - [ ] 实现模型生成异步任务
  - [ ] 前端轮询机制

- [x] **开发工具配置** (#39, 2025-10-24)
  - [x] 配置 Python Black, Flake8, MyPy
  - [x] 配置 ESLint, Prettier
  - [x] 添加 pre-commit hooks
  - [x] 创建测试目录结构
  - [x] 添加 vitest 配置
  - [x] 更新 package.json 和 requirements.txt

### P1 - 增强功能

- [ ] **图片风格化处理** (#待分配, 2025-10-25)
  - [x] 创建腾讯云 API 示例代码和文档 (example/tencent_cloud/)
  - [x] 更新 ARCH.md 和 INITIAL.md 技术选型
  - [x] 更新 IStyleEngine 接口定义
  - [x] 创建完整的风格化 API 设计文档 (docs/API_STYLE.md)
  - [ ] 实现腾讯云风格化客户端 (infrastructure/ai/tencent_style.py)
  - [ ] 实现风格化应用服务 (application/services/style_service.py)
  - [ ] 实现风格化 API 路由 (api/v1/routers/styles.py)
  - [ ] 实现风格化 Celery 任务 (infrastructure/tasks/style_tasks.py)
  - [ ] 前端风格选择器组件
  - [ ] 前端风格化预览功能
  - [ ] 集成测试和 API 测试

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

- [ ] **模型编辑**
  - [ ] 基础模型修复
  - [ ] 尺寸调整
  - [ ] 模型合并

- [ ] **社区功能准备**
  - [ ] 模型分享机制
  - [ ] 点赞和收藏

## 已完成任务

- [x] 2025-10-25: 图片风格化模块设计文档补充
  - 创建腾讯云图像风格化 API 示例代码 (example/tencent_cloud/)
  - 创建风格预设映射配置文件 (style_presets_mapping.json)
  - 编写完整的腾讯云 API 使用文档 (example/tencent_cloud/README.md)
  - 更新 ARCH.md 和 INITIAL.md 中的技术选型
  - 增强 IStyleEngine 接口以支持腾讯云 API
  - 创建完整的风格化 API 设计文档 (docs/API_STYLE.md)
  - 添加腾讯云 SDK 依赖到 requirements.txt
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
