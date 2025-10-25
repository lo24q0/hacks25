# 图片风格化 API 设计文档

## 1. API 概述

图片风格化模块提供将普通照片转换为不同艺术风格的能力，基于腾讯云图像风格化 API 实现。

### 1.1 核心功能

- ✅ 5 种预设风格转换（动漫、3D卡通、素描、水彩画、油画）
- ✅ 异步任务处理
- ✅ 任务状态查询
- ✅ 风格预设列表查询
- ✅ 结果图片下载

### 1.2 技术架构

```
前端上传图片
    ↓
API 路由接收请求
    ↓
创建风格化任务
    ↓
Celery 异步执行
    ↓
调用腾讯云 API
    ↓
保存结果图片
    ↓
返回下载链接
```

---

## 2. API 端点设计

### 2.1 创建风格化任务

**端点**: `POST /api/v1/styles/transfer`

**功能**: 上传图片并创建风格化任务

**请求**:

```http
POST /api/v1/styles/transfer HTTP/1.1
Content-Type: multipart/form-data
Authorization: Bearer <token> (P2 阶段启用)

file: <binary_image_data>
style_type: anime
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|-------|------|------|------|------|
| `file` | File | 是 | 上传的图片文件 | `.jpg`, `.png` |
| `style_type` | String | 是 | 风格类型 | `anime`, `cartoon_3d`, `sketch`, `watercolor`, `oil_painting` |
| `strength` | Integer | 否 | 风格强度 (0-100) | 默认根据风格类型自动选择 |

**请求示例 (curl)**:

```bash
curl -X POST "http://localhost:8000/api/v1/styles/transfer" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@portrait.jpg" \
  -F "style_type=anime"
```

**响应**:

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "style_type": "anime",
    "created_at": "2025-10-25T10:30:00Z",
    "estimated_time": 20
  },
  "message": "风格化任务已创建，请轮询查询结果",
  "timestamp": "2025-10-25T10:30:00Z"
}
```

**响应字段**:

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `task_id` | String (UUID) | 任务唯一标识 |
| `status` | String | 任务状态: `pending`, `processing`, `completed`, `failed` |
| `style_type` | String | 风格类型 |
| `created_at` | String (ISO8601) | 任务创建时间 |
| `estimated_time` | Integer | 预计处理时间（秒） |

**错误响应**:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "不支持的文件格式，仅支持 JPG、PNG、WEBP",
    "details": "文件类型: application/pdf"
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

---

### 2.2 查询任务状态

**端点**: `GET /api/v1/styles/tasks/{task_id}`

**功能**: 查询风格化任务的处理状态和结果

**请求**:

```http
GET /api/v1/styles/tasks/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
```

**响应（处理中）**:

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "style_type": "anime",
    "progress": 45,
    "created_at": "2025-10-25T10:30:00Z",
    "updated_at": "2025-10-25T10:30:15Z"
  },
  "timestamp": "2025-10-25T10:30:20Z"
}
```

**响应（已完成）**:

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "style_type": "anime",
    "input_image": "/uploads/550e8400_input.jpg",
    "result_image": "/outputs/550e8400_styled.jpg",
    "result_url": "http://localhost:8000/api/v1/storage/download/550e8400_styled.jpg",
    "metadata": {
      "original_size": "1024x1024",
      "result_size": "1024x1024",
      "processing_time": 18.5,
      "tencent_request_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    },
    "created_at": "2025-10-25T10:30:00Z",
    "completed_at": "2025-10-25T10:30:18Z"
  },
  "timestamp": "2025-10-25T10:30:20Z"
}
```

**响应（失败）**:

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "failed",
    "style_type": "anime",
    "error": {
      "code": "TENCENT_API_ERROR",
      "message": "图片分辨率过大",
      "suggestion": "请将图片压缩至 2048x2048 以下后重试"
    },
    "created_at": "2025-10-25T10:30:00Z",
    "failed_at": "2025-10-25T10:30:10Z"
  },
  "timestamp": "2025-10-25T10:30:20Z"
}
```

---

### 2.3 获取风格预设列表

**端点**: `GET /api/v1/styles/presets`

**功能**: 获取所有可用的风格预设信息

**请求**:

```http
GET /api/v1/styles/presets HTTP/1.1
```

**响应**:

```json
{
  "success": true,
  "data": {
    "presets": [
      {
        "id": "anime",
        "name": "动漫风格",
        "name_en": "Anime Style",
        "description": "将照片转换为日系动漫风格，适合人物照片",
        "preview_image": "/assets/style-previews/anime.jpg",
        "tags": ["二次元", "动漫", "卡通"],
        "recommended_strength": 80,
        "estimated_time": 20,
        "use_cases": ["人物肖像", "头像制作", "社交媒体内容"]
      },
      {
        "id": "cartoon_3d",
        "name": "3D卡通风格",
        "name_en": "3D Cartoon",
        "description": "转换为3D卡通效果，类似皮克斯动画风格",
        "preview_image": "/assets/style-previews/cartoon_3d.jpg",
        "tags": ["卡通", "3D", "可爱"],
        "recommended_strength": 75,
        "estimated_time": 30,
        "use_cases": ["儿童照片", "宠物照片", "创意头像"]
      }
      // ... 其他风格
    ],
    "total": 5
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

---

### 2.4 下载结果图片

**端点**: `GET /api/v1/storage/download/{filename}`

**功能**: 下载风格化后的图片

**请求**:

```http
GET /api/v1/storage/download/550e8400_styled.jpg HTTP/1.1
```

**响应**:

```http
HTTP/1.1 200 OK
Content-Type: image/jpeg
Content-Disposition: attachment; filename="550e8400_styled.jpg"
Content-Length: 1234567

<binary_image_data>
```

---

## 3. 数据模型

### 3.1 StyleTask（风格化任务）

```python
class StyleTask:
    """风格化任务模型"""
    id: UUID                    # 任务ID
    user_id: Optional[UUID]     # 用户ID (P2)
    status: TaskStatus          # 任务状态
    style_type: str             # 风格类型
    input_image_path: str       # 输入图片路径
    result_image_path: Optional[str]  # 结果图片路径
    strength: int = 80          # 风格强度
    metadata: StyleTaskMetadata # 元数据
    error: Optional[ErrorInfo]  # 错误信息
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
```

### 3.2 TaskStatus（任务状态）

```python
class TaskStatus(Enum):
    PENDING = "pending"         # 等待处理
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 失败
```

### 3.3 StylePreset（风格预设）

```python
class StylePreset:
    """风格预设"""
    id: str                     # 预设ID
    name: str                   # 中文名称
    name_en: str                # 英文名称
    description: str            # 描述
    tencent_style_id: int       # 腾讯云 StyleId
    preview_image: str          # 预览图路径
    tags: List[str]             # 标签
    recommended_strength: int   # 推荐强度
    estimated_time: int         # 预计时间（秒）
    use_cases: List[str]        # 适用场景
```

---

## 4. 错误码定义

### 4.1 客户端错误 (4xx)

| 错误码 | HTTP 状态码 | 描述 | 解决方案 |
|-------|------------|------|---------|
| `INVALID_FILE_FORMAT` | 400 | 不支持的文件格式 | 仅支持 JPG、PNG、WEBP |
| `FILE_TOO_LARGE` | 400 | 文件过大 | 压缩至 10MB 以下 |
| `INVALID_STYLE_TYPE` | 400 | 不支持的风格类型 | 使用 `/presets` 查询可用风格 |
| `TASK_NOT_FOUND` | 404 | 任务不存在 | 检查 task_id 是否正确 |
| `QUOTA_EXCEEDED` | 429 | 超出配额限制 | 等待配额重置或升级账户 (P2) |

### 4.2 服务端错误 (5xx)

| 错误码 | HTTP 状态码 | 描述 | 解决方案 |
|-------|------------|------|---------|
| `TENCENT_API_ERROR` | 502 | 腾讯云 API 调用失败 | 稍后重试 |
| `STORAGE_ERROR` | 500 | 文件存储失败 | 联系技术支持 |
| `TASK_TIMEOUT` | 504 | 任务处理超时 | 重新提交任务 |

---

## 5. 使用流程

### 5.1 完整的风格化流程

```javascript
// 1. 获取可用风格列表
const presetsResponse = await fetch('/api/v1/styles/presets');
const { presets } = await presetsResponse.json();
console.log('可用风格:', presets);

// 2. 上传图片并创建任务
const formData = new FormData();
formData.append('file', imageFile);
formData.append('style_type', 'anime');

const createResponse = await fetch('/api/v1/styles/transfer', {
  method: 'POST',
  body: formData
});
const { task_id } = await createResponse.json();

// 3. 轮询查询任务状态
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(`/api/v1/styles/tasks/${task_id}`);
  const { data } = await statusResponse.json();

  if (data.status === 'completed') {
    clearInterval(pollInterval);
    console.log('处理完成!', data.result_url);
    // 下载或显示结果图片
    displayImage(data.result_url);
  } else if (data.status === 'failed') {
    clearInterval(pollInterval);
    console.error('处理失败:', data.error.message);
  } else {
    console.log('处理中...', data.progress + '%');
  }
}, 2000); // 每 2 秒查询一次
```

### 5.2 前端状态管理（React 示例）

```typescript
// features/style-transfer/hooks/useStyleTransfer.ts
import { useState, useCallback } from 'react';

interface StyleTransferState {
  taskId: string | null;
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  resultUrl: string | null;
  error: string | null;
}

export const useStyleTransfer = () => {
  const [state, setState] = useState<StyleTransferState>({
    taskId: null,
    status: 'idle',
    progress: 0,
    resultUrl: null,
    error: null,
  });

  const transferStyle = useCallback(async (file: File, styleType: string) => {
    // 上传并创建任务
    setState(prev => ({ ...prev, status: 'uploading' }));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('style_type', styleType);

    const response = await fetch('/api/v1/styles/transfer', {
      method: 'POST',
      body: formData,
    });

    const { task_id } = await response.json();
    setState(prev => ({ ...prev, taskId: task_id, status: 'processing' }));

    // 开始轮询
    pollTaskStatus(task_id);
  }, []);

  const pollTaskStatus = async (taskId: string) => {
    const interval = setInterval(async () => {
      const response = await fetch(`/api/v1/styles/tasks/${taskId}`);
      const { data } = await response.json();

      if (data.status === 'completed') {
        clearInterval(interval);
        setState({
          taskId,
          status: 'completed',
          progress: 100,
          resultUrl: data.result_url,
          error: null,
        });
      } else if (data.status === 'failed') {
        clearInterval(interval);
        setState({
          taskId,
          status: 'failed',
          progress: 0,
          resultUrl: null,
          error: data.error.message,
        });
      } else {
        setState(prev => ({
          ...prev,
          progress: data.progress || 50,
        }));
      }
    }, 2000);
  };

  return { state, transferStyle };
};
```

---

## 6. 性能和限制

### 6.1 请求限制

| 限制类型 | 限制值 | 说明 |
|---------|-------|------|
| 单个文件大小 | 10 MB | 超过限制返回 400 错误 |
| 图片分辨率 | 2048 x 2048 | 建议范围，超过可能导致处理失败 |
| QPS（每秒请求数） | 5 | 腾讯云 API 限制 |
| 每日配额（免费） | 100 次 | 超过后按量计费 |
| 任务超时时间 | 60 秒 | 超时自动标记为失败 |

### 6.2 优化建议

1. **图片预处理**：
   - 前端上传前压缩图片
   - 建议分辨率：1024x1024 到 2048x2048
   - 建议格式：JPEG（文件更小）

2. **轮询策略**：
   - 初始间隔：2 秒
   - 指数退避：如果长时间未完成，增加轮询间隔
   - 最大轮询次数：30 次（避免无限轮询）

3. **缓存策略**：
   - 相同图片+风格的结果可缓存 7 天
   - 使用图片 hash + style_type 作为缓存 key

---

## 7. 测试用例

### 7.1 API 测试用例

```python
# tests/api/test_style_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_style_task(client: AsyncClient):
    """测试创建风格化任务"""
    files = {"file": ("test.jpg", open("test.jpg", "rb"), "image/jpeg")}
    data = {"style_type": "anime"}

    response = await client.post("/api/v1/styles/transfer", files=files, data=data)

    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert "task_id" in result["data"]
    assert result["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_invalid_style_type(client: AsyncClient):
    """测试无效的风格类型"""
    files = {"file": ("test.jpg", open("test.jpg", "rb"), "image/jpeg")}
    data = {"style_type": "invalid_style"}

    response = await client.post("/api/v1/styles/transfer", files=files, data=data)

    assert response.status_code == 400
    result = response.json()
    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_STYLE_TYPE"


@pytest.mark.asyncio
async def test_get_style_presets(client: AsyncClient):
    """测试获取风格预设列表"""
    response = await client.get("/api/v1/styles/presets")

    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert len(result["data"]["presets"]) == 5
```

---

## 8. 安全考虑

### 8.1 文件上传安全

- ✅ 文件类型白名单：仅允许 JPG、PNG、WEBP
- ✅ 文件大小限制：10 MB
- ✅ 文件名随机化：使用 UUID 避免路径遍历
- ✅ 临时文件自动清理：24 小时后删除

### 8.2 API 安全

- ✅ 速率限制：IP 级别和用户级别限流
- ✅ 输入验证：所有参数严格验证
- ✅ 错误信息脱敏：不暴露内部实现细节
- ⚠️ 认证授权：P2 阶段引入 JWT

---

## 附录

### A. 完整的请求/响应示例

参见 [example/tencent_cloud/README.md](../example/tencent_cloud/README.md)

### B. 风格预设配置

参见 [example/tencent_cloud/style_presets_mapping.json](../example/tencent_cloud/style_presets_mapping.json)

### C. 集成示例代码

参见 [example/tencent_cloud/image_style_transfer_example.py](../example/tencent_cloud/image_style_transfer_example.py)

---

**文档版本**: v1.0
**创建日期**: 2025-10-25
**最后更新**: 2025-10-25
**负责人**: AI Assistant
