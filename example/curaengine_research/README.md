# CuraEngine 集成研究文档

## 概述

本文档记录 CuraEngine 切片引擎集成到 3D 打印平台的研究过程和实施方案。

## CuraEngine 简介

**CuraEngine** 是 Ultimaker 开发的开源 3D 打印切片引擎，用于将 STL/3MF 模型转换为 G-code。它是 Cura 软件的核心引擎，支持通过命令行独立使用。

### 主要特性

- **开源**: AGPL-3.0 许可证
- **高性能**: C++ 实现，切片速度快
- **功能完整**: 支持填充、支撑、壁厚、底板附着等完整功能
- **可扩展**: JSON 格式的打印机/材料配置文件
- **命令行**: 支持脚本化和自动化集成

## 安装方案对比

### 方案 1: 使用 AppImage (推荐)

**优点**:
- 无需编译，开箱即用
- 文件大小适中 (~20-30 MB)
- 官方发布，稳定可靠

**缺点**:
- 需要 FUSE 支持 (Docker 中需要特殊配置)
- 版本更新需要手动下载

**实施步骤**:
```dockerfile
# 在 Dockerfile 中添加
RUN apt-get update && apt-get install -y wget fuse && \
    wget https://github.com/Ultimaker/CuraEngine/releases/download/5.x.x/CuraEngine-5.x.x-linux-x86_64.AppImage \
    -O /usr/local/bin/CuraEngine.AppImage && \
    chmod +x /usr/local/bin/CuraEngine.AppImage
```

### 方案 2: 从源码编译

**优点**:
- 可以定制和优化
- 获得最新功能

**缺点**:
- 编译时间长 (5-10 分钟)
- 需要大量依赖 (CMake, protobuf, etc.)
- 增加 Docker 镜像构建时间

**实施步骤**:
```dockerfile
# 需要安装编译依赖
RUN apt-get install -y git cmake build-essential libprotobuf-dev protobuf-compiler
# 克隆并编译
RUN git clone https://github.com/Ultimaker/CuraEngine.git && \
    cd CuraEngine && mkdir build && cd build && \
    cmake .. && make -j$(nproc) && \
    cp CuraEngine /usr/local/bin/
```

### 方案 3: 使用预编译二进制 (采用)

**优点**:
- 安装快速
- 镜像体积小
- Docker 友好

**缺点**:
- 依赖官方发布周期

## CuraEngine 命令行使用

### 基本语法

```bash
CuraEngine slice -v -j printer.def.json -l model.stl -o output.gcode
```

### 主要参数

| 参数 | 说明 | 示例 |
|-----|------|------|
| `slice` | 切片命令 | - |
| `-v` | 详细输出 | `-v` |
| `-j <file>` | 打印机定义文件 (JSON) | `-j bambu_h2d.def.json` |
| `-l <file>` | 输入模型文件 | `-l model.stl` |
| `-o <file>` | 输出 G-code 文件 | `-o output.gcode` |
| `-s <key>=<value>` | 覆盖设置 | `-s layer_height=0.2` |

### 常用设置参数

```bash
# 层高
-s layer_height=0.2

# 填充率
-s infill_sparse_density=20

# 打印速度
-s speed_print=50

# 支撑
-s support_enable=true

# 底板附着
-s adhesion_type=brim

# 温度设置
-s material_print_temperature=210
-s material_bed_temperature=60
```

## 打印机配置文件

CuraEngine 使用 JSON 格式的打印机定义文件，包含：

1. **打印机属性** - 打印床尺寸、喷嘴直径等
2. **默认设置** - 层高、速度、温度等
3. **材料配置** - 不同材料的参数
4. **质量预设** - 快速/标准/高质量配置

### Bambu Lab H2D 配置

Bambu Lab 打印机不在 Cura 官方支持列表中，需要自定义配置文件。

#### 打印机规格

| 参数 | 拓竹 H2D 规格 |
|-----|--------------|
| 打印尺寸 | 256 × 256 × 256 mm |
| 喷嘴直径 | 0.4 mm (标准) |
| 耗材直径 | 1.75 mm |
| 最大速度 | 500 mm/s |
| 固件类型 | Marlin-compatible |
| 热床类型 | 加热床 |
| Z 轴分辨率 | 0.005 mm |

#### 配置文件结构

```json
{
  "id": "bambu_h2d",
  "version": 2,
  "name": "Bambu Lab H2D",
  "inherits": "fdmprinter",
  "metadata": {
    "visible": true,
    "author": "Custom",
    "manufacturer": "Bambu Lab",
    "file_formats": "text/x-gcode",
    "platform": "bambu_h2d_platform.stl"
  },
  "overrides": {
    "machine_name": { "default_value": "Bambu H2D" },
    "machine_width": { "default_value": 256 },
    "machine_depth": { "default_value": 256 },
    "machine_height": { "default_value": 256 },
    "machine_heated_bed": { "default_value": true },
    "machine_center_is_zero": { "default_value": false },
    "gantry_height": { "default_value": 30 },
    "machine_gcode_flavor": { "default_value": "Marlin" },
    "machine_start_gcode": { "default_value": "G28 ;Home\\nG1 Z15.0 F6000 ;Move up" },
    "machine_end_gcode": { "default_value": "M104 S0\\nM140 S0\\nG28 X Y\\nM84" }
  }
}
```

## Python 集成实现

### ISlicer 接口

```python
class ISlicer(ABC):
    @abstractmethod
    async def slice_model(
        self, stl_path: str, printer: PrinterProfile,
        config: SlicingConfig, output_path: str
    ) -> GCodeResult:
        pass
```

### CuraEngineSlicer 实现

```python
import asyncio
import subprocess
from domain.interfaces.i_slicer import ISlicer, GCodeResult

class CuraEngineSlicer(ISlicer):
    def __init__(self, cura_engine_path="/usr/local/bin/CuraEngine"):
        self.cura_engine_path = cura_engine_path
        self.definitions_dir = "/app/resources/cura_definitions"

    async def slice_model(self, stl_path, printer, config, output_path):
        # 构建命令行参数
        cmd = [
            self.cura_engine_path,
            "slice",
            "-v",
            "-j", f"{self.definitions_dir}/{printer.id}.def.json",
            "-l", stl_path,
            "-o", output_path,
            "-s", f"layer_height={config.layer_height}",
            "-s", f"infill_sparse_density={config.infill_density}",
            "-s", f"speed_print={config.print_speed}",
            "-s", f"support_enable={str(config.support_enabled).lower()}",
            "-s", f"adhesion_type={config.adhesion_type}",
        ]

        # 异步执行
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"CuraEngine failed: {stderr.decode()}")

        # 解析输出获取统计信息
        return self._parse_result(output_path, stdout.decode())
```

## 集成步骤

### 1. Docker 环境配置

更新 `backend/Dockerfile`:
```dockerfile
# 安装 CuraEngine
RUN wget -O /tmp/CuraEngine.AppImage https://github.com/Ultimaker/CuraEngine/releases/download/5.x.x/CuraEngine.AppImage && \
    chmod +x /tmp/CuraEngine.AppImage && \
    /tmp/CuraEngine.AppImage --appimage-extract && \
    mv squashfs-root/usr/bin/CuraEngine /usr/local/bin/ && \
    rm -rf /tmp/CuraEngine.AppImage squashfs-root
```

### 2. 添加打印机配置文件

创建 `backend/resources/cura_definitions/bambu_h2d.def.json`

### 3. 实现 CuraEngineSlicer 类

创建 `backend/src/infrastructure/slicing/cura_slicer.py`

### 4. 更新依赖注入

在应用启动时注册 CuraEngineSlicer：
```python
# backend/src/main.py
from src.infrastructure.slicing.cura_slicer import CuraEngineSlicer

slicer = CuraEngineSlicer()
```

### 5. 编写测试

创建集成测试验证切片功能：
```python
# backend/tests/integration/test_cura_slicer.py
async def test_slice_simple_model():
    slicer = CuraEngineSlicer()
    result = await slicer.slice_model(...)
    assert os.path.exists(result.gcode_path)
```

## 预期性能

| 模型复杂度 | 文件大小 | 切片时间 | G-code 大小 |
|-----------|---------|---------|------------|
| 简单 (立方体) | < 100 KB | < 5 秒 | < 500 KB |
| 中等 (玩具) | 1-5 MB | 10-20 秒 | 1-5 MB |
| 复杂 (雕塑) | > 10 MB | 20-30 秒 | 5-20 MB |

**目标**: G-code 生成时间 < 30 秒 (符合需求)

## 已知问题和解决方案

### 问题 1: AppImage 在 Docker 中运行

**现象**: AppImage 需要 FUSE 支持
**解决**: 解压 AppImage 直接使用二进制文件

### 问题 2: 配置文件路径

**现象**: CuraEngine 找不到定义文件
**解决**: 使用绝对路径或设置环境变量 `CURA_ENGINE_SEARCH_PATH`

### 问题 3: G-code 兼容性

**现象**: Bambu Lab 打印机可能不识别某些 G-code
**解决**: 在配置文件中指定 Marlin 风格 G-code，自定义 start/end G-code

## 参考资料

- [CuraEngine GitHub](https://github.com/Ultimaker/CuraEngine)
- [CuraEngine Wiki](https://github.com/Ultimaker/CuraEngine/wiki)
- [Cura 打印机定义文档](https://github.com/Ultimaker/Cura/wiki/Definition-Files-Explained)
- [Bambu Lab H2D 规格](https://bambulab.com/en/h2d)
- [G-code 参考](https://marlinfw.org/meta/gcode/)

## 下一步工作

- [x] 研究 CuraEngine 安装方案
- [x] 设计 Python 集成接口
- [x] 创建 Bambu H2D 配置文件
- [ ] 实现 CuraEngineSlicer 类
- [ ] 更新 Dockerfile
- [ ] 编写集成测试
- [ ] 真机测试验证
