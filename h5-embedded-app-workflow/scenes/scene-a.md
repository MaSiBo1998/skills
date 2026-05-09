# 场景 A — 架构改造

不改业务逻辑，将项目改造为 script 标签加载 + Vite external 架构（`static-app/vendor/` 框架 JS 文件本地加载）。

---

## Step 1. 技术栈评估

- 识别当前项目构建工具（Vite / Webpack）、框架版本
- 确认 `react`、`react-dom` 等框架库在 `devDependencies` 中

**→ 写入 checkpoint**：更新 `.workflow-checkpoint.json`，标记 Step 1（技术栈评估）完成

---

## Step 2. vendor 架构建立

完整步骤见 `scenes/common/vendor-setup.md`。创建相关文件后执行 `npm run build:static`。

**→ 写入 checkpoint**: Step 2（vendor 架构建立）完成

---

## Step 3. 图片迁移

`build:static` 会自动将 `src/assets/` 迁移到 `static-app/images/`。将代码中残留的 `import from '@/assets/...'` 替换为 STATIC_URL。

**→ 写入 checkpoint**: Step 3（图片迁移）完成

---

## Step 4. 自动测试验收

完整步骤见 `scenes/common/testing.md`。重点检查 1/2/3/3a/11/12/13/14，跳过 4-10（未改业务逻辑）。

**→ 写入 checkpoint**: Step 4（自动测试验收）完成

---

## Step 5. 交付

输出：
- 场景 A — 架构改造清单（改了哪些配置文件）
- 测试结果
- Skill 改进建议：列出问题 → **询问用户是否更新技能文件**，确认后立即修改对应文件

**→ 清理 checkpoint**: 删除 `.workflow-checkpoint.json`，工作流完成

---

## 错误处理

- **构建失败**：检查 `build-static.mjs` 和 `vite.config.js` 配置，确认所有 vendor 库的路径和全局变量名正确后重试
- **vendor 校验失败**：检查 `FRAMEWORK_GLOBALS` 映射是否完整、node_modules 中对应包是否已安装
- **dev server 无法加载 static-app 资源**：检查 vite.config.js 中的 static-files 中间件配置
- **测试未通过**：修复对应问题后重跑单项测试，不阻塞整体交付
