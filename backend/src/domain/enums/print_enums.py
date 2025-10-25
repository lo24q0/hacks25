from enum import Enum


class TaskStatus(Enum):
    """
    打印任务状态枚举
    """
    PENDING = "pending"
    SLICING = "slicing"
    QUEUED = "queued"
    PRINTING = "printing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PrinterStatus(Enum):
    """
    打印机状态枚举
    """
    OFFLINE = "offline"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    PAUSED = "paused"


class AdapterType(Enum):
    """
    适配器类型枚举
    """
    BAMBU = "bambu"
    GENERIC = "generic"
    OCTOPRINT = "octoprint"


class ConnectionType(Enum):
    """
    连接类型枚举
    """
    NETWORK = "network"
    SERIAL = "serial"
    CLOUD = "cloud"


class AdhesionType(Enum):
    """
    底板附着类型枚举
    """
    NONE = "none"
    SKIRT = "skirt"
    BRIM = "brim"
    RAFT = "raft"


class MaterialType(Enum):
    """
    耗材类型枚举
    """
    PLA = "pla"
    ABS = "abs"
    PETG = "petg"
    TPU = "tpu"
