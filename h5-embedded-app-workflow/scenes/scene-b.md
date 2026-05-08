# 场景 B — 架构改造

不改业务逻辑，将项目改造为 script 标签加载 + Vite external 架构（`static-app/vendor/` 框架 JS 文件本地加载）。

---

## Step 1. 技术栈评估

- 识别当前项目构建工具（Vite / Webpack）、框架版本
- 确认 `react`、`react-dom` 等框架库在 `devDependencies` 中

---

## Step 2. vendor 架构建立

完整步骤见 `scenes/common/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

---

## Step 3. 图片迁移

`build:static` 会自动将 `src/assets/` 迁移到 `static-app/images/`。将代码中残留的 `import from '@/assets/...'` 替换为 STATIC_URL。

---

## Step 4. 自动测试验收

完整步骤见 `scenes/common/testing.md`。重点检查 1/2/3/3a/11/12/13/14，跳过 4-10（未改业务逻辑）。

---

## Step 5. 交付

输出：
- 场景 B — 架构改造清单（改了哪些配置文件）
- 测试结果
- Skill 改进建议
