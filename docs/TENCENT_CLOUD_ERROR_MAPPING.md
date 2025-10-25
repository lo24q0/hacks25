# 腾讯云 API 错误码映射文档

## 1. 概述

本文档定义了腾讯云图像风格化 API 错误码与系统统一错误码的映射关系,实现错误信息的统一处理和用户友好的错误提示。

### 1.1 设计目标

- ✅ **统一错误处理**: 将腾讯云返回的技术性错误码映射为系统统一的业务错误码
- ✅ **用户友好提示**: 提供清晰易懂的错误信息和解决建议
- ✅ **可扩展性**: 支持新增错误码映射
- ✅ **可追溯性**: 保留原始腾讯云错误信息用于问题排查

### 1.2 相关文件

| 文件路径 | 说明 |
|---------|------|
| `backend/src/shared/exceptions/tencent_cloud_exceptions.py` | 腾讯云异常类定义 |
| `backend/src/shared/config/tencent_cloud_error_mapping.py` | 错误码映射配置 |
| `example/tencent_cloud/error_handler.py` | 错误处理器实现 |
| `example/tencent_cloud/test_error_mapping.py` | 错误映射测试 |

---

## 2. 错误码映射表

### 2.1 图片相关错误

| 腾讯云错误码 | 系统错误码 | 错误描述 | HTTP 状态码 | 可重试 |
|-------------|-----------|---------|------------|-------|
| `FailedOperation.ImageDecodeFailed` | `INVALID_FILE_FORMAT` | 图片解码失败,无法识别文件格式 | 400 | ❌ |
| `FailedOperation.ImageResolutionExceed` | `IMAGE_RESOLUTION_TOO_HIGH` | 图片分辨率过大 | 400 | ❌ |
| `FailedOperation.ImageSizeExceed` | `FILE_TOO_LARGE` | 图片文件大小超出限制 | 400 | ❌ |
| `LimitExceeded.TooLargeFileError` | `FILE_TOO_LARGE` | 图片文件过大 | 400 | ❌ |
| `FailedOperation.ImageDownloadError` | `IMAGE_DOWNLOAD_FAILED` | 无法下载图片 | 400 | ❌ |

**解决建议**:
- `INVALID_FILE_FORMAT`: 请确保上传的是有效的 JPG、PNG 或 WEBP 图片文件
- `IMAGE_RESOLUTION_TOO_HIGH`: 请将图片压缩至 2048x2048 像素以下
- `FILE_TOO_LARGE`: 请将文件压缩至 10MB 以下

### 2.2 请求相关错误

| 腾讯云错误码 | 系统错误码 | 错误描述 | HTTP 状态码 | 可重试 |
|-------------|-----------|---------|------------|-------|
| `FailedOperation.RequestTimeout` | `REQUEST_TIMEOUT` | 请求处理超时 | 504 | ✅ |
| `FailedOperation.ServerError` | `TENCENT_API_ERROR` | 腾讯云服务暂时不可用 | 502 | ✅ |
| `FailedOperation.InnerError` | `TENCENT_API_ERROR` | 腾讯云内部处理错误 | 502 | ✅ |

**解决建议**:
- `REQUEST_TIMEOUT`: 请稍后重试,或尝试降低图片分辨率
- `TENCENT_API_ERROR`: 请稍后重试,如持续出现请联系技术支持

### 2.3 风格化相关错误

| 腾讯云错误码 | 系统错误码 | 错误描述 | HTTP 状态码 | 可重试 |
|-------------|-----------|---------|------------|-------|
| `FailedOperation.StyleNotSupported` | `INVALID_STYLE_TYPE` | 不支持的风格类型 | 400 | ❌ |
| `FailedOperation.ImageStyleTransferFail` | `STYLE_TRANSFER_FAILED` | 风格化处理失败 | 500 | ❌ |

**解决建议**:
- `INVALID_STYLE_TYPE`: 请使用 `/api/v1/styles/presets` 查询支持的风格列表
- `STYLE_TRANSFER_FAILED`: 请尝试更换其他风格或重新上传图片

### 2.4 认证和权限错误

| 腾讯云错误码 | 系统错误码 | 错误描述 | HTTP 状态码 | 可重试 |
|-------------|-----------|---------|------------|-------|
| `AuthFailure.SignatureFailure` | `AUTHENTICATION_FAILED` | API 密钥认证失败 | 401 | ❌ |
| `AuthFailure.SecretIdNotFound` | `AUTHENTICATION_FAILED` | API 密钥不存在 | 401 | ❌ |
| `AuthFailure.InvalidSecretId` | `AUTHENTICATION_FAILED` | API 密钥无效 | 401 | ❌ |

**解决建议**:
- `AUTHENTICATION_FAILED`: 请检查腾讯云 SecretId 和 SecretKey 配置,联系系统管理员

### 2.5 配额和限流错误

| 腾讯云错误码 | 系统错误码 | 错误描述 | HTTP 状态码 | 可重试 |
|-------------|-----------|---------|------------|-------|
| `ResourceUsSuspended.InsufficientBalance` | `INSUFFICIENT_BALANCE` | 腾讯云账户余额不足 | 402 | ❌ |
| `LimitExceeded.FreqLimit` | `RATE_LIMIT_EXCEEDED` | 请求过于频繁 | 429 | ✅ |
| `ResourceUsSuspended.Arrears` | `SERVICE_SUSPENDED` | 腾讯云服务已欠费暂停 | 402 | ❌ |

**解决建议**:
- `INSUFFICIENT_BALANCE`: 请充值腾讯云账户
- `RATE_LIMIT_EXCEEDED`: 请降低请求频率,稍后重试
- `SERVICE_SUSPENDED`: 请充值腾讯云账户恢复服务

### 2.6 参数相关错误

| 腾讯云错误码 | 系统错误码 | 错误描述 | HTTP 状态码 | 可重试 |
|-------------|-----------|---------|------------|-------|
| `InvalidParameter` | `INVALID_PARAMETER` | 请求参数错误 | 400 | ❌ |
| `MissingParameter` | `MISSING_PARAMETER` | 缺少必要参数 | 400 | ❌ |
| `InvalidParameterValue` | `INVALID_PARAMETER_VALUE` | 参数值不符合要求 | 400 | ❌ |

**解决建议**:
- `INVALID_PARAMETER`: 请检查请求参数是否符合 API 文档要求
- `MISSING_PARAMETER`: 请提供所有必需的参数
- `INVALID_PARAMETER_VALUE`: 请检查参数值的格式和范围

---

## 3. 使用指南

### 3.1 在代码中使用错误映射

#### 3.1.1 基础用法

```python
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from example.tencent_cloud.error_handler import TencentCloudErrorHandler

try:
    # 调用腾讯云 API
    result = tencent_client.ImageToImage(request)

except TencentCloudSDKException as e:
    # 使用错误处理器转换异常
    system_exception = TencentCloudErrorHandler.handle_exception(e)

    # 判断是否可重试
    if TencentCloudErrorHandler.should_retry(system_exception):
        print("错误可重试,正在重试...")
        # 执行重试逻辑
    else:
        # 返回错误响应给用户
        error_response = TencentCloudErrorHandler.format_error_response(system_exception)
        return error_response
```

#### 3.1.2 在 Celery 任务中使用

```python
from celery import shared_task
from example.tencent_cloud.error_handler import TencentCloudErrorHandler
from backend.src.shared.exceptions import TencentCloudAPIError

@shared_task(bind=True, max_retries=3)
def process_style_transfer(self, task_id: str, image_path: str, style_type: str):
    """风格化任务"""
    try:
        # 调用腾讯云 API
        result = client.transfer_style(image_path, style_type)
        return {"status": "success", "result": result}

    except TencentCloudAPIError as e:
        # 判断是否应该重试
        if TencentCloudErrorHandler.should_retry(e):
            # Celery 自动重试
            raise self.retry(exc=e, countdown=5)
        else:
            # 不可重试的错误,标记任务失败
            return {
                "status": "failed",
                "error": e.to_dict()
            }
```

#### 3.1.3 在 API 路由中使用

```python
from fastapi import APIRouter, HTTPException
from backend.src.shared.exceptions import TencentCloudAPIError
from example.tencent_cloud.error_handler import TencentCloudErrorHandler

router = APIRouter()

@router.post("/api/v1/styles/transfer")
async def transfer_style(file: UploadFile, style_type: str):
    """风格化接口"""
    try:
        # 调用风格化服务
        result = await style_service.transfer(file, style_type)
        return {"success": True, "data": result}

    except TencentCloudAPIError as e:
        # 判断错误类型
        if TencentCloudErrorHandler.is_client_error(e):
            # 客户端错误(4xx)
            http_status = 400
        else:
            # 服务端错误(5xx)
            http_status = 500

        # 格式化错误响应
        error_response = TencentCloudErrorHandler.format_error_response(e)
        raise HTTPException(status_code=http_status, detail=error_response)
```

### 3.2 直接使用映射配置

```python
from backend.src.shared.config.tencent_cloud_error_mapping import ErrorMapping

# 获取错误映射
tencent_code = "FailedOperation.ImageDecodeFailed"
mapping = ErrorMapping.get_mapping(tencent_code)

print(mapping["code"])        # INVALID_FILE_FORMAT
print(mapping["message"])     # 图片解码失败,无法识别文件格式
print(mapping["suggestion"])  # 请确保上传的是有效的 JPG、PNG 或 WEBP 图片文件

# 判断错误特性
is_retryable = ErrorMapping.is_retryable(tencent_code)  # False
is_client_error = ErrorMapping.is_client_error(tencent_code)  # True
```

---

## 4. 错误响应格式

### 4.1 API 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "图片解码失败,无法识别文件格式",
    "suggestion": "请确保上传的是有效的 JPG、PNG 或 WEBP 图片文件",
    "tencent_error_code": "FailedOperation.ImageDecodeFailed",
    "request_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

### 4.2 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| `success` | Boolean | 请求是否成功 |
| `error.code` | String | 系统错误码 |
| `error.message` | String | 用户友好的错误提示 |
| `error.suggestion` | String | 解决建议 |
| `error.tencent_error_code` | String | 腾讯云原始错误码(用于排查) |
| `error.request_id` | String | 请求 ID(用于问题追踪) |
| `timestamp` | String | 时间戳 |

---

## 5. 重试策略

### 5.1 可重试的错误

以下错误可以通过重试解决:

1. **请求超时**: `FailedOperation.RequestTimeout`
2. **服务端错误**: `FailedOperation.ServerError`
3. **内部错误**: `FailedOperation.InnerError`
4. **请求频率限制**: `LimitExceeded.FreqLimit`

### 5.2 推荐的重试配置

```python
RETRY_CONFIG = {
    "max_retries": 3,           # 最大重试次数
    "initial_interval": 2,      # 初始重试间隔(秒)
    "max_interval": 10,         # 最大重试间隔(秒)
    "backoff_factor": 2,        # 指数退避因子
}

# 重试间隔计算: interval = min(initial_interval * (backoff_factor ^ retry_count), max_interval)
# 第 1 次重试: 2 秒
# 第 2 次重试: 4 秒
# 第 3 次重试: 8 秒
```

### 5.3 重试示例代码

```python
import time
from backend.src.shared.exceptions import TencentCloudAPIError
from example.tencent_cloud.error_handler import TencentCloudErrorHandler

def transfer_with_retry(client, image_path, style_type, max_retries=3):
    """带重试的风格化调用"""
    for attempt in range(max_retries):
        try:
            return client.transfer_style(image_path, style_type)

        except TencentCloudAPIError as e:
            if TencentCloudErrorHandler.should_retry(e) and attempt < max_retries - 1:
                # 计算退避时间
                wait_time = min(2 ** attempt * 2, 10)
                print(f"请求失败,{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                # 不可重试或达到最大重试次数
                raise
```

---

## 6. 扩展错误码映射

### 6.1 添加新的错误码

在 `backend/src/shared/config/tencent_cloud_error_mapping.py` 中添加:

```python
TENCENT_ERROR_MAPPINGS = {
    # 现有映射...

    # 新增错误码
    "FailedOperation.NewErrorCode": {
        "code": "SYSTEM_ERROR_CODE",          # 系统错误码
        "message": "用户友好的错误提示",       # 错误信息
        "suggestion": "具体的解决建议",        # 解决建议
        "user_action": "用户应该采取的操作",   # 用户操作
        "http_status": 400,                   # HTTP 状态码
    },
}
```

### 6.2 添加可重试错误

在 `ErrorMapping.is_retryable()` 方法中添加:

```python
@classmethod
def is_retryable(cls, tencent_error_code: str) -> bool:
    retryable_errors = {
        "FailedOperation.RequestTimeout",
        "FailedOperation.ServerError",
        "FailedOperation.InnerError",
        "LimitExceeded.FreqLimit",
        "FailedOperation.NewRetryableError",  # 新增可重试错误
    }
    return tencent_error_code in retryable_errors
```

---

## 7. 测试

### 7.1 运行测试

```bash
cd example/tencent_cloud
python test_error_mapping.py
```

### 7.2 测试输出示例

```
================================================================================
🧪 测试腾讯云 API 错误码映射
================================================================================

────────────────────────────────────────────────────────────────────────────────
📝 测试错误码: FailedOperation.ImageDecodeFailed
────────────────────────────────────────────────────────────────────────────────
✅ 系统错误码: INVALID_FILE_FORMAT
✅ 用户提示: 图片解码失败,无法识别文件格式
✅ 解决建议: 请确保上传的是有效的 JPG、PNG 或 WEBP 图片文件
✅ HTTP 状态码: 400
✅ 是否可重试: False
```

### 7.3 单元测试

```python
# tests/shared/test_error_mapping.py
import pytest
from backend.src.shared.config.tencent_cloud_error_mapping import ErrorMapping

def test_get_mapping():
    """测试获取错误映射"""
    mapping = ErrorMapping.get_mapping("FailedOperation.ImageDecodeFailed")
    assert mapping["code"] == "INVALID_FILE_FORMAT"
    assert mapping["http_status"] == 400

def test_unknown_error_code():
    """测试未知错误码"""
    mapping = ErrorMapping.get_mapping("UnknownErrorCode")
    assert mapping["code"] == "UNKNOWN_ERROR"
    assert mapping["http_status"] == 500

def test_is_retryable():
    """测试可重试判断"""
    assert ErrorMapping.is_retryable("FailedOperation.RequestTimeout") is True
    assert ErrorMapping.is_retryable("FailedOperation.ImageDecodeFailed") is False
```

---

## 8. 最佳实践

### 8.1 错误处理原则

1. **捕获具体异常**: 优先捕获 `TencentCloudAPIError` 及其子类
2. **保留原始信息**: 始终保留腾讯云返回的原始错误码和 request_id
3. **友好的用户提示**: 使用映射后的错误信息,而不是直接返回技术性错误
4. **适当重试**: 仅对可重试的错误进行重试,避免无效重试

### 8.2 日志记录

```python
import logging
from backend.src.shared.exceptions import TencentCloudAPIError

logger = logging.getLogger(__name__)

try:
    result = client.transfer_style(image_path, style_type)
except TencentCloudAPIError as e:
    # 记录详细的错误信息用于排查
    logger.error(
        f"腾讯云 API 调用失败: "
        f"tencent_code={e.tencent_error_code}, "
        f"system_code={e.error_code}, "
        f"request_id={e.request_id}, "
        f"message={e.user_message}"
    )
    raise
```

### 8.3 监控告警

建议对以下错误设置监控告警:

- **认证错误** (`AuthFailure.*`): 可能配置有误,需要立即处理
- **余额不足** (`ResourceUsSuspended.InsufficientBalance`): 需要充值
- **高频错误** (同一错误码在短时间内大量出现): 可能存在系统性问题

---

## 9. 参考资料

### 9.1 相关文档

- [腾讯云 API 错误码文档](https://cloud.tencent.com/document/api/1668/55923#6.-.E9.94.99.E8.AF.AF.E7.A0.81)
- [图片风格化 API 文档](https://cloud.tencent.com/document/product/1668/88066)
- [系统 API 设计文档](./API_STYLE.md)

### 9.2 更新日志

- **2025-10-25**: 初始版本,定义了 23 个错误码映射

---

**文档版本**: v1.0  
**创建日期**: 2025-10-25  
**最后更新**: 2025-10-25  
**维护者**: AI Assistant
