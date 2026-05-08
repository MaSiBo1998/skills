# 场景 B — 架构改造

不改业务逻辑，将项目改造为 script 标签加载 + Vite external 架构（`static-app/vendor/` 框架 JS 文件本地加载）。

---

## Step 1. 技术栈评估

- 识别当前项目构建工具（Vite / Webpack）、框架版本
- 确认 `react`、`react-dom` 等框架库在 `devDependencies` 中
- 检查 `node_modules` 中是否有对应包

---

## Step 2. vendor 架构建立

完整步骤见 `scenes/common/vendor-setup.md`。创建 `scripts/build-static.mjs`、更新 `vite.config.js`、更新 `index.html`、配置 `package.json`，然后执行 `npm run build:static`。

---

## Step 3. 图片迁移

将 `src/assets/` 图片迁移到 `static-app/images/`（`build:static` 会自动执行此步骤）。

代码中将引用被迁移图片的 `import` 替换为 `STATIC_URL` 路径：

```js
const STATIC_URL = document.querySelector('meta[name="app-resource"]')?.content || '/static-app/'
<img src={`${STATIC_URL}images/logo.png`} />
```

---

## Step 4. 自动测试验收

运行测试清单（逐项执行，输出 通过/失败）：

```
□ 1. 类型检查（tsc --noEmit）
□ 2. Lint（eslint）
□ 3. 构建测试（npm run build）
□ 3a. vendor 完整性校验
□ 4. 页面渲染检查
□ 11. H5 内嵌规范检查
□ 12. 浏览器兼容检查
□ 13. 构建架构检查 —— dist/ 不含 7 个 vendor 库、index.html 有 script 标签
□ 14. 性能检查
```

---

## Step 5. 交付

输出：
- 场景 B 架构改造清单（改了哪些配置文件）
- 测试结果
- **Skill 改进建议**：发现的问题 + 优化建议，同步更新到 SKILL.md
