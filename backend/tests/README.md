# 后端测试目录

## 目录结构

```
tests/
├── unit/              # 单元测试 (60%覆盖率目标)
│   ├── domain/        # 领域层测试
│   ├── application/   # 应用服务层测试
│   ├── infrastructure/# 基础设施层测试
│   └── api/           # API层测试
├── integration/       # 集成测试 (30%覆盖率目标)
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── api/
└── e2e/               # 端到端测试 (10%覆盖率目标)
    └── workflows/     # 完整业务流程测试
```

## 测试规范

### 单元测试
- 测试单个函数或类的行为
- 使用 mock 隔离外部依赖
- 快速执行,适合频繁运行
- 覆盖率目标: >80% (领域层), >70% (应用层), >60% (API层)

### 集成测试
- 测试多个组件协作
- 可使用真实依赖(数据库、Redis等)
- 验证接口契约
- 运行时间较长

### 端到端测试
- 测试完整业务流程
- 从 API 请求到响应的全链路
- 覆盖关键用户场景
- 数量少但价值高

## 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/domain/test_model3d.py

# 查看覆盖率报告
pytest --cov=src --cov-report=html
```

## 测试命名规范

测试文件: `test_<module_name>.py`
测试类: `Test<ClassName>`
测试函数: `test_<function_name>_<scenario>_<expected_result>`

示例:
```python
def test_model3d_start_generation_changes_status_to_processing():
    pass

def test_model3d_mark_completed_when_file_path_is_none_raises_error():
    pass
```
