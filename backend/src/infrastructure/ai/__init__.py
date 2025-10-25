"""
AI 服务集成模块。

提供 Meshy AI API 客户端、腾讯云风格化服务及3D模型生成服务。
"""

from infrastructure.ai.image_to_3d_service import ImageTo3DService
from infrastructure.ai.tencent_style import TencentCloudStyleEngine
from infrastructure.ai.meshy_client import (
    MeshyAPIError,
    MeshyAuthenticationError,
    MeshyClient,
    MeshyRateLimitError,
    MeshyServerError,
    MeshyValidationError,
)
from infrastructure.ai.meshy_model_generator import MeshyModelGenerator
from infrastructure.ai.meshy_models import (
    AIModel,
    ArtStyle,
    GenerationConfig,
    ImageTo3DRequest,
    MeshyTaskListResponse,
    MeshyTaskResponse,
    ModelUrls,
    SymmetryMode,
    TaskMode,
    TaskStatus,
    TextTo3DPreviewRequest,
    TextTo3DRefineRequest,
    TextureUrls,
    TopologyType,
)
from infrastructure.ai.text_to_3d_service import TextTo3DService

__all__ = [
    # Client
    "MeshyClient",
    # Exceptions
    "MeshyAPIError",
    "MeshyAuthenticationError",
    "MeshyRateLimitError",
    "MeshyServerError",
    "MeshyValidationError",
    # Services
    "TextTo3DService",
    "ImageTo3DService",
    "MeshyModelGenerator",
    "TencentCloudStyleEngine",
    # Models - Request
    "TextTo3DPreviewRequest",
    "TextTo3DRefineRequest",
    "ImageTo3DRequest",
    "GenerationConfig",
    # Models - Response
    "MeshyTaskResponse",
    "MeshyTaskListResponse",
    "ModelUrls",
    "TextureUrls",
    # Enums
    "ArtStyle",
    "TopologyType",
    "SymmetryMode",
    "AIModel",
    "TaskMode",
    "TaskStatus",
]
