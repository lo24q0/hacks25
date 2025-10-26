# Linux 3D 切片引擎调研报告

**调研日期**: 2025-10-26
**项目**: 3D模型打印系统
**目标打印机**: 拓竹 Bambu Lab H2D
**调研背景**: CuraEngine 在 Linux 环境下安装困难，需要寻找替代方案

---

## 1. 调研概述

### 1.1 评估标准

| 标准 | 权重 | 说明 |
|------|------|------|
| Linux 安装难度 | ⭐⭐⭐⭐⭐ | 能否通过包管理器或 AppImage 轻松安装 |
| 命令行支持 | ⭐⭐⭐⭐⭐ | 是否支持无 GUI 的命令行切片 |
| Bambu Lab 支持 | ⭐⭐⭐⭐ | 是否有官方或社区的拓竹打印机配置 |
| 文档完善度 | ⭐⭐⭐⭐ | 命令行使用文档是否齐全 |
| 社区活跃度 | ⭐⭐⭐ | 是否持续维护和更新 |
| 集成复杂度 | ⭐⭐⭐⭐ | 与现有 Python 后端集成的难度 |

---

## 2. 候选切片引擎

### 2.1 PrusaSlicer CLI ⭐⭐⭐⭐⭐ (强烈推荐)

#### 基本信息
- **官网**: https://github.com/prusa3d/PrusaSlicer
- **许可证**: AGPL-3.0
- **语言**: C++
- **维护状态**: ✅ 活跃维护 (最新版本 2.7.x)

#### Linux 安装方式

**方式 1: AppImage (推荐)**
```bash
# 下载最新版本
wget https://github.com/prusa3d/PrusaSlicer/releases/download/version_2.7.4/PrusaSlicer-2.7.4+linux-x64-GTK3.AppImage

# 赋予执行权限
chmod +x PrusaSlicer-*.AppImage

# 运行 (无需安装)
./PrusaSlicer-*.AppImage --help
```

**方式 2: 从源码编译**
```bash
# Ubuntu/Debian 依赖
sudo apt-get install -y git cmake libboost-dev libboost-regex-dev \
    libboost-filesystem-dev libboost-thread-dev libboost-log-dev \
    libboost-locale-dev libcurl4-openssl-dev libwxgtk3.0-gtk3-dev \
    build-essential pkg-config libtbb-dev zlib1g-dev libcereal-dev \
    libeigen3-dev libnlopt-cxx-dev

# 克隆仓库
git clone https://github.com/prusa3d/PrusaSlicer.git
cd PrusaSlicer

# 编译
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# 生成的可执行文件在 build/src/prusa-slicer
```

#### 命令行使用

```bash
# 基础切片命令
prusa-slicer --export-gcode \
    --load config.ini \
    --output output.gcode \
    input.stl

# 无 GUI 模式
prusa-slicer-console --export-gcode input.stl

# 覆盖参数
prusa-slicer --export-gcode \
    --layer-height 0.2 \
    --fill-density 20% \
    --print-center 128,128 \
    input.stl
```

#### 优势
✅ **安装简单**: AppImage 开箱即用，无需复杂依赖
✅ **命令行完善**: 支持 `--export-gcode` 和详细参数覆盖
✅ **配置文件支持**: 可导入 `.ini` 配置文件
✅ **Bambu Lab 支持**: 社区有丰富的拓竹打印机配置
✅ **切片质量高**: 业界公认的优秀切片算法
✅ **文档齐全**: 官方文档详细，社区资源丰富

#### 劣势
⚠️ AppImage 文件较大 (~150MB)
⚠️ 首次运行需要生成配置文件

#### 集成建议
**难度**: ⭐⭐ (简单)

1. 在 Dockerfile 中下载 AppImage
2. 创建 `PrusaSlicer` 类实现 `ISlicer` 接口
3. 通过 `subprocess` 调用命令行
4. 解析输出的 G-code 文件获取统计信息

---

### 2.2 OrcaSlicer ⭐⭐⭐⭐⭐ (最佳 Bambu Lab 支持)

#### 基本信息
- **官网**: https://github.com/SoftFever/OrcaSlicer
- **许可证**: AGPL-3.0
- **语言**: C++ (基于 PrusaSlicer 二次开发)
- **维护状态**: ✅ 活跃维护
- **特点**: **专为 Bambu Lab 打印机优化**

#### Linux 安装方式

**方式 1: AppImage (推荐)**
```bash
# 下载最新版本
wget https://github.com/SoftFever/OrcaSlicer/releases/download/v2.1.1/OrcaSlicer_Linux_V2.1.1.AppImage

chmod +x OrcaSlicer_*.AppImage
```

**方式 2: Ubuntu PPA**
```bash
sudo add-apt-repository ppa:softfever/orcaslicer
sudo apt update
sudo apt install orcaslicer
```

#### 命令行使用
```bash
# 命令行模式 (语法与 PrusaSlicer 类似)
orcaslicer --export-gcode input.stl

# 使用配置文件
orcaslicer --load bambu_h2d_profile.ini --export-gcode input.stl
```

#### 优势
✅ **Bambu Lab 原生支持**: 内置拓竹所有机型配置，包括 H2D
✅ **优化的切片算法**: 针对拓竹打印机的打印特性优化
✅ **社区活跃**: 拓竹用户首选切片软件
✅ **安装简单**: AppImage 或 PPA 安装
✅ **配置文件兼容**: 可导入/导出配置

#### 劣势
⚠️ 相对较新 (2022年起)，文档相对较少
⚠️ 命令行文档不如 PrusaSlicer 完善

#### 集成建议
**难度**: ⭐⭐ (简单)

**这是最推荐的方案**，因为:
1. 拓竹打印机配置开箱即用
2. 切片质量针对拓竹优化
3. 安装部署简单
4. 命令行接口与 PrusaSlicer 兼容

---

### 2.3 SuperSlicer ⭐⭐⭐⭐

#### 基本信息
- **官网**: https://github.com/supermerill/SuperSlicer
- **许可证**: AGPL-3.0
- **语言**: C++ (PrusaSlicer 增强版)
- **维护状态**: ⚠️ 维护频率下降

#### Linux 安装方式
```bash
# AppImage
wget https://github.com/supermerill/SuperSlicer/releases/download/2.5.59.11/SuperSlicer-2.5.59.11-Linux.AppImage
chmod +x SuperSlicer-*.AppImage
```

#### 命令行使用
```bash
superslicer --export-gcode input.stl
```

#### 优势
✅ 功能最丰富 (比 PrusaSlicer 更多高级选项)
✅ 命令行支持完善
✅ AppImage 安装简单

#### 劣势
⚠️ 维护频率下降 (最后更新 2023)
⚠️ 功能过于复杂，对简单需求来说过剩

---

### 2.4 CuraEngine (原计划方案)

#### 重新评估安装方式

**方式 1: 从源码编译 (推荐)**
```bash
# 安装依赖
sudo apt-get install git cmake gcc g++ libprotobuf-dev protobuf-compiler

# 克隆仓库
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine

# 编译
mkdir build && cd build
cmake ..
make -j$(nproc)

# 安装
sudo make install
```

**方式 2: Docker 镜像**
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    git cmake gcc g++ libprotobuf-dev protobuf-compiler
RUN git clone https://github.com/Ultimaker/CuraEngine.git && \
    cd CuraEngine && mkdir build && cd build && \
    cmake .. && make -j$(nproc) && make install
```

#### 优势
✅ 轻量级 (仅命令行工具，无 GUI)
✅ 拓竹官方推荐
✅ 已有项目集成代码

#### 劣势
⚠️ **安装复杂**: 需要编译，依赖多
⚠️ 配置文件格式复杂 (JSON 定义)
⚠️ 命令行参数冗长

#### 当前状态
- ⚠️ 项目已实现 `CuraEngineSlicer` (backend/src/infrastructure/slicing/cura_slicer.py:14)
- ⚠️ 但 Linux 环境部署困难

---

### 2.5 Slic3r (原版)

#### 基本信息
- **官网**: https://github.com/slic3r/Slic3r
- **许可证**: AGPL-3.0
- **维护状态**: ❌ 已停止维护 (2018年后)

#### 评估结论
❌ **不推荐**: 项目已过时，社区已转向 PrusaSlicer

---

## 3. 对比总结

| 切片引擎 | 安装难度 | 命令行支持 | Bambu 支持 | 文档质量 | 社区活跃 | 推荐指数 |
|---------|---------|-----------|-----------|---------|---------|---------|
| **OrcaSlicer** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| **PrusaSlicer** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| SuperSlicer | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| CuraEngine | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Slic3r | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ❌ | ❌ |

---

## 4. 推荐方案

### 方案 A: OrcaSlicer (最佳 Bambu Lab 体验) ⭐⭐⭐⭐⭐

**适用场景**:
- 专注于拓竹打印机
- 需要最佳切片质量
- 希望快速部署

**实施步骤**:
1. 在 Dockerfile 中下载 OrcaSlicer AppImage
2. 创建 `backend/src/infrastructure/slicing/orca_slicer.py`
3. 实现 `ISlicer` 接口
4. 使用内置的 Bambu H2D 配置文件

**预计工作量**: 4-6 小时

---

### 方案 B: PrusaSlicer (最成熟稳定) ⭐⭐⭐⭐⭐

**适用场景**:
- 需要长期稳定支持
- 可能扩展到其他打印机品牌
- 需要详细的文档支持

**实施步骤**:
1. 在 Dockerfile 中下载 PrusaSlicer AppImage
2. 创建 `backend/src/infrastructure/slicing/prusa_slicer.py`
3. 准备 Bambu H2D 配置文件 (从社区获取)
4. 实现命令行调用逻辑

**预计工作量**: 4-6 小时

---

### 方案 C: 双引擎支持 (灵活性最高)

**实施策略**:
1. 主引擎: OrcaSlicer (拓竹优化)
2. 备用引擎: PrusaSlicer (通用支持)
3. 通过环境变量切换: `SLICER_ENGINE=orca|prusa`

**实施步骤**:
1. 实现两个 Slicer 类
2. 创建工厂模式选择引擎
3. 在 API 中支持客户端选择切片引擎

**预计工作量**: 8-10 小时

---

## 5. 部署建议

### Dockerfile 示例 (OrcaSlicer)

```dockerfile
FROM python:3.11-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    wget \
    fuse \
    libfuse2 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 下载 OrcaSlicer
RUN wget -O /usr/local/bin/orcaslicer \
    https://github.com/SoftFever/OrcaSlicer/releases/download/v2.1.1/OrcaSlicer_Linux_V2.1.1.AppImage \
    && chmod +x /usr/local/bin/orcaslicer

# 配置 AppImage 在容器中运行
ENV APPIMAGE_EXTRACT_AND_RUN=1

WORKDIR /app
```

### Docker Compose 配置

```yaml
services:
  backend:
    build: ./backend
    environment:
      - SLICER_ENGINE=orca
      - ORCA_SLICER_PATH=/usr/local/bin/orcaslicer
    volumes:
      - ./data:/app/data
```

---

## 6. 迁移计划

### 从 CuraEngine 迁移到 OrcaSlicer/PrusaSlicer

#### 阶段 1: 准备工作 (1 小时)
- [ ] 选择目标切片引擎 (OrcaSlicer 或 PrusaSlicer)
- [ ] 在本地测试 AppImage 运行
- [ ] 准备 Bambu H2D 配置文件

#### 阶段 2: 实现新 Slicer (4-6 小时)
- [ ] 创建新的 Slicer 实现类
- [ ] 实现 `slice_model` 方法
- [ ] 实现 G-code 解析逻辑
- [ ] 编写单元测试

#### 阶段 3: 集成测试 (2 小时)
- [ ] 更新 Dockerfile
- [ ] 测试容器化部署
- [ ] 端到端切片测试
- [ ] 验证 G-code 输出

#### 阶段 4: 部署上线 (1 小时)
- [ ] 更新配置文件
- [ ] 更新文档
- [ ] 部署到生产环境

**总工作量**: 8-10 小时

---

## 7. 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| AppImage 在容器中运行失败 | 高 | 低 | 使用 `APPIMAGE_EXTRACT_AND_RUN=1` 环境变量 |
| 配置文件格式不兼容 | 中 | 中 | 提前测试，准备配置转换脚本 |
| 切片速度变慢 | 低 | 低 | OrcaSlicer/PrusaSlicer 性能与 CuraEngine 相当 |
| G-code 格式差异 | 中 | 低 | 拓竹打印机使用标准 G-code，兼容性好 |

---

## 8. 结论与建议

### 最终推荐: **OrcaSlicer** ⭐⭐⭐⭐⭐

**理由**:
1. ✅ **原生支持拓竹 H2D**: 无需配置，开箱即用
2. ✅ **安装最简单**: AppImage 单文件，无依赖地狱
3. ✅ **切片质量最优**: 专为拓竹打印机优化
4. ✅ **社区活跃**: 拓竹用户首选，问题容易解决
5. ✅ **集成难度低**: 与现有架构完美兼容

### 备选方案: **PrusaSlicer**
- 适合未来扩展到其他打印机品牌
- 文档和生态更成熟
- 如果 OrcaSlicer 遇到问题，可快速切换

### 不推荐继续使用 CuraEngine
- ❌ Linux 安装困难 (需要编译)
- ❌ 配置复杂 (JSON 定义文件)
- ❌ 相比 OrcaSlicer，无显著优势

---

## 9. 下一步行动

1. **立即执行**: 实现 OrcaSlicer 集成
2. **P1 阶段**: 添加 PrusaSlicer 作为备选
3. **P2 阶段**: 支持用户选择切片引擎

---

**调研人**: Claude
**审核状态**: 待审核
**更新日期**: 2025-10-26
