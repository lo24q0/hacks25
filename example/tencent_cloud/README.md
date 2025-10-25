# 腾讯云图像风格化 API 使用文档

## 目录

- [产品介绍](#产品介绍)
- [快速开始](#快速开始)
- [API 调用示例](#api-调用示例)
- [风格预设说明](#风格预设说明)
- [最佳实践](#最佳实践)
- [错误处理](#错误处理)
- [集成到项目](#集成到项目)

---

## 产品介绍

### 服务概述

腾讯云**智能创作引擎**提供的图像风格化能力,可以将普通照片转换为多种艺术风格,包括:

- 🎨 动漫风格 (Anime)
- 🎭 3D卡通风格 (Cartoon)
- ✏️ 素描风格 (Sketch)
- 🖌️ 水彩画风格 (Watercolor)
- 🎨 油画风格 (Oil Painting)

### 官方文档

- **产品文档**: https://cloud.tencent.com/document/product/1668/88066
- **API 文档**: https://cloud.tencent.com/document/api/1668/55923
- **SDK 下载**: https://cloud.tencent.com/document/sdk/Python

---

## 快速开始

### 1. 开通服务

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 搜索"智能创作引擎"并开通服务
3. 进入 [访问管理 - API 密钥](https://console.cloud.tencent.com/cam/capi) 获取 `SecretId` 和 `SecretKey`

### 2. 安装 SDK

```bash
pip install tencentcloud-sdk-python-aiart
```

**版本要求**:
- Python >= 3.7
- tencentcloud-sdk-python-aiart >= 3.0.0

### 3. 环境变量配置

创建 `.env` 文件:

```bash
# 腾讯云 API 凭证
TENCENT_CLOUD_SECRET_ID=AKIDxxxxxxxxxxxxxxxx
TENCENT_CLOUD_SECRET_KEY=xxxxxxxxxxxxxxxx

# 可选:指定地域
TENCENT_CLOUD_REGION=ap-guangzhou  # 可选: ap-beijing, ap-shanghai
```

### 4. 运行示例代码

```bash
python image_style_transfer_example.py
```

---

## API 调用示例

### 基础调用

```python
from image_style_transfer_example import TencentCloudStyleTransfer

# 初始化客户端
client = TencentCloudStyleTransfer(
    secret_id="YOUR_SECRET_ID",
    secret_key="YOUR_SECRET_KEY",
    region="ap-guangzhou"
)

# 执行风格转换
result = client.transfer_style(
    image_path="input.jpg",      # 输入图片路径
    style_type="anime",          # 风格类型
    output_path="output.jpg"     # 输出路径
)

print(f"转换成功! 请求ID: {result['request_id']}")
print(f"输出文件: {result['output_path']}")
```

### 支持的风格类型

| 风格 ID | 中文名称 | 英文名称 | 腾讯云 StyleId | 推荐强度 |
|---------|---------|----------|---------------|---------|
| `anime` | 动漫风格 | Anime Style | 201 | 80 |
| `cartoon` | 3D卡通 | 3D Cartoon | 202 | 75 |
| `sketch` | 素描风格 | Sketch | 203 | 70 |
| `watercolor` | 水彩画 | Watercolor | 204 | 85 |
| `oil_painting` | 油画 | Oil Painting | 205 | 90 |

### 请求参数说明

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `InputImage` | String | 是 | 输入图片,支持 Base64 或 URL |
| `StyleId` | Integer | 是 | 风格 ID,见上表 |
| `Strength` | Integer | 否 | 风格强度 0-100,默认 80 |
| `RspImgType` | String | 否 | 返回类型: `base64` 或 `url` |

### 返回结果说明

```python
{
    "result_image": "base64_encoded_image_data",  # Base64 编码的结果图片
    "image_url": "https://temp.url/image.jpg",    # 临时 URL (1小时有效)
    "request_id": "xxxxxxxx-xxxx-xxxx-xxxx",      # 请求 ID
    "output_path": "output.jpg"                   # 本地保存路径
}
```

---

## 风格预设说明

详细的风格预设配置请参考 [style_presets_mapping.json](./style_presets_mapping.json)。

### 各风格特点

#### 1. 动漫风格 (Anime)

- **适用场景**: 人物肖像、头像制作
- **效果特点**: 日系二次元风格,线条清晰,色彩鲜艳
- **最佳实践**:
  - 使用清晰的人脸照片
  - 人脸占比建议 > 30%
  - 避免背景过于复杂
- **处理时间**: 约 10-20 秒

#### 2. 3D卡通风格 (Cartoon)

- **适用场景**: 儿童照片、宠物照片、创意头像
- **效果特点**: 类似皮克斯动画,3D 质感强
- **最佳实践**:
  - 图片分辨率不超过 2000x2000
  - 光线充足的照片效果更好
- **处理时间**: 约 15-30 秒

#### 3. 素描风格 (Sketch)

- **适用场景**: 艺术创作、设计参考
- **效果特点**: 铅笔素描,黑白输出
- **限制**: 不保留颜色信息
- **处理时间**: 约 5-15 秒

#### 4. 水彩画风格 (Watercolor)

- **适用场景**: 风景照片、花卉照片
- **效果特点**: 柔和淡雅,细节模糊
- **最佳实践**: 适合意境表达,不适合需要保留细节的场景
- **处理时间**: 约 10-20 秒

#### 5. 油画风格 (Oil Painting)

- **适用场景**: 肖像、风景、艺术收藏
- **效果特点**: 笔触明显,色彩浓郁
- **最佳实践**: 使用高质量原图,分辨率 > 1024x1024
- **处理时间**: 约 20-30 秒

---

## 最佳实践

### 1. 图片质量要求

```python
# 推荐配置
IMAGE_CONFIG = {
    "min_resolution": (512, 512),     # 最小分辨率
    "max_resolution": (2048, 2048),   # 最大分辨率
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": [".jpg", ".jpeg", ".png", ".webp"]
}
```

### 2. 异步处理 (Celery 集成)

```python
# backend/src/infrastructure/tasks/style_tasks.py
from celery import shared_task
from infrastructure.ai.tencent_style import TencentCloudStyleTransfer

@shared_task(bind=True, max_retries=3)
def process_style_transfer(self, task_id: str, image_path: str, style_type: str):
    """
    异步风格化任务。

    Args:
        task_id: 任务ID
        image_path: 图片路径
        style_type: 风格类型
    """
    try:
        client = TencentCloudStyleTransfer(
            secret_id=settings.TENCENT_CLOUD_SECRET_ID,
            secret_key=settings.TENCENT_CLOUD_SECRET_KEY,
        )

        output_path = f"/tmp/styled/{task_id}.jpg"
        result = client.transfer_style(
            image_path=image_path,
            style_type=style_type,
            output_path=output_path,
        )

        return {
            "status": "success",
            "output_path": output_path,
            "request_id": result["request_id"],
        }

    except Exception as e:
        # 重试机制
        self.retry(exc=e, countdown=5)
```

### 3. 错误重试策略

```python
import time
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

def transfer_with_retry(client, image_path, style_type, max_retries=3):
    """
    带重试的风格转换。

    Args:
        client: TencentCloudStyleTransfer 实例
        image_path: 图片路径
        style_type: 风格类型
        max_retries: 最大重试次数
    """
    for attempt in range(max_retries):
        try:
            return client.transfer_style(image_path, style_type)
        except TencentCloudSDKException as e:
            if "RequestTimeout" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"请求超时,{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                raise
```

### 4. 成本控制

```python
# 用户配额管理
class UserQuota:
    MAX_DAILY_STYLE_TRANSFERS = 10  # 每日最大调用次数

    async def check_quota(self, user_id: str) -> bool:
        """
        检查用户配额。

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否有剩余配额
        """
        today_count = await self.get_today_usage(user_id)
        return today_count < self.MAX_DAILY_STYLE_TRANSFERS
```

---

## 错误处理

### 统一错误处理

项目已实现完整的错误码映射机制,将腾讯云返回的技术性错误码映射为用户友好的错误提示。

**详细文档**: 请参阅 [腾讯云错误码映射文档](../../docs/TENCENT_CLOUD_ERROR_MAPPING.md)

### 常见错误码

| 错误码 | 系统错误码 | 错误描述 | 解决方案 | 可重试 |
|-------|-----------|---------|---------|-------|
| `FailedOperation.ImageDecodeFailed` | `INVALID_FILE_FORMAT` | 图片解码失败 | 检查图片格式和 Base64 编码 | ❌ |
| `FailedOperation.ImageResolutionExceed` | `IMAGE_RESOLUTION_TOO_HIGH` | 图片分辨率过大 | 压缩至 2048x2048 以下 | ❌ |
| `FailedOperation.RequestTimeout` | `REQUEST_TIMEOUT` | 请求超时 | 重试或降低分辨率 | ✅ |
| `LimitExceeded.TooLargeFileError` | `FILE_TOO_LARGE` | 文件过大 | 压缩至 10MB 以下 | ❌ |
| `ResourceUsSuspended.InsufficientBalance` | `INSUFFICIENT_BALANCE` | 余额不足 | 充值账户 | ❌ |

### 使用错误处理器

```python
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from error_handler import TencentCloudErrorHandler

try:
    result = client.transfer_style(
        image_path="input.jpg",
        style_type="anime"
    )
except TencentCloudSDKException as e:
    # 使用错误处理器转换异常
    system_exception = TencentCloudErrorHandler.handle_exception(e)

    # 获取用户友好的错误信息
    print(f"错误: {system_exception.user_message}")
    print(f"建议: {system_exception.suggestion}")

    # 判断是否可重试
    if TencentCloudErrorHandler.should_retry(system_exception):
        print("正在重试...")
        # 执行重试逻辑
    else:
        # 返回错误给用户
        error_response = TencentCloudErrorHandler.format_error_response(system_exception)
        return error_response
```

### 测试错误处理

运行测试脚本查看完整的错误码映射:

```bash
python test_error_mapping.py
```

---

## 集成到项目

### 1. 目录结构

```
backend/src/
├── infrastructure/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── tencent_style.py      # 腾讯云风格化客户端
│   │   └── base.py
│   └── tasks/
│       └── style_tasks.py         # Celery 风格化任务
├── application/
│   └── services/
│       └── style_service.py       # 风格化应用服务
└── api/
    └── v1/
        └── routers/
            └── styles.py          # 风格化 API 路由
```

### 2. 实现风格化客户端

```python
# backend/src/infrastructure/ai/tencent_style.py
from domain.interfaces.i_style_engine import IStyleEngine, StylePreset
from typing import List
import json
from pathlib import Path

class TencentCloudStyleEngine(IStyleEngine):
    """腾讯云风格化引擎实现"""

    def __init__(self, secret_id: str, secret_key: str):
        # 复用 example 中的客户端代码
        from example.tencent_cloud.image_style_transfer_example import TencentCloudStyleTransfer
        self.client = TencentCloudStyleTransfer(secret_id, secret_key)
        self._load_presets()

    def _load_presets(self):
        """加载风格预设配置"""
        config_path = Path("example/tencent_cloud/style_presets_mapping.json")
        with open(config_path) as f:
            data = json.load(f)
            self.presets = [StylePreset(**p) for p in data["presets"]]

    async def transfer_style(self, image_path: str, style_preset_id: str, output_path: str) -> str:
        """执行风格迁移"""
        result = self.client.transfer_style(
            image_path=image_path,
            style_type=style_preset_id,
            output_path=output_path
        )
        return result["output_path"]

    def get_available_styles(self) -> List[StylePreset]:
        """获取可用风格列表"""
        return self.presets

    def get_style_preset(self, preset_id: str) -> StylePreset:
        """获取指定风格预设"""
        for preset in self.presets:
            if preset.id == preset_id:
                return preset
        raise ValueError(f"风格预设不存在: {preset_id}")
```

### 3. API 路由实现

```python
# backend/src/api/v1/routers/styles.py
from fastapi import APIRouter, UploadFile, HTTPException
from application.services.style_service import StyleService

router = APIRouter(prefix="/styles", tags=["styles"])

@router.post("/transfer")
async def transfer_style(
    file: UploadFile,
    style_type: str,
    service: StyleService = Depends(get_style_service)
):
    """
    图片风格化接口。

    Args:
        file: 上传的图片文件
        style_type: 风格类型 (anime, cartoon, sketch, watercolor, oil_painting)

    Returns:
        任务ID和状态
    """
    # 保存上传文件
    file_path = await save_upload_file(file)

    # 创建异步任务
    task = await service.create_style_task(file_path, style_type)

    return {
        "task_id": task.id,
        "status": task.status,
        "message": "风格化任务已创建,请轮询查询结果"
    }

@router.get("/presets")
async def get_style_presets(service: StyleService = Depends(get_style_service)):
    """获取可用的风格预设列表"""
    presets = service.get_available_styles()
    return {"presets": presets}
```

### 4. 配置管理

```python
# backend/src/infrastructure/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 腾讯云配置
    TENCENT_CLOUD_SECRET_ID: str
    TENCENT_CLOUD_SECRET_KEY: str
    TENCENT_CLOUD_REGION: str = "ap-guangzhou"

    # 风格化配置
    STYLE_TRANSFER_MAX_RETRIES: int = 3
    STYLE_TRANSFER_TIMEOUT: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 费用说明

### 计费模式

- **免费额度**: 每月 100 次
- **超量计费**: 0.1 元/次 (价格仅供参考)
- **详细价格**: https://cloud.tencent.com/document/product/1668/55924

### 成本优化建议

1. **缓存结果**: 相同图片+风格的结果可以缓存
2. **用户限额**: 限制每个用户每日调用次数
3. **图片压缩**: 自动压缩过大图片,节省处理时间和成本
4. **监控告警**: 设置每日调用量告警,避免超支

---

## 技术支持

- **官方文档**: https://cloud.tencent.com/document/product/1668
- **API 工具**: https://console.cloud.tencent.com/api/explorer
- **工单支持**: https://console.cloud.tencent.com/workorder

---

## 更新日志

- **2025-10-25**: 初始版本,支持 5 种基础风格
- 计划支持更多风格类型和自定义参数

---

**最后更新**: 2025-10-25
**维护者**: AI Assistant
**版本**: v1.0
