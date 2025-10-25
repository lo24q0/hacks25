"""
腾讯云风格化引擎实现模块。

封装腾讯云图像风格化 API,实现 IStyleEngine 接口。
复用 example/tencent_cloud/image_style_transfer_example.py 的验证代码。
"""

import base64
import json
from pathlib import Path
from typing import List

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.aiart.v20221229 import aiart_client, models

from domain.interfaces.i_style_engine import IStyleEngine, StylePreset
from shared.exceptions.tencent_cloud_exceptions import TencentCloudAPIError
from shared.config.tencent_cloud_error_mapping import TencentCloudErrorMapping


class TencentCloudStyleEngine(IStyleEngine):
    """
    腾讯云图像风格化引擎实现。

    使用腾讯云智能创作引擎的图像风格化能力。

    Args:
        secret_id: 腾讯云 API SecretId
        secret_key: 腾讯云 API SecretKey
        region: 地域,默认广州 (ap-guangzhou)

    示例:
        >>> engine = TencentCloudStyleEngine(
        ...     secret_id="YOUR_SECRET_ID",
        ...     secret_key="YOUR_SECRET_KEY"
        ... )
        >>> result_path = await engine.transfer_style(
        ...     image_path="/tmp/input.jpg",
        ...     style_preset_id="anime",
        ...     output_path="/tmp/output.jpg"
        ... )
    """

    STYLE_TYPES_MAPPING = {
        "anime": "201",
        "cartoon_3d": "202",
        "sketch": "203",
        "watercolor": "204",
        "oil_painting": "205",
    }

    def __init__(self, secret_id: str, secret_key: str, region: str = "ap-guangzhou"):
        """
        初始化腾讯云风格化引擎。

        Args:
            secret_id: 腾讯云 API SecretId
            secret_key: 腾讯云 API SecretKey
            region: 地域
        """
        self.cred = credential.Credential(secret_id, secret_key)

        http_profile = HttpProfile()
        http_profile.endpoint = "aiart.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile

        self.client = aiart_client.AiartClient(self.cred, region, client_profile)

        self._presets: List[StylePreset] = []
        self._load_presets()

    def _load_presets(self) -> None:
        """
        加载风格预设配置。

        从 example/tencent_cloud/style_presets_mapping.json 加载预设。
        """
        config_path = Path(__file__).parent.parent.parent.parent.parent / "example" / "tencent_cloud" / "style_presets_mapping.json"

        if not config_path.exists():
            raise FileNotFoundError(f"风格预设配置文件不存在: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        for preset_data in data["presets"]:
            preset = StylePreset(
                id=preset_data["id"],
                name=preset_data["name"],
                description=preset_data["description"],
                model_name="TencentCloud",
                preview_image=preset_data["preview_image"],
                name_en=preset_data.get("name_en"),
                tags=preset_data.get("tags", []),
                recommended_strength=preset_data.get("recommended_strength", 80),
                tencent_style_id=preset_data["tencent_style_id"],
                estimated_time=self._estimate_time(preset_data["id"]),
            )
            self._presets.append(preset)

    def _estimate_time(self, style_id: str) -> int:
        """
        预估处理时间。

        Args:
            style_id: 风格ID

        Returns:
            int: 预计处理时间(秒)
        """
        time_mapping = {
            "anime": 15,
            "cartoon_3d": 25,
            "sketch": 10,
            "watercolor": 15,
            "oil_painting": 25,
        }
        return time_mapping.get(style_id, 20)

    def _image_to_base64(self, image_path: str) -> str:
        """
        将图片文件转换为 Base64 编码。

        Args:
            image_path: 图片文件路径

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

    def _save_base64_image(self, base64_data: str, output_path: str) -> None:
        """
        保存 Base64 编码的图片到文件。

        Args:
            base64_data: Base64 编码的图片数据
            output_path: 输出文件路径
        """
        image_data = base64.b64decode(base64_data)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "wb") as f:
            f.write(image_data)

    async def transfer_style(
        self,
        image_path: str,
        style_preset_id: str,
        output_path: str,
    ) -> str:
        """
        执行图像风格化转换。

        Args:
            image_path: 源图片路径
            style_preset_id: 风格预设ID
            output_path: 输出文件路径

        Returns:
            str: 风格化后的图片路径

        Raises:
            FileNotFoundError: 如果源图片不存在
            ValueError: 如果风格预设不存在
            TencentCloudAPIError: 如果 API 调用失败
        """
        if style_preset_id not in self.STYLE_TYPES_MAPPING:
            raise ValueError(
                f"不支持的风格类型: {style_preset_id}. "
                f"可选值: {', '.join(self.STYLE_TYPES_MAPPING.keys())}"
            )

        try:
            req = models.ImageToImageRequest()

            image_base64 = self._image_to_base64(image_path)
            req.InputImage = image_base64

            req.Styles = [self.STYLE_TYPES_MAPPING[style_preset_id]]

            resp = self.client.ImageToImage(req)

            result_image = resp.ResultImage
            if result_image:
                self._save_base64_image(result_image, output_path)
                return output_path
            else:
                raise TencentCloudAPIError(
                    error_code="NO_RESULT_IMAGE",
                    message="API 返回结果中没有图片数据",
                    tencent_error_code="NO_RESULT_IMAGE",
                )

        except TencentCloudSDKException as e:
            error_mapping = TencentCloudErrorMapping.get_error_mapping(e.code)

            raise TencentCloudAPIError(
                error_code=error_mapping["system_error_code"],
                message=error_mapping["error_message"],
                tencent_error_code=e.code,
                tencent_request_id=e.get_request_id(),
                user_message=error_mapping["user_message"],
                suggestion=error_mapping["suggestion"],
                is_retryable=error_mapping["is_retryable"],
                original_exception=e,
            )

    def get_available_styles(self) -> List[StylePreset]:
        """
        获取可用的风格预设列表。

        Returns:
            List[StylePreset]: 风格预设列表
        """
        return self._presets

    def get_style_preset(self, preset_id: str) -> StylePreset:
        """
        根据ID获取风格预设。

        Args:
            preset_id: 预设ID

        Returns:
            StylePreset: 风格预设

        Raises:
            ValueError: 如果预设不存在
        """
        for preset in self._presets:
            if preset.id == preset_id:
                return preset

        raise ValueError(f"风格预设不存在: {preset_id}")
