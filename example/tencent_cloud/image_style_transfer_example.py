"""
腾讯云图像风格化 API 调用示例

文档参考: https://cloud.tencent.com/document/product/1668/88066

功能说明:
    使用腾讯云智能创作引擎提供的图像风格化能力,将普通照片转换为不同艺术风格。

使用前准备:
    1. 在腾讯云控制台开通"智能创作引擎"服务
    2. 获取 SecretId 和 SecretKey (访问管理 -> 访问密钥)
    3. 安装 SDK: pip install tencentcloud-sdk-python-aiart
"""

import json
import base64
from typing import Optional
from pathlib import Path

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.aiart.v20221229 import aiart_client, models


class TencentCloudStyleTransfer:
    """
    腾讯云图像风格化客户端封装。

    支持多种风格转换，包括动漫、卡通、素描等。
    """

    # 风格类型映射 (根据腾讯云文档)
    STYLE_TYPES = {
        "anime": 201,      # 动漫风格
        "cartoon": 202,    # 3D卡通
        "sketch": 203,     # 素描风格
        "watercolor": 204, # 水彩画
        "oil_painting": 205, # 油画风格
    }

    def __init__(self, secret_id: str, secret_key: str, region: str = "ap-guangzhou"):
        """
        初始化客户端。

        Args:
            secret_id (str): 腾讯云 API SecretId
            secret_key (str): 腾讯云 API SecretKey
            region (str): 地域,默认广州。可选: ap-guangzhou, ap-beijing
        """
        self.cred = credential.Credential(secret_id, secret_key)

        # HTTP 配置
        http_profile = HttpProfile()
        http_profile.endpoint = "aiart.tencentcloudapi.com"

        # 客户端配置
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile

        # 初始化客户端
        self.client = aiart_client.AiartClient(self.cred, region, client_profile)

    def image_to_base64(self, image_path: str) -> str:
        """
        将图片文件转换为 Base64 编码。

        Args:
            image_path (str): 图片文件路径

        Returns:
            str: Base64 编码的图片数据

        Raises:
            FileNotFoundError: 如果文件不存在
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        with open(path, "rb") as f:
            image_data = f.read()

        return base64.b64encode(image_data).decode("utf-8")

    def transfer_style(
        self,
        image_path: str,
        style_type: str = "anime",
        output_path: Optional[str] = None,
    ) -> dict:
        """
        执行图像风格化转换。

        Args:
            image_path (str): 输入图片路径
            style_type (str): 风格类型,可选值: anime, cartoon, sketch, watercolor, oil_painting
            output_path (Optional[str]): 输出图片路径,如果提供则自动保存

        Returns:
            dict: 包含以下字段
                - result_image: Base64 编码的结果图片
                - image_url: 结果图片的临时 URL (有效期 1 小时)
                - request_id: 请求 ID,用于问题排查

        Raises:
            ValueError: 如果风格类型不支持
            TencentCloudSDKException: API 调用失败
        """
        # 验证风格类型
        if style_type not in self.STYLE_TYPES:
            raise ValueError(
                f"不支持的风格类型: {style_type}. "
                f"可选值: {', '.join(self.STYLE_TYPES.keys())}"
            )

        try:
            # 构造请求
            req = models.ImageToImageRequest()

            # 图片数据 (Base64)
            image_base64 = self.image_to_base64(image_path)
            req.InputImage = image_base64

            # 风格类型
            req.StyleId = self.STYLE_TYPES[style_type]

            # 其他可选参数
            # req.Strength = 80  # 风格强度 0-100,默认80
            # req.RspImgType = "url"  # 返回类型: url 或 base64

            # 发起请求
            resp = self.client.ImageToImage(req)

            # 解析响应
            result = {
                "result_image": resp.ResultImage,  # Base64 图片
                "image_url": getattr(resp, "ResultUrl", None),  # 临时 URL
                "request_id": resp.RequestId,
            }

            # 如果指定输出路径,保存图片
            if output_path and result["result_image"]:
                self._save_base64_image(result["result_image"], output_path)
                result["output_path"] = output_path

            return result

        except TencentCloudSDKException as e:
            print(f"API 调用失败: {e}")
            raise

    def _save_base64_image(self, base64_data: str, output_path: str) -> None:
        """
        保存 Base64 编码的图片到文件。

        Args:
            base64_data (str): Base64 编码的图片数据
            output_path (str): 输出文件路径
        """
        image_data = base64.b64decode(base64_data)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "wb") as f:
            f.write(image_data)

        print(f"图片已保存到: {output_path}")


# ============== 使用示例 ==============

def example_basic_usage():
    """基础使用示例"""
    # 初始化客户端
    client = TencentCloudStyleTransfer(
        secret_id="YOUR_SECRET_ID",
        secret_key="YOUR_SECRET_KEY",
        region="ap-guangzhou",
    )

    # 执行风格转换
    result = client.transfer_style(
        image_path="input.jpg",
        style_type="anime",  # 转为动漫风格
        output_path="output_anime.jpg",
    )

    print(f"请求 ID: {result['request_id']}")
    print(f"结果图片 URL: {result.get('image_url')}")


def example_multiple_styles():
    """批量转换多种风格"""
    client = TencentCloudStyleTransfer(
        secret_id="YOUR_SECRET_ID",
        secret_key="YOUR_SECRET_KEY",
    )

    input_image = "portrait.jpg"
    styles = ["anime", "cartoon", "sketch"]

    for style in styles:
        output_path = f"output_{style}.jpg"
        print(f"\n正在转换 {style} 风格...")

        try:
            result = client.transfer_style(
                image_path=input_image,
                style_type=style,
                output_path=output_path,
            )
            print(f"✓ 成功: {output_path}")
        except Exception as e:
            print(f"✗ 失败: {e}")


def example_async_pattern():
    """
    异步处理模式 (用于 FastAPI/Celery 集成)

    在实际项目中,这个逻辑会放在 Celery 任务中执行。
    """
    import os
    from typing import Dict, Any

    def style_transfer_task(
        task_id: str,
        image_path: str,
        style_type: str,
        output_dir: str,
    ) -> Dict[str, Any]:
        """
        风格化任务 (模拟 Celery 任务)。

        Args:
            task_id (str): 任务 ID
            image_path (str): 输入图片路径
            style_type (str): 风格类型
            output_dir (str): 输出目录

        Returns:
            Dict[str, Any]: 任务结果
        """
        try:
            # 从环境变量读取配置
            secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
            secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")

            client = TencentCloudStyleTransfer(secret_id, secret_key)

            # 执行转换
            output_path = f"{output_dir}/{task_id}_styled.jpg"
            result = client.transfer_style(
                image_path=image_path,
                style_type=style_type,
                output_path=output_path,
            )

            return {
                "status": "success",
                "task_id": task_id,
                "output_path": output_path,
                "image_url": result.get("image_url"),
                "request_id": result["request_id"],
            }

        except Exception as e:
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(e),
            }

    # 示例调用
    result = style_transfer_task(
        task_id="task_123456",
        image_path="/tmp/uploads/photo.jpg",
        style_type="anime",
        output_dir="/tmp/outputs",
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("腾讯云图像风格化 API 使用示例\n")
    print("请根据需要运行以下示例函数:")
    print("1. example_basic_usage() - 基础使用")
    print("2. example_multiple_styles() - 批量转换")
    print("3. example_async_pattern() - 异步处理模式")
