# 3D模型打印系统技术架构设计文档 - 前端

## 1. 前端架构概述

### 1.1 设计原则

- **组件化开发**：按功能模块划分可复用组件
- **状态管理集中化**：使用Zustand管理全局状态
- **性能优先**：3D渲染优化,按需加载
- **响应式设计**：支持桌面端和移动端
- **类型安全**：TypeScript严格模式

---

### 2.1 前端技术栈

| 技术类别 | 选型 | 版本要求 | 选型理由 |
|---------|------|---------|---------|
| 核心框架 | React | 18.3+ | 生态成熟，组件化开发，适合SPA |
| 3D渲染引擎 | Three.js | r160+ | 功能强大，WebGL渲染性能优异 |
| React 3D库 | React Three Fiber | 8.0+ | React组件化封装Three.js，开发效率高 |
| UI框架 | Tailwind CSS | 3.4+ | 原子化CSS，快速开发，包体积小 |
| 组件库 | Headless UI | 2.0+ | 无样式UI组件，配合Tailwind使用 |
| 状态管理 | Zustand | 4.5+ | 轻量级，API简洁，适合中小型项目 |
| 文件上传 | React Dropzone | 14.0+ | 拖拽上传，预览功能完善 |
| HTTP客户端 | Axios | 1.6+ | 请求拦截、错误处理、取消请求 |
| 构建工具 | Vite | 5.0+ | 快速热更新，构建性能优异 |


---

## 2. 前端目录结构

### 2.1 整体结构

```
frontend/                 # 前端项目
├── src/
│   ├── app/             # 应用入口
│   ├── features/        # 功能模块（按领域划分）
│   ├── shared/          # 共享组件和工具
│   └── infrastructure/  # 基础设施（API客户端）
├── public/
├── package.json
└── vite.config.ts
```


```
frontend/src/
├── app/                     # 应用入口
│   ├── App.tsx
│   ├── main.tsx
│   ├── router.tsx
│   └── store.ts             # Zustand store
│
├── features/                # 功能模块（按业务领域）
│   ├── model-generation/    # 模型生成模块
│   │   ├── components/
│   │   │   ├── TextInput.tsx
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── ModelPreview.tsx    # Three.js预览
│   │   │   └── GenerationProgress.tsx
│   │   ├── hooks/
│   │   │   ├── useModelGeneration.ts
│   │   │   └── useModelPreview.ts
│   │   ├── api/
│   │   │   └── modelApi.ts
│   │   ├── types/
│   │   │   └── model.types.ts
│   │   └── pages/
│   │       └── GenerationPage.tsx
│   │
│   ├── style-transfer/      # 风格化模块
│   │   ├── components/
│   │   │   ├── StyleSelector.tsx
│   │   │   └── StylePreview.tsx
│   │   ├── hooks/
│   │   │   └── useStyleTransfer.ts
│   │   └── api/
│   │       └── styleApi.ts
│   │
│   ├── print-preparation/   # 打印准备模块
│   │   ├── components/
│   │   │   ├── PrinterSelector.tsx
│   │   │   ├── SlicingConfig.tsx
│   │   │   └── GCodeDownload.tsx
│   │   ├── hooks/
│   │   │   └── usePrintSlicing.ts
│   │   └── api/
│   │       └── printApi.ts
│   │
│   └── user/                # 用户模块（P2）
│       ├── components/
│       │   ├── LoginForm.tsx
│       │   └── ModelHistory.tsx
│       ├── hooks/
│       │   └── useAuth.ts
│       └── api/
│           └── authApi.ts
│
├── shared/                  # 共享组件和工具
│   ├── components/
│   │   ├── ui/             # UI基础组件
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loading.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Layout.tsx
│   ├── hooks/
│   │   ├── useAsync.ts
│   │   └── useLocalStorage.ts
│   ├── utils/
│   │   ├── format.ts
│   │   └── validation.ts
│   └── types/
│       └── common.types.ts
│
├── infrastructure/          # 基础设施
│   ├── api/
│   │   ├── client.ts        # Axios配置
│   │   ├── interceptors.ts
│   │   └── endpoints.ts
│   └── three/               # Three.js封装
│       ├── SceneManager.ts
│       ├── ModelLoader.ts
│       └── Controls.ts
│
├── assets/                  # 静态资源
│   ├── images/
│   ├── fonts/
│   └── styles/
│       └── globals.css
│
└── types/                   # 全局类型定义
    └── index.d.ts
```

#### 5.4.3 模块化原则

- **前端按功能模块组织**：每个feature包含完整的UI、逻辑、API调用
- **后端按分层架构组织**：清晰的职责分离
- **共享代码独立管理**：避免循环依赖
- **测试代码镜像源码结构**：便于定位和维护


---

## 3. 性能优化策略

### 9.1 前端优化

1. **资源优化**：
   - Three.js按需加载
   - 图片懒加载
   - 代码分割（Vite动态导入）
   - Gzip压缩

2. **渲染优化**：
   - 模型LOD（细节层次）
   - Web Worker处理大文件
   - 虚拟滚动（历史记录）

3. **缓存策略**：
   - Service Worker缓存静态资源
   - LocalStorage缓存用户配置
   - IndexedDB缓存模型元数据


---

## 4. 开发规范

### 4.1 TypeScript规范

- ESLint + Prettier
- 严格模式（strict: true）
- 组件必须类型化
- 禁止使用any

### 4.2 测试策略

**测试金字塔**：
```
    /\
   /E2E\      <- 10% (关键业务流程)
  /------\
 /  API   \   <- 30% (API集成测试)
/----------\
/   Unit    \ <- 60% (单元测试)
```

**覆盖率要求**：
- 组件层：>70%
- Hooks层：>80%
- 工具函数：>90%

---

**文档版本**: v1.0  
**创建日期**: 2025-10-24  
**最后更新**: 2025-10-24
