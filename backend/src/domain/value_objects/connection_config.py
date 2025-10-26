from typing import Optional
from pydantic import BaseModel, Field
from src.domain.enums.print_enums import ConnectionType


class ConnectionConfig(BaseModel):
    """
    打印机连接配置(值对象)

    Attributes:
        connection_type: 连接类型
        host: IP地址或域名
        port: 端口号
        access_code: 访问码
        serial_number: 设备序列号
        use_ssl: 是否使用SSL
    """

    connection_type: ConnectionType = Field(..., description="连接类型")
    host: Optional[str] = Field(None, description="IP地址或域名")
    port: Optional[int] = Field(None, description="端口号")
    access_code: Optional[str] = Field(None, description="访问码")
    serial_number: Optional[str] = Field(None, description="设备序列号")
    use_ssl: bool = Field(default=False, description="是否使用SSL")
