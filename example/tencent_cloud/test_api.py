"""
腾讯云图像风格化 API 配置验证脚本

用于验证 API 密钥配置是否正确，并测试基本功能。
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def check_environment():
    """检查环境变量配置"""
    print("=" * 60)
    print("🔍 步骤 1: 检查环境变量配置")
    print("=" * 60)

    # 加载环境变量
    env_path = Path(__file__).parent.parent.parent / ".env"
    if not env_path.exists():
        print(f"❌ 错误：找不到 .env 文件")
        print(f"   期望路径: {env_path}")
        print("\n请执行以下命令创建 .env 文件:")
        print("   cp .env.example .env")
        return False

    load_dotenv(env_path)
    print(f"✅ 找到 .env 文件: {env_path}")

    # 检查密钥配置
    secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
    region = os.getenv("TENCENT_CLOUD_REGION", "ap-guangzhou")

    if not secret_id or secret_id == "your_secret_id_here":
        print("❌ 错误：TENCENT_CLOUD_SECRET_ID 未配置")
        print("   请在 .env 文件中设置正确的 SecretId")
        return False

    if not secret_key or secret_key == "your_secret_key_here":
        print("❌ 错误：TENCENT_CLOUD_SECRET_KEY 未配置")
        print("   请在 .env 文件中设置正确的 SecretKey")
        return False

    print("✅ 环境变量配置正确")
    print(f"   SecretId: {secret_id[:10]}...{secret_id[-4:]}")
    print(f"   SecretKey: {secret_key[:10]}...{secret_key[-4:]}")
    print(f"   Region: {region}")

    return True


def check_dependencies():
    """检查依赖是否安装"""
    print("\n" + "=" * 60)
    print("📦 步骤 2: 检查依赖包")
    print("=" * 60)

    try:
        from tencentcloud.aiart.v20221229 import aiart_client

        print("✅ tencentcloud-sdk-python-aiart 已安装")
        return True
    except ImportError as e:
        print("❌ 错误：缺少依赖包")
        print(f"   {e}")
        print("\n请执行以下命令安装依赖:")
        print("   pip install tencentcloud-sdk-python-aiart")
        return False


def check_test_image():
    """检查测试图片"""
    print("\n" + "=" * 60)
    print("🖼️  步骤 3: 检查测试图片")
    print("=" * 60)

    # 尝试多个可能的文件名
    possible_names = ["test_image.jpg", "test_input.jpg", "test.jpg"]
    test_image = None

    for name in possible_names:
        path = Path(__file__).parent / name
        if path.exists():
            test_image = path
            break

    if test_image is None:
        test_image = Path(__file__).parent / "test_input.jpg"  # 默认使用这个名字

    if not test_image.exists():
        print(f"⚠️  警告：找不到测试图片")
        print(f"   期望路径: {test_image}")
        print("\n建议：")
        print("   1. 准备一张测试图片（人物照片效果最佳）")
        print("   2. 命名为 test_input.jpg")
        print(f"   3. 放到 {test_image.parent} 目录")
        print("\n跳过实际 API 测试...\n")
        return False

    # 检查文件大小
    size_mb = test_image.stat().st_size / (1024 * 1024)
    print(f"✅ 找到测试图片: {test_image.name}")
    print(f"   文件大小: {size_mb:.2f} MB")

    if size_mb > 10:
        print("   ⚠️  警告: 文件大小超过 10MB，建议压缩")

    return True


def test_api():
    """测试 API 调用"""
    print("=" * 60)
    print("🎨 步骤 4: 测试 API 调用")
    print("=" * 60)

    try:
        from image_style_transfer_example import TencentCloudStyleTransfer

        # 查找测试图片
        possible_names = ["test_image.jpg", "test_input.jpg", "test.jpg"]
        input_image = None

        for name in possible_names:
            path = Path(__file__).parent / name
            if path.exists():
                input_image = name
                break

        if input_image is None:
            input_image = "test_input.jpg"  # 默认

        # 加载环境变量
        secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
        secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
        region = os.getenv("TENCENT_CLOUD_REGION", "ap-guangzhou")

        # 初始化客户端
        print("\n🔧 初始化腾讯云客户端...")
        client = TencentCloudStyleTransfer(
            secret_id=secret_id, secret_key=secret_key, region=region
        )
        print("✅ 客户端初始化成功")

        # 测试风格转换
        print("\n🎨 开始测试图片风格化...")
        print(f"   输入图片: {input_image}")
        print("   风格类型: anime (动漫风格)")
        print("   输出图片: test_output_anime.jpg")
        print("\n   ⏳ 处理中，预计需要 10-30 秒...")

        result = client.transfer_style(
            image_path=input_image,
            style_type="anime",
            output_path="test_output_anime.jpg",
        )

        print("\n" + "=" * 60)
        print("🎉 测试成功！")
        print("=" * 60)
        print(f"✅ 请求ID: {result['request_id']}")
        print(f"✅ 输出文件: {result.get('output_path')}")

        if result.get("image_url"):
            print(f"✅ 临时URL: {result['image_url'][:50]}...")

        print("\n" + "=" * 60)
        print("✅ 配置验证完成！")
        print("=" * 60)
        print("你现在可以:")
        print("1. 查看生成的图片: test_output_anime.jpg")
        print("2. 查看使用文档: README.md")
        print("3. 开始集成到项目中")
        print("=" * 60)

        return True

    except FileNotFoundError as e:
        print(f"\n❌ 错误：找不到文件")
        print(f"   {e}")
        print("\n请确保:")
        print("   1. test_input.jpg 存在于当前目录")
        print("   2. 文件路径正确")
        return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n" + "=" * 60)
        print("🔧 故障排查建议")
        print("=" * 60)
        print("1. 检查 SecretId 和 SecretKey 是否正确")
        print("   - 登录腾讯云控制台验证")
        print("   - 确保密钥状态为 '启用'")
        print("\n2. 检查是否已开通智能创作引擎服务")
        print("   - 访问: https://console.cloud.tencent.com/aiart")
        print("   - 确认服务已开通")
        print("\n3. 检查账户余额")
        print("   - 查看免费额度是否用完")
        print("   - 确认账户无欠费")
        print("\n4. 检查网络连接")
        print("   - 确保可以访问腾讯云 API")
        print("   - 尝试更换网络环境")
        print("\n5. 查看详细错误信息")
        print(f"   - 错误类型: {type(e).__name__}")
        print(f"   - 错误详情: {str(e)}")
        print("=" * 60)
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 腾讯云图像风格化 API 配置验证工具")
    print("=" * 60)
    print()

    # 步骤 1: 检查环境变量
    if not check_environment():
        print("\n❌ 配置验证失败，请先完成环境变量配置")
        print("详细步骤请参考: SETUP.md")
        sys.exit(1)

    # 步骤 2: 检查依赖
    if not check_dependencies():
        print("\n❌ 配置验证失败，请先安装依赖")
        sys.exit(1)

    # 步骤 3: 检查测试图片
    has_test_image = check_test_image()

    if not has_test_image:
        print("\n" + "=" * 60)
        print("⚠️  跳过 API 测试")
        print("=" * 60)
        print("环境配置正确，但缺少测试图片。")
        print("你可以:")
        print("1. 准备测试图片后重新运行此脚本")
        print("2. 或直接开始集成到项目中")
        print("=" * 60)
        return

    # 步骤 4: 测试 API
    if not test_api():
        sys.exit(1)


if __name__ == "__main__":
    main()
