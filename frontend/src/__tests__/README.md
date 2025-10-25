# 前端测试目录

## 目录结构

```
__tests__/
├── unit/          # 单元测试
│   ├── components/  # 组件测试
│   ├── hooks/       # Hooks测试
│   └── utils/       # 工具函数测试
├── integration/   # 集成测试
│   ├── features/    # 功能模块测试
│   └── api/         # API调用测试
└── e2e/           # 端到端测试
    └── flows/       # 用户流程测试
```

## 测试工具

- **Vitest**: 测试运行器
- **React Testing Library**: 组件测试
- **MSW**: API mock
- **Playwright/Cypress**: E2E测试(待引入)

## 运行测试

```bash
# 运行所有测试
npm run test

# 监听模式
npm run test:watch

# 覆盖率报告
npm run test:coverage
```

## 测试规范

### 组件测试
- 测试用户交互行为
- 避免测试实现细节
- 使用 data-testid 而非 className

### Hooks测试
- 使用 @testing-library/react-hooks
- 测试状态变化和副作用

### 工具函数测试
- 纯函数单元测试
- 覆盖边界条件

## 测试命名

测试文件: `<ComponentName>.test.tsx` 或 `<utilName>.test.ts`

测试用例:
```typescript
describe('ModelPreview', () => {
  it('should render 3D scene when model is loaded', () => {
    // ...
  })
  
  it('should show loading state while model is loading', () => {
    // ...
  })
})
```
