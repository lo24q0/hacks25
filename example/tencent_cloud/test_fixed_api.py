"""
测试修复后的 API 代码
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from image_style_transfer_example import TencentCloudStyleTransfer

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

print("=" * 60)
print("🧪 测试修复后的示例代码")
print("=" * 60)

# 获取配置
secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
region = os.getenv("TENCENT_CLOUD_REGION", "ap-guangzhou")

print(f"✅ SecretId: {secret_id[:10]}...{secret_id[-4:]}")
print(f"✅ Region: {region}")

# 初始化客户端
print("\n🔧 初始化客户端...")
client = TencentCloudStyleTransfer(
    secret_id=secret_id,
    secret_key=secret_key,
    region=region
)
print("✅ 客户端初始化成功")

# 测试动漫风格
print("\n🎨 测试动漫风格转换...")
print("   输入: test_image.jpg")
print("   输出: test_output_anime_fixed.jpg")
print("   ⏳ 处理中...")

result = client.transfer_style(
    image_path="test_image.jpg",
    style_type="anime",
    output_path="test_output_anime_fixed.jpg"
)

print("\n" + "=" * 60)
print("🎉 测试成功！")
print("=" * 60)
print(f"✅ RequestId: {result['request_id']}")
print(f"✅ 输出文件: {result['output_path']}")

# 测试其他风格
print("\n" + "=" * 60)
print("🎨 测试更多风格...")
print("=" * 60)

styles = [
    ("cartoon_3d", "3D卡通"),
    ("sketch", "素描"),
]

for style_id, style_name in styles:
    print(f"\n📝 {style_name}风格...")
    output_file = f"test_output_{style_id}.jpg"

    try:
        result = client.transfer_style(
            image_path="test_image.jpg",
            style_type=style_id,
            output_path=output_file
        )
        print(f"   ✅ 成功: {output_file}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")

print("\n" + "=" * 60)
print("✅ 所有测试完成！")
print("=" * 60)
print("生成的文件:")
import glob
for f in sorted(glob.glob("test_output_*.jpg")):
    size = Path(f).stat().st_size / 1024
    print(f"   - {f} ({size:.1f} KB)")
