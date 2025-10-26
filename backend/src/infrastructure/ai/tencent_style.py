"""
腾讯云风格化引擎实现模块。

封装腾讯云图像风格化 API,实现 IStyleEngine 接口。
复用 example/tencent_cloud/image_style_transfer_example.py 的验证代码。
"""

import base64
import json
import logging
import time
from pathlib import Path
from typing import Dict, List

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.aiart.v20221229 import aiart_client, models

from src.domain.interfaces.i_style_engine import IStyleEngine, StylePreset
from src.shared.exceptions.tencent_cloud_exceptions import TencentCloudAPIError
from src.shared.config.tencent_cloud_error_mapping import ErrorMapping

logger = logging.getLogger(__name__)


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
        logger.debug(
            f"初始化腾讯云风格化引擎 | region={region}, "
            f"secret_id={secret_id[:8]}***{secret_id[-4:] if len(secret_id) > 12 else '***'}"
        )

        self.cred = credential.Credential(secret_id, secret_key)

        http_profile = HttpProfile()
        http_profile.endpoint = "aiart.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile

        self.client = aiart_client.AiartClient(self.cred, region, client_profile)

        self._presets: List[StylePreset] = []
        self._load_presets()

        logger.info(
            f"腾讯云风格化引擎初始化完成 | region={region}, presets_count={len(self._presets)}"
        )

    def _load_presets(self) -> None:
        """
        加载风格预设配置。

        从 resources/tencent_cloud/style_presets_mapping.json 加载预设。
        """
        config_path = (
            Path(__file__).parent.parent.parent.parent
            / "resources"
            / "tencent_cloud"
            / "style_presets_mapping.json"
        )

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
    ) -> Dict[str, str]:
        """
        执行图像风格化转换。

        Args:
            image_path: 源图片路径
            style_preset_id: 风格预设ID

        Returns:
            Dict[str, str]: 包含以下字段的字典:
                - result_image_base64: 风格化后的图片 Base64 编码数据
                - request_id: 腾讯云请求ID

        Raises:
            FileNotFoundError: 如果源图片不存在
            ValueError: 如果风格预设不存在
            TencentCloudAPIError: 如果 API 调用失败
        """
        if style_preset_id not in self.STYLE_TYPES_MAPPING:
            error_msg = (
                f"不支持的风格类型: {style_preset_id}. "
                f"可选值: {', '.join(self.STYLE_TYPES_MAPPING.keys())}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 获取图片大小
        image_path_obj = Path(image_path)
        image_size_mb = (
            image_path_obj.stat().st_size / (1024 * 1024) if image_path_obj.exists() else 0
        )

        logger.debug(
            f"开始调用腾讯云风格化 API | style_id={style_preset_id}, "
            f"tencent_style_id={self.STYLE_TYPES_MAPPING[style_preset_id]}, "
            f"image_path={image_path}, image_size={image_size_mb:.2f}MB"
        )

        start_time = time.time()

        try:
            req = models.ImageToImageRequest()

            image_base64 = self._image_to_base64(image_path)
            req.InputImage = image_base64

            req.Styles = [self.STYLE_TYPES_MAPPING[style_preset_id]]

            logger.debug(f"发起腾讯云 API 请求 | style_id={style_preset_id}")

            resp = self.client.ImageToImage(req)

            elapsed_time = time.time() - start_time
            result_image = resp.ResultImage
            request_id = resp.RequestId

            logger.debug(
                f"腾讯云 API 响应成功 | request_id={request_id}, "
                f"elapsed_time={elapsed_time:.2f}s, has_result={bool(result_image)}"
            )

            if result_image:
                # 返回 Base64 数据而非保存到文件
                # 原因: 由调用方通过 StorageService 统一保存,符合存储抽象层原则
                result_size_mb = len(result_image) / (1024 * 1024) * 0.75  # Base64 约为原始大小 75%
                logger.info(
                    f"风格化处理成功 | style_id={style_preset_id}, request_id={request_id}, "
                    f"elapsed_time={elapsed_time:.2f}s, result_size_est={result_size_mb:.2f}MB"
                )

                return {
                    "result_image_base64": result_image,
                    "request_id": request_id or "",
                }
            else:
                logger.error(f"腾讯云 API 返回结果中没有图片数据 | request_id={request_id}")
                raise TencentCloudAPIError(
                    error_code="NO_RESULT_IMAGE",
                    message="API 返回结果中没有图片数据",
                    tencent_error_code="NO_RESULT_IMAGE",
                    tencent_request_id=request_id or "",
                )

        except TencentCloudSDKException as e:
            elapsed_time = time.time() - start_time
            error_mapping = ErrorMapping.get_mapping(e.code)

            logger.error(
                f"腾讯云 API 调用失败 | style_id={style_preset_id}, "
                f"tencent_error_code={e.code}, request_id={e.get_request_id()}, "
                f"elapsed_time={elapsed_time:.2f}s, error_message={str(e)}"
            )

            raise TencentCloudAPIError(
                error_code=error_mapping["code"],
                message=error_mapping["message"],
                tencent_error_code=e.code,
                tencent_request_id=e.get_request_id(),
                user_message=error_mapping.get("user_action", "请稍后重试"),
                suggestion=error_mapping["suggestion"],
                is_retryable=ErrorMapping.is_retryable(e.code),
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
