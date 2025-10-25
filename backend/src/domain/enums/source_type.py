from enum import Enum


class SourceType(Enum):
    """
    3D模型生成的源类型。

    Attributes:
        TEXT: 文本描述生成
        IMAGE: 图片生成
    """

    TEXT = "text"
    IMAGE = "image"


class StorageBackend(Enum):
    """
    存储后端类型。

    Attributes:
        LOCAL: 本地文件系统
        MINIO: MinIO对象存储
        S3: AWS S3或兼容服务
    """

    LOCAL = "local"
    MINIO = "minio"
    S3 = "s3"
