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

- [x] **异步任务处理** (#32, 2025-10-24)
  - [x] 配置 Redis 和 Celery
  - [x] 实现测试任务(delayed_return)
  - [x] 任务状态查询接口
  - [x] Docker Compose 添加 Celery Worker 服务
  - [ ] 实现模型生成异步任务
  - [ ] 前端轮询机制

### P1 - 增强功能

- [ ] **打印机适配系统** (#45, 2025-10-24)
  - [ ] P0 阶段 - 核心功能 (5-7天)
    - [ ] 任务组1: 领域模型和接口 (1天)
      - [ ] 创建 domain/models/printer.py (Printer, ConnectionConfig, PrinterCapabilities)
      - [ ] 创建 domain/models/print_job.py (PrintJob, PrintQueue, SlicingConfig)
      - [ ] 创建 domain/interfaces/i_printer_adapter.py
      - [ ] 创建相关枚举和值对象
      - [ ] 编写单元测试
    - [ ] 任务组2: Bambu H2D 适配器 (2天)
      - [ ] 研究 BambuTools/bambulabs_api 源码
      - [ ] 实现 infrastructure/printer_adapters/bambu_adapter.py
      - [ ] MQTT 连接和消息处理
      - [ ] FTP 文件上传
      - [ ] 状态解析和命令发送
      - [ ] 集成测试
    - [ ] 任务组3: 打印任务队列 (1.5天)
      - [ ] 实现 application/services/print_job_queue_service.py
      - [ ] 队列添加、删除、重排序逻辑
      - [ ] 等待时间估算算法
      - [ ] 单元测试
    - [ ] 任务组4: 切片引擎集成 (1天)
      - [ ] 下载和配置 CuraEngine
      - [ ] 实现 infrastructure/slicing/cura_engine.py
      - [ ] 创建拓竹 H2D 打印机配置文件
      - [ ] 实现 G-code 分析(时间、材料、层数)
      - [ ] Celery 异步任务: slice_model_task
    - [ ] 任务组5: API 接口 (1.5天)
      - [ ] 定义 Schemas (printer.py, print_job.py, print_queue.py)
      - [ ] 实现路由 (printers.py, print_jobs.py, print_queue.py, slice.py)
      - [ ] 实现应用服务层
      - [ ] WebSocket 实时进度推送
    - [ ] 任务组6: 前端 UI (2天)
      - [ ] 打印机管理页面(PrinterListPage, PrinterCard, AddPrinterModal)
      - [ ] 打印队列页面(QueuePage, JobQueueItem, CurrentJobCard)
      - [ ] 任务创建页面(CreateJobPage, SlicingConfigEditor)
      - [ ] 打印监控页面(JobMonitorPage, ProgressBar, TemperatureChart)
      - [ ] WebSocket 集成
  - [ ] P1 阶段 - 增强功能 (3-4天)
    - [ ] 打印机配置管理(导入/导出配置)
    - [ ] 多打印机类型支持(通用适配器、Prusa适配器)
    - [ ] 打印历史和统计(历史记录、统计图表)
    - [ ] 高级队列管理(自动调度、批量操作)
  - [ ] P2 阶段 - 高级功能 (2-3天)
    - [ ] 远程监控增强(打印机摄像头、告警通知)
    - [ ] 材料管理(材料库、成本追踪)
    - [ ] 高级切片功能(G-code可视化、切片优化)

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
- [x] 2025-10-24: 完成打印机适配系统架构设计 (#45)

## 工作中发现的子任务

### 待添加
- 需要创建 README.md 说明项目设置和运行方式
- 需要准备 Docker Compose 配置模板
- 需要准备环境变量模板 (.env.example)

### 技术债务
- INITAL.md 文件名拼写错误 (应为 INITIAL.md)

### 新增需求 (来自 #45)
- 需要添加 paho-mqtt 依赖 (MQTT 客户端)
- 需要添加 pygcode 依赖 (G-code 分析)
- 需要下载和配置 CuraEngine
- 需要创建拓竹 H2D 打印机配置文件
- 需要在前端添加 chart.js 和 socket.io-client 依赖

## 备注

- 优先完成 P0 MVP 核心功能,确保端到端流程走通
- 每个任务完成后立即标记并提交代码
- 遇到问题及时记录到"工作中发现"部分
