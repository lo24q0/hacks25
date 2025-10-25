# 打印机适配架构设计文档

## 1. 概述

### 1.1 设计目标

本文档定义了3D打印平台的打印机适配架构，旨在提供：

1. **通用接口设计**：支持可扩展的适配器模式，便于接入多种打印机设备
2. **易用API**：为其他模块提供简洁的打印任务管理接口
3. **设备管理**：支持打印机配置、状态监控和维护功能
4. **队列管理**：支持打印任务队列和友好的任务管理交互
5. **Bambu H2D支持**：首要支持拓竹（Bambu Lab）H2D打印机

### 1.2 核心原则

- **接口抽象**：打印机适配器实现统一接口，隔离具体设备差异
- **插件化架构**：新增打印机型号时无需修改核心代码
- **异步处理**：打印任务异步执行，避免阻塞主流程
- **可观测性**：完整的任务状态追踪和错误报告

---

## 2. 整体架构

### 2.1 架构视图

```
┌─────────────────────────────────────────────────────────────┐
│                      API层                                   │
│                   (Print Router)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   应用服务层                                  │
│                 (Print Service)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Task Manager  │  │Queue Manager │  │Config Manager│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    领域服务层                                 │
│             (Printer Domain Services)                       │
│  ┌──────────────────────────────────────────────┐           │
│  │        IPrinterAdapter (接口)                 │           │
│  └───────────┬──────────────────────┬───────────┘           │
│              │                      │                       │
│   ┌──────────▼─────────┐  ┌────────▼──────────┐            │
│   │ BambuAdapter       │  │ GenericAdapter    │            │
│   │ (拓竹H2D)           │  │ (通用适配器)       │            │
│   └────────────────────┘  └───────────────────┘            │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼─────┐  ┌────────▼────────┐  ┌────▼──────────┐
│  Slicer     │  │  File Storage   │  │  Task Queue   │
│  Engine     │  │  Service        │  │  (Celery)     │
└─────────────┘  └─────────────────┘  └───────────────┘
```

### 2.2 核心组件

#### 2.2.1 Print Service（应用服务）

**职责**：
- 编排打印流程（切片 → 队列 → 发送）
- 管理打印任务生命周期
- 协调适配器和队列管理器

#### 2.2.2 Task Manager（任务管理器）

**职责**：
- 创建、查询、取消打印任务
- 追踪任务状态变化
- 提供任务统计和历史记录

#### 2.2.3 Queue Manager（队列管理器）

**职责**：
- 管理打印任务队列（FIFO/优先级）
- 任务调度和分配
- 队列状态监控

#### 2.2.4 Config Manager（配置管理器）

**职责**：
- 管理打印机配置文件
- 打印参数预设管理
- 设备注册和注销

#### 2.2.5 Printer Adapter（打印机适配器）

**职责**：
- 实现特定打印机协议
- 状态查询和控制指令
- 文件传输和打印启动

---

## 3. 领域模型设计

### 3.1 核心实体

#### 3.1.1 PrintTask（打印任务聚合根）

```python
class PrintTask:
    """
    打印任务聚合根
    
    Attributes:
        id: 任务唯一标识
        model_id: 关联的3D模型ID
        printer_id: 目标打印机ID
        status: 任务状态
        queue_position: 队列位置（None表示未入队）
        slicing_config: 切片配置
        gcode_path: G-code文件路径
        estimated_time: 预估打印时长
        estimated_material: 预估耗材量（克）
        actual_start_time: 实际开始时间
        actual_end_time: 实际结束时间
        progress: 打印进度 (0-100)
        error_message: 错误信息
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: UUID
    model_id: UUID
    printer_id: str
    status: TaskStatus
    queue_position: Optional[int]
    slicing_config: SlicingConfig
    gcode_path: Optional[str]
    estimated_time: Optional[timedelta]
    estimated_material: Optional[float]
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    progress: int = 0
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    def start_slicing(self) -> None:
        """
        开始切片处理
        
        Raises:
            InvalidStateError: 如果任务状态不允许切片
        """
        pass
    
    def enqueue(self, position: int) -> None:
        """
        加入打印队列
        
        Args:
            position: 队列位置
        """
        pass
    
    def start_printing(self) -> None:
        """
        开始打印
        
        Raises:
            InvalidStateError: 如果任务状态不允许打印
        """
        pass
    
    def update_progress(self, progress: int) -> None:
        """
        更新打印进度
        
        Args:
            progress: 进度百分比 (0-100)
        """
        pass
    
    def mark_completed(self) -> None:
        """标记任务完成"""
        pass
    
    def mark_failed(self, error: str) -> None:
        """
        标记任务失败
        
        Args:
            error: 错误信息
        """
        pass
    
    def cancel(self) -> None:
        """
        取消任务
        
        Raises:
            InvalidStateError: 如果任务状态不允许取消
        """
        pass
```

#### 3.1.2 Printer（打印机实体）

```python
class Printer:
    """
    打印机实体
    
    Attributes:
        id: 打印机唯一标识
        name: 打印机名称
        model: 打印机型号（如 "Bambu H2D"）
        adapter_type: 适配器类型
        connection_config: 连接配置（IP、端口、认证信息）
        profile: 打印机硬件配置
        status: 打印机状态
        current_task_id: 当前打印任务ID
        is_enabled: 是否启用
        created_at: 创建时间
        last_heartbeat: 最后心跳时间
    """
    id: str
    name: str
    model: str
    adapter_type: AdapterType
    connection_config: ConnectionConfig
    profile: PrinterProfile
    status: PrinterStatus
    current_task_id: Optional[UUID]
    is_enabled: bool
    created_at: datetime
    last_heartbeat: Optional[datetime]
    
    def is_available(self) -> bool:
        """
        检查打印机是否可用
        
        Returns:
            bool: 打印机在线、空闲且已启用则返回True
        """
        pass
    
    def update_status(self, status: PrinterStatus) -> None:
        """
        更新打印机状态
        
        Args:
            status: 新状态
        """
        pass
    
    def assign_task(self, task_id: UUID) -> None:
        """
        分配打印任务
        
        Args:
            task_id: 任务ID
            
        Raises:
            PrinterBusyError: 如果打印机不可用
        """
        pass
```

### 3.2 值对象

#### 3.2.1 PrinterProfile（打印机配置文件）

```python
class PrinterProfile:
    """
    打印机硬件配置（值对象）
    
    Attributes:
        bed_size: 打印平台尺寸 (x, y, z) mm
        nozzle_diameter: 喷嘴直径 mm
        filament_diameter: 耗材直径 mm
        max_print_speed: 最大打印速度 mm/s
        max_travel_speed: 最大移动速度 mm/s
        firmware_flavor: 固件类型（Marlin, Klipper, 拓竹等）
        supported_formats: 支持的文件格式列表
    """
    bed_size: Tuple[int, int, int]
    nozzle_diameter: float
    filament_diameter: float
    max_print_speed: int
    max_travel_speed: int
    firmware_flavor: str
    supported_formats: List[str]
    
    def validate(self) -> ValidationResult:
        """
        验证配置有效性
        
        Returns:
            ValidationResult: 验证结果
        """
        pass
```

#### 3.2.2 SlicingConfig（切片配置）

```python
class SlicingConfig:
    """
    切片配置（值对象）
    
    Attributes:
        layer_height: 层高 (0.1-0.3mm)
        infill_density: 填充率 (0-100%)
        print_speed: 打印速度 mm/s
        travel_speed: 移动速度 mm/s
        support_enabled: 是否启用支撑
        adhesion_type: 底板附着类型 (skirt, brim, raft)
        material_type: 耗材类型 (PLA, ABS, PETG)
        nozzle_temperature: 喷嘴温度 °C
        bed_temperature: 热床温度 °C
    """
    layer_height: float
    infill_density: int
    print_speed: int
    travel_speed: int
    support_enabled: bool
    adhesion_type: AdhesionType
    material_type: MaterialType
    nozzle_temperature: int
    bed_temperature: int
    
    def validate(self) -> ValidationResult:
        """
        验证配置合理性
        
        Returns:
            ValidationResult: 验证结果
        """
        pass
    
    @classmethod
    def get_preset(cls, preset_name: str) -> "SlicingConfig":
        """
        获取预设配置
        
        Args:
            preset_name: 预设名称 (fast, standard, high_quality)
            
        Returns:
            SlicingConfig: 预设配置
        """
        pass
```

#### 3.2.3 ConnectionConfig（连接配置）

```python
class ConnectionConfig:
    """
    打印机连接配置（值对象）
    
    Attributes:
        connection_type: 连接类型（网络、串口、云端）
        host: IP地址或域名
        port: 端口号
        access_code: 访问码（拓竹使用）
        serial_number: 设备序列号
        use_ssl: 是否使用SSL
    """
    connection_type: ConnectionType
    host: Optional[str]
    port: Optional[int]
    access_code: Optional[str]
    serial_number: Optional[str]
    use_ssl: bool = False
```

### 3.3 枚举类型

```python
class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"           # 待切片
    SLICING = "slicing"          # 切片中
    QUEUED = "queued"            # 已入队
    PRINTING = "printing"        # 打印中
    PAUSED = "paused"            # 已暂停
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"      # 已取消

class PrinterStatus(Enum):
    """打印机状态"""
    OFFLINE = "offline"          # 离线
    IDLE = "idle"                # 空闲
    BUSY = "busy"                # 打印中
    ERROR = "error"              # 错误状态
    PAUSED = "paused"            # 暂停中

class AdapterType(Enum):
    """适配器类型"""
    BAMBU = "bambu"              # 拓竹
    GENERIC = "generic"          # 通用（基于G-code文件）
    OCTOPRINT = "octoprint"      # OctoPrint

class ConnectionType(Enum):
    """连接类型"""
    NETWORK = "network"          # 网络连接
    SERIAL = "serial"            # 串口连接
    CLOUD = "cloud"              # 云端API

class AdhesionType(Enum):
    """底板附着类型"""
    NONE = "none"
    SKIRT = "skirt"
    BRIM = "brim"
    RAFT = "raft"

class MaterialType(Enum):
    """耗材类型"""
    PLA = "pla"
    ABS = "abs"
    PETG = "petg"
    TPU = "tpu"
```

---

## 4. 接口设计

### 4.1 IPrinterAdapter（打印机适配器接口）

```python
class IPrinterAdapter(ABC):
    """
    打印机适配器接口
    
    所有打印机适配器必须实现此接口
    """
    
    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> bool:
        """
        连接打印机
        
        Args:
            config: 连接配置
            
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    async def get_status(self) -> PrinterStatus:
        """
        获取打印机状态
        
        Returns:
            PrinterStatus: 当前状态
        """
        pass
    
    @abstractmethod
    async def send_file(self, file_path: str) -> bool:
        """
        发送打印文件
        
        Args:
            file_path: 文件路径（.gcode 或 .3mf）
            
        Returns:
            bool: 发送是否成功
        """
        pass
    
    @abstractmethod
    async def start_print(self, file_name: str) -> bool:
        """
        开始打印
        
        Args:
            file_name: 文件名
            
        Returns:
            bool: 启动是否成功
        """
        pass
    
    @abstractmethod
    async def pause_print(self) -> bool:
        """
        暂停打印
        
        Returns:
            bool: 暂停是否成功
        """
        pass
    
    @abstractmethod
    async def resume_print(self) -> bool:
        """
        恢复打印
        
        Returns:
            bool: 恢复是否成功
        """
        pass
    
    @abstractmethod
    async def cancel_print(self) -> bool:
        """
        取消打印
        
        Returns:
            bool: 取消是否成功
        """
        pass
    
    @abstractmethod
    async def get_progress(self) -> PrintProgress:
        """
        获取打印进度
        
        Returns:
            PrintProgress: 进度信息
        """
        pass
```

### 4.2 ISlicer（切片引擎接口）

```python
class ISlicer(ABC):
    """
    切片引擎接口
    """
    
    @abstractmethod
    async def slice(
        self,
        model_path: str,
        printer_profile: PrinterProfile,
        config: SlicingConfig,
        output_path: str
    ) -> SliceResult:
        """
        切片3D模型
        
        Args:
            model_path: 模型文件路径（STL/OBJ）
            printer_profile: 打印机配置
            config: 切片配置
            output_path: 输出文件路径
            
        Returns:
            SliceResult: 切片结果
        """
        pass
    
    @abstractmethod
    def estimate_print_time(
        self,
        gcode_path: str
    ) -> timedelta:
        """
        估算打印时间
        
        Args:
            gcode_path: G-code文件路径
            
        Returns:
            timedelta: 预估打印时长
        """
        pass
    
    @abstractmethod
    def estimate_material_usage(
        self,
        gcode_path: str,
        filament_diameter: float
    ) -> float:
        """
        估算耗材用量
        
        Args:
            gcode_path: G-code文件路径
            filament_diameter: 耗材直径
            
        Returns:
            float: 耗材重量（克）
        """
        pass
```

### 4.3 IQueueManager（队列管理接口）

```python
class IQueueManager(ABC):
    """
    打印队列管理接口
    """
    
    @abstractmethod
    async def enqueue(self, task: PrintTask, priority: int = 0) -> int:
        """
        任务入队
        
        Args:
            task: 打印任务
            priority: 优先级（数字越大优先级越高）
            
        Returns:
            int: 队列位置
        """
        pass
    
    @abstractmethod
    async def dequeue(self) -> Optional[PrintTask]:
        """
        任务出队
        
        Returns:
            Optional[PrintTask]: 下一个待打印任务
        """
        pass
    
    @abstractmethod
    async def get_queue_status(self) -> QueueStatus:
        """
        获取队列状态
        
        Returns:
            QueueStatus: 队列状态信息
        """
        pass
    
    @abstractmethod
    async def remove_task(self, task_id: UUID) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功移除
        """
        pass
    
    @abstractmethod
    async def reorder_queue(self, task_id: UUID, new_position: int) -> bool:
        """
        调整任务队列位置
        
        Args:
            task_id: 任务ID
            new_position: 新位置
            
        Returns:
            bool: 是否成功调整
        """
        pass
```

---

## 5. Bambu H2D 适配器实现

### 5.1 BambuAdapter

基于 [bambulabs_api](https://github.com/BambuTools/bambulabs_api) 实现。

```python
class BambuAdapter(IPrinterAdapter):
    """
    拓竹（Bambu Lab）打印机适配器
    
    主要功能：
    - 状态监控（MQTT订阅）
    - 文件传输（FTP/MQTT）
    - 打印控制（通过MQTT发送命令）
    """
    
    def __init__(self):
        self._mqtt_client: Optional[mqtt.Client] = None
        self._ftp_client: Optional[ftplib.FTP] = None
        self._current_status: PrinterStatus = PrinterStatus.OFFLINE
        self._current_progress: int = 0
    
    async def connect(self, config: ConnectionConfig) -> bool:
        """
        连接拓竹打印机
        
        实现步骤：
        1. 建立MQTT连接（监听状态）
        2. 建立FTP连接（传输文件）
        3. 订阅状态主题
        
        Args:
            config: 连接配置（包含IP、端口、access_code）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # MQTT连接
            self._mqtt_client = mqtt.Client()
            self._mqtt_client.username_pw_set("bblp", config.access_code)
            self._mqtt_client.on_message = self._on_message
            
            await self._mqtt_client.connect_async(config.host, config.port or 8883)
            await self._mqtt_client.subscribe("device/{}/report".format(config.serial_number))
            
            # FTP连接
            self._ftp_client = ftplib.FTP()
            self._ftp_client.connect(config.host, config.port or 990)
            self._ftp_client.login("bblp", config.access_code)
            
            self._current_status = PrinterStatus.IDLE
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Bambu printer: {e}")
            return False
    
    async def send_file(self, file_path: str) -> bool:
        """
        发送 .gcode.3mf 文件到打印机
        
        实现步骤：
        1. 转换G-code为3MF格式（拓竹要求）
        2. 通过FTP上传文件
        3. 验证上传成功
        
        Args:
            file_path: 本地文件路径
            
        Returns:
            bool: 上传是否成功
        """
        if not file_path.endswith(".gcode.3mf"):
            file_path = self._convert_to_3mf(file_path)
        
        try:
            with open(file_path, "rb") as f:
                self._ftp_client.storbinary(f"STOR {os.path.basename(file_path)}", f)
            return True
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False
    
    async def start_print(self, file_name: str) -> bool:
        """
        通过MQTT发送打印指令
        
        Args:
            file_name: 文件名
            
        Returns:
            bool: 指令发送是否成功
        """
        command = {
            "print": {
                "command": "project_file",
                "param": f"Metadata/plate_1.gcode",
                "file": file_name
            }
        }
        
        topic = f"device/{self._serial_number}/request"
        self._mqtt_client.publish(topic, json.dumps(command))
        return True
    
    async def get_status(self) -> PrinterStatus:
        """
        获取打印机状态
        
        状态来源于MQTT订阅的消息
        
        Returns:
            PrinterStatus: 当前状态
        """
        return self._current_status
    
    async def get_progress(self) -> PrintProgress:
        """
        获取打印进度
        
        Returns:
            PrintProgress: 进度信息
        """
        return PrintProgress(
            percentage=self._current_progress,
            layer_current=self._layer_current,
            layer_total=self._layer_total,
            time_elapsed=self._time_elapsed,
            time_remaining=self._time_remaining
        )
    
    def _on_message(self, client, userdata, msg):
        """
        MQTT消息回调
        
        解析拓竹打印机的状态报告并更新内部状态
        """
        try:
            data = json.loads(msg.payload)
            
            # 提取关键状态字段
            self._current_progress = data.get("print", {}).get("mc_percent", 0)
            
            status_code = data.get("print", {}).get("gcode_state", "")
            self._current_status = self._map_status(status_code)
            
            self._layer_current = data.get("print", {}).get("layer_num", 0)
            self._layer_total = data.get("print", {}).get("total_layer_num", 0)
        except Exception as e:
            logger.error(f"Failed to parse MQTT message: {e}")
    
    def _map_status(self, status_code: str) -> PrinterStatus:
        """
        映射拓竹状态码到通用状态
        
        Args:
            status_code: 拓竹状态码
            
        Returns:
            PrinterStatus: 通用状态
        """
        mapping = {
            "IDLE": PrinterStatus.IDLE,
            "RUNNING": PrinterStatus.BUSY,
            "PAUSE": PrinterStatus.PAUSED,
            "FINISH": PrinterStatus.IDLE,
            "FAILED": PrinterStatus.ERROR,
        }
        return mapping.get(status_code, PrinterStatus.OFFLINE)
    
    def _convert_to_3mf(self, gcode_path: str) -> str:
        """
        转换G-code为拓竹3MF格式
        
        拓竹打印机要求使用 .gcode.3mf 格式
        
        Args:
            gcode_path: G-code文件路径
            
        Returns:
            str: 转换后的文件路径
        """
        # 实现G-code打包为3MF容器格式
        # 3MF本质是ZIP文件，包含G-code和元数据
        pass
```

### 5.2 参考实现

**关键代码提取自 bambulabs_api**：

1. **状态查询**：订阅 MQTT 主题 `device/{serial}/report`
2. **文件传输**：通过 FTP 上传 `.gcode.3mf` 文件
3. **打印启动**：发布 MQTT 消息到 `device/{serial}/request`

```python
# MQTT 消息示例（开始打印）
{
    "print": {
        "command": "project_file",
        "param": "Metadata/plate_1.gcode",
        "file": "example.gcode.3mf",
        "bed_type": "auto",
        "use_ams": false
    }
}

# MQTT 状态报告示例
{
    "print": {
        "gcode_state": "RUNNING",
        "mc_percent": 45,
        "layer_num": 120,
        "total_layer_num": 250,
        "mc_remaining_time": 3600
    }
}
```

---

## 6. 打印队列管理

### 6.1 队列架构

```
┌────────────────────────────────────────────────────┐
│              QueueManager                          │
│                                                    │
│  ┌──────────────────────────────────────────┐     │
│  │     Priority Queue (Redis Sorted Set)   │     │
│  │                                          │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │     │
│  │  │Task 1   │  │Task 2   │  │Task 3   │  │     │
│  │  │Priority:│  │Priority:│  │Priority:│  │     │
│  │  │  10     │  │   5     │  │   1     │  │     │
│  │  └─────────┘  └─────────┘  └─────────┘  │     │
│  └──────────────────────────────────────────┘     │
│                                                    │
│  ┌──────────────────────────────────────────┐     │
│  │       Task Scheduler (Celery Beat)       │     │
│  └──────────────────────────────────────────┘     │
└────────────────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Available Printers Pool     │
        │   ┌─────┐  ┌─────┐  ┌─────┐  │
        │   │ H2D │  │ H2D │  │ XXX │  │
        │   │ #1  │  │ #2  │  │ #1  │  │
        │   └─────┘  └─────┘  └─────┘  │
        └───────────────────────────────┘
```

### 6.2 QueueManager 实现

```python
class QueueManager(IQueueManager):
    """
    基于Redis的打印队列管理器
    
    使用Redis Sorted Set实现优先级队列
    """
    
    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client
        self._queue_key = "print_queue"
        self._task_key_prefix = "print_task:"
    
    async def enqueue(self, task: PrintTask, priority: int = 0) -> int:
        """
        任务入队
        
        实现步骤：
        1. 序列化任务对象
        2. 存储到Redis（task_id -> task_data）
        3. 加入优先级队列（Sorted Set）
        4. 计算队列位置
        
        Args:
            task: 打印任务
            priority: 优先级（数字越大越靠前）
            
        Returns:
            int: 队列位置（从1开始）
        """
        task_key = f"{self._task_key_prefix}{task.id}"
        task_data = task.model_dump_json()
        
        # 存储任务数据
        await self._redis.set(task_key, task_data)
        
        # 加入优先级队列（分数 = -priority，确保高优先级在前）
        score = -priority
        await self._redis.zadd(self._queue_key, {str(task.id): score})
        
        # 计算队列位置
        position = await self._redis.zrank(self._queue_key, str(task.id))
        
        task.status = TaskStatus.QUEUED
        task.queue_position = position + 1
        
        return position + 1
    
    async def dequeue(self) -> Optional[PrintTask]:
        """
        任务出队（FIFO + 优先级）
        
        Returns:
            Optional[PrintTask]: 下一个待打印任务
        """
        # 获取分数最低（优先级最高）的任务
        result = await self._redis.zpopmin(self._queue_key, 1)
        
        if not result:
            return None
        
        task_id, _ = result[0]
        task_key = f"{self._task_key_prefix}{task_id}"
        task_data = await self._redis.get(task_key)
        
        if not task_data:
            return None
        
        task = PrintTask.model_validate_json(task_data)
        task.queue_position = None
        
        return task
    
    async def get_queue_status(self) -> QueueStatus:
        """
        获取队列状态
        
        Returns:
            QueueStatus: 队列状态信息
        """
        queue_length = await self._redis.zcard(self._queue_key)
        
        # 获取前5个任务
        task_ids = await self._redis.zrange(self._queue_key, 0, 4)
        
        tasks = []
        for task_id in task_ids:
            task_key = f"{self._task_key_prefix}{task_id}"
            task_data = await self._redis.get(task_key)
            if task_data:
                tasks.append(PrintTask.model_validate_json(task_data))
        
        return QueueStatus(
            total=queue_length,
            pending_tasks=tasks,
            estimated_wait_time=self._estimate_wait_time(tasks)
        )
    
    async def remove_task(self, task_id: UUID) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功移除
        """
        removed = await self._redis.zrem(self._queue_key, str(task_id))
        
        if removed:
            task_key = f"{self._task_key_prefix}{task_id}"
            await self._redis.delete(task_key)
            return True
        
        return False
    
    def _estimate_wait_time(self, tasks: List[PrintTask]) -> timedelta:
        """
        估算等待时间
        
        Args:
            tasks: 队列中的任务列表
            
        Returns:
            timedelta: 估算的等待时长
        """
        total_time = sum(
            (task.estimated_time or timedelta(0)).total_seconds()
            for task in tasks
        )
        return timedelta(seconds=total_time)
```

### 6.3 任务调度器

```python
@celery_app.task
def process_print_queue():
    """
    定时任务：处理打印队列
    
    执行周期：每30秒
    
    流程：
    1. 查询可用打印机
    2. 从队列取出任务
    3. 分配任务到打印机
    4. 启动打印
    """
    queue_manager = get_queue_manager()
    printer_service = get_printer_service()
    
    # 获取所有空闲打印机
    available_printers = printer_service.get_available_printers()
    
    for printer in available_printers:
        task = await queue_manager.dequeue()
        
        if not task:
            break
        
        try:
            # 分配任务
            printer.assign_task(task.id)
            
            # 获取适配器
            adapter = get_adapter(printer.adapter_type)
            await adapter.connect(printer.connection_config)
            
            # 发送文件并启动打印
            await adapter.send_file(task.gcode_path)
            await adapter.start_print(os.path.basename(task.gcode_path))
            
            # 更新任务状态
            task.start_printing()
            task.actual_start_time = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to start print task {task.id}: {e}")
            task.mark_failed(str(e))
```

---

## 7. API设计

### 7.1 REST API端点

#### 7.1.1 打印任务管理

```
POST   /api/v1/prints/tasks
GET    /api/v1/prints/tasks
GET    /api/v1/prints/tasks/{task_id}
DELETE /api/v1/prints/tasks/{task_id}
POST   /api/v1/prints/tasks/{task_id}/pause
POST   /api/v1/prints/tasks/{task_id}/resume
POST   /api/v1/prints/tasks/{task_id}/cancel
```

**示例：创建打印任务**

```python
@router.post("/tasks", response_model=PrintTaskResponse)
async def create_print_task(
    request: CreatePrintTaskRequest,
    print_service: PrintService = Depends()
) -> PrintTaskResponse:
    """
    创建打印任务
    
    Args:
        request: 请求参数
            - model_id: 3D模型ID
            - printer_id: 打印机ID
            - slicing_config: 切片配置（可选，使用预设）
            - priority: 优先级（可选，默认0）
    
    Returns:
        PrintTaskResponse: 任务信息
    """
    task = await print_service.create_task(
        model_id=request.model_id,
        printer_id=request.printer_id,
        slicing_config=request.slicing_config or SlicingConfig.get_preset("standard"),
        priority=request.priority
    )
    
    return PrintTaskResponse.from_domain(task)
```

#### 7.1.2 打印机管理

```
GET    /api/v1/printers
POST   /api/v1/printers
GET    /api/v1/printers/{printer_id}
PUT    /api/v1/printers/{printer_id}
DELETE /api/v1/printers/{printer_id}
GET    /api/v1/printers/{printer_id}/status
```

**示例：注册打印机**

```python
@router.post("/printers", response_model=PrinterResponse)
async def register_printer(
    request: RegisterPrinterRequest,
    config_manager: ConfigManager = Depends()
) -> PrinterResponse:
    """
    注册打印机
    
    Args:
        request: 请求参数
            - name: 打印机名称
            - model: 打印机型号
            - adapter_type: 适配器类型
            - connection_config: 连接配置
    
    Returns:
        PrinterResponse: 打印机信息
    """
    printer = await config_manager.register_printer(
        name=request.name,
        model=request.model,
        adapter_type=request.adapter_type,
        connection_config=request.connection_config
    )
    
    return PrinterResponse.from_domain(printer)
```

#### 7.1.3 队列管理

```
GET    /api/v1/prints/queue
POST   /api/v1/prints/queue/reorder
```

**示例：查询队列状态**

```python
@router.get("/queue", response_model=QueueStatusResponse)
async def get_queue_status(
    queue_manager: IQueueManager = Depends()
) -> QueueStatusResponse:
    """
    获取打印队列状态
    
    Returns:
        QueueStatusResponse: 队列状态
            - total: 总任务数
            - pending_tasks: 待打印任务列表
            - estimated_wait_time: 估算等待时间
    """
    status = await queue_manager.get_queue_status()
    
    return QueueStatusResponse(
        total=status.total,
        pending_tasks=[PrintTaskSummary.from_domain(t) for t in status.pending_tasks],
        estimated_wait_time=status.estimated_wait_time.total_seconds()
    )
```

### 7.2 请求/响应模型

```python
class CreatePrintTaskRequest(BaseModel):
    """创建打印任务请求"""
    model_id: UUID
    printer_id: str
    slicing_config: Optional[SlicingConfig] = None
    priority: int = 0

class PrintTaskResponse(BaseModel):
    """打印任务响应"""
    id: UUID
    model_id: UUID
    printer_id: str
    status: TaskStatus
    queue_position: Optional[int]
    progress: int
    estimated_time: Optional[int]  # 秒
    estimated_material: Optional[float]  # 克
    created_at: datetime
    
    @classmethod
    def from_domain(cls, task: PrintTask) -> "PrintTaskResponse":
        """从领域对象转换"""
        return cls(
            id=task.id,
            model_id=task.model_id,
            printer_id=task.printer_id,
            status=task.status,
            queue_position=task.queue_position,
            progress=task.progress,
            estimated_time=int(task.estimated_time.total_seconds()) if task.estimated_time else None,
            estimated_material=task.estimated_material,
            created_at=task.created_at
        )

class RegisterPrinterRequest(BaseModel):
    """注册打印机请求"""
    name: str
    model: str
    adapter_type: AdapterType
    connection_config: ConnectionConfig

class PrinterResponse(BaseModel):
    """打印机响应"""
    id: str
    name: str
    model: str
    status: PrinterStatus
    is_available: bool
    current_task_id: Optional[UUID]
```

---

## 8. 任务拆解

### 8.1 P0阶段（核心功能，2天）

#### 8.1.1 Day 1：基础架构

**任务1：领域模型实现**
- [ ] 定义 `PrintTask` 聚合根
- [ ] 定义 `Printer` 实体
- [ ] 定义值对象（`SlicingConfig`, `PrinterProfile`, `ConnectionConfig`）
- [ ] 定义枚举类型（`TaskStatus`, `PrinterStatus`, `AdapterType`）
- [ ] 编写单元测试

**任务2：接口定义**
- [ ] 定义 `IPrinterAdapter` 接口
- [ ] 定义 `ISlicer` 接口
- [ ] 定义 `IQueueManager` 接口

**任务3：切片引擎集成**
- [ ] 集成 CuraEngine 命令行工具
- [ ] 实现 `CuraSlicer` 类
- [ ] 实现拓竹H2D配置文件
- [ ] 测试切片功能

**验收标准**：
- 可成功切片STL文件生成G-code
- 支持基础切片参数配置

#### 8.1.2 Day 2：适配器与队列

**任务4：Bambu适配器实现**
- [ ] 实现 `BambuAdapter` 基础结构
- [ ] 实现MQTT连接和状态订阅
- [ ] 实现FTP文件传输
- [ ] 实现打印启动指令
- [ ] 实现G-code转3MF格式
- [ ] 测试与拓竹H2D打印机通信

**任务5：队列管理器实现**
- [ ] 实现 `QueueManager` 类（基于Redis）
- [ ] 实现任务入队/出队逻辑
- [ ] 实现队列查询接口
- [ ] 编写单元测试

**任务6：API实现**
- [ ] 实现 `/api/v1/prints/tasks` 端点（创建、查询、取消）
- [ ] 实现 `/api/v1/printers` 端点（注册、查询）
- [ ] 实现 `/api/v1/prints/queue` 端点
- [ ] 编写API测试

**验收标准**：
- 可通过API创建打印任务
- 任务能正确入队和调度
- 可成功发送文件到拓竹H2D打印机
- 可启动打印并获取状态

### 8.2 P1阶段（增强功能，1-2天）

**任务7：任务监控**
- [ ] 实现任务进度实时更新（MQTT订阅）
- [ ] 实现任务失败重试机制
- [ ] 实现任务完成通知

**任务8：打印机管理**
- [ ] 实现打印机心跳检测
- [ ] 实现打印机离线/上线状态同步
- [ ] 实现打印机配置热更新

**任务9：队列优化**
- [ ] 实现任务优先级调整
- [ ] 实现等待时间估算优化
- [ ] 实现队列可视化界面

**验收标准**：
- 打印进度实时更新（误差<5%）
- 打印机状态准确同步
- 支持任务优先级调整

### 8.3 P2阶段（扩展功能，未来）

**任务10：多打印机支持**
- [ ] 实现通用适配器（基于G-code传输）
- [ ] 实现OctoPrint适配器
- [ ] 实现打印机自动发现

**任务11：高级队列功能**
- [ ] 实现打印机池（多台设备负载均衡）
- [ ] 实现任务批量操作
- [ ] 实现队列统计和分析

**任务12：监控与告警**
- [ ] 实现打印失败告警
- [ ] 实现耗材不足检测
- [ ] 实现打印完成推送

---

## 9. 部署架构

### 9.1 组件部署

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                       │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Backend  │  │ Celery   │  │  Redis   │             │
│  │ (FastAPI)│  │ Worker   │  │          │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                    │
│       └─────────────┼─────────────┘                    │
│                     │                                  │
│  ┌──────────────────▼──────────────────┐               │
│  │      Printer Adapters               │               │
│  │  ┌──────────┐  ┌──────────┐        │               │
│  │  │  Bambu   │  │  Generic │        │               │
│  │  │ Adapter  │  │ Adapter  │        │               │
│  │  └──────────┘  └──────────┘        │               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
                      │
                      │ MQTT/FTP
                      ▼
        ┌──────────────────────────┐
        │  Bambu H2D Printer       │
        │  IP: 192.168.1.100       │
        └──────────────────────────┘
```

### 9.2 配置文件示例

**docker-compose.yml**

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  celery_worker:
    build: ./backend
    command: celery -A infrastructure.tasks.celery_app worker --loglevel=info -Q print_queue
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  celery_beat:
    build: ./backend
    command: celery -A infrastructure.tasks.celery_app beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**打印机配置文件 (printers.yaml)**

```yaml
printers:
  - id: "bambu_h2d_01"
    name: "拓竹 H2D #1"
    model: "Bambu H2D"
    adapter_type: "bambu"
    connection:
      type: "network"
      host: "192.168.1.100"
      port: 8883
      access_code: "12345678"
      serial_number: "01S00C123456789"
      use_ssl: true
    profile:
      bed_size: [256, 256, 256]
      nozzle_diameter: 0.4
      filament_diameter: 1.75
      max_print_speed: 500
      firmware_flavor: "bambu"
      supported_formats: [".gcode.3mf"]
```

---

## 10. 监控与可观测性

### 10.1 关键指标

**业务指标**：
- 打印任务创建数（每小时）
- 打印成功率（成功/总数）
- 平均打印时长
- 平均队列等待时间

**技术指标**：
- 打印机在线率
- 切片任务平均耗时
- 文件传输成功率
- MQTT消息延迟

### 10.2 日志设计

```python
# 任务创建日志
logger.info(
    "Print task created",
    extra={
        "task_id": task.id,
        "model_id": task.model_id,
        "printer_id": task.printer_id,
        "estimated_time": task.estimated_time
    }
)

# 打印启动日志
logger.info(
    "Print started",
    extra={
        "task_id": task.id,
        "printer_id": printer.id,
        "file_name": file_name
    }
)

# 打印完成日志
logger.info(
    "Print completed",
    extra={
        "task_id": task.id,
        "actual_time": actual_time,
        "success": True
    }
)

# 错误日志
logger.error(
    "Print failed",
    extra={
        "task_id": task.id,
        "printer_id": printer.id,
        "error": str(e)
    }
)
```

---

## 11. 风险与应对

### 11.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| bambulabs_api 库维护停止 | 高 | 中 | 提取核心代码自行维护，准备备用实现 |
| MQTT连接不稳定 | 中 | 中 | 实现断线重连机制，心跳检测 |
| 3MF转换失败 | 中 | 低 | 提供G-code直接传输备用方案 |
| 队列任务丢失 | 高 | 低 | Redis持久化，任务状态定期备份 |

### 11.2 兼容性风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| 拓竹固件更新导致协议变化 | 高 | 中 | 定期测试新固件，维护多版本适配 |
| CuraEngine配置不兼容 | 中 | 低 | 提供配置文件版本管理 |

---

## 12. 未来扩展

### 12.1 多打印机支持

- 实现OctoPrint适配器（支持Marlin/Klipper固件）
- 实现Prusa打印机适配器
- 实现打印机自动发现（mDNS/UPnP）

### 12.2 高级功能

- 打印失败自动暂停和恢复
- 耗材用量统计和告警
- 打印质量监控（摄像头集成）
- 多色打印支持（AMS集成）

### 12.3 云端扩展

- 远程打印（云端中转）
- 打印任务历史分析
- 打印农场管理（多台设备统一管理）

---

## 13. 总结

### 13.1 设计亮点

1. **清晰的接口抽象**：`IPrinterAdapter` 接口隔离设备差异，易于扩展
2. **优先级队列**：基于Redis实现高性能任务调度
3. **异步处理**：切片和打印任务异步执行，不阻塞用户体验
4. **实时状态同步**：通过MQTT订阅实现打印进度实时更新
5. **完整的任务生命周期管理**：从创建到完成的全流程追踪

### 13.2 技术选型合理性

- **MQTT**：拓竹打印机原生支持，低延迟，适合实时状态同步
- **Redis**：高性能，支持优先级队列和分布式锁
- **Celery**：成熟的异步任务框架，支持定时任务和重试

### 13.3 开发建议

1. **优先实现拓竹H2D适配器**：满足P0阶段需求
2. **尽早集成真实设备测试**：验证MQTT和FTP通信
3. **队列管理先简后繁**：P0实现基础FIFO，P1引入优先级
4. **预留扩展接口**：为多打印机支持做好准备

---

**文档版本**: v1.0  
**创建日期**: 2025-10-25  
**作者**: Claude (Architect)  
**审核状态**: 待审核  
**相关文档**:
- `ARCH.md` - 整体架构设计
- `INITIAL.md` - 产品需求文档
- Issue #45 - 打印机适配设计需求
