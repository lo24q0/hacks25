"""
腾讯云 API 错误处理器

提供统一的错误处理和映射功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径,以便导入 backend 模块
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.shared.config.tencent_cloud_error_mapping import ErrorMapping
from backend.src.shared.exceptions.tencent_cloud_exceptions import (
    TencentCloudAPIError,
    ImageProcessingError,
    QuotaExceededError,
    AuthenticationError,
)
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)


class TencentCloudErrorHandler:
    """
    腾讯云 API 错误处理器

    负责捕获腾讯云 SDK 异常并映射为系统定义的异常类型
    """

    @staticmethod
    def handle_exception(
        exception: TencentCloudSDKException, request_id: str | None = None
    ) -> TencentCloudAPIError:
        """
        处理腾讯云 SDK 异常,转换为系统异常

        Args:
            exception: 腾讯云 SDK 异常
            request_id: 请求 ID

        Returns:
            转换后的系统异常
        """
        tencent_error_code = exception.get_code()
        tencent_error_message = exception.get_message()

        # 获取错误映射配置
        mapping = ErrorMapping.get_mapping(tencent_error_code)

        # 构造系统异常
        error_kwargs = {
            "tencent_error_code": tencent_error_code,
            "tencent_error_message": tencent_error_message,
            "mapped_error_code": mapping["code"],
            "user_message": mapping["message"],
            "suggestion": mapping.get("suggestion"),
            "request_id": request_id or exception.get_request_id(),
        }

        # 根据错误类型创建特定的异常
        if tencent_error_code.startswith("FailedOperation.Image"):
            return ImageProcessingError(**error_kwargs)
        elif tencent_error_code.startswith("ResourceUsSuspended"):
            return QuotaExceededError(**error_kwargs)
        elif tencent_error_code.startswith("AuthFailure"):
            return AuthenticationError(**error_kwargs)
        else:
            return TencentCloudAPIError(**error_kwargs)

    @staticmethod
    def should_retry(exception: TencentCloudAPIError) -> bool:
        """
        判断是否应该重试请求

        Args:
            exception: 系统异常

        Returns:
            True 如果应该重试,否则 False
        """
        return ErrorMapping.is_retryable(exception.tencent_error_code)

    @staticmethod
    def is_client_error(exception: TencentCloudAPIError) -> bool:
        """
        判断是否为客户端错误(4xx)

        Args:
            exception: 系统异常

        Returns:
            True 如果是客户端错误,否则 False
        """
        return ErrorMapping.is_client_error(exception.tencent_error_code)

    @staticmethod
    def is_server_error(exception: TencentCloudAPIError) -> bool:
        """
        判断是否为服务端错误(5xx)

        Args:
            exception: 系统异常

        Returns:
            True 如果是服务端错误,否则 False
        """
        return ErrorMapping.is_server_error(exception.tencent_error_code)

    @staticmethod
    def format_error_response(exception: TencentCloudAPIError) -> dict:
        """
        格式化错误响应(用于 API 返回)

        Args:
            exception: 系统异常

        Returns:
            格式化的错误响应字典
        """
        return {
            "success": False,
            "error": exception.to_dict(),
            "timestamp": None,  # 实际使用时由 API 层添加时间戳
        }
