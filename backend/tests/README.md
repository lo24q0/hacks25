# 打印机适配模块测试文档

## 测试概述

本测试套件为打印机适配模块提供全面的测试覆盖,包括单元测试、集成测试和API测试。

## 测试结构

```
tests/
├── conftest.py              # pytest配置和公共fixtures
├── unit/                    # 单元测试
│   ├── domain/             # 领域模型测试
│   │   ├── test_print_task.py       (15个测试)
│   │   ├── test_printer.py          (9个测试)
│   │   └── test_slicing_config.py   (7个测试)
│   ├── infrastructure/     # 基础设施层测试
│   │   └── test_mock_slicer.py      (6个测试)
│   └── api/                # API层测试
│       └── test_prints_router.py    (8个测试)
```

## 运行测试

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行领域模型测试
pytest tests/unit/domain/

# 运行特定测试文件
pytest tests/unit/domain/test_print_task.py
```

## 测试覆盖率目标

- 领域层: >80%
- 应用服务层: >70%
- API层: >60%
- 总体: >70%

总测试用例数: **45个**
