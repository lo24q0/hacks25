# OrcaSlicer 配置说明

## 概述

OrcaSlicer 是基于 PrusaSlicer 的增强版本，专为 Bambu Lab 打印机优化。

## Bambu Lab 打印机支持

OrcaSlicer **内置了所有 Bambu Lab 打印机的配置文件**，包括：

- Bambu Lab H2D
- Bambu Lab X1 Carbon
- Bambu Lab P1P
- Bambu Lab P1S
- Bambu Lab A1 系列

**无需额外配置文件**，直接通过命令行参数 `--printer "Bambu Lab H2D"` 即可使用。

## 命令行使用

### 基础切片命令

```bash
orcaslicer --export-gcode \
    --printer "Bambu Lab H2D" \
    --layer-height 0.2 \
    --fill-density 20% \
    --output output.gcode \
    input.stl
```

### 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--printer` | 打印机型号 | `"Bambu Lab H2D"` |
| `--layer-height` | 层高 (mm) | `0.2` |
| `--fill-density` | 填充率 | `20%` |
| `--speed` | 打印速度 (mm/s) | `150` |
| `--support-material` | 启用支撑 | (无参数值) |
| `--brim-width` | Brim 宽度 (mm) | `5` |
| `--output` | 输出文件路径 | `output.gcode` |

## 自定义配置 (可选)

如果需要更高级的自定义配置，可以：

1. 在 OrcaSlicer GUI 中创建配置文件
2. 导出为 `.ini` 文件
3. 放置在此目录下
4. 使用 `--load config.ini` 参数加载

## 配置文件示例

```ini
[print:Bambu H2D Standard]
layer_height = 0.2
fill_density = 20%
support_material = 0
brim_width = 5

[printer:Bambu Lab H2D]
bed_shape = 0x0,256x0,256x256,0x256
max_print_height = 256
nozzle_diameter = 0.4
```

## 环境变量

在 Docker 容器中运行 OrcaSlicer AppImage 需要设置：

```bash
export APPIMAGE_EXTRACT_AND_RUN=1
```

这个环境变量已在 Dockerfile 中配置。

## 参考资源

- [OrcaSlicer GitHub](https://github.com/SoftFever/OrcaSlicer)
- [OrcaSlicer Wiki](https://github.com/SoftFever/OrcaSlicer/wiki)
- [Bambu Lab 官方文档](https://wiki.bambulab.com/)
