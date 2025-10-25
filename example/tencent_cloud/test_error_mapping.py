"""
测试腾讯云 API 错误码映射

演示如何使用错误处理器和错误映射
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.shared.config.tencent_cloud_error_mapping import ErrorMapping
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from error_handler import TencentCloudErrorHandler


def test_error_mapping():
    """测试错误码映射功能"""
    print("=" * 80)
    print("🧪 测试腾讯云 API 错误码映射")
    print("=" * 80)

    # 测试用例:常见的腾讯云错误码
    test_cases = [
        "FailedOperation.ImageDecodeFailed",
        "FailedOperation.ImageResolutionExceed",
        "FailedOperation.RequestTimeout",
        "LimitExceeded.TooLargeFileError",
        "ResourceUsSuspended.InsufficientBalance",
        "AuthFailure.SignatureFailure",
        "UnknownErrorCode",  # 未知错误码
    ]

    for tencent_code in test_cases:
        print(f"\n{'─' * 80}")
        print(f"📝 测试错误码: {tencent_code}")
        print("─" * 80)

        # 获取映射
        mapping = ErrorMapping.get_mapping(tencent_code)

        print(f"✅ 系统错误码: {mapping['code']}")
        print(f"✅ 用户提示: {mapping['message']}")
        print(f"✅ 解决建议: {mapping.get('suggestion', 'N/A')}")
        print(f"✅ HTTP 状态码: {mapping.get('http_status', 500)}")
        print(f"✅ 是否可重试: {ErrorMapping.is_retryable(tencent_code)}")


def test_error_handler():
    """测试错误处理器"""
    print("\n\n" + "=" * 80)
    print("🧪 测试错误处理器")
    print("=" * 80)

    # 模拟腾讯云 SDK 异常
    test_errors = [
        {
            "code": "FailedOperation.ImageDecodeFailed",
            "message": "图片解码失败",
        },
        {
            "code": "FailedOperation.RequestTimeout",
            "message": "请求超时",
        },
        {
            "code": "ResourceUsSuspended.InsufficientBalance",
            "message": "账户余额不足",
        },
    ]

    for error_info in test_errors:
        print(f"\n{'─' * 80}")
        print(f"📝 模拟错误: {error_info['code']}")
        print("─" * 80)

        # 创建模拟异常
        sdk_exception = TencentCloudSDKException(
            code=error_info["code"],
            message=error_info["message"],
            requestId="test-request-id-12345",
        )

        # 使用错误处理器转换异常
        system_exception = TencentCloudErrorHandler.handle_exception(sdk_exception)

        print(f"✅ 异常类型: {type(system_exception).__name__}")
        print(f"✅ 系统错误码: {system_exception.error_code}")
        print(f"✅ 用户提示: {system_exception.user_message}")
        print(f"✅ 解决建议: {system_exception.suggestion}")
        print(f"✅ 请求 ID: {system_exception.request_id}")
        print(f"✅ 是否可重试: {TencentCloudErrorHandler.should_retry(system_exception)}")

        # 格式化为 API 响应
        api_response = TencentCloudErrorHandler.format_error_response(system_exception)
        print(f"✅ API 响应格式:")
        import json

        print(json.dumps(api_response, indent=2, ensure_ascii=False))


def test_error_categories():
    """测试错误分类"""
    print("\n\n" + "=" * 80)
    print("🧪 测试错误分类")
    print("=" * 80)

    test_codes = [
        "FailedOperation.ImageDecodeFailed",  # 4xx 客户端错误
        "FailedOperation.ServerError",  # 5xx 服务端错误
        "AuthFailure.SignatureFailure",  # 4xx 认证错误
        "ResourceUsSuspended.InsufficientBalance",  # 4xx 配额错误
    ]

    print(f"\n{'错误码':<50} {'客户端错误':<12} {'服务端错误':<12} {'可重试':<8}")
    print("─" * 82)

    for code in test_codes:
        is_client = ErrorMapping.is_client_error(code)
        is_server = ErrorMapping.is_server_error(code)
        is_retry = ErrorMapping.is_retryable(code)

        print(
            f"{code:<50} "
            f"{'✅' if is_client else '❌':<12} "
            f"{'✅' if is_server else '❌':<12} "
            f"{'✅' if is_retry else '❌':<8}"
        )


def display_all_mappings():
    """显示所有错误码映射"""
    print("\n\n" + "=" * 80)
    print("📋 所有错误码映射一览")
    print("=" * 80)

    mappings = ErrorMapping.get_all_mappings()

    print(f"\n总共定义了 {len(mappings)} 个错误码映射\n")

    # 按类别分组
    categories = {
        "图片相关错误": [],
        "请求相关错误": [],
        "认证和权限错误": [],
        "配额和限流错误": [],
        "参数相关错误": [],
        "风格化相关错误": [],
    }

    for code, mapping in mappings.items():
        if "Image" in code:
            categories["图片相关错误"].append((code, mapping))
        elif "Auth" in code:
            categories["认证和权限错误"].append((code, mapping))
        elif "ResourceUs" in code or "LimitExceeded" in code:
            categories["配额和限流错误"].append((code, mapping))
        elif "Parameter" in code:
            categories["参数相关错误"].append((code, mapping))
        elif "Style" in code:
            categories["风格化相关错误"].append((code, mapping))
        elif "Request" in code or "Server" in code or "Inner" in code:
            categories["请求相关错误"].append((code, mapping))

    for category, items in categories.items():
        if items:
            print(f"\n### {category} ({len(items)} 个)\n")
            for code, mapping in items:
                print(f"**{code}**")
                print(f"  - 系统码: {mapping['code']}")
                print(f"  - 提示: {mapping['message']}")
                print(f"  - HTTP: {mapping.get('http_status', 500)}")
                print()


if __name__ == "__main__":
    # 运行所有测试
    test_error_mapping()
    test_error_handler()
    test_error_categories()
    display_all_mappings()

    print("\n" + "=" * 80)
    print("✅ 所有测试完成!")
    print("=" * 80)
