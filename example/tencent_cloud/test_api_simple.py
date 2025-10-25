"""
简化的腾讯云 API 测试脚本
用于验证正确的 API 调用方式
"""

import os
import base64
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# 导入腾讯云 SDK
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.aiart.v20221229 import aiart_client, models

# 获取配置
secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
region = os.getenv("TENCENT_CLOUD_REGION", "ap-guangzhou")

print("=" * 60)
print("🧪 简化的腾讯云 API 测试")
print("=" * 60)
print(f"SecretId: {secret_id[:10]}...{secret_id[-4:]}")
print(f"Region: {region}")

# 读取测试图片
test_image = Path(__file__).parent / "test_image.jpg"
print(f"\n📷 读取测试图片: {test_image.name}")

with open(test_image, "rb") as f:
    image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")

print(f"✅ 图片大小: {len(image_data) / 1024:.2f} KB")
print(f"✅ Base64 长度: {len(image_base64)} 字符")

# 初始化客户端
print("\n🔧 初始化客户端...")
cred = credential.Credential(secret_id, secret_key)
http_profile = HttpProfile()
http_profile.endpoint = "aiart.tencentcloudapi.com"

client_profile = ClientProfile()
client_profile.httpProfile = http_profile

client = aiart_client.AiartClient(cred, region, client_profile)
print("✅ 客户端初始化成功")

# 构造请求
print("\n📤 发送 API 请求...")
print("   API: ImageToImage")
print("   风格: 201 (动漫风格)")

try:
    req = models.ImageToImageRequest()

    # 设置参数 - 尝试不同的参数名称
    req.InputImage = image_base64

    # 尝试打印请求对象的所有属性
    print("\n🔍 请求对象的属性:")
    for attr in dir(req):
        if not attr.startswith('_'):
            print(f"   - {attr}")

    # 尝试设置 StyleId
    try:
        req.StyleId = 201
        print("\n✅ 成功设置 StyleId = 201")
    except Exception as e:
        print(f"\n⚠️  设置 StyleId 失败: {e}")

    # 发起请求
    print("\n⏳ 调用 API...")
    resp = client.ImageToImage(req)

    print("\n" + "=" * 60)
    print("🎉 API 调用成功！")
    print("=" * 60)
    print(f"RequestId: {resp.RequestId}")

    if hasattr(resp, 'ResultImage') and resp.ResultImage:
        print(f"✅ 返回了 Base64 图片数据（长度: {len(resp.ResultImage)} 字符）")

        # 保存图片
        result_image_data = base64.b64decode(resp.ResultImage)
        output_path = Path(__file__).parent / "test_output_simple.jpg"

        with open(output_path, "wb") as f:
            f.write(result_image_data)

        print(f"✅ 图片已保存: {output_path.name}")

    if hasattr(resp, 'ResultUrl') and resp.ResultUrl:
        print(f"✅ 临时 URL: {resp.ResultUrl}")

except TencentCloudSDKException as e:
    print("\n" + "=" * 60)
    print("❌ API 调用失败")
    print("=" * 60)
    print(f"错误码: {e.code}")
    print(f"错误信息: {e.message}")
    print(f"RequestId: {e.requestId}")

    print("\n💡 可能的原因:")
    print("1. API 参数名称可能已变更")
    print("2. 需要检查最新的 API 文档")
    print("3. SDK 版本可能不匹配")

    print("\n🔗 参考文档:")
    print("   https://cloud.tencent.com/document/api/1668/55923")

except Exception as e:
    print(f"\n❌ 未知错误: {e}")
    import traceback
    traceback.print_exc()
