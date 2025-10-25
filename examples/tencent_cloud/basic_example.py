"""
腾讯云图像风格化 API 基础示例

演示如何使用腾讯云 SDK 调用图像风格化接口
"""

import os
import base64
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.aiart.v20221229 import aiart_client, models


def image_to_base64(image_path: str) -> str:
    """
    将图片文件转换为 Base64 编码
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        Base64 编码的图片字符串
    """
    with open(image_path, "rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode("utf-8")


def base64_to_image(base64_str: str, output_path: str) -> None:
    """
    将 Base64 编码转换为图片文件
    
    Args:
        base64_str: Base64 编码的图片字符串
        output_path: 输出图片路径
    """
    image_data = base64.b64decode(base64_str)
    with open(output_path, "wb") as f:
        f.write(image_data)


def style_transfer(
    input_image_path: str,
    output_image_path: str,
    style_type: str = "101",  # 默认动漫风格
    strength_level: int = 50,
    secret_id: str = None,
    secret_key: str = None,
    region: str = "ap-guangzhou",
) -> dict:
    """
    执行图像风格化转换
    
    Args:
        input_image_path: 输入图片路径
        output_image_path: 输出图片路径
        style_type: 风格类型代码 (101:动漫, 102:卡通, 103:3D卡通, 201:油画, 202:水彩, 203:素描)
        strength_level: 风格化强度 0-100, 默认50
        secret_id: 腾讯云 SecretId (如果不传,从环境变量读取)
        secret_key: 腾讯云 SecretKey (如果不传,从环境变量读取)
        region: 地域,默认 ap-guangzhou (广州)
        
    Returns:
        包含处理结果的字典
        
    Raises:
        TencentCloudSDKException: SDK 异常
        FileNotFoundError: 输入文件不存在
    """
    try:
        # 获取访问凭证
        if secret_id is None:
            secret_id = os.getenv("TENCENT_SECRET_ID")
        if secret_key is None:
            secret_key = os.getenv("TENCENT_SECRET_KEY")
            
        if not secret_id or not secret_key:
            raise ValueError("请提供 SecretId 和 SecretKey,或设置环境变量 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY")
        
        # 创建认证对象
        cred = credential.Credential(secret_id, secret_key)
        
        # 配置 HTTP 选项
        http_profile = HttpProfile()
        http_profile.endpoint = "aiart.tencentcloudapi.com"
        http_profile.reqTimeout = 60  # 设置超时时间 60秒
        
        # 创建客户端配置
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        
        # 创建客户端
        client = aiart_client.AiartClient(cred, region, client_profile)
        
        # 读取并编码图片
        input_image_base64 = image_to_base64(input_image_path)
        
        # 构造请求
        req = models.ImageToImageRequest()
        params = {
            "InputImage": input_image_base64,
            "Styles": [style_type],
            "StrengthLevel": strength_level,
            "LogoAdd": 0,  # 不添加水印
        }
        req.from_json_string(str(params).replace("'", '"'))
        
        # 发起请求
        resp = client.ImageToImage(req)
        
        # 保存结果图片
        if resp.ResultImage:
            base64_to_image(resp.ResultImage, output_image_path)
            
        # 返回结果
        return {
            "success": True,
            "request_id": resp.RequestId,
            "output_path": output_image_path,
            "style_type": style_type,
            "strength_level": strength_level,
        }
        
    except TencentCloudSDKException as e:
        return {
            "success": False,
            "error_code": e.code,
            "error_message": e.message,
            "request_id": e.requestId,
        }
    except Exception as e:
        return {
            "success": False,
            "error_message": str(e),
        }


def main():
    """
    主函数:演示基本用法
    """
    # 示例:将图片转换为动漫风格
    result = style_transfer(
        input_image_path="input.jpg",
        output_image_path="output_anime.jpg",
        style_type="101",  # 动漫风格
        strength_level=70,  # 风格强度 70%
    )
    
    if result["success"]:
        print(f"✅ 风格化成功!")
        print(f"   Request ID: {result['request_id']}")
        print(f"   输出文件: {result['output_path']}")
    else:
        print(f"❌ 风格化失败!")
        print(f"   错误信息: {result.get('error_message', 'Unknown error')}")
        if "error_code" in result:
            print(f"   错误码: {result['error_code']}")


if __name__ == "__main__":
    main()
