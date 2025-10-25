"""
测试使用 Styles 参数（而不是 StyleId）
"""

import os
import base64
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.aiart.v20221229 import aiart_client, models

secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
region = os.getenv("TENCENT_CLOUD_REGION", "ap-guangzhou")

print("🧪 测试使用 Styles 参数")
print("=" * 60)

# 读取图片
test_image = Path(__file__).parent / "test_image.jpg"
with open(test_image, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# 初始化客户端
cred = credential.Credential(secret_id, secret_key)
http_profile = HttpProfile()
http_profile.endpoint = "aiart.tencentcloudapi.com"
client_profile = ClientProfile()
client_profile.httpProfile = http_profile
client = aiart_client.AiartClient(cred, region, client_profile)

try:
    req = models.ImageToImageRequest()
    req.InputImage = image_base64

    # 尝试使用 Styles 参数（数组）
    print("📝 设置参数:")
    print("   - InputImage: Base64 图片数据")
    print("   - Styles: ['201'] (动漫风格)")

    req.Styles = ["201"]  # 使用字符串数组

    print("\n⏳ 发送请求...")
    resp = client.ImageToImage(req)

    print("\n" + "=" * 60)
    print("🎉 成功！")
    print("=" * 60)
    print(f"RequestId: {resp.RequestId}")

    if resp.ResultImage:
        result_data = base64.b64decode(resp.ResultImage)
        output_path = Path(__file__).parent / "test_output_success.jpg"
        with open(output_path, "wb") as f:
            f.write(result_data)
        print(f"✅ 图片已保存: {output_path.name}")

except TencentCloudSDKException as e:
    print(f"\n❌ 失败: {e.code} - {e.message}")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
