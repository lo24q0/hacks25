"""
Meshy AI API 数据模型定义。

包含文本转3D、图片转3D的请求和响应模型。
参考: https://docs.meshy.ai/en/api/
"""

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ArtStyle(str, Enum):
    """艺术风格枚举"""

    REALISTIC = "realistic"
    SCULPTURE = "sculpture"


class TopologyType(str, Enum):
    """网格拓扑类型枚举"""

    QUAD = "quad"
    TRIANGLE = "triangle"


class SymmetryMode(str, Enum):
    """对称模式枚举"""

    OFF = "off"
    AUTO = "auto"
    ON = "on"


class AIModel(str, Enum):
    """AI 模型版本枚举"""

    MESHY_4 = "meshy-4"
    MESHY_5 = "meshy-5"
    MESHY_6 = "meshy-6"
    LATEST = "latest"


class TaskMode(str, Enum):
    """任务模式枚举"""

    PREVIEW = "preview"
    REFINE = "refine"


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class TextTo3DPreviewRequest(BaseModel):
    """
    文本转3D预览任务请求模型。

    用于创建初始预览模型。
    """

    mode: Literal[TaskMode.PREVIEW] = Field(
        default=TaskMode.PREVIEW, description="任务模式,固定为 preview"
    )
    prompt: str = Field(..., max_length=600, description="3D模型描述文本,最大600字符")
    art_style: ArtStyle = Field(
        default=ArtStyle.REALISTIC, description="艺术风格"
    )
    ai_model: AIModel = Field(default=AIModel.MESHY_5, description="AI 模型版本")
    topology: TopologyType = Field(
        default=TopologyType.TRIANGLE, description="网格拓扑类型"
    )
    target_polycount: int = Field(
        default=30000, ge=100, le=300000, description="目标面数,范围 100-300000"
    )
    should_remesh: bool = Field(default=True, description="是否启用重网格化")
    symmetry_mode: SymmetryMode = Field(
        default=SymmetryMode.AUTO, description="对称模式"
    )
    is_a_t_pose: bool = Field(default=False, description="是否为T-pose(用于角色生成)")
    seed: Optional[int] = Field(default=None, description="随机种子,用于可重现生成")
    moderation: bool = Field(default=False, description="是否启用内容审核")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """
        验证 prompt 长度。

        Args:
            v: prompt 文本

        Returns:
            str: 验证后的 prompt

        Raises:
            ValueError: 如果 prompt 为空或过长
        """
        if not v or not v.strip():
            raise ValueError("prompt 不能为空")
        if len(v) > 600:
            raise ValueError("prompt 长度不能超过 600 字符")
        return v.strip()


class TextTo3DRefineRequest(BaseModel):
    """
    文本转3D细化任务请求模型。

    用于对预览模型进行纹理细化。
    """

    mode: Literal[TaskMode.REFINE] = Field(
        default=TaskMode.REFINE, description="任务模式,固定为 refine"
    )
    preview_task_id: str = Field(..., description="已完成的预览任务 ID")
    enable_pbr: bool = Field(
        default=False, description="是否生成 PBR 贴图(金属度、粗糙度、法线)"
    )
    texture_prompt: Optional[str] = Field(
        default=None, max_length=600, description="纹理引导文本,最大600字符"
    )
    texture_image_url: Optional[str] = Field(
        default=None, description="纹理参考图片 URL 或 base64 数据 URI"
    )


class ImageTo3DRequest(BaseModel):
    """
    图片转3D任务请求模型。

    用于从单张图片生成3D模型。
    """

    image_url: str = Field(..., description="图片 URL 或 base64 数据 URI")
    ai_model: AIModel = Field(default=AIModel.MESHY_5, description="AI 模型版本")
    topology: TopologyType = Field(
        default=TopologyType.TRIANGLE, description="网格拓扑类型"
    )
    target_polycount: int = Field(
        default=30000, ge=100, le=300000, description="目标面数,范围 100-300000"
    )
    should_remesh: bool = Field(default=True, description="是否启用重网格化")
    symmetry_mode: SymmetryMode = Field(
        default=SymmetryMode.AUTO, description="对称模式"
    )
    should_texture: bool = Field(default=True, description="是否生成纹理")
    enable_pbr: bool = Field(
        default=False, description="是否生成 PBR 贴图(金属度、粗糙度、法线)"
    )
    texture_prompt: Optional[str] = Field(
        default=None, max_length=600, description="纹理引导文本,最大600字符"
    )
    texture_image_url: Optional[str] = Field(
        default=None, description="纹理参考图片 URL"
    )
    is_a_t_pose: bool = Field(default=False, description="是否为T-pose(用于角色生成)")
    moderation: bool = Field(default=False, description="是否启用内容审核")

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        """
        验证图片 URL。

        Args:
            v: 图片 URL

        Returns:
            str: 验证后的 URL

        Raises:
            ValueError: 如果 URL 为空
        """
        if not v or not v.strip():
            raise ValueError("image_url 不能为空")
        return v.strip()


class ModelUrls(BaseModel):
    """模型文件 URL 集合"""

    glb: Optional[str] = Field(default=None, description="GLB 格式模型 URL")
    fbx: Optional[str] = Field(default=None, description="FBX 格式模型 URL")
    obj: Optional[str] = Field(default=None, description="OBJ 格式模型 URL")
    mtl: Optional[str] = Field(default=None, description="MTL 材质文件 URL")
    usdz: Optional[str] = Field(default=None, description="USDZ 格式模型 URL")


class TextureUrls(BaseModel):
    """纹理贴图 URL 集合"""

    base_color: Optional[str] = Field(default=None, description="基础颜色贴图 URL")
    metallic: Optional[str] = Field(default=None, description="金属度贴图 URL")
    normal: Optional[str] = Field(default=None, description="法线贴图 URL")
    roughness: Optional[str] = Field(default=None, description="粗糙度贴图 URL")


class MeshyTaskResponse(BaseModel):
    """
    Meshy 任务响应模型。

    包含任务状态、进度、模型 URL 等信息。
    """

    id: str = Field(..., description="任务 ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: int = Field(default=0, ge=0, le=100, description="任务进度百分比")
    prompt: Optional[str] = Field(default=None, description="生成提示词")
    art_style: Optional[ArtStyle] = Field(default=None, description="艺术风格")
    model_urls: Optional[ModelUrls] = Field(default=None, description="模型文件 URLs")
    texture_urls: Optional[TextureUrls] = Field(
        default=None, description="纹理贴图 URLs"
    )
    thumbnail_url: Optional[str] = Field(default=None, description="缩略图 URL")
    video_url: Optional[str] = Field(default=None, description="预览视频 URL")
    task_error: Optional[dict] = Field(default=None, description="任务错误信息")
    created_at: Optional[int] = Field(default=None, description="创建时间戳")
    started_at: Optional[int] = Field(default=None, description="开始时间戳")
    finished_at: Optional[int] = Field(default=None, description="完成时间戳")
    expires_at: Optional[int] = Field(default=None, description="过期时间戳")


class MeshyTaskListResponse(BaseModel):
    """
    Meshy 任务列表响应模型。

    用于分页查询任务列表。
    """

    data: list[MeshyTaskResponse] = Field(default_factory=list, description="任务列表")
    total: int = Field(default=0, description="总任务数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页大小")


class GenerationConfig(BaseModel):
    """
    生成任务配置模型。

    统一的生成参数配置。
    """

    art_style: ArtStyle = Field(
        default=ArtStyle.REALISTIC, description="艺术风格"
    )
    ai_model: AIModel = Field(default=AIModel.MESHY_5, description="AI 模型版本")
    topology: TopologyType = Field(
        default=TopologyType.TRIANGLE, description="网格拓扑类型"
    )
    target_polycount: int = Field(
        default=30000, ge=100, le=300000, description="目标面数,范围 100-300000"
    )
    should_remesh: bool = Field(default=True, description="是否启用重网格化")
    symmetry_mode: SymmetryMode = Field(
        default=SymmetryMode.AUTO, description="对称模式"
    )
    enable_pbr: bool = Field(
        default=False, description="是否生成 PBR 贴图"
    )
    is_a_t_pose: bool = Field(default=False, description="是否为T-pose")
    moderation: bool = Field(default=False, description="是否启用内容审核")

    @field_validator("target_polycount")
    @classmethod
    def validate_polycount(cls, v: int) -> int:
        """
        验证目标面数。

        Args:
            v: 目标面数

        Returns:
            int: 验证后的面数

        Raises:
            ValueError: 如果面数超出范围
        """
        if v < 100 or v > 300000:
            raise ValueError("target_polycount 必须在 100-300000 之间")
        return v

    def to_text_to_3d_request(
        self, prompt: str, seed: Optional[int] = None
    ) -> TextTo3DPreviewRequest:
        """
        转换为文本转3D请求模型。

        Args:
            prompt: 文本描述
            seed: 随机种子

        Returns:
            TextTo3DPreviewRequest: 请求模型
        """
        return TextTo3DPreviewRequest(
            prompt=prompt,
            art_style=self.art_style,
            ai_model=self.ai_model,
            topology=self.topology,
            target_polycount=self.target_polycount,
            should_remesh=self.should_remesh,
            symmetry_mode=self.symmetry_mode,
            is_a_t_pose=self.is_a_t_pose,
            seed=seed,
            moderation=self.moderation,
        )

    def to_image_to_3d_request(
        self,
        image_url: str,
        texture_prompt: Optional[str] = None,
        texture_image_url: Optional[str] = None,
    ) -> ImageTo3DRequest:
        """
        转换为图片转3D请求模型。

        Args:
            image_url: 图片 URL
            texture_prompt: 纹理引导文本
            texture_image_url: 纹理参考图片 URL

        Returns:
            ImageTo3DRequest: 请求模型
        """
        return ImageTo3DRequest(
            image_url=image_url,
            ai_model=self.ai_model,
            topology=self.topology,
            target_polycount=self.target_polycount,
            should_remesh=self.should_remesh,
            symmetry_mode=self.symmetry_mode,
            enable_pbr=self.enable_pbr,
            texture_prompt=texture_prompt,
            texture_image_url=texture_image_url,
            is_a_t_pose=self.is_a_t_pose,
            moderation=self.moderation,
        )
