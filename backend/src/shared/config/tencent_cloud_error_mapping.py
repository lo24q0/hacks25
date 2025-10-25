"""
腾讯云 API 错误码映射配置

将腾讯云返回的错误码映射为系统统一的错误码和用户友好的错误信息

文档参考:
- 腾讯云 API 错误码: https://cloud.tencent.com/document/api/1668/55923#6.-.E9.94.99.E8.AF.AF.E7.A0.81
- 系统错误码定义: docs/API_STYLE.md
"""

from typing import Dict, Any


class ErrorMapping:
    """错误映射配置类"""

    # 错误码映射表
    TENCENT_ERROR_MAPPINGS: Dict[str, Dict[str, Any]] = {
        # ==================== 图片相关错误 ====================
        "FailedOperation.ImageDecodeFailed": {
            "code": "INVALID_FILE_FORMAT",
            "message": "图片解码失败,无法识别文件格式",
            "suggestion": "请确保上传的是有效的 JPG、PNG 或 WEBP 图片文件",
            "user_action": "重新上传有效的图片文件",
            "http_status": 400,
        },
        "FailedOperation.ImageResolutionExceed": {
            "code": "IMAGE_RESOLUTION_TOO_HIGH",
            "message": "图片分辨率过大",
            "suggestion": "请将图片压缩至 2048x2048 像素以下",
            "user_action": "压缩图片后重试",
            "http_status": 400,
        },
        "FailedOperation.ImageSizeExceed": {
            "code": "FILE_TOO_LARGE",
            "message": "图片文件大小超出限制",
            "suggestion": "请将文件压缩至 10MB 以下",
            "user_action": "压缩图片后重试",
            "http_status": 400,
        },
        "LimitExceeded.TooLargeFileError": {
            "code": "FILE_TOO_LARGE",
            "message": "图片文件过大",
            "suggestion": "请将文件大小控制在 10MB 以内",
            "user_action": "压缩图片后重试",
            "http_status": 400,
        },
        "FailedOperation.ImageDownloadError": {
            "code": "IMAGE_DOWNLOAD_FAILED",
            "message": "无法下载图片",
            "suggestion": "请检查图片 URL 是否有效或重新上传图片",
            "user_action": "重新上传图片",
            "http_status": 400,
        },
        # ==================== 请求相关错误 ====================
        "FailedOperation.RequestTimeout": {
            "code": "REQUEST_TIMEOUT",
            "message": "请求处理超时",
            "suggestion": "请稍后重试,或尝试降低图片分辨率",
            "user_action": "稍后重试",
            "http_status": 504,
        },
        "FailedOperation.ServerError": {
            "code": "TENCENT_API_ERROR",
            "message": "腾讯云服务暂时不可用",
            "suggestion": "请稍后重试",
            "user_action": "稍后重试",
            "http_status": 502,
        },
        "FailedOperation.InnerError": {
            "code": "TENCENT_API_ERROR",
            "message": "腾讯云内部处理错误",
            "suggestion": "请稍后重试,如持续出现请联系技术支持",
            "user_action": "稍后重试",
            "http_status": 502,
        },
        # ==================== 风格化相关错误 ====================
        "FailedOperation.StyleNotSupported": {
            "code": "INVALID_STYLE_TYPE",
            "message": "不支持的风格类型",
            "suggestion": "请使用 /api/v1/styles/presets 查询支持的风格列表",
            "user_action": "选择支持的风格",
            "http_status": 400,
        },
        "FailedOperation.ImageStyleTransferFail": {
            "code": "STYLE_TRANSFER_FAILED",
            "message": "风格化处理失败",
            "suggestion": "请尝试更换其他风格或重新上传图片",
            "user_action": "更换风格或重新上传",
            "http_status": 500,
        },
        # ==================== 认证和权限错误 ====================
        "AuthFailure.SignatureFailure": {
            "code": "AUTHENTICATION_FAILED",
            "message": "API 密钥认证失败",
            "suggestion": "请检查腾讯云 SecretId 和 SecretKey 配置",
            "user_action": "联系系统管理员",
            "http_status": 401,
        },
        "AuthFailure.SecretIdNotFound": {
            "code": "AUTHENTICATION_FAILED",
            "message": "API 密钥不存在",
            "suggestion": "请检查腾讯云 SecretId 配置",
            "user_action": "联系系统管理员",
            "http_status": 401,
        },
        "AuthFailure.InvalidSecretId": {
            "code": "AUTHENTICATION_FAILED",
            "message": "API 密钥无效",
            "suggestion": "请使用有效的腾讯云 API 密钥",
            "user_action": "联系系统管理员",
            "http_status": 401,
        },
        # ==================== 配额和限流错误 ====================
        "ResourceUsSuspended.InsufficientBalance": {
            "code": "INSUFFICIENT_BALANCE",
            "message": "腾讯云账户余额不足",
            "suggestion": "请充值腾讯云账户",
            "user_action": "联系系统管理员充值",
            "http_status": 402,
        },
        "LimitExceeded.FreqLimit": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "请求过于频繁",
            "suggestion": "请降低请求频率,稍后重试",
            "user_action": "稍后重试",
            "http_status": 429,
        },
        "ResourceUsSuspended.Arrears": {
            "code": "SERVICE_SUSPENDED",
            "message": "腾讯云服务已欠费暂停",
            "suggestion": "请充值腾讯云账户恢复服务",
            "user_action": "联系系统管理员",
            "http_status": 402,
        },
        # ==================== 参数相关错误 ====================
        "InvalidParameter": {
            "code": "INVALID_PARAMETER",
            "message": "请求参数错误",
            "suggestion": "请检查请求参数是否符合 API 文档要求",
            "user_action": "检查输入参数",
            "http_status": 400,
        },
        "MissingParameter": {
            "code": "MISSING_PARAMETER",
            "message": "缺少必要参数",
            "suggestion": "请提供所有必需的参数",
            "user_action": "补充必要参数",
            "http_status": 400,
        },
        "InvalidParameterValue": {
            "code": "INVALID_PARAMETER_VALUE",
            "message": "参数值不符合要求",
            "suggestion": "请检查参数值的格式和范围",
            "user_action": "修正参数值",
            "http_status": 400,
        },
    }

    # 默认错误映射(用于未知错误码)
    DEFAULT_ERROR_MAPPING = {
        "code": "UNKNOWN_ERROR",
        "message": "未知错误",
        "suggestion": "请稍后重试,如问题持续请联系技术支持",
        "user_action": "稍后重试或联系技术支持",
        "http_status": 500,
    }

    @classmethod
    def get_mapping(cls, tencent_error_code: str) -> Dict[str, Any]:
        """
        获取腾讯云错误码对应的映射配置

        Args:
            tencent_error_code: 腾讯云返回的错误码

        Returns:
            错误映射配置字典
        """
        return cls.TENCENT_ERROR_MAPPINGS.get(
            tencent_error_code, cls.DEFAULT_ERROR_MAPPING
        )

    @classmethod
    def is_client_error(cls, tencent_error_code: str) -> bool:
        """
        判断是否为客户端错误(4xx)

        Args:
            tencent_error_code: 腾讯云返回的错误码

        Returns:
            True 如果是客户端错误,否则 False
        """
        mapping = cls.get_mapping(tencent_error_code)
        http_status = mapping.get("http_status", 500)
        return 400 <= http_status < 500

    @classmethod
    def is_server_error(cls, tencent_error_code: str) -> bool:
        """
        判断是否为服务端错误(5xx)

        Args:
            tencent_error_code: 腾讯云返回的错误码

        Returns:
            True 如果是服务端错误,否则 False
        """
        mapping = cls.get_mapping(tencent_error_code)
        http_status = mapping.get("http_status", 500)
        return http_status >= 500

    @classmethod
    def is_retryable(cls, tencent_error_code: str) -> bool:
        """
        判断错误是否可重试

        Args:
            tencent_error_code: 腾讯云返回的错误码

        Returns:
            True 如果可以重试,否则 False
        """
        # 可重试的错误类型
        retryable_errors = {
            "FailedOperation.RequestTimeout",
            "FailedOperation.ServerError",
            "FailedOperation.InnerError",
            "LimitExceeded.FreqLimit",
        }
        return tencent_error_code in retryable_errors

    @classmethod
    def get_all_mappings(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有错误码映射

        Returns:
            完整的错误码映射字典
        """
        return cls.TENCENT_ERROR_MAPPINGS.copy()
