# bambulabs_api 库分析文档

## 1. 概述

**仓库地址**: https://github.com/BambuTools/bambulabs_api

**PyPI 包名**: `bambulabs_api`

**最低 Python 版本**: 3.10+

**状态**: 活跃维护,生产就绪

## 2. 核心架构

### 2.1 主要模块

```
bambulabs_api/
├── client.py           # Printer 类 - 主入口
├── mqtt_client.py      # MQTT 客户端 - 状态监听和命令发送
├── ftp_client.py       # FTP 客户端 - 文件上传
├── camera_client.py    # 摄像头客户端 - 实时视频流
├── ams.py              # AMS (自动换料系统) 支持
├── filament_info.py    # 耗材信息
├── states_info.py      # 状态枚举和类型
└── printer_info.py     # 打印机信息
```

### 2.2 核心类

#### Printer (client.py)

主要的客户端类,封装了所有功能:

```python
class Printer:
    def __init__(self, ip_address: str, access_code: str, serial: str):
        self.mqtt_client = PrinterMQTTClient(...)
        self.camera_client = PrinterCamera(...)
        self.ftp_client = PrinterFTPClient(...)

    # 连接管理
    def connect(self)
    def disconnect(self)

    # 状态查询
    def get_state() -> GcodeState
    def get_percentage() -> int
    def get_time() -> int
    def current_layer_num() -> int
    def total_layer_num() -> int

    # 打印控制
    def start_print(filename, plate_number, use_ams, ...)
    def pause_print()
    def resume_print()
    def stop_print()

    # 文件上传
    def upload_file(file: BinaryIO, filename: str)

    # 其他功能
    def turn_light_on()
    def turn_light_off()
    def gcode(gcode: str | list[str])
```

#### PrinterMQTTClient (mqtt_client.py)

MQTT 客户端,处理所有 MQTT 通信:
- 连接管理
- 消息订阅和发布
- 状态解析
- 命令发送

#### PrinterFTPClient (ftp_client.py)

FTP 客户端,处理文件上传:
- FTPS 连接
- 文件上传
- 文件管理

## 3. 使用方式

### 3.1 基本用法

```python
import bambulabs_api as bl

# 创建打印机实例
printer = bl.Printer(
    ip_address="192.168.1.100",
    access_code="12345678",
    serial="00M00A123456789"
)

# 连接
printer.connect()

# 查询状态
state = printer.get_state()  # GcodeState 枚举
progress = printer.get_percentage()  # 0-100
remaining_time = printer.get_time()  # 秒

# 上传文件
with open("model.gcode.3mf", "rb") as f:
    path = printer.upload_file(f, "model.gcode.3mf")

# 开始打印
printer.start_print(
    filename="model.gcode.3mf",
    plate_number=1,  # 或 "Metadata/plate_1.gcode"
    use_ams=False
)

# 控制打印
printer.pause_print()
printer.resume_print()
printer.stop_print()

# 断开连接
printer.disconnect()
```

### 3.2 状态枚举

```python
from bambulabs_api import GcodeState

# 打印机状态
GcodeState.IDLE
GcodeState.RUNNING
GcodeState.PAUSE
GcodeState.FINISH
GcodeState.FAILED
GcodeState.UNKNOWN
```

## 4. 与我们架构的集成

### 4.1 优势

1. **成熟稳定**: 活跃维护,生产环境验证
2. **功能完整**: 支持所有拓竹打印机功能
3. **API 清晰**: 易于集成到我们的 IPrinterAdapter 接口
4. **测试完善**: 自带测试套件
5. **文档齐全**: 有完整的 API 文档

### 4.2 集成方案

#### 方案: 适配器模式

将 `bambulabs_api.Printer` 封装到我们的 `BambuAdapter`:

```python
from bambulabs_api import Printer as BambuPrinter, GcodeState

class BambuAdapter(IPrinterAdapter):
    def __init__(self):
        self._printer: Optional[BambuPrinter] = None

    async def connect(self, config: ConnectionConfig) -> bool:
        self._printer = BambuPrinter(
            ip_address=config.host,
            access_code=config.password,
            serial=config.serial_number
        )
        self._printer.connect()
        return True

    async def get_status(self) -> PrinterStatus:
        state = self._printer.get_state()
        return self._map_status(state)

    def _map_status(self, gcode_state: GcodeState) -> PrinterStatus:
        mapping = {
            GcodeState.IDLE: PrinterStatus.IDLE,
            GcodeState.RUNNING: PrinterStatus.BUSY,
            GcodeState.PAUSE: PrinterStatus.PAUSED,
            GcodeState.FINISH: PrinterStatus.IDLE,
            GcodeState.FAILED: PrinterStatus.ERROR,
        }
        return mapping.get(gcode_state, PrinterStatus.OFFLINE)
```

### 4.3 接口映射

| IPrinterAdapter 方法 | bambulabs_api.Printer 方法 |
|---------------------|---------------------------|
| `connect()` | `Printer.connect()` |
| `disconnect()` | `Printer.disconnect()` |
| `get_status()` | `Printer.get_state()` |
| `send_file()` | `Printer.upload_file()` |
| `start_print()` | `Printer.start_print()` |
| `pause_print()` | `Printer.pause_print()` |
| `resume_print()` | `Printer.resume_print()` |
| `cancel_print()` | `Printer.stop_print()` |
| `get_progress()` | `Printer.get_percentage()`, `Printer.current_layer_num()` 等 |

## 5. 依赖要求

### 5.1 核心依赖

```
paho_mqtt       # MQTT 客户端
webcolors       # 颜色处理 (AMS 相关)
pillow          # 图像处理 (摄像头相关)
```

### 5.2 安装方式

```bash
pip install bambulabs_api
```

或添加到 `requirements.txt`:

```
bambulabs_api>=2.7.0
```

## 6. 特性支持

### 6.1 已支持功能

- ✅ MQTT 连接和状态监听
- ✅ FTP 文件上传
- ✅ 打印控制 (开始/暂停/恢复/停止)
- ✅ 状态查询 (进度/层数/温度等)
- ✅ 灯光控制
- ✅ G-code 命令发送
- ✅ AMS 自动换料系统
- ✅ 摄像头视频流 (X1 系列)

### 6.2 已知限制

根据 README:
- X1 打印机摄像头集成不完整 (< 2.7.0)
- **H2D 打印机未经测试** ⚠️

## 7. 重构计划

### 7.1 代码变更

1. **BambuAdapter 重构**
   - 移除自定义 MQTT/FTP 实现
   - 使用 bambulabs_api.Printer 封装
   - 保持 IPrinterAdapter 接口不变

2. **依赖更新**
   - 添加 `bambulabs_api>=2.7.0` 到 requirements.txt

3. **测试更新**
   - 更新 Mock 测试
   - 保持测试接口不变

### 7.2 优势

1. **减少代码量**: 删除自定义 MQTT/FTP 实现 (~200 行)
2. **提高稳定性**: 使用经过验证的库
3. **获得更多功能**: AMS, 摄像头, G-code 命令等
4. **更好的维护**: 跟随上游更新

### 7.3 风险

1. **H2D 兼容性**: 库声明 H2D 未测试
   - 缓解: 保留原实现作为备选
   - 建议: 真机测试验证兼容性

2. **额外依赖**: webcolors, pillow
   - 影响: 增加约 5MB 依赖
   - 可接受: 功能换体积

## 8. 对比分析

### 8.1 自定义实现 vs bambulabs_api

| 维度 | 自定义实现 | bambulabs_api |
|-----|----------|--------------|
| 代码量 | ~250 行 | ~50 行 (适配器) |
| 依赖 | paho-mqtt | bambulabs_api (含 paho-mqtt) |
| 功能 | 基础 MQTT/FTP | 完整功能 |
| 稳定性 | 未验证 | 生产验证 |
| 维护 | 自行维护 | 社区维护 |
| H2D 支持 | 未测试 | 未测试 ⚠️ |
| 文档 | 自行编写 | 官方文档 |

### 8.2 推荐方案

**推荐使用 bambulabs_api**,原因:

1. ✅ 成熟稳定,生产验证
2. ✅ 功能完整,持续更新
3. ✅ 减少维护负担
4. ✅ API 清晰易用
5. ⚠️ H2D 兼容性需验证 (但原实现也未验证)

**备选方案**: 保留原自定义实现作为 fallback

## 9. 实现示例

### 9.1 新的 BambuAdapter

```python
"""
使用 bambulabs_api 的 BambuAdapter 实现
"""

import asyncio
from typing import Optional
import bambulabs_api as bl
from bambulabs_api import GcodeState

from domain.interfaces.i_printer_adapter import IPrinterAdapter, PrintProgress
from domain.enums.print_enums import PrinterStatus
from domain.value_objects.connection_config import ConnectionConfig


class BambuAdapter(IPrinterAdapter):
    """
    拓竹(Bambu Lab)打印机适配器

    使用 bambulabs_api 库封装
    """

    def __init__(self):
        self._printer: Optional[bl.Printer] = None

    async def connect(self, config: ConnectionConfig) -> bool:
        try:
            self._printer = bl.Printer(
                ip_address=config.host,
                access_code=config.password,
                serial=config.serial_number
            )

            # 只启动 MQTT (不启动摄像头)
            self._printer.mqtt_start()

            # 等待连接就绪
            await asyncio.sleep(2)

            return self._printer.mqtt_client_connected()
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def disconnect(self) -> None:
        if self._printer:
            self._printer.disconnect()
            self._printer = None

    async def get_status(self) -> PrinterStatus:
        if not self._printer:
            return PrinterStatus.OFFLINE

        state = self._printer.get_state()
        return self._map_status(state)

    async def send_file(self, file_path: str) -> bool:
        if not self._printer:
            return False

        try:
            with open(file_path, 'rb') as f:
                filename = os.path.basename(file_path)
                self._printer.upload_file(f, filename)
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    async def start_print(self, file_name: str) -> bool:
        if not self._printer:
            return False

        return self._printer.start_print(
            filename=file_name,
            plate_number=1,  # 或 "Metadata/plate_1.gcode"
            use_ams=False
        )

    async def pause_print(self) -> bool:
        if not self._printer:
            return False
        return self._printer.pause_print()

    async def resume_print(self) -> bool:
        if not self._printer:
            return False
        return self._printer.resume_print()

    async def cancel_print(self) -> bool:
        if not self._printer:
            return False
        return self._printer.stop_print()

    async def get_progress(self) -> PrintProgress:
        if not self._printer:
            return PrintProgress(0, 0, 0, 0, 0)

        return PrintProgress(
            percentage=self._printer.get_percentage() or 0,
            layer_current=self._printer.current_layer_num(),
            layer_total=self._printer.total_layer_num(),
            time_elapsed=0,  # bambulabs_api 不提供此字段
            time_remaining=self._printer.get_time() or 0
        )

    def _map_status(self, gcode_state: GcodeState) -> PrinterStatus:
        """映射状态"""
        mapping = {
            GcodeState.IDLE: PrinterStatus.IDLE,
            GcodeState.RUNNING: PrinterStatus.BUSY,
            GcodeState.PAUSE: PrinterStatus.PAUSED,
            GcodeState.FINISH: PrinterStatus.IDLE,
            GcodeState.FAILED: PrinterStatus.ERROR,
        }
        return mapping.get(gcode_state, PrinterStatus.OFFLINE)
```

## 10. 下一步行动

1. ✅ 分析 bambulabs_api 库
2. ⏳ 重构 BambuAdapter 使用 bambulabs_api
3. ⏳ 更新 requirements.txt
4. ⏳ 更新测试
5. ⏳ 更新文档
6. ⏳ 真机测试 H2D 兼容性

---

**分析完成日期**: 2025-10-25
**分析者**: Claude
**推荐方案**: 使用 bambulabs_api 库
