# 开发工具配置指南

## 概述

本项目已配置以下代码质量工具:
- **Python**: Black, Flake8, MyPy
- **TypeScript/JavaScript**: ESLint, Prettier
- **Git Hooks**: pre-commit

## 安装开发依赖

### 后端 (Python)

```bash
cd backend
pip install -r requirements.txt
```

或使用可选开发依赖:

```bash
pip install -e ".[dev]"
```

### 前端 (Node.js)

```bash
cd frontend
npm install
```

## Pre-commit 配置

### 安装 pre-commit

```bash
# 使用 pip
pip install pre-commit

# 或使用 homebrew (macOS)
brew install pre-commit
```

### 安装 Git Hooks

在项目根目录运行:

```bash
pre-commit install
```

### 手动运行检查

```bash
# 检查所有文件
pre-commit run --all-files

# 检查暂存的文件
pre-commit run

# 检查特定文件
pre-commit run --files backend/src/main.py
```

## 代码格式化

### Python (Black)

```bash
cd backend
black src/
```

配置: `backend/pyproject.toml`
- 最大行长度: 100
- 目标 Python 版本: 3.10, 3.11, 3.12

### TypeScript (Prettier)

```bash
cd frontend
npm run format
# 或
npx prettier --write "src/**/*.{ts,tsx,js,jsx,css,json}"
```

配置: `frontend/.prettierrc`
- 无分号
- 单引号
- 最大行宽: 100

## 代码检查

### Python (Flake8)

```bash
cd backend
flake8 src/
```

配置: `backend/.flake8`
- 最大行长度: 100
- 最大复杂度: 10
- 忽略规则: E203 (Black兼容), W503

### TypeScript (ESLint)

```bash
cd frontend
npm run lint
# 或
npx eslint "src/**/*.{ts,tsx}"
```

配置: `frontend/eslint.config.js`
- TypeScript 严格模式
- React Hooks 规则
- React Refresh 规则

### Python (MyPy 类型检查)

```bash
cd backend
mypy src/
```

配置: `backend/pyproject.toml`
- 严格模式 (strict = true)
- Python 版本: 3.10

## 测试

### 后端测试

```bash
cd backend
pytest

# 查看覆盖率
pytest --cov=src --cov-report=html

# 运行特定测试
pytest tests/unit/domain/
```

测试目录结构:
```
tests/
├── unit/          # 单元测试 (目标覆盖率 80%)
├── integration/   # 集成测试 (目标覆盖率 30%)
└── e2e/           # 端到端测试 (目标覆盖率 10%)
```

### 前端测试

```bash
cd frontend
npm run test

# 监听模式
npm run test:watch

# 覆盖率
npm run test:coverage
```

测试目录: `frontend/src/__tests__/`

## IDE 配置建议

### VS Code

推荐安装以下扩展:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Flake8 (ms-python.flake8)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)

`.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm

1. Settings → Tools → Black → Enable on save
2. Settings → Tools → External Tools → 添加 Flake8
3. Settings → Editor → Inspections → 启用 MyPy

## CI/CD 集成

pre-commit 配置已包含在 `.pre-commit-config.yaml` 中,可在 CI 环境运行:

```bash
pre-commit run --all-files
```

GitHub Actions 示例:

```yaml
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```

## 常见问题

### Q: pre-commit 运行很慢?
A: 首次运行会安装依赖,后续运行会快很多。可使用 `--no-verify` 跳过 hooks (不推荐)。

### Q: MyPy 报错 "Missing type annotation"?
A: 确保函数参数和返回值都有类型注解,这是严格模式的要求。

### Q: Flake8 和 Black 冲突?
A: 配置文件已处理兼容性 (E203, W503),如仍有问题请检查 `.flake8` 配置。

### Q: ESLint 升级后配置文件格式不兼容?
A: 项目使用 ESLint 9.x 的新配置格式 (eslint.config.js),旧版 `.eslintrc` 不兼容。

## 更多信息

- [Black 文档](https://black.readthedocs.io/)
- [Flake8 文档](https://flake8.pycqa.org/)
- [MyPy 文档](https://mypy.readthedocs.io/)
- [ESLint 文档](https://eslint.org/docs/)
- [Prettier 文档](https://prettier.io/docs/)
- [pre-commit 文档](https://pre-commit.com/)
