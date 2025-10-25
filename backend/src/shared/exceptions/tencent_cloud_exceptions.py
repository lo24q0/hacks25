"""
腾讯云 API 异常定义

定义与腾讯云 API 交互时可能出现的异常类型
"""

from .infrastructure_exceptions import ExternalServiceError


class TencentCloudAPIError(ExternalServiceError):
    """
    腾讯云 API 调用错误

    Args:
        tencent_error_code: 腾讯云返回的错误码
        tencent_error_message: 腾讯云返回的错误信息
        mapped_error_code: 映射后的系统错误码
        user_message: 面向用户的错误提示
        suggestion: 解决建议
        request_id: 腾讯云请求 ID,用于问题排查
    """

    def __init__(
        self,
        tencent_error_code: str,
        tencent_error_message: str,
        mapped_error_code: str,
        user_message: str,
        suggestion: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            service_name="TencentCloud",
            message=user_message,
        )
        self.tencent_error_code = tencent_error_code
        self.tencent_error_message = tencent_error_message
        self.error_code = mapped_error_code  # 覆盖父类的 error_code
        self.user_message = user_message
        self.suggestion = suggestion
        self.request_id = request_id

    def to_dict(self) -> dict:
        """
        转换为字典格式,用于 API 响应

        Returns:
            包含错误详情的字典
        """
        return {
            "code": self.error_code,
            "message": self.user_message,
            "suggestion": self.suggestion,
            "tencent_error_code": self.tencent_error_code,
            "request_id": self.request_id,
        }


class ImageProcessingError(TencentCloudAPIError):
    """图片处理相关错误"""

    pass


class QuotaExceededError(TencentCloudAPIError):
    """配额超限错误"""

    pass


class AuthenticationError(TencentCloudAPIError):
    """认证错误"""

    pass
