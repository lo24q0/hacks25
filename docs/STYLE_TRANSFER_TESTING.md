# 图片风格化功能验证指南

## 📋 功能概述

前端图片风格化功能已完成开发,包括以下模块:

### ✅ 已实现的文件

1. **类型定义**: [frontend/src/features/style-transfer/types/style.types.ts](../frontend/src/features/style-transfer/types/style.types.ts)
   - StylePreset, StyleTask, TaskStatus 等接口定义

2. **API 调用**: [frontend/src/features/style-transfer/api/styleApi.ts](../frontend/src/features/style-transfer/api/styleApi.ts)
   - getStylePresets() - 获取风格列表
   - createStyleTask() - 创建任务
   - getTaskStatus() - 查询状态
   - downloadResult() - 下载结果

3. **核心组件**:
   - [StyleSelector](../frontend/src/features/style-transfer/components/StyleSelector.tsx) - 风格选择器
   - [StylePreview](../frontend/src/features/style-transfer/components/StylePreview.tsx) - 结果对比预览
   - [StyleProgress](../frontend/src/features/style-transfer/components/StyleProgress.tsx) - 进度显示

4. **自定义 Hook**: [useStyleTransfer](../frontend/src/features/style-transfer/hooks/useStyleTransfer.ts)
   - 管理整个风格化流程
   - 自动轮询任务状态
   - 错误处理和重试

5. **页面组件**: [StyleTransferPage](../frontend/src/features/style-transfer/pages/StyleTransferPage.tsx)
   - 整合所有功能的主页面
   - 分步骤引导用户操作

6. **路由配置**: 已添加 `/style-transfer` 路由

7. **导航栏**: 已添加"图片风格化"入口

---

## 🚀 启动验证

### 1. 启动后端服务

```bash
cd backend

# 确保已安装依赖
pip install -r requirements.txt

# 启动 FastAPI 服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 另开终端启动 Celery Worker
celery -A src.infrastructure.tasks.celery_app worker --loglevel=info
```

### 2. 确保 Redis 运行

```bash
# 使用 Docker 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 或使用 Docker Compose
docker-compose up -d redis
```

### 3. 配置环境变量

确保 `.env` 文件包含腾讯云配置:

```env
# 腾讯云 API 凭证
TENCENT_CLOUD_SECRET_ID=你的_SECRET_ID
TENCENT_CLOUD_SECRET_KEY=你的_SECRET_KEY
TENCENT_CLOUD_REGION=ap-guangzhou
```

### 4. 启动前端服务

```bash
cd frontend

# 安装依赖(如果需要)
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:5173

---

## ✅ 功能验证步骤

### 测试场景 1: 完整流程验证

1. **访问风格化页面**
   - 点击顶部导航栏的"图片风格化"
   - 或直接访问 http://localhost:5173/style-transfer

2. **上传图片**
   - 拖拽或点击上传区域选择图片
   - 支持格式: JPG, PNG, WEBP
   - 文件大小不超过 10MB
   - 验证: 图片预览正确显示

3. **选择风格**
   - 查看 5 种风格卡片是否正确显示
   - 点击任意风格卡片
   - 验证: 选中的卡片显示绿色勾选标记

4. **开始风格化**
   - 点击"开始风格化"按钮
   - 验证:
     - 显示进度条和处理状态
     - 预计时间倒计时正常
     - 每 2 秒自动轮询状态

5. **查看结果**
   - 等待处理完成(约 15-30 秒)
   - 验证:
     - 原图和风格化图片并排显示
     - 切换对比模式可滑动查看
     - 滑块拖动流畅

6. **下载图片**
   - 点击"下载图片"按钮
   - 验证: 文件名格式为 `{风格名}_{任务ID}.jpg`

7. **开始新的风格化**
   - 点击"开始新的风格化"按钮
   - 验证: 重置到步骤 1,可重新上传

---

### 测试场景 2: 不同风格验证

使用相同的图片测试所有 5 种风格:

| 风格ID | 风格名称 | 适用场景 | 预计时间 |
|--------|---------|---------|---------|
| anime | 动漫风格 | 人物肖像 | ~15秒 |
| cartoon_3d | 3D卡通 | 儿童/宠物照片 | ~25秒 |
| sketch | 素描风格 | 黑白艺术 | ~10秒 |
| watercolor | 水彩画 | 风景照片 | ~15秒 |
| oil_painting | 油画 | 肖像/风景 | ~25秒 |

**验证要点**:
- ✅ 每种风格都能正常处理
- ✅ 处理时间接近预估值
- ✅ 风格效果明显可见
- ✅ 结果图片质量良好

---

### 测试场景 3: 错误处理验证

#### 3.1 文件验证错误

- 上传不支持的格式(如 PDF)
  - 预期: 显示错误提示"不支持的文件格式"

- 上传超大文件(>10MB)
  - 预期: 显示错误提示"文件过大"

#### 3.2 网络错误

- 关闭后端服务
  - 预期: 显示"网络连接失败"错误

- 任务处理超时
  - 预期: 显示超时提示,建议重试

#### 3.3 API 错误

- 腾讯云 API 配置错误
  - 预期: 显示友好的错误提示
  - 包含解决建议

---

### 测试场景 4: UI/UX 验证

1. **响应式设计**
   - 调整浏览器窗口大小
   - 验证: 布局自适应正确

2. **加载状态**
   - 风格列表加载时显示 Spin
   - 任务处理时显示进度动画

3. **状态标签**
   - 等待处理: 蓝色标签 + 时钟图标
   - 处理中: 橙色标签 + 旋转图标
   - 已完成: 绿色标签 + 勾选图标
   - 失败: 红色标签 + 警告图标

4. **对比模式**
   - 普通模式: 左右并排显示
   - 对比模式: 滑块交互流畅
   - 标签显示清晰

---

## 🐛 已知问题和限制

### 当前版本限制

1. **预览图占位符**
   - 风格卡片使用渐变色占位符
   - TODO: 替换为实际的风格预览图

2. **图片URL处理**
   - 结果图片使用后端返回的路径
   - 需要确保路径拼接正确

3. **错误恢复**
   - 任务失败后需要手动重置
   - TODO: 添加自动重试机制

### 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ⚠️ IE 不支持

---

## 📊 性能指标

### 预期性能

| 指标 | 目标值 | 说明 |
|-----|-------|------|
| 页面加载时间 | < 2秒 | 首次访问 |
| 风格列表加载 | < 500ms | API 调用 |
| 图片上传响应 | < 100ms | 本地处理 |
| 任务创建耗时 | < 1秒 | API 调用 + 异步任务 |
| 轮询间隔 | 2秒 | 自动查询状态 |
| 最大轮询次数 | 60次 | 防止无限轮询 |

### 监控要点

- 任务成功率
- 平均处理时间
- 错误类型分布
- 用户放弃率

---

## 🔍 调试技巧

### 1. 查看网络请求

打开浏览器开发者工具 -> Network:

```
GET /api/v1/styles/presets        // 获取风格列表
POST /api/v1/styles/transfer      // 创建任务
GET /api/v1/styles/tasks/{id}     // 查询状态
GET /api/v1/styles/tasks/{id}/result  // 下载结果
```

### 2. 查看 Console 日志

```javascript
// Hook 状态变化
console.log('State:', state);

// API 调用
console.log('API Request:', request);
console.log('API Response:', response);

// 轮询信息
console.log('Polling task status...', taskId);
```

### 3. 查看后端日志

```bash
# FastAPI 日志
tail -f logs/app.log

# Celery Worker 日志
celery -A src.infrastructure.tasks.celery_app worker --loglevel=debug
```

### 4. 常见问题排查

**问题**: 风格列表不显示
- 检查: 后端 API 是否正常 `curl http://localhost:8000/api/v1/styles/presets`
- 检查: CORS 配置是否正确

**问题**: 任务一直处于 pending 状态
- 检查: Celery Worker 是否启动
- 检查: Redis 连接是否正常

**问题**: 结果图片不显示
- 检查: 图片路径是否正确
- 检查: 后端文件服务是否正常

---

## 📝 验证清单

### 功能完整性

- [ ] 能访问风格化页面
- [ ] 能上传图片并预览
- [ ] 能查看 5 种风格预设
- [ ] 能选择风格并高亮显示
- [ ] 能创建风格化任务
- [ ] 能显示处理进度
- [ ] 能自动轮询任务状态
- [ ] 能查看风格化结果
- [ ] 能切换对比模式
- [ ] 能下载结果图片
- [ ] 能重置并开始新任务

### 错误处理

- [ ] 文件格式验证正确
- [ ] 文件大小限制生效
- [ ] 网络错误提示友好
- [ ] API 错误有解决建议
- [ ] 超时后能正确提示

### UI/UX

- [ ] 步骤引导清晰
- [ ] 加载状态显示正确
- [ ] 状态标签颜色准确
- [ ] 对比模式交互流畅
- [ ] Toast 提示及时准确

### 性能

- [ ] 页面加载快速
- [ ] 图片上传响应及时
- [ ] 轮询不影响界面
- [ ] 内存占用合理

---

## 🎯 后续优化方向

### 短期优化(P1)

1. **添加实际预览图**
   - 为每种风格准备示例图片
   - 替换当前的渐变色占位符

2. **优化轮询策略**
   - 实现指数退避算法
   - 根据预估时间动态调整间隔

3. **完善错误提示**
   - 添加更详细的错误码映射
   - 提供一键重试按钮

4. **性能优化**
   - 图片压缩预处理
   - 懒加载风格预设

### 长期优化(P2)

1. **批量风格化**
   - 一次上传多张图片
   - 应用相同风格

2. **历史记录**
   - 保存用户的风格化历史
   - 支持重新下载

3. **高级功能**
   - 自定义风格强度滑块
   - 局部风格化(选区)
   - 风格混合

4. **社交功能**
   - 分享风格化作品
   - 查看热门风格

---

## 📞 联系支持

如遇到问题,请:

1. 查看本文档的"常见问题排查"部分
2. 查看后端日志和浏览器 Console
3. 提交 Issue 到项目仓库

---

**文档版本**: v1.0
**创建日期**: 2025-10-26
**最后更新**: 2025-10-26
**维护者**: AI Assistant
