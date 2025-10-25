"""
腾讯云图像风格化 API 异步处理示例

演示如何使用 Celery 异步任务处理图像风格化
"""

import os
import base64
from typing import Optional
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.aiart.v20221229 import aiart_client, models


class TencentCloudStyleClient:
    """
    腾讯云图像风格化客户端封装
    
    提供同步和异步的图像风格化功能
    """
    
    # 风格类型映射
    STYLE_TYPES = {
        "anime": "101",      # 动漫
        "cartoon": "102",    # 卡通
        "cartoon_3d": "103", # 3D卡通
        "oil_painting": "201",  # 油画
        "watercolor": "202",    # 水彩
        "sketch": "203",        # 素描
        "pencil": "301",        # 铅笔画
        "color_pencil": "302",  # 彩色铅笔画
    }
    
    def __init__(
        self,
        secret_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: str = "ap-guangzhou",
        timeout: int = 60,
    ):
        """
        初始化客户端
        
        Args:
            secret_id: 腾讯云 SecretId
            secret_key: 腾讯云 SecretKey
            region: 地域
            timeout: 请求超时时间(秒)
        """
        self.secret_id = secret_id or os.getenv("TENCENT_SECRET_ID")
        self.secret_key = secret_key or os.getenv("TENCENT_SECRET_KEY")
        self.region = region
        self.timeout = timeout
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("请提供 SecretId 和 SecretKey")
        
        self._init_client()
    
    def _init_client(self) -> None:
        """初始化腾讯云客户端"""
        cred = credential.Credential(self.secret_id, self.secret_key)
        
        http_profile = HttpProfile()
        http_profile.endpoint = "aiart.tencentcloudapi.com"
        http_profile.reqTimeout = self.timeout
        
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        
        self.client = aiart_client.AiartClient(cred, self.region, client_profile)
    
    def image_to_base64(self, image_path: str) -> str:
        """将图片转换为 Base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def base64_to_image(self, base64_str: str, output_path: str) -> None:
        """将 Base64 保存为图片"""
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(base64_str))
    
    def transfer_style(
        self,
        input_image: str,
        output_path: str,
        style: str = "anime",
        strength: int = 50,
        add_logo: bool = False,
    ) -> dict:
        """
        执行风格迁移
        
        Args:
            input_image: 输入图片路径或Base64字符串
            output_path: 输出图片路径
            style: 风格名称(anime, cartoon, oil_painting等)
            strength: 风格强度 0-100
            add_logo: 是否添加水印
            
        Returns:
            处理结果字典
        """
        try:
            # 获取风格代码
            style_code = self.STYLE_TYPES.get(style, "101")
            
            # 判断输入是路径还是Base64
            if os.path.isfile(input_image):
                input_base64 = self.image_to_base64(input_image)
            else:
                input_base64 = input_image
            
            # 构造请求
            req = models.ImageToImageRequest()
            params = {
                "InputImage": input_base64,
                "Styles": [style_code],
                "StrengthLevel": strength,
                "LogoAdd": 1 if add_logo else 0,
            }
            req.from_json_string(str(params).replace("'", '"'))
            
            # 发起请求
            resp = self.client.ImageToImage(req)
            
            # 保存结果
            if resp.ResultImage:
                self.base64_to_image(resp.ResultImage, output_path)
            
            return {
                "success": True,
                "request_id": resp.RequestId,
                "output_path": output_path,
                "style": style,
                "style_code": style_code,
            }
            
        except TencentCloudSDKException as e:
            return {
                "success": False,
                "error_code": e.code,
                "error_message": e.message,
                "request_id": getattr(e, "requestId", None),
            }
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e),
            }
    
    def batch_transfer(
        self,
        input_images: list[str],
        output_dir: str,
        style: str = "anime",
        strength: int = 50,
    ) -> list[dict]:
        """
        批量处理图片
        
        Args:
            input_images: 输入图片路径列表
            output_dir: 输出目录
            style: 风格名称
            strength: 风格强度
            
        Returns:
            处理结果列表
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for i, input_path in enumerate(input_images):
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}_{style}{ext}")
            
            result = self.transfer_style(
                input_image=input_path,
                output_path=output_path,
                style=style,
                strength=strength,
            )
            result["index"] = i
            result["input_path"] = input_path
            results.append(result)
        
        return results


# ==================== Celery 异步任务示例 ====================

# 注意:需要在实际项目中配置 Celery
# from celery import Celery
# 
# app = Celery('style_tasks', broker='redis://localhost:6379/0')
# 
# @app.task(bind=True, max_retries=3)
# def async_style_transfer(
#     self,
#     input_image_path: str,
#     output_image_path: str,
#     style: str = "anime",
#     strength: int = 50,
# ) -> dict:
#     """
#     Celery 异步风格化任务
#     
#     Args:
#         input_image_path: 输入图片路径
#         output_image_path: 输出图片路径
#         style: 风格名称
#         strength: 风格强度
#         
#     Returns:
#         处理结果字典
#     """
#     try:
#         client = TencentCloudStyleClient()
#         result = client.transfer_style(
#             input_image=input_image_path,
#             output_path=output_image_path,
#             style=style,
#             strength=strength,
#         )
#         return result
#         
#     except Exception as exc:
#         # 重试机制
#         raise self.retry(exc=exc, countdown=5)


def main():
    """演示客户端使用"""
    
    # 初始化客户端
    client = TencentCloudStyleClient(
        region="ap-guangzhou",
        timeout=60,
    )
    
    # 单张图片处理
    print("处理单张图片...")
    result = client.transfer_style(
        input_image="input.jpg",
        output_path="output_anime.jpg",
        style="anime",
        strength=70,
    )
    print(f"结果: {result}")
    
    # 批量处理
    print("\n批量处理图片...")
    results = client.batch_transfer(
        input_images=["img1.jpg", "img2.jpg", "img3.jpg"],
        output_dir="./outputs",
        style="cartoon",
        strength=60,
    )
    
    success_count = sum(1 for r in results if r["success"])
    print(f"成功: {success_count}/{len(results)}")
    
    # 打印可用风格
    print("\n可用风格:")
    for name, code in TencentCloudStyleClient.STYLE_TYPES.items():
        print(f"  {name}: {code}")


if __name__ == "__main__":
    main()
