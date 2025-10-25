# Bambulabs API 集成研究文档

## 1. 概述

本文档记录了 bambulabs_api 库的集成研究过程,用于实现拓竹(Bambu Lab)打印机的 MQTT/FTP 真实通信功能。

## 2. bambulabs_api 库调研

### 2.1 库信息

**GitHub 仓库**: https://github.com/Doridian/bambulabs_api

bambulabs_api 是一个用于与 Bambu Lab 3D 打印机通信的 Python 库,支持:
- MQTT 协议进行状态监控和控制
- FTP 协议进行文件传输
- 实时状态更新
- 打印任务控制

### 2.2 主要功能模块

1. **MQTT 通信**
   - 订阅打印机状态报告
   - 发送打印控制命令
   - 实时进度监控

2. **FTP 文件传输**
   - 上传 .gcode.3mf 文件
   - 管理打印机存储

3. **状态管理**
   - 打印机状态解析
   - 进度追踪
   - 错误处理

## 3. 核心 API 分析

### 3.1 连接配置

拓竹打印机连接需要以下参数:
- **IP 地址**: 打印机局域网IP
- **Access Code**: 打印机屏幕上的访问码
- **Serial Number**: 打印机序列号

### 3.2 MQTT 主题结构

```
device/{serial_number}/report    # 状态报告(打印机 -> 客户端)
device/{serial_number}/request   # 控制命令(客户端 -> 打印机)
```

### 3.3 MQTT 消息格式

**状态报告示例:**
```json
{
  "print": {
    "gcode_state": "RUNNING",
    "mc_percent": 45,
    "mc_remaining_time": 3600,
    "layer_num": 120,
    "total_layer_num": 250,
    "subtask_name": "example.gcode.3mf",
    "nozzle_temper": 220,
    "bed_temper": 60
  }
}
```

**打印控制命令示例:**
```json
{
  "print": {
    "command": "project_file",
    "param": "Metadata/plate_1.gcode",
    "file": "example.gcode.3mf",
    "bed_type": "auto",
    "use_ams": false
  }
}
```

**暂停命令:**
```json
{
  "print": {
    "command": "pause"
  }
}
```

**恢复命令:**
```json
{
  "print": {
    "command": "resume"
  }
}
```

**停止命令:**
```json
{
  "print": {
    "command": "stop"
  }
}
```

### 3.4 FTP 配置

- **端口**: 990 (FTPS)
- **用户名**: "bblp"
- **密码**: Access Code

## 4. 集成方案设计

### 4.1 依赖库选择

由于 bambulabs_api 可能不在 PyPI 上或版本不稳定,我们有两个方案:

**方案A: 直接使用 bambulabs_api**
```bash
pip install git+https://github.com/Doridian/bambulabs_api.git
```

**方案B: 自行实现(使用标准库)**
```python
# MQTT: paho-mqtt
# FTP: ftplib (标准库)
```

### 4.2 推荐方案

**推荐使用方案B(自行实现)**,原因:
1. 更好的控制和可维护性
2. 避免第三方库的不稳定性
3. 可以针对项目需求定制
4. 依赖更少,部署更简单

所需依赖:
```
paho-mqtt>=1.6.0    # MQTT 客户端
```

## 5. 实现计划

### 5.1 核心组件

1. **MQTTHandler**: 处理 MQTT 连接和消息
2. **FTPHandler**: 处理文件传输
3. **BambuAdapter**: 整合两者,实现 IPrinterAdapter 接口

### 5.2 实现步骤

1. ✅ 研究 bambulabs_api 协议和消息格式
2. ⏳ 实现 MQTT 连接和状态订阅
3. ⏳ 实现 FTP 文件上传
4. ⏳ 实现打印控制命令
5. ⏳ 集成到 BambuAdapter
6. ⏳ 编写测试用例

## 6. 技术细节

### 6.1 MQTT 连接参数

```python
mqtt_config = {
    "host": printer_ip,
    "port": 8883,  # MQTT over TLS
    "username": "bblp",
    "password": access_code,
    "tls": True,
    "cert_reqs": ssl.CERT_NONE  # 拓竹使用自签名证书
}
```

### 6.2 状态映射

| 拓竹状态码 | PrinterStatus 枚举 |
|-----------|-------------------|
| IDLE      | IDLE             |
| RUNNING   | BUSY             |
| PAUSE     | PAUSED           |
| FINISH    | IDLE             |
| FAILED    | ERROR            |

### 6.3 错误处理

需要处理的错误场景:
1. 网络连接失败
2. 认证失败(Access Code 错误)
3. 文件传输失败
4. MQTT 消息解析错误
5. 打印机离线

## 7. 测试策略

### 7.1 单元测试
- MQTT 消息解析
- 状态映射逻辑
- 错误处理

### 7.2 集成测试
- Mock MQTT broker
- Mock FTP server
- 端到端流程测试

### 7.3 真机测试
- 需要真实的拓竹 H2D 打印机
- 验证文件传输
- 验证打印控制

## 8. 参考资料

1. Bambu Lab API 非官方文档: https://github.com/Doridian/bambulabs_api/wiki
2. MQTT 协议: https://mqtt.org/
3. paho-mqtt 文档: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php

## 9. 下一步行动

1. 安装 paho-mqtt 依赖
2. 创建 MQTT 和 FTP 工具模块
3. 更新 BambuAdapter 实现
4. 编写测试用例
5. 更新项目文档

---

**创建日期**: 2025-10-25
**作者**: Claude
**状态**: 研究中
