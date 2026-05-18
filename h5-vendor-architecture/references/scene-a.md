# 场景 A — 架构改造

不改业务逻辑，将项目改造为 script 标签加载 + Vite external 架构（`static-app/vendor/` 框架文件本地加载）。

## 约束

- 以目标项目当前 vendor 架构为准（如 `vite.config.ts` / `scripts/build-static.mjs` / `static-app/vendor`）。
- 仅改构建链路，不改业务页面与业务接口逻辑。

---

## Step 1. 技术栈评估

- 识别当前项目构建工具（Vite / Webpack）、框架版本
- 确认 `react`、`react-dom` 等框架库已安装

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（技术栈评估）完成

---

## Step 2. vendor 架构建立

完整步骤见 `h5-vendor-architecture/references/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

**→ 写入 checkpoint**: Step 2（vendor 架构建立）完成

---

## Step 3. 自动测试验收

完整步骤见 `h5-testing-checklist/references/testing-workflow.md`。重点检查 1/2/3/3.5/10/11/12/13/14，跳过 4-9（未改业务逻辑）。

**→ 写入 checkpoint**: Step 3（自动测试验收）完成

---

## Step 4. 交付

完整步骤见 `h5-testing-checklist/references/delivery.md`。输出架构改造清单（改了哪些配置文件）、测试结果、待用户验收项。

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查 `build-static.mjs` 和 `vite.config.ts`（或 `vite.config.js`）配置，确认所有 vendor 库路径、external 列表、全局变量映射正确后重试
- **业务入口被误改**：若为适配 vendor 修改了 `src/main.tsx`、路由入口或业务页面，立即回退业务改动，将适配迁移到 `vite.config.ts`（例如使用 build-only 虚拟模块处理 `react-dom/client`）
- **vendor 执行时机报错**：若出现 `antd-mobile.js` 的 `document.body.appendChild` 空指针错误，检查 vendor `<script>` 是否带 `defer`，且是否注入到最终 `dist/index.html` 的 `<head>` 最前面
- **vendor 注入顺序错误**：若 vendor 标签在 Vite polyfill、主包或 modulepreload 后面，检查 `vendorScriptsPlugin` 是否使用 `transformIndexHtml.order = 'post'` 并插入 `<head>` 之后
- **vendor 校验失败**：检查 `FRAMEWORK_GLOBALS` 映射是否完整、node_modules 中对应包是否已安装
- **dev server 无法加载 static-app 资源**：检查 `vite.config.ts`（或 `vite.config.js`）中的 `static-files` 中间件配置
- **测试未通过**：修复对应问题后重跑单项测试，不阻塞整体交付
